from sqlalchemy import ForeignKey, create_engine, MetaData, Table, Column, Integer, String, DateTime, func

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

# Create an SQLite engine in echo mode
engine = create_engine('sqlite:///:memory:', echo=True)

# This will print the SQL for the table creation
metadata.create_all(engine)
