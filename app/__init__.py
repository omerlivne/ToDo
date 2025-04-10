# __init__.py
from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Import blueprints
    from app.routes.index import index_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.groups import groups_bp
    from app.routes.tasks import tasks_bp

    # Register blueprints
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(tasks_bp)

    return app