from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from config import Config
from services.database_service import (
    execute_query,
    fetch_all,
    fetch_one
)

faq_bp = Blueprint(
    "faq",
    __name__
)


def login_required():
    return "user_id" in session


@faq_bp.route("/faqs")
def faq_list():

    if not login_required():
        return redirect(url_for("auth.login"))

    company_id = session["company_id"]

    faqs = fetch_all(
        Config.DATABASE_PATH,
        """
        SELECT *
        FROM faqs
        WHERE company_id=?
        ORDER BY id DESC
        """,
        (company_id,)
    )

    return render_template(
        "faqs/faq_list.html",
        faqs=faqs
    )


@faq_bp.route("/faqs/add", methods=["GET", "POST"])
def add_faq():

    if not login_required():
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        question = request.form.get("question")
        answer = request.form.get("answer")
        category = request.form.get("category")

        execute_query(
            Config.DATABASE_PATH,
            """
            INSERT INTO faqs
            (
                company_id,
                question,
                answer,
                category
            )
            VALUES
            (?, ?, ?, ?)
            """,
            (
                session["company_id"],
                question,
                answer,
                category
            )
        )

        flash(
            "FAQ Added Successfully!",
            "success"
        )

        return redirect(url_for("faq.faq_list"))

    return render_template(
        "faqs/add_faq.html"
    )


@faq_bp.route("/faqs/edit/<int:faq_id>", methods=["GET", "POST"])
def edit_faq(faq_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        question = request.form.get("question")
        answer = request.form.get("answer")
        category = request.form.get("category")

        execute_query(
            Config.DATABASE_PATH,
            """
            UPDATE faqs

            SET
                question=?,
                answer=?,
                category=?

            WHERE id=?
            """,
            (
                question,
                answer,
                category,
                faq_id
            )
        )

        flash(
            "FAQ Updated Successfully!",
            "success"
        )

        return redirect(url_for("faq.faq_list"))

    faq = fetch_one(
        Config.DATABASE_PATH,
        """
        SELECT *
        FROM faqs
        WHERE id=?
        """,
        (faq_id,)
    )

    return render_template(
        "faqs/edit_faq.html",
        faq=faq
    )


@faq_bp.route("/faqs/delete/<int:faq_id>")
def delete_faq(faq_id):

    if not login_required():
        return redirect(url_for("auth.login"))

    execute_query(
        Config.DATABASE_PATH,
        """
        DELETE FROM faqs
        WHERE id=?
        """,
        (faq_id,)
    )

    flash(
        "FAQ Deleted Successfully!",
        "success"
    )

    return redirect(url_for("faq.faq_list"))


@faq_bp.route("/faqs/search")
def search_faq():

    if not login_required():
        return redirect(url_for("auth.login"))

    keyword = request.args.get("keyword", "")

    company_id = session["company_id"]

    faqs = fetch_all(
        Config.DATABASE_PATH,
        """
        SELECT *
        FROM faqs

        WHERE company_id=?

        AND
        (
            question LIKE ?
            OR answer LIKE ?
            OR category LIKE ?
        )

        ORDER BY id DESC
        """,
        (
            company_id,
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        )
    )

    return render_template(
        "faqs/faq_list.html",
        faqs=faqs,
        keyword=keyword
    )