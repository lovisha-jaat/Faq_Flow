import os
import sqlite3
from threading import Lock

import numpy as np
import requests
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
    api_key = current_app.config.get(
        "AI_API_KEY"
    ) or os.getenv("AI_API_KEY")

    model_name = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.5-flash"
    )

    if not api_key:
        raise ValueError(
            "AI_API_KEY is missing from the .env file."
        )

    context_parts = []

    for number, chunk in enumerate(
        chunks,
        start=1
    ):
        source = (
            chunk.get("source_url")
            or chunk.get("source_name")
            or "Uploaded data"
        )

        context_parts.append(
            f"""
Source {number}: {source}
Content:
{chunk["content"]}
"""
        )

    context_text = "\n".join(
        context_parts
    )

    prompt = f"""
You are FAQFlow AI, a company knowledge assistant.

Answer the visitor's question using only the supplied company
knowledge.

Rules:
1. Do not invent policies, prices, dates or contact details.
2. Combine information from multiple sources when useful.
3. Give a clear and concise answer.
4. If the answer is not present in the context, reply exactly:
   "I could not find this information in the company's knowledge base."
5. Do not mention TF-IDF, database chunks or internal retrieval.

COMPANY KNOWLEDGE:
{context_text}

VISITOR QUESTION:
{question}
"""

    api_url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model_name}:generateContent"
    )

    response = requests.post(
        api_url,
        params={
            "key": api_key
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 500
            }
        },
        timeout=45
    )

    if not response.ok:
        raise RuntimeError(
            "Gemini API error: "
            + response.text[:300]
        )

    data = response.json()

    candidates = data.get(
        "candidates",
        []
    )

    if not candidates:
        raise RuntimeError(
            "Gemini returned no answer."
        )

    parts = (
        candidates[0]
        .get("content", {})
        .get("parts", [])
    )

    answer = " ".join(
        part.get("text", "")
        for part in parts
    ).strip()

    if not answer:
        raise RuntimeError(
            "Gemini returned an empty answer."
        )

    return answer


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