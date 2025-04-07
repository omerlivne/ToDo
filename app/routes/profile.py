# routes/profile.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.extensions import db
from app.forms.profile import ProfileEditForm
from app.models import User

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def manage_profile():
    """Handle profile updates for username and password."""
    form = ProfileEditForm(username=current_user.username)

    if form.validate_on_submit():
        action_performed  = False

        # Username update logic
        if form.username.data != current_user.username:
            current_user.username = form.username.data
            action_performed = True

        # Password update logic
        if form.password.data:
            current_user.password_hash = User.hash_password(form.password.data)
            action_performed = True

        # Commit changes if any
        if action_performed:
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("index.home"))
        else:
            flash("No changes were made.", "info")
            return redirect(url_for("profile.manage_profile"))

    return render_template("profile/manage.html", form=form)