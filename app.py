from todo import app, db
from todo.models import User
from todo.routes import *

if __name__ == '__main__':
    app.run(debug=True)