import os
from flask import render_template, send_from_directory
import requests
from config import app, login_manager,connex_app, login_manager
import config
from models import User, Grocery, Account
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from shared import bcrypt
from users import login_logic, create, change_password, read_all_by_account
from groceries import add, read_items, update, delete
from forms import RegisterForm, LoginForm, GroceryForm, PasswordEmail, PasswordReset, AddUserForm
from datetime import datetime, timedelta
from edamam_api import get_groceries_from_edamam
from receipts import process_receipts_and_add_groceries
from re import findall
from init_db import init_db
from pytesseract import pytesseract
from PIL import Image   
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError
import re
import sys
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import connexion
import pathlib
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from extension import db, ma
from config import app
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_migrate import Migrate

secret_key = app.config["SECRET_KEY"]


# Setup Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Setup itsdangerous
serializer = URLSafeTimedSerializer(secret_key)

# login_manager.init_app(app)
# This handles user loading on login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


migrate = Migrate(app, db)




#This is the route for the homepage
@app.route("/")
def home():
   return render_template("home.html")


#Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
   form = LoginForm()
   
   if request.method == 'POST' and form.validate_on_submit():
      user = User.query.filter_by(email=form.email.data).first()
      
      # Check if the user exists
      if not user:
         flash('Email not registered', 'danger')
         return render_template('login.html', form=form)
      
      
      user_data = {
         "email": form.email.data,
         "password": form.password.data
      }
      
      response = login_logic(user_data)
      
      
      if response and "token" in response:
         token = response.get('token')
         session['token'] = token
         login_user(user)
         #flash('Logged in successfully!', 'success')
         return redirect(url_for('dashboard'))
      else:
         flash('Invalid password.', 'danger')
   return render_template('login.html', form=form)


#Logout Route
@app.route('/logout')
@login_required
def logout():
   logout_user()
   session.pop('token', None)
   flash('Logged out successfully!', 'success')
   return redirect(url_for('login'))
      

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
      
      
      response = create(user_data)
         #print(response.text)
      if response:
         flash('Registration successful!', 'success')
         return redirect(url_for('register'))
      else:
         flash('Registration failed', 'warning' )
      
   return render_template('register.html', form=form)
      

   
  # Dashboard Route
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
   form = GroceryForm()
   
   if request.method == "POST":
      if form.item.data:
         if form.validate_on_submit():   
            result = {
               "user_id": current_user.id,
               "item": form.item.data,
               "quantity": form.quantity.data,
               "price": form.price.data,
               "account_id": current_user.account_id 
            }
            response = add(result)
         
            if response:
               #flash("Item added successfully", 'success')
               return redirect(url_for('dashboard'))
            else:
               flash('Something went wrong', 'warning')
         
   grouped_groceries = read_items(current_user.account_id)
   now = datetime.utcnow().date().strftime('%Y-%m-%d')
   yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
   
   return render_template("dashboard.html", form=form, grouped_groceries=grouped_groceries, now=now, yesterday=yesterday)


# Receipts processing Route

@app.route("/process_receipt", methods=["POST"])
@login_required
def process_receipt():
   form = GroceryForm()
   
   #patterns = {
      #"aldi": r'([\w\s\-\/]+[a-zA-Z\s\-\/]+[\w])\s+([£€$]?\d+[,.]\d{2})',
      #"food_warehouse": r'(\d+)\s*([\w\s\-\/\d]+[\w])\s*([£€$]?\d+[,.]\d{2})\s*([£€$]?\d+[,.]\d{2})',
      #"general": r'([\w\s\-\/]*[a-zA-Z\s\-\/]+[\w\s\-\/]*)\s*[£€$®]*\s*([£€$]?\d+[,.]\d{2})'
   #}
   if form.receipt.data:
      # Convert the uploaded file to bytes
      receipt_bytes = form.receipt.data.read()
      
      # Set up the Form Recognizer client
      endpoint = os.environ.get("FORM_RECOGNIZER_ENDPOINT")
      key = os.environ.get("FORM_RECOGNIZER_KEY")
            # Display the value of the 'key' variable

      
      form_recognizer_client = FormRecognizerClient(endpoint, AzureKeyCredential(key))
      print(f"Type of key: {type(key)}")  # Check the type of the 'key' variable
      print(f"Value of key: {key}") 
      
      # Use the client to analyze the receipt
      
      poller = form_recognizer_client.begin_recognize_receipts(receipt_bytes)
      result = poller.result()
      
      extracted_groceries = []
         #sace the receipt to the uploads folder
         #filename = secure_filename(form.receipt.data.filename)
         #filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
         #form.receipt.data.save(filepath)
         
      for receipt in result:
         for name, field in receipt.fields.items():
            if name == "Items":
               for idx, items in enumerate(field.value):
                  item_name ="Unknown"
                  item_price = "0.00"
                  
                  # Ensure that items.value is not None before accessing its attributes
                  if items and items.value:
                     name_field = items.value.get("Name")
                     total_price_field = items.value.get("TotalPrice")
                     
                     # Check if the fields exist and then get their values
                     if name_field:
                        item_name = name_field.value or "Unknown"
                     if total_price_field:
                        item_price = total_price_field.value or "0.00"
                     
                  # Add the extracted item to the list
                  extracted_groceries.append({
                     "item": item_name, 
                     "price": item_price
                     })
         #pass the extracted data to the frontend
         return render_template("verify.html", form=form, extracted_groceries=extracted_groceries)
   else:
      flash('No receipt uploaded', 'warning')
      return redirect(url_for('dashboard'))
         

# save extracted and verified items to db
@app.route("/save_groceries", methods=["POST"])
@login_required

def save_groceries():
   #form = VerifyGroceryForm(request.form)
   items = request.form.getlist('item[]')
   quantities = request.form.getlist('quantity[]')
   prices = request.form.getlist('price[]')
   
   print("Items:", items)
   print("Quantities:", quantities)
   print("Prices:", prices)
   
      
   for i in range(len(items)):
      
      #create a grocery object
      new_grocery = Grocery(
         user_id=current_user.id,
         item=items[i],
         quantity=quantities[i],
         price=prices[i]
      )
      db.session.add(new_grocery)
      
   db.session.commit()
   #added_groceries = read_items(current_user.id)
   
   #print("added groceries:",added_groceries)
      
   #flash('Items added successfully', 'success')
   return redirect(url_for('dashboard'))


# Edit 
@app.route("/edit/<int:grocery_id>", methods=["GET", "POST"])
@login_required
def edit_grocery(grocery_id):
    # Get the grocery item by its ID
    grocery = Grocery.query.get_or_404(grocery_id)

    # Ensure the item belongs to the logged-in user
    if grocery.user_id != current_user.id:
        flash("You don't have permission to edit this item.", 'danger')
        return redirect(url_for('dashboard'))

    form = GroceryForm()

    if form.validate_on_submit():
        grocery_data = {
            "item": form.item.data,
            "quantity": form.quantity.data,
            "price": form.price.data
        }
        response, status_code = update(grocery_id, grocery_data)
        if status_code == 200:
            flash('Item updated successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('An error occurred while updating the item.', 'danger')

    elif request.method == "GET":
        form.item.data = grocery.item
        form.quantity.data = grocery.quantity
        form.price.data = grocery.price

    return render_template('edit.html', form=form, item=grocery)



#Delete
@app.route("/delete/<int:grocery_id>", methods=["POST"])
@login_required
def delete_grocery(grocery_id):
    response = delete(grocery_id)
    if response.status_code == 200:
        flash('Item deleted successfully!', 'success')
    else:
        flash('Failed to delete the item.', 'danger')
    return redirect(url_for('dashboard'))



# Search 
@app.route("/search")
def search_groceries():
    query = request.args.get('query')
    groceries = get_groceries_from_edamam(query)
    return jsonify({'groceries': groceries})
 

#Reset Password
@app.route('/send_mail', methods=['GET','POST'])
def reset_password():
   form = PasswordEmail()
   
   if request.method == 'POST' and form.validate_on_submit():
      email = form.email.data
      user = User.query.filter_by(email=email).first()
      
      if user:
         token = serializer.dumps(email, salt='password-reset-salt')
         reset_url = url_for('reset_with_token', token=token, _external=True)

         msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'] ,recipients=[email])
         msg.body = f'Please click the following link to reset your password: {reset_url}'
         mail.send(msg)

         return redirect(url_for('login'))
      
      else:
         return render_template('pass_email.html', message='Email does not exist.')
   return render_template('pass_email.html', form=form)
 
 
 #Reset Password with token
@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
   password_reset_form = PasswordReset()
   
   try:
      email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
   except SignatureExpired:
      return render_template('pass_reset.html', message='The token is expired.')
   
   user = User.query.filter_by(email=email).first()
   
   if user:
      if request.method == 'POST' and password_reset_form.validate_on_submit():
         change_password(user.id, password_reset_form.password.data)
         return redirect(url_for('login'))
      else:
         return render_template('password.html', form=password_reset_form, token=token)
      
   else:
      return render_template('password.html', message='Invalid token.', token=token)
  
 
 # Add user
@app.route("/add_user", methods=["GET", "POST"])
@login_required
def add_user():
   # Ensure the user is an admin
   if not current_user:
      flash("You don't have permission to add users.", 'danger')
      return redirect(url_for('dashboard'))

   form = AddUserForm()

   if form.validate_on_submit():
      # Create a new user object
      new_user = User(
         first_name=form.first_name.data,
         last_name=form.last_name.data,
         email=form.email.data,
         password=bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
         account_id=current_user.account_id
      )
      db.session.add(new_user)
      db.session.commit()

      # Send an email to the new user to create their password
      token = serializer.dumps(new_user.email, salt='password-reset-salt')
      reset_url = url_for('reset_with_token', token=token, _external=True)

      msg = Message('Create Your Password', sender=app.config['MAIL_USERNAME'], recipients=[new_user.email])
      msg.body = f'Please click the following link to create your password: {reset_url}'
      mail.send(msg)

      flash('User added successfully.', 'success')
      return redirect(url_for('dashboard'))

   return render_template('add_user.html', form=form)

#user list
@app.route('/users')
@login_required
def user_management():
   grouped_users = read_all_by_account(current_user.account_id)
   return render_template('user.html', grouped_users=grouped_users)
   
 
 
@app.context_processor
def inject_datetime():
    return {'datetime': datetime, 'timedelta': timedelta}  



if __name__ == "__main__":
        port = int(os.environ.get("PORT", 8000))
        app.run(host="0.0.0.0", port=port, debug=False)

    
#if __name__ == '__main__':
     #port = int(os.environ.get('PORT', 5000))  # Use PORT if it's there, otherwise default to 5000 for local development.
     #app.run(host='0.0.0.0', port=port)
    