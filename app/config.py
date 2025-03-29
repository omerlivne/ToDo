# app/config.py
import os
from pathlib import Path

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{Path(__file__).parent.parent}/data.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False