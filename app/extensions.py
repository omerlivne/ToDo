# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bcrypt = Bcrypt()

# Configure login manager
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(user_id)

login_manager.login_view = "auth.login"