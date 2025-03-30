# routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms.auth import RegistrationForm, LoginForm
from app.models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration. Uses RegistrationForm for validation."""
    if current_user.is_authenticated:
        return redirect(url_for("index.home"))  # Prevent logged-in users from re-registering

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.create(username=form.username.data, password=form.password.data)
        login_user(user)
        flash("Account created! You are now logged in.", "success")
        return redirect(url_for("index.home"))

    return render_template("auth/register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticates users. Relies on LoginForm for input sanitization."""
    if current_user.is_authenticated:
        return redirect(url_for("index.home"))  # Block logged-in users from login page

    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("index.home"))
        flash("Invalid credentials.", "danger")  # Generic message for security

    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    """Terminates user sessions. No validation needed for logout actions."""
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))

