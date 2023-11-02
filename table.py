from app import db
from models import User, Grocery
from config import app


with app.app_context():
    groceries = Grocery.query.all()

    for grocery in groceries:
        user = User.query.get(grocery.user_id)
        grocery.account_id = user.account_id

    db.session.commit()