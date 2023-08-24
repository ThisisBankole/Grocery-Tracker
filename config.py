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

load_dotenv()

# This creates the variable basedir pointing to the directory that the program is running in.
basedir = pathlib.Path(__file__).parent.resolve()
# This uses the basedir variable to create the Connexion app instance and give it the path to the directory that contains your specification file.
connex_app = connexion.App(__name__, specification_dir=basedir)
app = connex_app.app


# This tells SQLAlchemy to use SQLite as the database and a file named shopa.db in the current directory as the database file.
#app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DB_URL').replace('postgres://', 'postgresql://')
if os.environ.get('FLASK_ENV') == 'development':
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('LOCAL_DB_URL').replace('postgres://', 'postgresql://')
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('PROD_DB_URL').replace('postgres://', 'postgresql://')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
# This initializes SQLAlchemy by passing the app configuration information to SQLAlchemy and assigning the result to a db variable.
db=SQLAlchemy(app)
# This initializes Marshmallow and allows it to work with the SQLAlchemy components attached to the app.
ma=Marshmallow(app)
#Initializes Migrate for database migration support
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
