from flask import (
    Blueprint,
    request,
    jsonify
)

from services.ai_service import generate_ai_response
from services.database_service import execute_query
from config import Config

api_bp = Blueprint(
    "api",
    __name__
)


@api_bp.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No data received."
        }), 400

    company_id = data.get("company_id")
    question = data.get("question")

    if not company_id or not question:
        return jsonify({
            "status": "error",
            "message": "company_id and question are required."
        }), 400

    result = generate_ai_response(
        company_id,
        question
    )

    execute_query(
        Config.DATABASE_PATH,
        """
        INSERT INTO queries
        (
            company_id,
            user_question,
            bot_answer,
            status
        )
        VALUES
        (?, ?, ?, ?)
        """,
        (
            company_id,
            question,
            result["answer"],
            result["status"]
        )
    )

    return jsonify({
        "status": result["status"],
        "answer": result["answer"],
        "category": result["category"],
        "score": result["score"]
    })


@api_bp.route("/api/health")
def health():

    return jsonify({
        "status": "success",
        "message": "FAQFlow AI API is running."
    })