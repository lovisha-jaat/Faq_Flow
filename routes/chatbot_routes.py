from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
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
        return redirect(url_for("auth.login"))

    return render_template(
        "chatbot/chatbot.html"
    )


@chatbot_bp.route("/chatbot/preview")
def chatbot_preview():

    if not login_required():
        return redirect(url_for("auth.login"))

    return render_template(
        "chatbot/chatbot_preview.html"
    )


@chatbot_bp.route("/chatbot/integration")
def integration():

    if not login_required():
        return redirect(url_for("auth.login"))

    company_id = session["company_id"]

    widget_code = f"""
<!-- FAQFlow AI Chatbot -->
<script>
(function() {{
    var script = document.createElement("script");
    script.src = "/static/js/widget.js";
    script.setAttribute("data-company-id", "{company_id}");
    document.body.appendChild(script);
}})();
</script>
"""

    return render_template(
        "chatbot/integration.html",
        widget_code=widget_code
    )