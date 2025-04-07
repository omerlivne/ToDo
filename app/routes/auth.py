# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.forms.auth import RegistrationForm, LoginForm
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration with form validation."""

    # Block logged-in users from registration page
    if current_user.is_authenticated:
        return redirect(url_for("index.home"))

    form = RegistrationForm()

    # Process valid registration data
    if form.validate_on_submit():
        # Create user with validated credentials
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # Start authenticated session for new user
        login_user(user)
        flash("Account created! You are now logged in.", "success")
        return redirect(url_for("index.home"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate existing users."""

    # Block logged-in users from login page
    if current_user.is_authenticated:
        return redirect(url_for("index.home"))

    form = LoginForm()

    # Process valid login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Verify credentials against database
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index.home"))

        # Failed authentication guard
        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required  # Restrict to authenticated users only
def logout():
    """Terminate user session securely."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))