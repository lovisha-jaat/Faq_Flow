from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for
)

from config import Config
from services.database_service import fetch_one, fetch_all

dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


def login_required():
    """
    Check whether user is logged in.
    """

    if "user_id" not in session:
        return False

    return True


@dashboard_bp.route("/dashboard")
def dashboard():

    if not login_required():
        return redirect(url_for("auth.login"))

    company_id = session["company_id"]

    total_faqs = fetch_one(

        Config.DATABASE_PATH,

        """
        SELECT COUNT(*) AS total
        FROM faqs
        WHERE company_id=?
        """,

        (company_id,)

    )

    total_queries = fetch_one(

        Config.DATABASE_PATH,

        """
        SELECT COUNT(*) AS total
        FROM queries
        WHERE company_id=?
        """,

        (company_id,)

    )

    answered = fetch_one(

        Config.DATABASE_PATH,

        """
        SELECT COUNT(*) AS total
        FROM queries

        WHERE company_id=?
        AND status='answered'
        """,

        (company_id,)

    )

    unanswered = fetch_one(

        Config.DATABASE_PATH,

        """
        SELECT COUNT(*) AS total
        FROM queries

        WHERE company_id=?
        AND status='unanswered'
        """,

        (company_id,)

    )

    recent_queries = fetch_all(

        Config.DATABASE_PATH,

        """
        SELECT *

        FROM queries

        WHERE company_id=?

        ORDER BY id DESC

        LIMIT 10
        """,

        (company_id,)

    )

    return render_template(

        "dashboard/dashboard.html",

        total_faqs=total_faqs["total"],

        total_queries=total_queries["total"],

        answered_queries=answered["total"],

        unanswered_queries=unanswered["total"],

        recent_queries=recent_queries

    )


@dashboard_bp.route("/profile")
def profile():

    if not login_required():
        return redirect(url_for("auth.login"))

    user = fetch_one(

        Config.DATABASE_PATH,

        """
        SELECT
            users.*,
            companies.company_name,
            companies.website,
            companies.description

        FROM users

        JOIN companies

        ON users.company_id=companies.id

        WHERE users.id=?

        """,

        (session["user_id"],)

    )

    return render_template(

        "dashboard/profile.html",

        user=user

    )


@dashboard_bp.route("/settings")
def settings():

    if not login_required():
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard/settings.html"
    )