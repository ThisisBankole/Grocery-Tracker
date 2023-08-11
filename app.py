import os
from flask import render_template
from config import bcrypt, app
import config
from users import create
from models import User, Grocery
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for


secret_key = app.config["SECRET_KEY"]

app = config.connex_app
# 
app.add_api(config.basedir / "swagger.yml")


class RegisterForm(FlaskForm):
   first_name = StringField(label="First Name", validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder" : "First Name"})
   last_name = StringField(label="Last Name", validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder" : "Last Name"})
   email = StringField(label= "Email Address", validators=[InputRequired(), Length(min=2, max=200)],render_kw={"placeholder" : "Email Address"} )
   password = PasswordField(label="Password", validators=[InputRequired(), Length(min=8, max=50)], render_kw={"placeholder" : "Password"})
   submit = SubmitField("Register")



#This is the route for the homepage
@app.route("/")
def home():
   return render_template("home.html")


#Register Route
@app.route("/register", methods=["GET", "POST"])
def register():
   form = RegisterForm()
   if request.method == 'POST' and form.validate_on_submit():
      hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
      user_data = {
               "first_name": form.first_name.data,
               "last_name": form.last_name.data,
               "email": form.email.data,
               "password": hashed_password  # Encrypting password before sending to the API.
         }
      created_user = create(user_data)
      if created_user:
         flash('Registration successful!', 'success')
         return redirect(url_for('home'))
      else:
         flash('Registration failed', 'warning' )
         
   return render_template('register.html', form=form)
   

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    