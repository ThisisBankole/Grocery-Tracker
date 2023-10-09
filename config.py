import pathlib
import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask.cli import load_dotenv
import os
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import os
import json
import base64

load_dotenv()


# Check if the app is running in production (on Platform.sh)
# Use SQLite for local development
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if os.getenv('PLATFORM_BRANCH'):
    relationships = json.loads(base64.b64decode(os.environ.get('PLATFORM_RELATIONSHIPS')).decode('utf-8'))
    db_relationship = relationships['postgresdatabase'][0]
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{db_relationship['username']}:{db_relationship['password']}@{db_relationship['host']}:{db_relationship['port']}/{db_relationship['path']}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL') 

#'sqlite:///' + os.path.join(BASE_DIR, 'tmp', 'shopa.db')

#activate venv
#source venv/bin/activate

#app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///shopa.db'







app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
# This initializes SQLAlchemy by passing the app configuration information to SQLAlchemy and assigning the result to a db variable.
db=SQLAlchemy(app)
# This initializes Marshmallow and allows it to work with the SQLAlchemy components attached to the app.
ma=Marshmallow(app)
migrate = Migrate(app, db)

#This code defines a User class which inherits from UserMixin. UserMixin is a helper class in Flask-Login that includes default implementations for user object properties and methods like is_authenticated, is_active, etc.
# The User class has a constructor (__init__) that takes a dictionary as a parameter and initializes the object's id, email, and password attributes based on the dictionary.
class User(UserMixin):
    def __init__ (self, dictionary):
        self.id = dictionary['id']
        self.email = dictionary['email']
        self.password = dictionary['password']
 

# Uses the load_dotenv function to load environment variables from a .env file (if it exists) into the environment. 
# This allows the app to access sensitive or configuration data without hardcoding it.


# After each request, this function ensures that the responses are not cached by the browser. 
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Initializes the LoginManager which helps manage user sessions for a Flask app.
# Specifies that the login view should be used for logging users in.
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


#Defines a user loader function. When Flask-Login needs to know about a specific user, it uses this function. 
# The function queries the database for the user by user_id and returns a User object.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



print(load_dotenv())
