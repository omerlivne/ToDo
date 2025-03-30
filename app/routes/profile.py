# routes/profile.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.forms.profile import ProfileEditForm
from app.models.user import User

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def manage_profile():
    """Handles profile updates using validated form inputs."""
    form = ProfileEditForm()
    if form.validate_on_submit():
        action_performed = False

        # Update username if changed
        if form.username.data != current_user.username:
            current_user.update_username(form.username.data)
            action_performed = True

        # Update password if provided
        if form.password.data:
            current_user.update_password(form.password.data)
            action_performed = True

        # Feedback based on actions
        if action_performed:
            flash("Profile updated successfully!", "success")
        else:
            flash("No changes were made.", "info")

        return redirect(url_for("index.home"))

    # Pre-fill the username field
    form.username.data = current_user.username
    return render_template("profile/manage.html", form=form)