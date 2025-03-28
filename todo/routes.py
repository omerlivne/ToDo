# todo\routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from todo.forms import LoginForm, RegistrationForm, GroupForm, TaskForm, GroupEditForm, ProfileEditForm, TaskEditForm
from todo.models import User, Task, Group, UserGroup, bcrypt
from todo import app, db
from sqlalchemy import func, case, asc, desc

@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Registration successful! You are now logged in', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.username.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Login unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileEditForm(original_username=current_user.username)
    if form.validate_on_submit():
        # Store the old username for updating foreign keys
        old_username = current_user.username

        # Update username if it has changed
        if form.username.data != current_user.username:
            current_user.username = form.username.data

            # Update foreign key references in Group and UserGroup tables
            Group.query.filter_by(owner=old_username).update({"owner": current_user.username})
            UserGroup.query.filter_by(user_id=old_username).update({"user_id": current_user.username})

        # Update password if a new one is provided
        if form.password.data:
            current_user.password_hash = bcrypt.generate_password_hash(form.password.data)

        # Commit all changes to the database
        db.session.commit()

        # Re-login the user to update the session
        login_user(current_user)

        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))

    # Pre-fill the form with the current user's data
    form.username.data = current_user.username
    return render_template('profile.html', form=form)

@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    form = GroupForm()
    if form.validate_on_submit():
        # Create a new group
        group = Group(
            name=form.name.data,
            description=form.description.data,
            owner=current_user.username
        )
        db.session.add(group)
        db.session.commit()
        group.add_member(current_user.username, admin=True)
        flash('Group created successfully!', 'success')
        return redirect(url_for('groups'))

    # Handle group deletion if the "remove_group" parameter is present
    remove_group_id = request.form.get('remove_group')
    if remove_group_id:
        group = Group.query.get(remove_group_id)
        if not group:
            flash('Group not found', 'danger')
        elif current_user.username != group.owner:
            flash('You are not authorized to delete this group', 'danger')
        else:
            db.session.delete(group)
            db.session.commit()
            flash('Group deleted successfully!', 'success')
        return redirect(url_for('groups'))

    # Sort the groups alphabetically by name (A-Z)
    sorted_groups = sorted(current_user.groups, key=lambda x: x.name)

    # Display the list of groups
    return render_template('groups.html', form=form, groups=sorted_groups)

@app.route('/groups/<int:group_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_group(group_id):
    group = Group.query.get(group_id)
    if not group:
        flash('Group not found', 'danger')
        return redirect(url_for('groups'))

    if current_user.username not in group.members:
        flash('You are not a member of this group', 'danger')
        return redirect(url_for('groups'))

    form = GroupEditForm()
    if form.validate_on_submit():
        # Track if a specific action (like adding or removing a user) was performed
        specific_action_performed = False

        # Only admins and the owner can update group details (name and description)
        if current_user.username in group.admins or current_user.username == group.owner:
            group.update_group(form.name.data, form.description.data)
        else:
            # Normal members cannot update group details, but they can still add members
            pass

        # Handle adding new members (only if a username is provided)
        new_member_username = request.form.get('new_member_username')
        if new_member_username:  # Only proceed if a username is entered
            if new_member_username == current_user.username:
                flash('You cannot add yourself to the group', 'warning')
                specific_action_performed = True
            else:
                user = User.query.filter_by(username=new_member_username).first()
                if user:
                    if new_member_username in group.members:
                        flash(f'{new_member_username} is already a member of the group', 'warning')
                        specific_action_performed = True
                    else:
                        group.add_member(new_member_username)
                        flash(f'{new_member_username} has been added to the group', 'success')
                        specific_action_performed = True
                else:
                    flash('User not found', 'danger')
                    specific_action_performed = True

        # Handle removing members
        remove_member_username = request.form.get('remove_member_username')
        if remove_member_username:
            # Only the owner and admins can remove members
            if current_user.username != group.owner and not group.is_admin(current_user.username):
                flash('You are not authorized to remove members from this group', 'danger')
            else:
                # Owner cannot remove themselves
                if remove_member_username == current_user.username and current_user.username == group.owner:
                    flash('You cannot remove yourself as the owner of the group', 'warning')
                # Admins cannot remove other admins or the owner
                elif current_user.username != group.owner and (remove_member_username in group.admins or remove_member_username == group.owner):
                    flash('You are not authorized to remove this member', 'danger')
                else:
                    # Remove the member
                    user_group = UserGroup.query.filter_by(user_id=remove_member_username, group_id=group_id).first()
                    if user_group:
                        db.session.delete(user_group)
                        db.session.commit()
                        flash(f'{remove_member_username} has been removed from the group', 'success')
                        specific_action_performed = True
                    else:
                        flash('Member not found in the group', 'danger')

        # Handle admin promotions if the user is the owner
        if current_user.username == group.owner:
            new_admins = request.form.getlist('admins')
            for username in group.members:
                if username == group.owner:
                    continue
                is_admin = username in new_admins
                group.update_member_permission(username, is_admin)

        # Only show the general success message if no specific action was performed
        if not specific_action_performed:
            flash('Group updated successfully!', 'success')

        return redirect(url_for('manage_group', group_id=group_id))

    # Populate the form with existing group details
    form.name.data = group.name
    form.description.data = group.description

    # Prepare member list with proper ordering and labels
    members = []
    for username in group.members:
        if username == current_user.username:
            display_name = "You"  # Replace the current user's name with "You"
        else:
            display_name = username

        # Determine the role label
        if username == group.owner:
            role_label = "Owner"
        elif username in group.admins:
            role_label = "Admin"
        else:
            role_label = "Member"

        members.append({'username': username, 'display_name': display_name, 'role': role_label})

    # Sort members: You first, then Owner, then Admins alphabetically, then Members alphabetically
    members.sort(key=lambda x: (
        0 if x['display_name'] == "You" else
        1 if x['role'] == "Owner" else
        2 if x['role'] == "Admin" else 3,
        x['display_name']
    ))

    return render_template('manage_group.html', form=form, group=group, members=members)


@app.route('/groups/<int:group_id>', methods=['GET', 'POST'])
@login_required
def tasks(group_id):
    group = Group.query.get(group_id)
    if not group:
        flash('Group not found', 'danger')
        return redirect(url_for('groups'))
    if current_user.username not in group.members:
        flash('You are not a member of this group', 'danger')
        return redirect(url_for('groups'))

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
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks', group_id=group_id))

    # Sorting logic
    sort = request.args.get('sort', 'due_date')
    tasks_query = Task.query.filter_by(group_id=group_id)

    if sort == 'name':
        tasks_query = tasks_query.order_by(
            func.lower(Task.name).asc()
        )

    elif sort == 'due_date':
        if db.engine.name == 'postgresql':
            tasks_query = tasks_query.order_by(
                asc(Task.due_date).nulls_last(),
                func.lower(Task.name).asc()  # Secondary sort
        )
        else:
            tasks_query = tasks_query.order_by(
                case((Task.due_date.is_(None), 1), else_=0).asc(),
                Task.due_date.asc(),
                func.lower(Task.name).asc()  # Secondary sort
        )
    elif sort == 'status':
        status_order = case(
            (Task.status == 'Pending', 0),
            (Task.status == 'In Progress', 1),
            (Task.status == 'Completed', 2),
            else_=3
    )

        tasks_query = tasks_query.order_by(
            status_order.asc(),
            func.lower(Task.name).asc()  # Secondary sort
    )
    elif sort == 'creator':
        tasks_query = tasks_query.order_by(
            func.lower(Task.author).asc(),
            func.lower(Task.name).asc()  # Secondary sort
    )

    tasks = tasks_query.all()

    return render_template('tasks.html',
                         form=form,
                         tasks=tasks,
                         group=group,
                         sort=sort)

@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    group = Group.query.get(task.group_id)

    if current_user.username not in group.members:
        flash('You are not a member of this group', 'danger')
        return redirect(url_for('groups'))

    form = TaskEditForm(obj=task)

    if form.validate_on_submit():
        is_authorized = current_user.username == task.author or current_user.username == group.owner or group.is_admin(
            current_user.username
            )

        # Only update restricted fields if authorized
        if is_authorized:
            task.name = form.name.data
            task.description = form.description.data
            task.due_date = form.due_date.data
            field_count = 3  # Track if we're updating more than just status
        else:
            field_count = 0

        # Always update status
        task.status = form.status.data
        db.session.commit()

        # Different flash messages based on authorization
        if is_authorized or field_count > 0:
            flash('Task updated successfully!', 'success')
        else:
            flash('Task status updated successfully!', 'success')

        return redirect(url_for('tasks', group_id=task.group_id))

    return render_template('edit_task.html', form=form, task=task, group=group)


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    group = Group.query.get(task.group_id)
    group_id = task.group_id

    # Authorization check
    if not (current_user.username == task.author or
            current_user.username == group.owner or
            group.is_admin(current_user.username)):
        flash('You are not authorized to delete this task', 'danger')
        return redirect(url_for('tasks', group_id=group_id))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks', group_id=group_id))