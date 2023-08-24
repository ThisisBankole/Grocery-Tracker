
from config import db
from collections import defaultdict, OrderedDict
from flask import abort, make_response
from models import Grocery, User, grocery_schema
import jwt
from shared import secret_key, bcrypt
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

# function to process receipts and add grocery items to the database using sqlalchemy
def process_receipts_and_add_groceries(user_id, receipt_data):
    for data in receipt_data:
        grocery = Grocery(
            user_id=user_id,
            item=data['item'],
            price=data['price'],
            quantity=data['quantity']
        )
        db.session.add(grocery)
        db.session.commit()

