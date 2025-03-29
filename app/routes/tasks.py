# routes/tasks.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import case, asc, func
from app.forms.tasks import TaskForm, TaskEditForm
from app.models.task import Task
from app.models.group import Group
from app.extensions import db

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/groups/<int:group_id>/tasks", methods=["GET", "POST"])
@login_required
def manage_tasks(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user.username not in group.members:
        flash("Access denied", "danger")
        return redirect(url_for("groups.manage_groups"))

    # Create new task
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            name=form.name.data,
            description=form.description.data,
            due_date=form.due_date.data,
            author=current_user.username,
            group_id=group_id
        )
        db.session.add(task)
        db.session.commit()
        flash("Task created successfully!", "success")
        return redirect(url_for("tasks.manage_tasks", group_id=group_id))

    # Handle task deletion
    if request.method == "POST" and "delete_task" in request.form:
        task = Task.query.get(request.form["delete_task"])
        if task and (current_user.username == task.author
                     or current_user.username == group.owner
                     or group.is_admin(current_user.username)):
            db.session.delete(task)
            db.session.commit()
            flash("Task deleted", "success")
        else:
            flash("Unauthorized action", "danger")
        return redirect(url_for("tasks.manage_tasks", group_id=group_id))

    # Sorting logic
    sort_by = request.args.get("sort", "due_date")
    tasks_query = Task.query.filter_by(group_id=group_id)

    if sort_by == "name":
        tasks_query = tasks_query.order_by(func.lower(Task.name).asc())
    elif sort_by == "status":
        status_order = case(
            (Task.status == "Pending", 0),
            (Task.status == "In Progress", 1),
            (Task.status == "Completed", 2),
            else_=3
        )
        tasks_query = tasks_query.order_by(status_order.asc(), func.lower(Task.name).asc())
    elif sort_by == "creator":
        tasks_query = tasks_query.order_by(func.lower(Task.author).asc())
    else:  # Default: due_date
        tasks_query = tasks_query.order_by(
            asc(Task.due_date).nulls_last() if db.engine.name == "postgresql"
            else case((Task.due_date.is_(None), 1), else_=0).asc(),
            Task.due_date.asc()
        )

    tasks = tasks_query.all()
    return render_template("tasks/main.html", form=form, tasks=tasks, group=group, sort=sort_by)


@tasks_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    group = Group.query.get(task.group_id)

    if current_user.username not in group.members:
        flash('Access denied', 'danger')
        return redirect(url_for('groups.manage_groups'))

    is_authorized = (current_user.username == task.author or
                     current_user.username == group.owner or
                     group.is_admin(current_user.username))

    form = TaskEditForm(obj=task)

    if form.validate_on_submit():
        if is_authorized:  # Only update restricted fields if authorized
            task.name = form.name.data
            task.description = form.description.data
            task.due_date = form.due_date.data

        # Always allow status updates
        task.status = form.status.data
        db.session.commit()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.manage_tasks', group_id=group.id))

    # Pass authorization status to template
    return render_template('tasks/manage.html',
                           form=form,
                           task=task,
                           group=group,
                           can_edit=is_authorized
                           )