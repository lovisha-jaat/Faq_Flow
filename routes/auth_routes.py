from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from config import Config
from services.database_service import (
    execute_query,
    fetch_one
)

auth_bp = Blueprint(
    "auth",
    __name__
)
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        company_name = request.form.get("company_name")
        website = request.form.get("website")
        description = request.form.get("description")

        # Check email already exists
        existing_user = fetch_one(
            Config.DATABASE_PATH,
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        if existing_user:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(url_for("auth.register"))

        # Create Company
        company_id = execute_query(
            Config.DATABASE_PATH,

            """
            INSERT INTO companies
            (
                company_name,
                website,
                description
            )
            VALUES
            (?, ?, ?)
            """,

            (
                company_name,
                website,
                description
            )
        )

        hashed_password = generate_password_hash(
            password
        )

        execute_query(

            Config.DATABASE_PATH,

            """
            INSERT INTO users
            (
                name,
                email,
                password,
                company_id
            )
            VALUES
            (?, ?, ?, ?)
            """,

            (
                name,
                email,
                hashed_password,
                company_id
            )

        )

        flash(
            "Registration Successful.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html"
    )
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = fetch_one(

            Config.DATABASE_PATH,

            """
            SELECT
                users.*,
                companies.company_name

            FROM users

            JOIN companies

            ON users.company_id=companies.id

            WHERE email=?

            """,

            (email,)

        )

        if user:

            if check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["id"]

                session["company_id"] = user["company_id"]

                session["company_name"] = user["company_name"]

                session["user_name"] = user["name"]

                flash(
                    "Login Successful.",
                    "success"
                )

                return redirect(
                    url_for("dashboard.dashboard")
                )

        flash(
            "Invalid Email or Password.",
            "danger"
        )

    return render_template(
        "auth/login.html"
    )
@auth_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged Out Successfully.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )