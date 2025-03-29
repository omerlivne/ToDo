# routes/profile.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app.forms.profile import ProfileEditForm
from app.extensions import db, bcrypt

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def manage_profile():
    form = ProfileEditForm()
    if form.validate_on_submit():
        # Update username if changed
        if form.username.data != current_user.username:
            current_user.username = form.username.data

        # Update password if provided
        if form.password.data:
            current_user.password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("index.home"))

    # Pre-fill username
    form.username.data = current_user.username
    return render_template("profile/manage.html", form=form)