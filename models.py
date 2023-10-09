from datetime import datetime
from config import UserMixin
from marshmallow import fields
from shared import bcrypt
from extension import db, ma

# This defines the Grocery class. 
# Inheriting from db.Model from config.py file gives User the SQLAlchemy features to connect to the database and access its tables.
class Grocery(db.Model):
    __tablename__ = "grocery"  # This connects the class definition to the user database table.
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id")) 
    item = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    
    

class GrocerySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Grocery
        load_instance = True
        sqla_session = db.session
        include_fk = True
        


# This defines the User class. 
# Inheriting from db.Model from config.py file gives User the SQLAlchemy features to connect to the database and access its tables.
class User(db.Model, UserMixin):
    __tablename__ = "user"  # This connects the class definition to the user database table.
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
    
    groceries = db.relationship (
        Grocery,
        backref = "User",
        cascade = "all, delete, delete-orphan",
        single_parent = True,
        order_by = "desc(Grocery.timestamp)"
        
    )
    
    
class UserCreateSchema(ma.SQLAlchemyAutoSchema):
    password = fields.Str(load_only=True)
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = False

class UserDetailSchema(ma.SQLAlchemyAutoSchema):
    password = fields.Str(load_only=True)
    groceries = fields.Nested(GrocerySchema, many=True)
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session
        include_relationships = True
        
 
    
class GroceryItem(db.Model):
    __tablename__ = "grocery_item"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)  # store the unique item name

    
user_create_schema = UserCreateSchema()
user_detail_schema = UserDetailSchema(many=True)
grocery_schema = GrocerySchema()


