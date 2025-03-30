# models/user.py
from flask_login import UserMixin
from app.extensions import db, bcrypt
from app.models.user_group import UserGroup

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, username: str, password: str) -> None:
        """Initialize a user. Hashes the password for secure storage."""
        self.username = username
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    @classmethod
    def create(cls, username: str, password: str) -> 'User':
        """Persists a new user to the database. Returns the user for immediate use (e.g., auto-login)."""
        user = cls(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def authenticate(cls, username: str, password: str) -> 'User | None':
        """Verifies credentials. Returns `User` for session creation or `None` for failed logins."""
        user = cls.query.filter_by(username=username).first()
        return user if user and user.check_password(password) else None

    def check_password(self, password: str) -> bool:
        """Compares plaintext password with stored hash. Returns boolean for authentication decisions."""
        return bcrypt.check_password_hash(self.password_hash, password)

    def update_username(self, new_username: str) -> None:
        """Updates username. Relies on form/database for validation, not model logic."""
        self.username = new_username
        db.session.commit()

    def update_password(self, new_password: str) -> None:
        """Updates password hash. Assumes validation is handled externally (e.g., forms)."""
        self.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
        db.session.commit()

    @property
    def groups(self) -> list:
        """Returns groups the user belongs to. Used for UI/API membership listings."""
        return [ug.group for ug in UserGroup.query.filter_by(user_id=self.id).all()]

    @property
    def owned_groups(self) -> list:
        """Returns groups the user owns. Enables owner-specific workflows."""
        return [ug.group for ug in UserGroup.query.filter_by(user_id=self.id, role=2).all()]

    def can_edit_group(self, group_id: int) -> bool:
        """Checks edit permissions. Returns boolean for UI/routes to gatekeep actions."""
        role = UserGroup.get_role(group_id, self.id)
        return role in (1, 2)