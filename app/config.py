# config.py
from pathlib import Path

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(__file__).parent.parent}/data.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your_secret_key_here"
