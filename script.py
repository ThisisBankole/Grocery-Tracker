from sqlalchemy import ForeignKey, create_engine, MetaData, Table, Column, Integer, String, DateTime, func
import os
from dotenv import load_dotenv

load_dotenv()

metadata = MetaData()

user_table = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True),
    Column('first_name', String(100), nullable=False),
    Column('last_name', String(100), nullable=False),
    Column('email', String(100), nullable=False),
    Column('password', String(100), nullable=False),
    Column('timestamp', DateTime, default=func.now(), onupdate=func.now())
)
grocery_table = Table(
    'grocery', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False,),
    Column('item', String(100), nullable=False),
    Column('timestamp', DateTime, default=func.now(), onupdate=func.now())
)

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)


# This will print the SQL for the table creation
metadata.create_all(engine)
