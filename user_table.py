from app import db
from models import User, Account
from config import app


with app.app_context():
   # Get all users
   users = User.query.all()

   for user in users:
      # Create a new account for the user
      account = Account()
      db.session.add(account)
      db.session.commit()

      # Assign the account to the user
      user.account_id = account.id

   # Commit the changes
   db.session.commit()