# todo\routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from todo.forms import LoginForm, RegistrationForm, GroupForm, TaskForm
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
