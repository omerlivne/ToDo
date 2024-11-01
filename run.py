from app import app, db
from app.models import User
from app.routes import *

if __name__ == '__main__':
    app.run(debug=True)