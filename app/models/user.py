# models/user.py
from flask_login import UserMixin
from app.extensions import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(12), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    user_groups = db.relationship('UserGroup', back_populates='user')

    def __init__(self, username: str, password: str) -> None:
        """Initialize a new User instance with username and hashed password."""
        self.username = username
        self.password_hash = User.hash_password(password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Generate bcrypt hash from plaintext password."""
        return bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def groups(self) -> list['Group | None']:
        """List of admin user."""
        return [ug.group for ug in self.user_groups]