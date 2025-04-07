# routes/groups.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.forms.groups import GroupForm, GroupEditForm
from app.models.group import Group
from app.models.user import User

groups_bp = Blueprint("groups", __name__)

@groups_bp.route("/groups", methods=["GET", "POST"])
@login_required
def manage_groups():
    """Handle group creation/deletion and list user's groups."""
    form = GroupForm()

    # Group creation logic
    if form.validate_on_submit():
        new_group = Group(name=form.name.data, description=form.description.data)
        db.session.add(new_group)
        db.session.commit()
        new_group.add_member(user_id=current_user.id, role=2)
        db.session.commit()
        flash("Group created successfully!", "success")
        return redirect(url_for("groups.manage_groups"))

    # Group deletion
    if request.method == "POST" and "remove_group" in request.form:
        group = Group.query.get(request.form["remove_group"])
        if not group:
            flash("Group not found", "danger")
        elif not group.is_owner(user_id=current_user.id):
            flash("Permission denied", "danger")
        else:
            db.session.delete(group)
            db.session.commit()
            flash("Group deleted", "success")
        return redirect(url_for("groups.manage_groups"))

    sorted_groups = sorted(current_user.groups, key=lambda g: g.name.lower())

    return render_template("groups/main.html", form=form, groups=sorted_groups)

@groups_bp.route("/group/<int:group_id>/manage", methods=["GET", "POST"])
@login_required
def manage_single_group(group_id: int):
    """Manage group settings and members."""
    group = Group.query.get(group_id)

    # Group existence check
    if not group:
        flash("Group not found", "danger")
        return redirect(url_for("groups.manage_groups"))

    # Membership check
    if current_user not in group.members:
        flash("Access denied", "danger")
        return redirect(url_for("groups.manage_groups"))

    form = GroupEditForm(obj=group)

    if form.validate_on_submit():
        modified = False
        flash_count = 0

        # Group metadata updates (owner/admins only)
        if ((group.is_owner(current_user.id) or current_user in group.admins) and
                (form.name.data != group.name or form.description.data != group.description)):
                group.name = form.name.data
                group.description = form.description.data
                modified = True
                flash("Group details updated!", "success")
                flash_count += 1

        # Add member logic
        new_member_username = request.form.get("new_member_username")
        if new_member_username:
            new_member = User.query.filter_by(username=new_member_username).first()
            if new_member:
                if new_member == current_user:
                    flash("Cannot add yourself", "warning")
                    flash_count += 1
                elif new_member in group.members:
                    flash("User already in group", "warning")
                    flash_count += 1
                else:
                    group.add_member(user_id=new_member.id)
                    modified = True
                    flash(f"Added {new_member_username}", "success")
                    flash_count += 1
            else:
                flash('User not found', 'danger')
                flash_count += 1

        # Remove member (owner/admins only)
        remove_username = request.form.get("remove_member_username")
        if remove_username:
            remove_member = User.query.filter_by(username=remove_username).first()
            if remove_member:

                if remove_member not in group.members:
                    flash(f"{remove_username} is not a member", "warning")
                    flash_count += 1
                    return redirect(url_for("groups.manage_single_group", group_id=group_id))

                remover_role = group.get_user_role(current_user.id)
                target_role = group.get_user_role(remove_member.id)

                # Removal logic
                if current_user == remove_member:
                    flash("Cannot remove yourself", "warning")
                    flash_count += 1
                elif target_role == 2:
                    flash("Cannot remove owner", "warning")
                    flash_count += 1
                elif remover_role == 2:
                    group.remove_member(user_id=remove_member.id)
                    modified = True
                    flash(f"Removed {remove_username}", "success")
                    flash_count += 1
                elif remover_role == 1 and target_role == 0:
                    group.remove_member(user_id=remove_member.id)
                    modified = True
                    flash(f"Removed {remove_username}", "success")
                    flash_count += 1
                elif remover_role == 1:
                    flash("Admins cannot remove other admins", "danger")
                    flash_count += 1
                else:
                    flash("Permission denied", "danger")
                    flash_count += 1
            else:
                flash('User not found', 'danger')
                flash_count += 1

        # Role updates
        if group.is_owner(current_user.id):
            admin_ids = [int(id_str) for id_str in request.form.getlist("admins")]
            for user in group.members:
                if group.is_owner(user.id):
                    continue

                current_role = group.get_user_role(user.id)
                target_role = 1 if user.id in admin_ids else 0

                if current_role is not None and current_role != target_role:
                    group.update_role(user_id=user.id, new_role=target_role)
                    modified = True
                    flash("Group permission updated", "success")
                    flash_count += 1

        # Commit changes if ANY modification occurred
        if modified:
            db.session.commit()
        elif flash_count == 0:
            flash("No changes were made.", "info")

        return redirect(url_for("groups.manage_single_group", group_id=group_id))

    # Sort members: current user first, then owner, admins, members
    members = []
    for user in group.members:
        role = "Owner" if group.is_owner(user.id) else "Admin" if user in group.admins else "Member"
        members.append({
            "id": user.id,
            "username": user.username,
            "role": role,
            "is_you": user == current_user
        }
        )

    # Sort members
    members.sort(key=lambda x: (0 if x["is_you"] else 1 if x["role"] == "Owner" else 2, x["username"].lower()))


    members.sort(key=lambda x: (
        0 if x["is_you"] else
        1 if x['role'] == "Owner" else
        2 if x['role'] == "Admin" else 3,
        x["username"].lower()
    ))

    return render_template("groups/manage.html", form=form, group=group, members=members)