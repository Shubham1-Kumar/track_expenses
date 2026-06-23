import os

from flask import Flask, render_template, redirect, request, session, url_for

from database.db import create_user, get_db, get_user_by_email, init_db, seed_db
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
# Required for flask.session to sign cookies. Override in production via the
# SECRET_KEY env var; the dev fallback keeps the tutorial runnable out of the box.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validation — each branch re-renders the form with the submitted
        # values and an error message. Never redirect on validation failure.
        error = None
        if not name or not email or not password:
            error = "All fields are required."
        elif len(name) > 100:
            error = "Name must be 100 characters or fewer."
        else:
            parts = email.split("@")
            if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
                error = "Please enter a valid email address."
            elif len(password) < 8:
                error = "Password must be at least 8 characters."
            elif get_user_by_email(email) is not None:
                error = "An account with that email already exists."

        if error:
            return render_template("register.html", error=error, name=name, email=email)

        new_id = create_user(name, email, generate_password_hash(password))
        session["user_id"] = new_id
        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Single generic error for "unknown email" and "wrong password" so
        # callers cannot enumerate which accounts exist.
        error = None
        if not email or not password:
            error = "Email and password are required."
        else:
            user = get_user_by_email(email)
            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Invalid email or password."

        if error:
            return render_template("login.html", error=error, email=email)

        session["user_id"] = user["id"]
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    # Safe on an empty session — Flask's session.clear() is a no-op when no
    # keys are set, so this works whether the user is signed in or not.
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    # Bootstrap the data layer once per process before serving requests.
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
