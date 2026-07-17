import os
import time
import requests

from flask import current_app
import sqlite3
from threading import Lock

import numpy as np
from flask import current_app
from sklearn.feature_extraction.text import (
    TfidfVectorizer
)
from sklearn.metrics.pairwise import (
    cosine_similarity
)


MODEL_CACHE = {}
CACHE_LOCK = Lock()

MINIMUM_SIMILARITY = 0.05
MAX_CONTEXT_CHUNKS = 5


def get_database_path():
    return current_app.config.get(
        "DATABASE",
        os.path.join(
            current_app.root_path,
            "database",
            "faqflow.db"
        )
    )


def create_knowledge_table():
    connection = sqlite3.connect(
        get_database_path()
    )

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
    connection.close()


def get_company_chunks(company_id):
    create_knowledge_table()

    connection = sqlite3.connect(
        get_database_path()
    )

    connection.row_factory = sqlite3.Row

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
        (company_id,)
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def invalidate_company_model(company_id):
    with CACHE_LOCK:
        MODEL_CACHE.pop(
            int(company_id),
            None
        )


def train_company_model(company_id):
    """
    This builds a retrieval index.

    It does not fine-tune Gemini.
    """

    chunks = get_company_chunks(
        company_id
    )

    if not chunks:
        return None

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=25000
    )

    matrix = vectorizer.fit_transform(
        texts
    )

    model = {
        "vectorizer": vectorizer,
        "matrix": matrix,
        "chunks": chunks,
        "chunk_count": len(chunks)
    }

    with CACHE_LOCK:
        MODEL_CACHE[int(company_id)] = model

    return model


def get_company_model(company_id):
    company_id = int(company_id)

    chunks = get_company_chunks(
        company_id
    )

    if not chunks:
        return None

    with CACHE_LOCK:
        model = MODEL_CACHE.get(
            company_id
        )

    if (
        model and
        model["chunk_count"] == len(chunks)
    ):
        return model

    return train_company_model(
        company_id
    )


def retrieve_context(
    company_id,
    question
):
    model = get_company_model(
        company_id
    )

    if not model:
        return [], 0

    question_vector = model[
        "vectorizer"
    ].transform([question])

    scores = cosine_similarity(
        question_vector,
        model["matrix"]
    )[0]

    best_indices = np.argsort(
        scores
    )[::-1][:MAX_CONTEXT_CHUNKS]

    selected_chunks = []

    for index in best_indices:
        score = float(scores[index])

        if score <= 0:
            continue

        chunk = dict(
            model["chunks"][int(index)]
        )

        chunk["similarity"] = score

        selected_chunks.append(chunk)

    best_score = (
        selected_chunks[0]["similarity"]
        if selected_chunks
        else 0
    )

    return selected_chunks, best_score


def ask_gemini(question, chunks):
    """
    Generate an answer using retrieved company knowledge.

    Retries temporary Gemini errors such as 429, 500 and 503.
    """

    api_key = (
        current_app.config.get("AI_API_KEY")
        or os.getenv("AI_API_KEY")
    )

    if not api_key:
        raise ValueError(
            "Gemini API key is missing."
        )

    model_name = os.getenv(
        "GEMINI_MODEL",
        "gemini-flash-latest"
    ).strip()

    # Remove common incorrect values
    model_name = model_name.removeprefix("models/")
    model_name = model_name.removesuffix(
        ":generateContent"
    )

    api_url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model_name}:generateContent"
    )

    context_parts = []

    # Send only the two most relevant chunks
    for number, chunk in enumerate(
        chunks[:2],
        start=1
    ):
        content = str(
            chunk.get("content", "")
        ).strip()

        # Prevent very large prompts
        content = content[:2500]

        source = (
            chunk.get("source_url")
            or chunk.get("source_name")
            or "Uploaded company data"
        )

        context_parts.append(
            f"""
Source {number}: {source}
Company information:
{content}
"""
        )

    context_text = "\n".join(
        context_parts
    )

    prompt = f"""
You are FAQFlow AI, a company support assistant.

Answer the visitor's question using only the company information
provided below.

Rules:
- Do not invent information.
- Give a direct and concise answer.
- Use only the supplied company knowledge.
- If the answer is unavailable, reply:
  "I could not find this information in the company's knowledge base."

Company knowledge:
{context_text}

Visitor question:
{question}
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 300
        }
    }

    retry_status_codes = {
        429,
        500,
        502,
        503,
        504
    }

    maximum_attempts = 4

    for attempt in range(maximum_attempts):
        try:
            response = requests.post(
                api_url,
                params={
                    "key": api_key
                },
                json=payload,
                timeout=(10, 60)
            )

        except requests.exceptions.Timeout:
            if attempt < maximum_attempts - 1:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                "The AI service took too long to respond."
            )

        except requests.exceptions.ConnectionError:
            if attempt < maximum_attempts - 1:
                time.sleep(2 ** attempt)
                continue

            raise RuntimeError(
                "Unable to connect to the AI service."
            )

        if response.status_code in retry_status_codes:
            if attempt < maximum_attempts - 1:
                wait_time = 2 ** attempt

                current_app.logger.warning(
                    "Gemini temporary error %s. "
                    "Retrying in %s seconds.",
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
                    .get(
                        "message",
                        "Gemini request failed."
                    )
                )

            except ValueError:
                error_message = (
                    "Gemini request failed."
                )

            raise RuntimeError(error_message)

        data = response.json()

        candidates = data.get(
            "candidates",
            []
        )

        if not candidates:
            raise RuntimeError(
                "The AI service returned no answer."
            )

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        answer = " ".join(
            part.get("text", "")
            for part in parts
            if part.get("text")
        ).strip()

        if not answer:
            raise RuntimeError(
                "The AI service returned an empty answer."
            )

        return answer

    raise RuntimeError(
        "The AI service is temporarily unavailable."
    )

def answer_question(company_id, question):
    question = str(question).strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "status": "invalid",
            "similarity": 0
        }

    chunks, best_score = retrieve_context(
        company_id,
        question
    )

    if (
        not chunks or
        best_score < MINIMUM_SIMILARITY
    ):
        return {
            "answer": (
                "I could not find this information "
                "in the company's knowledge base."
            ),
            "status": "unanswered",
            "similarity": round(
                best_score,
                4
            )
        }

    answer = ask_gemini(
        question,
        chunks
    )

    sources = []

    for chunk in chunks:
        source = (
            chunk.get("source_url")
            or chunk.get("source_name")
        )

        if source and source not in sources:
            sources.append(source)

    return {
        "answer": answer,
        "status": "answered",
        "similarity": round(
            best_score,
            4
        ),
        "sources": sources[:3]
    }