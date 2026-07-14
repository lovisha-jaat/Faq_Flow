import re

from config import Config
from services.database_service import fetch_all


def normalize_text(text):
    """
    Convert text into lowercase and remove special characters.
    """

    text = text.lower()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def calculate_match_score(user_question, faq_question):
    """
    Calculate similarity score between
    user question and FAQ question.
    """

    user_words = set(normalize_text(user_question).split())
    faq_words = set(normalize_text(faq_question).split())

    stop_words = {
        "the",
        "is",
        "are",
        "a",
        "an",
        "to",
        "of",
        "for",
        "on",
        "at",
        "can",
        "i",
        "you",
        "my",
        "your",
        "how",
        "what",
        "when",
        "where",
        "do",
        "does"
    }

    user_words -= stop_words
    faq_words -= stop_words

    if len(user_words) == 0 or len(faq_words) == 0:
        return 0

    common = user_words.intersection(faq_words)

    total = user_words.union(faq_words)

    score = len(common) / len(total)

    return score


def get_company_faqs(company_id):
    """
    Return all FAQs of a company.
    """

    query = """
        SELECT *
        FROM faqs
        WHERE company_id = ?
    """

    return fetch_all(
        Config.DATABASE_PATH,
        query,
        (company_id,)
    )


def find_best_faq(company_id, user_question):
    """
    Find best matching FAQ.
    """

    faqs = get_company_faqs(company_id)

    best_faq = None
    best_score = 0

    for faq in faqs:

        score = calculate_match_score(
            user_question,
            faq["question"]
        )

        if score > best_score:

            best_score = score

            best_faq = faq

    return best_faq, best_score


def search_faq(company_id, user_question):
    """
    Return chatbot answer.
    """

    faq, score = find_best_faq(
        company_id,
        user_question
    )

    if faq and score >= 0.15:

        return {
            "status": "answered",
            "answer": faq["answer"],
            "category": faq["category"],
            "score": round(score, 2)
        }

    return {
        "status": "unanswered",
        "answer": "Sorry, I couldn't find an answer for this question.",
        "category": "Unknown",
        "score": 0
    }