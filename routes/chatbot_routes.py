from flask import (
    Blueprint,
    redirect,
    render_template,
    session,
    url_for
)


chatbot_bp = Blueprint(
    "chatbot",
    __name__
)


def login_required():
    return "user_id" in session


@chatbot_bp.route("/chatbot")
def chatbot():
    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "chatbot/chatbot.html"
    )


@chatbot_bp.route("/chatbot/preview")
def chatbot_preview():
    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "chatbot/chatbot_preview.html"
    )


@chatbot_bp.route("/chatbot/integration")
def integration():
    if not login_required():
        return redirect(
            url_for("auth.login")
        )

    company_id = session.get("company_id")

    if not company_id:
        return redirect(
            url_for("auth.login")
        )

    widget_code = f"""<!-- FAQFlow AI Chatbot -->
<script
    src="http://127.0.0.1:5000/static/js/widget.js"
    data-company-id="{company_id}"
    data-api-base="http://127.0.0.1:5000"
></script>"""

    return render_template(
        "chatbot/integration.html",
        widget_code=widget_code
    )