from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(view_function):
    """
    Ensure that the user is logged in before accessing a route.
    """

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:
            flash(
                "Please login first.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        return view_function(*args, **kwargs)

    return wrapped_view