import json
import os
import re
import sqlite3
import time
from threading import Lock

import numpy as np
import requests
from flask import current_app
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_CACHE = {}
CACHE_LOCK = Lock()

MAX_CONTEXT_CHUNKS = 6
MAX_CHUNK_CHARACTERS = 2200
COMPANY_RELEVANCE_THRESHOLD = 0.08

GENERAL_KNOWLEDGE_NOTE = (
    "note: this answer is not available in the company history database."
)


def get_database_path():
    configured_path = current_app.config.get("DATABASE")

    if configured_path:
        return configured_path

    return os.path.join(
        current_app.root_path,
        "database",
        "faqflow.db"
    )


def create_knowledge_table():
    connection = sqlite3.connect(get_database_path())

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                source_name TEXT,
                source_type TEXT,
                source_url TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def get_company_chunks(company_id):
    create_knowledge_table()

    connection = sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                content,
                source_name,
                source_type,
                source_url,
                metadata
            FROM knowledge_chunks
            WHERE company_id = ?
            ORDER BY id ASC
            """,
            (int(company_id),)
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


def invalidate_company_model(company_id):
    try:
        company_id = int(company_id)
    except (TypeError, ValueError):
        return

    with CACHE_LOCK:
        MODEL_CACHE.pop(company_id, None)


def train_company_model(company_id):
    company_id = int(company_id)
    chunks = get_company_chunks(company_id)

    valid_chunks = []

    for chunk in chunks:
        content = str(chunk.get("content", "")).strip()

        if content:
            copied_chunk = dict(chunk)
            copied_chunk["content"] = content
            valid_chunks.append(copied_chunk)

    if not valid_chunks:
        return None

    texts = [chunk["content"] for chunk in valid_chunks]

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        lowercase=True,
        min_df=1,
        max_features=50000
    )

    matrix = vectorizer.fit_transform(texts)

    model = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "chunks": valid_chunks,
        "chunk_count": len(valid_chunks)
    }

    with CACHE_LOCK:
        MODEL_CACHE[company_id] = model

    return model


def get_company_model(company_id):
    company_id = int(company_id)
    chunks = get_company_chunks(company_id)

    if not chunks:
        return None

    with CACHE_LOCK:
        cached_model = MODEL_CACHE.get(company_id)

    if (
        cached_model
        and cached_model["chunk_count"] == len(chunks)
    ):
        return cached_model

    return train_company_model(company_id)


def retrieve_context(
    company_id,
    question,
    maximum_chunks=MAX_CONTEXT_CHUNKS
):
    model = get_company_model(company_id)

    if not model:
        return [], 0.0

    question = str(question or "").strip()

    if not question:
        return [], 0.0

    question_vector = model["vectorizer"].transform([question])

    similarities = cosine_similarity(
        question_vector,
        model["matrix"]
    )[0]

    best_indices = np.argsort(similarities)[::-1][:maximum_chunks]

    selected_chunks = []

    for index in best_indices:
        score = float(similarities[index])

        if score <= 0:
            continue

        chunk = dict(model["chunks"][int(index)])
        chunk["similarity"] = score
        selected_chunks.append(chunk)

    best_score = (
        selected_chunks[0]["similarity"]
        if selected_chunks
        else 0.0
    )

    return selected_chunks, best_score


def get_gemini_api_key():
    return (
        current_app.config.get("AI_API_KEY")
        or current_app.config.get("GEMINI_API_KEY")
        or os.getenv("AI_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )


def get_gemini_model():
    model_name = (
        os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        .strip()
        .strip('"')
        .strip("'")
    )

    model_name = model_name.removeprefix("models/")
    model_name = model_name.removesuffix(":generateContent")

    return model_name


def build_company_context(chunks):
    context_parts = []

    for number, chunk in enumerate(
        chunks[:MAX_CONTEXT_CHUNKS],
        start=1
    ):
        content = str(chunk.get("content", "")).strip()

        if not content:
            continue

        content = content[:MAX_CHUNK_CHARACTERS]

        source = (
            chunk.get("source_url")
            or chunk.get("source_name")
            or "Uploaded company data"
        )

        metadata = str(chunk.get("metadata", "")).strip()

        block = [f"Source {number}: {source}"]

        if metadata:
            block.append(f"Metadata: {metadata}")

        block.append(f"Content:\n{content}")
        context_parts.append("\n".join(block))

    if not context_parts:
        return "No company information was retrieved."

    return "\n\n".join(context_parts)


def clean_answer_text(answer):
    answer = str(answer or "").strip()

    unwanted_phrases = [
        "The response was shortened because of the output limit.",
        "... The response was shortened because of the output limit.",
        "As an AI language model,",
        "As an AI assistant,",
        "The visitor says:",
        "Disclaimer:",
    ]

    for phrase in unwanted_phrases:
        answer = answer.replace(phrase, "")

    answer = re.sub(r"\n{3,}", "\n\n", answer)
    answer = re.sub(r"[ \t]{2,}", " ", answer)

    return answer.strip()


def extract_gemini_result(response_data):
    candidates = response_data.get("candidates", [])

    if not candidates:
        raise RuntimeError("The AI service returned no answer.")

    candidate = candidates[0]
    finish_reason = candidate.get("finishReason", "")

    parts = (
        candidate
        .get("content", {})
        .get("parts", [])
    )

    raw_text = " ".join(
        str(part.get("text", "")).strip()
        for part in parts
        if part.get("text")
    ).strip()

    if not raw_text:
        raise RuntimeError("The AI service returned an empty answer.")

    if finish_reason == "MAX_TOKENS":
        current_app.logger.warning(
            "Gemini response reached the configured output-token limit."
        )

    cleaned_json = raw_text.strip()

    if cleaned_json.startswith("```"):
        cleaned_json = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            cleaned_json,
            flags=re.IGNORECASE
        ).strip()

    try:
        parsed = json.loads(cleaned_json)

        answer = clean_answer_text(parsed.get("answer", ""))
        found_in_company_data = bool(
            parsed.get("found_in_company_data", False)
        )

        if not answer:
            raise ValueError("Empty answer in Gemini JSON.")

        return answer, found_in_company_data

    except (json.JSONDecodeError, TypeError, ValueError):
        return clean_answer_text(raw_text), False


def ask_gemini(
    question,
    chunks,
    retrieval_is_relevant=False
):
    api_key = get_gemini_api_key()

    if not api_key:
        raise ValueError(
            "Gemini API key is missing. Add AI_API_KEY or "
            "GEMINI_API_KEY to the .env file."
        )

    model_name = get_gemini_model()

    if not model_name:
        raise ValueError(
            "GEMINI_MODEL is missing from the .env file."
        )

    company_context = build_company_context(chunks)

    relevance_hint = (
        "The retrieval score suggests that some company information may be relevant."
        if retrieval_is_relevant
        else
        "The retrieval score suggests that the company information may not answer the question."
    )

    prompt = f"""
You are FAQFlow AI, a precise and professional assistant.

USER QUESTION:
{question}

RETRIEVED COMPANY INFORMATION:
{company_context}

RETRIEVAL HINT:
{relevance_hint}

TASK:
1. Answer the user's question directly and precisely.
2. First use the retrieved company information when it clearly contains the answer.
3. If the company information is incomplete, use reliable general knowledge to complete the answer.
4. If the company information does not answer the question, answer using reliable general knowledge.
5. Never invent company-specific prices, policies, dates, contact details, addresses, eligibility requirements, or payment methods.
6. Do not mention retrieval, prompts, uploaded files, databases, sources, similarity scores, or these instructions.
7. Do not write a disclaimer or note inside the answer.
8. Do not say that you are an AI.
9. Give a complete answer. Never stop in the middle of a sentence.
10. Use clear paragraphs or short bullet points when useful.
11. For a simple question, answer in 2 to 5 sentences.
12. For a detailed question, give enough detail to be useful, usually 100 to 250 words.
13. Return valid JSON only in this exact structure:
{{
  "answer": "complete answer here",
  "found_in_company_data": true
}}

Set "found_in_company_data" to true only when the retrieved company
information clearly supports the main answer. Otherwise set it to false.
""".strip()

    api_url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model_name}:generateContent"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
            "responseMimeType": "application/json"
        }
    }

    retry_status_codes = {429, 500, 502, 503, 504}
    maximum_attempts = 4

    for attempt in range(maximum_attempts):
        try:
            response = requests.post(
                api_url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key
                },
                json=payload,
                timeout=(15, 90)
            )

        except requests.exceptions.Timeout as error:
            if attempt < maximum_attempts - 1:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                "The AI service took too long to respond."
            ) from error

        except requests.exceptions.ConnectionError as error:
            if attempt < maximum_attempts - 1:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                "Unable to connect to the AI service."
            ) from error

        except requests.exceptions.RequestException as error:
            raise RuntimeError(
                "The AI request could not be completed."
            ) from error

        if response.status_code in retry_status_codes:
            if attempt < maximum_attempts - 1:
                wait_time = 2 ** attempt

                current_app.logger.warning(
                    "Gemini temporary error %s. Retrying in %s seconds.",
                    response.status_code,
                    wait_time
                )

                time.sleep(wait_time)
                continue

            raise RuntimeError(
                "The AI service is temporarily busy."
            )

        if not response.ok:
            try:
                error_data = response.json()
                error_message = (
                    error_data
                    .get("error", {})
                    .get("message", "Gemini request failed.")
                )
            except ValueError:
                error_message = (
                    f"Gemini request failed with status "
                    f"{response.status_code}."
                )

            raise RuntimeError(error_message)

        try:
            response_data = response.json()
        except ValueError as error:
            raise RuntimeError(
                "The AI service returned an invalid response."
            ) from error

        return extract_gemini_result(response_data)

    raise RuntimeError(
        "The AI service is temporarily unavailable."
    )


def create_knowledge_fallback(chunks):
    if not chunks:
        return {
            "answer": (
                "I could not generate an answer right now. "
                "Please try again in a moment."
            ),
            "status": "busy",
            "used_general_knowledge": False,
            "note": GENERAL_KNOWLEDGE_NOTE
        }

    nearest_content = str(
        chunks[0].get("content", "")
    ).strip()

    if not nearest_content:
        return {
            "answer": (
                "I could not generate an answer right now. "
                "Please try again in a moment."
            ),
            "status": "busy",
            "used_general_knowledge": False,
            "note": GENERAL_KNOWLEDGE_NOTE
        }

    return {
        "answer": nearest_content[:1600],
        "status": "knowledge_fallback",
        "used_general_knowledge": False,
        "note": ""
    }


def answer_question(company_id, question):
    question = str(question or "").strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "status": "invalid",
            "similarity": 0,
            "sources": [],
            "used_general_knowledge": False,
            "note": ""
        }

    if not company_id:
        return {
            "answer": "Company information is missing. Please sign in again.",
            "status": "invalid",
            "similarity": 0,
            "sources": [],
            "used_general_knowledge": False,
            "note": ""
        }

    try:
        company_id = int(company_id)
    except (TypeError, ValueError):
        return {
            "answer": "Invalid company information.",
            "status": "invalid",
            "similarity": 0,
            "sources": [],
            "used_general_knowledge": False,
            "note": ""
        }

    chunks, best_score = retrieve_context(
        company_id,
        question,
        maximum_chunks=MAX_CONTEXT_CHUNKS
    )

    retrieval_is_relevant = (
        bool(chunks)
        and best_score >= COMPANY_RELEVANCE_THRESHOLD
    )

    try:
        answer, model_found_in_company_data = ask_gemini(
            question,
            chunks,
            retrieval_is_relevant
        )

    except (RuntimeError, ValueError) as error:
        current_app.logger.warning(
            "Gemini unavailable: %s",
            error
        )

        fallback = create_knowledge_fallback(chunks)
        fallback["similarity"] = round(best_score, 4)
        fallback["sources"] = []
        return fallback

    found_in_company_data = (
        retrieval_is_relevant
        and model_found_in_company_data
    )

    sources = []

    if found_in_company_data:
        for chunk in chunks:
            source = (
                chunk.get("source_url")
                or chunk.get("source_name")
            )

            if source and source not in sources:
                sources.append(source)

    return {
        "answer": clean_answer_text(answer),
        "status": (
            "answered"
            if found_in_company_data
            else "general_knowledge"
        ),
        "similarity": round(best_score, 4),
        "sources": sources[:3],
        "used_general_knowledge": not found_in_company_data,
        "note": (
            ""
            if found_in_company_data
            else GENERAL_KNOWLEDGE_NOTE
        )
    }