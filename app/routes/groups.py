# routes/groups.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.groups import GroupForm, GroupEditForm
from app.models import Group
from app.logic.group import create_group, delete_group, add_member, remove_member, is_group_admin

groups_bp = Blueprint("groups", __name__)


@groups_bp.route("/groups/", methods=["GET", "POST"])
@login_required
def manage_groups():
    # Create group handler
    form = GroupForm()
    if form.validate_on_submit():
        group = create_group(form.name.data, form.description.data, current_user.username)
        if group:
            flash("Group created!", "success")
        else:
            flash("Failed to create group. Please try again.", "danger")
        return redirect(url_for("groups.manage_groups"))

    # Delete group handler
    if request.method == "POST" and "remove_group" in request.form:
        group = Group.query.get(request.form["remove_group"])
        success = delete_group(group, current_user.username) if group else False
        flash("Group deleted!" if success else "Unauthorized", "success" if success else "danger")
        return redirect(url_for("groups.manage_groups"))

    return render_template("groups/main.html", form=form, groups=current_user.groups)

@groups_bp.route("/groups/<int:group_id>/manage", methods=["GET", "POST"])
@login_required
def manage_single_group(group_id):
    group = Group.query.get_or_404(group_id)

    if form.validate_on_submit():
        # Update group details
        if current_user.username == group.owner or group.is_admin(current_user.username):
            if group_logic.update_group(group, form.name.data, form.description.data):
                action_performed = True

        # Add member
        new_member = request.form.get("new_member_username")
        if new_member:
            # ... validation logic ...
            group_logic.add_member(group, new_member)

        # Remove member
        remove_member = request.form.get("remove_member_username")
        if remove_member:
            success = group_logic.remove_member(group, remove_member)
            if success:
                flash(f"Removed {remove_member}", "success")
                action_performed = True

        # Update admin status
        if current_user.username == group.owner:
            new_admins = request.form.getlist("admins")
            for member in group.members:
                if member != group.owner:
                    is_admin = member in new_admins
                    if group_logic.update_member_permission(group, member, is_admin):
                        action_performed = True

        if not action_performed:
            flash("Group updated", "success")

        return redirect(url_for("groups.manage_single_group", group_id=group_id))

    # Pre-fill form and prepare member list
    form.name.data = group.name
    form.description.data = group.description

    # Build sorted member list
    members = []
    for username in group.members:
        role = "Owner" if username == group.owner else "Admin" if username in group.admins else "Member"
        display_name = "You" if username == current_user.username else username
        members.append({"username": username, "display_name": display_name, "role": role})

    # Sort: You > Owner > Admins > Members (alphabetical)
    members.sort(key=lambda x: (
        0 if x["display_name"] == "You" else
        1 if x["role"] == "Owner" else
        2 if x["role"] == "Admin" else 3,
        x["display_name"].lower()
    ))

    return render_template("groups/manage.html", form=form, group=group, members=members)