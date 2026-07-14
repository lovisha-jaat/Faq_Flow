"""
AI Service

Currently this file returns a default response.

Later we will integrate:
- OpenAI GPT
- Google Gemini
- Claude
- Ollama (Local AI)
"""

from services.faq_service import search_faq


def generate_ai_response(company_id, user_question):
    """
    Generate chatbot response.

    Current Version:
    ----------------
    Searches company FAQs.

    Future Version:
    ----------------
    If FAQ is not found,
    call an AI model.
    """

    result = search_faq(
        company_id,
        user_question
    )

    # FAQ Found
    if result["status"] == "answered":
        return result

    # Future AI logic can be added here.
    return {
        "status": "unanswered",
        "answer": (
            "Sorry, I couldn't find an answer in the FAQ database. "
            "Please contact the company for more information."
        ),
        "category": "Unknown",
        "score": 0
    }