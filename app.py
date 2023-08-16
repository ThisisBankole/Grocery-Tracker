import os
from flask import render_template
import requests
from config import app, login_manager, db
import config
from models import User, Grocery
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from shared import bcrypt, secret_key
from users import login_logic, create
from groceries import add, read_items, update, delete
from forms import RegisterForm, LoginForm, GroceryForm
from datetime import datetime, timedelta
from edamam_api import get_groceries_from_edamam
#import logging


#logging.basicConfig(level=logging.DEBUG)



config.connex_app.add_api(config.basedir / "swagger.yml")

# login_manager.init_app(app)
# This handles user loading on login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))



#This is the route for the homepage
@app.route("/")
def home():
   return render_template("home.html")


#Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
   form = LoginForm()
   
   if request.method == 'POST' and form.validate_on_submit():
      user_data = {
         "email": form.email.data,
         "password": form.password.data
      }
      response = login_logic(user_data)
      if response and "token" in response:
         token = response.get('token')
         session['token'] = token
         user = User.query.filter_by(email=form.email.data).first()
         login_user(user)
         flash('Logged in successfully!', 'success')
         return redirect(url_for('dashboard'))
      else:
         flash('Invalid credentials.', 'danger')
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
      #print(f"Form data: item={form.item.data}, quantity={form.quantity.data}, price={form.price.data}")
      if form.validate_on_submit():
         result = {
            "user_id": current_user.id,
            "item": form.item.data,
            "quantity": form.quantity.data,
            "price": form.price.data
         }
         response = add(result)
      
         if response:
            flash("Item added successfully", 'success')
            return redirect(url_for('dashboard'))
         else:
            flash('Something went wrong', 'warning')
         
   
   grouped_groceries = read_items(current_user.id)
   now = datetime.utcnow().date().strftime('%Y-%m-%d')
   yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
   
   return render_template("dashboard.html", form=form, grouped_groceries=grouped_groceries, now=now, yesterday=yesterday)



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
 
 
@app.context_processor
def inject_datetime():
    return {'datetime': datetime, 'timedelta': timedelta}  


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
    
#if __name__ == '__main__':
     #port = int(os.environ.get('PORT', 5000))  # Use PORT if it's there, otherwise default to 5000 for local development.
     #app.run(host='0.0.0.0', port=port)
    