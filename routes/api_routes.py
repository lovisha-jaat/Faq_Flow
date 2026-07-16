import os
import sqlite3

from flask import (
    Blueprint,
    current_app,
    jsonify,
    request
)

from services.ai_service import answer_question


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


def get_database_path():
    configured_path = current_app.config.get(
        "DATABASE"
    )

    if configured_path:
        return configured_path

    return os.path.join(
        current_app.root_path,
        "database",
        "faqflow.db"
    )


def save_query(
    company_id,
    question,
    result
):
    connection = sqlite3.connect(
        get_database_path()
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            category TEXT,
            status TEXT,
            similarity REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        INSERT INTO queries (
            company_id,
            question,
            answer,
            category,
            status,
            similarity
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            company_id,
            question,
            result.get("answer"),
            result.get("category"),
            result.get("status"),
            result.get("similarity", 0)
        )
    )

    connection.commit()
    connection.close()


@api_bp.route(
    "/chat",
    methods=["POST"]
)
def chat():
    data = request.get_json(
        silent=True
    ) or {}

    company_id = data.get(
        "company_id"
    )

    question = str(
        data.get("question", "")
    ).strip()

    if not company_id:
        return jsonify({
            "error": "Company ID is required."
        }), 400

    if not question:
        return jsonify({
            "error": "Question is required."
        }), 400

    try:
        result = answer_question(
            company_id,
            question
        )

        save_query(
            company_id,
            question,
            result
        )

        return jsonify(result), 200

    except Exception:
        current_app.logger.exception(
            "Chatbot API error."
        )

        return jsonify({
            "error": (
                "The chatbot could not process "
                "your question."
            )
        }), 500