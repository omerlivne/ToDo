# app/logic/task.py
from app.extensions import db
from app.models.task import Task
from app.models.group import Group

def create_task(name, description, due_date, author, group_id):
    """Create a new task"""
    task = Task(
        name=name,
        description=description,
        due_date=due_date,
        author=author,
        group_id=group_id
    )
    db.session.add(task)
    db.session.commit()
    return task

def delete_task(task):
    """Delete a task"""
    db.session.delete(task)
    db.session.commit()

def update_task(task: Task, name: str, description: str, due_date, status: str) -> None:
    """Update task details"""
    task.name = name
    task.description = description
    task.due_date = due_date
    task.status = status
    db.session.commit()

def get_sorted_tasks(group_id: int, sort_by: str = "due_date"):
    """Query and sort tasks for a group"""
    tasks_query = Task.query.filter_by(group_id=group_id)

    if sort_by == "name":
        tasks_query = tasks_query.order_by(Task.name.asc())
    elif sort_by == "status":
        tasks_query = tasks_query.order_by(Task.status.asc())
    elif sort_by == "creator":
        tasks_query = tasks_query.order_by(Task.author.asc())
    else:  # Default: due_date
        tasks_query = tasks_query.order_by(Task.due_date.asc())

    return tasks_query.all()

def is_task_author(task: Task, username: str) -> bool:
    """Check if user is the task creator"""
    return task.author == username

def is_group_owner_or_admin(group: Group, username: str) -> bool:
    """Check if user owns or administers the group"""
    return (group.owner == username) or (username in group.admins)