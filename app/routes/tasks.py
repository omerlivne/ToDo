# routes/tasks.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.tasks import TaskForm, TaskEditForm
from app.models.task import Task
from app.models import User
from app.models.group import Group
from app.extensions import db
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route('/group/<int:group_id>/tasks', methods=['GET', 'POST'])
@login_required
def manage_tasks(group_id):
    """Handle task listing creation"""

    group = Group.query.get(group_id)

    # Group existence check
    if not group:
        flash("Group not found", "danger")
        return redirect(url_for("groups.manage_groups"))

    # Membership check
    if current_user not in group.members:
        flash("Access denied", "danger")
        return redirect(url_for("groups.manage_groups"))

    # Create new task
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            name=form.name.data,
            description=form.description.data,
            due_date=form.due_date.data,
            author_id=current_user.id,
            group_id=group_id
        )
        db.session.add(new_task)
        db.session.commit()
        flash("Task created successfully!", "success")
        return redirect(url_for("tasks.manage_tasks", group_id=group_id))

    # Handle task deletion
    if request.method == "POST" and "delete_task" in request.form:
        task = Task.query.get(request.form["delete_task"])
        if task and task.group_id == group_id:
            if current_user.id == task.author_id or group.is_owner(current_user.id) or current_user in group.admins:
                db.session.delete(task)
                db.session.commit()
                flash("Task deleted", "success")
            else:
                flash("Unauthorized action", "danger")
        else:
            flash("Task not found", "danger")
        return redirect(url_for("tasks.manage_tasks", group_id=group_id))

    # Sorting tasks
    sort_by = request.args.get("sort", "due_date")
    sorted_tasks = sorted(group.tasks, key=lambda t: (
        {
            "due_date": t.due_date or datetime.max,
            "name": t.name.lower(),
            "status": ["Pending", "In Progress", "Completed"].index(t.status),
            "creator": User.query.get(t.author_id).username.lower()
        }.get(sort_by, "due_date"),  # Primary sort key
        t.name.lower()  # Secondary sort by name for all options
    )
                          )

    return render_template("tasks/main.html",
                         form=form,
                         tasks=sorted_tasks,
                         group=group,
                         sort=sort_by,
                         User=User)

@tasks_bp.route('/task/<int:task_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_single_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        flash("Task not found", "danger")
        return redirect(url_for("groups.manage_groups"))

    group = Group.query.get(task.group_id)

    # Group existence check
    if not group:
        flash("Group not found", "danger")
        return redirect(url_for("groups.manage_groups"))

    # Membership check
    if current_user not in group.members:
        flash("Access denied", "danger")
        return redirect(url_for("groups.manage_groups"))

    form = TaskEditForm(obj=task)

    if form.validate_on_submit():
        modified = False

        if current_user.id == task.author_id or group.is_owner(current_user.id) or current_user in group.admins:
            if form.name.data != task.name or form.description.data != group.description or form.due_date.data != task.due_date:
                task.name = form.name.data
                task.description = form.description.data
                task.due_date = form.due_date.data
                modified = True

        # Always allow status updates
        if form.status.data != task.status:
            task.status = form.status.data
            modified = True

        if modified:
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('tasks.manage_tasks', group_id=group.id))
        else:
            flash('No changes were made.', 'info')
            return redirect(url_for('tasks.manage_single_task', task_id=task_id))

    # Pass authorization status to template
    return render_template('tasks/manage.html',
                           form=form,
                           task=task,
                           group=group)