from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField, IntegerField, DecimalField
from wtforms.validators import InputRequired, Length, ValidationError


# Register Form
class RegisterForm(FlaskForm):
   first_name = StringField(label="First Name", validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder" : "First Name"})
   last_name = StringField(label="Last Name", validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder" : "Last Name"})
   email = StringField(label= "Email Address", validators=[InputRequired(), Length(min=2, max=200)],render_kw={"placeholder" : "Email Address"} )
   password = PasswordField(label="Password", validators=[InputRequired(), Length(min=8, max=50)], render_kw={"placeholder" : "Password"})
   submit = SubmitField("Register")


#Login Form
class LoginForm(FlaskForm):
   email = StringField(label= "Email Address", validators=[InputRequired(), Length(min=2, max=200)],render_kw={"placeholder" : "Email Address"} )
   password = PasswordField(label="Password", validators=[InputRequired(), Length(min=8, max=50)], render_kw={"placeholder" : "Password"})
   submit = SubmitField("Log In")
   

#Item Form
class GroceryForm(FlaskForm):
    item = StringField(label= "Name of Item", validators=[InputRequired(), Length(min=2, max=200)],render_kw={"placeholder" : "Name of Item"} )
    quantity = IntegerField(label= "Quantity" , default=0, render_kw={"placeholder" : "Quantity"} )
    price = DecimalField(label= "Amount", default=0.0, render_kw={"placeholder" : "Amount"})
    submit = SubmitField("Add")