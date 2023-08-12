from config import db
from flask import abort, make_response
from models import User, user_create_schema, user_detail_schema
import jwt
from shared import secret_key, bcrypt
from datetime import datetime, timedelta


# This is a function used for returning the list of users. GET/api/users | 
# I am using users_schema which is an instance of the Marshmallow UserSchema class (models.py) that was created with the parameter many=True. 
# With this parameter you tell UserSchema to expect an iterable to serialize. 
# This is important because the users variable contains a list of database items.
def read_all():
    users = User.query.all()
    return user_detail_schema.dump(users)


#This is a function used for creating a user. 
# This receives a user object. This object must contain id, which must not exist in the database already. 
# If the id is unique, then I deserialize the person object as new_user and add it to db.session. 
# Once I commit new_user to the database, the database engine assigns a new primary key value and a UTC-based timestamp to the object.


def create(user):
    email = user.get("email")
    existing_user = User.query.filter(User.email == email).one_or_none()
    
    if existing_user is None:
        print(user)
        new_user = user_create_schema.load(user, session=db.session)
        db.session.add(new_user)
        db.session.commit()
        return user_create_schema.dump(new_user)
    else:
        abort(
            401,
            f"User already exist"
        )
    

#This is a function used for autheticating users

def login(credentials):
    existing_user = User.query.filter_by(email=credentials["email"]).first()
    hashed_password = bcrypt.check_password_hash(existing_user.password, credentials["password"])
    
    if existing_user and hashed_password:
        token = jwt.encode({
           'user_id': User.id, 
           'exp' : datetime.utcnow() + timedelta(hours=24)
        }, secret_key, algorithm = 'HS256')
        return {"token": token}
    
    else:
        abort(401, "Invalid credentials")


