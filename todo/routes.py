# todo\routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from todo.forms import LoginForm, RegistrationForm, GroupForm, TaskForm, GroupEditForm
from todo.models import User, Task, Group
from todo import app, db


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


@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    form = GroupForm()
    if form.validate_on_submit():
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

    return render_template('groups.html', form=form, groups=current_user.groups)


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
        return redirect(f"{url_for('groups')}/{group_id}")

    return render_template('tasks.html', form=form, tasks=Task.query.filter_by(group_id=group_id).all())


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
        # Update group details if the user is an admin or owner
        if current_user.username in group.admins or current_user.username == group.owner:
            group.update_group(form.name.data, form.description.data)

        # Handle adding new members (only if a username is provided)
        new_member_username = request.form.get('new_member_username')
        if new_member_username:  # Only proceed if a username is entered
            user = User.query.filter_by(username=new_member_username).first()
            if user:
                group.add_member(new_member_username)
                flash(f'{new_member_username} has been added to the group', 'success')
            else:
                flash('User not found', 'danger')

        # Handle admin promotions if the user is the owner
        if current_user.username == group.owner:
            new_admins = request.form.getlist('admins')
            for username in group.members:
                if username == group.owner:
                    continue
                is_admin = username in new_admins
                group.update_member_permission(username, is_admin)

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

        members.append({'username': display_name, 'role': role_label})

    # Sort members: You first, then Owner, then Admins alphabetically, then Members alphabetically
    members.sort(key=lambda x: (
        0 if x['username'] == "You" else
        1 if x['role'] == "Owner" else
        2 if x['role'] == "Admin" else 3,
        x['username']
    ))

    return render_template('manage_group.html', form=form, group=group, members=members)