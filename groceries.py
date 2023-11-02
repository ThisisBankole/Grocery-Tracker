from config import db, app
from collections import defaultdict, OrderedDict
from flask import abort, make_response
from models import Grocery, User, grocery_schema
import jwt
#from shared import secret_key, bcrypt
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError


def read_items(account_id):
    #print(f"Reading items for account_id: {account_id}")
    grocery = Grocery.query.filter_by(account_id=account_id).order_by(Grocery.timestamp.desc()).all()
   # print(f"Retrieved {len(grocery)} groceries")
    grouped_grocery = defaultdict(list)
    
    for g in grocery:
        date_str = g.timestamp.strftime('%Y-%m-%d')
        grocery_data = grocery_schema.dump(g)
        #print(f"Grocery data: {grocery_data}")
        grouped_grocery[date_str].append(grocery_data)
    
        
    #ordered_groceries = OrderedDict(sorted(grouped_grocery.items(), key=lambda t: t[0], reverse=True))
        
    return grouped_grocery


def read_item(grocery_id):
    grocery =  db.session.get(Grocery, grocery_id)
    if grocery:
        return grocery_schema.dump(grocery), 200
    else:
       abort(
            401,
            f"Something went wrong, try again"
        ) 
    

def add(grocery):
    try:
        new_grocery = grocery_schema.load(grocery, session=db.session)
        db.session.add(new_grocery)
        db.session.commit()
        return grocery_schema.dump(new_grocery), 200
    except IntegrityError:
        db.session.rollback()
        abort(
            401,
            f"Something went wrong, try again"
        )
    except Exception as e:
        db.session.rollback()
        abort(505, f"Server error: {str(e)}")
    
    
def update(grocery_id, grocery):
    existing_grocery = db.session.get(Grocery, grocery_id) 
    if existing_grocery:
        update_grocery = grocery_schema.load(grocery, session=db.session)
        existing_grocery.item = update_grocery.item
        existing_grocery.price = update_grocery.price
        existing_grocery.quantity = update_grocery.quantity
        db.session.merge(existing_grocery)
        db.session.commit()
        return grocery_schema.dump(update_grocery), 200
    else:
        abort(
            401,
            f"Something went wrong, try again"
        )
        
        
def delete(grocery_id):
    existing_grocery = db.session.get(Grocery, grocery_id)
    if existing_grocery:
        db.session.delete(existing_grocery)
        db.session.commit()
        return make_response(
            f"Item deleted successfully", 200
        )
    else:
        abort(
            401,
            f"Could not delete item"
        )