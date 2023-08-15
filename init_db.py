# import required libraries and modules
import pathlib
from config import db, app  # Import the database instance and the app instance from your config.py

# Import your models
from models import Grocery, User, GroceryItem  # Add any other models you may create in the future

# Now you'll create the tables based on the models
def init_db():
    with app.app_context():  # Push an application context to use Flask-SQLAlchemy outside a request
        db.create_all()

if __name__ == '__main__':
    init_db()
