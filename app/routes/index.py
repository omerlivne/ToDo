# routes/index.py
from flask import Blueprint, render_template
from flask_login import login_required

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
@login_required
def home():
    return render_template("index.html")