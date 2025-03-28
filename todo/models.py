# todo\models.py
from todo import db, login_manager
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()


# User loader for Flask-Login
@login_manager.user_loader
def load_user(username):
    return User.query.get(username)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    username = db.Column(db.String(), primary_key=True)
    password_hash = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        # Use Bcrypt to hash the password before storing in the database
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        # Use Bcrypt to check the password against the stored hash
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

    @property
    def groups(self):
        return Group.query.join(UserGroup, UserGroup.group_id == Group.id).filter(
            UserGroup.user_id == self.username).all()


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner = db.Column(db.String(), db.ForeignKey('users.username'), nullable=False)

    def __init__(self, name, description, owner):
        self.name = name
        self.description = description
        self.owner = owner

    @property
    def members(self):
        users = User.query.join(UserGroup).filter(UserGroup.group_id == self.id).all()
        return map(lambda user: user.username, users)

    @property
    def admins(self):
        admins = UserGroup.query.filter_by(group_id=self.id, admin=True).all()
        return map(lambda user_group: user_group.user_id, admins)

    def add_member(self, username, admin=False):
        user_group = UserGroup(username, self.id)
        user_group.admin = admin
        db.session.add(user_group)
        db.session.commit()

    def update_group(self, name, description):
        self.name = name
        self.description = description
        db.session.commit()

    def set_admin(self, username, admin_status):
        user_group = UserGroup.query.filter_by(user_id=username, group_id=self.id).first()
        if user_group:
            user_group.admin = admin_status
            db.session.commit()

    def is_admin(self, username):
        user_group = UserGroup.query.filter_by(user_id=username, group_id=self.id).first()
        if user_group and user_group.admin:
            return True
        return False

    def update_member_permission(self, username, is_admin):
        # Update the user's admin status
        user_group = UserGroup.query.filter_by(user_id=username, group_id=self.id).first()
        if user_group:
            user_group.admin = is_admin
            db.session.commit()


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(), nullable=False, default="Pending")
    creation_date = db.Column(db.DateTime, default=datetime.now())
    due_date = db.Column(db.DateTime, nullable=True)
    author = db.Column(db.String(), db.ForeignKey('users.username'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)

    def __init__(self, name, description, due_date, author, group_id):
        self.name = name
        self.description = description
        self.due_date = due_date
        self.author = author
        self.group_id = group_id


class UserGroup(db.Model):
    __tablename__ = 'users_groups'

    user_id = db.Column(db.String(), db.ForeignKey('users.username'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), primary_key=True)
    admin = db.Column(db.Boolean(), default=False)

    def __init__(self, user_id, group_id):
        self.user_id = user_id
        self.group_id = group_id
