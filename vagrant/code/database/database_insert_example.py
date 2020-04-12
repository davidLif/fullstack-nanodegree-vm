from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

# This command creates the connections between our class definitions and the corresponding tables in the db.
Base.metadata.bind = engine

# create a session, add an entry, commit and exit
DBSession = sessionmaker(bind=engine)
session = DBSession()
first_restaurant = Restaurant(name="Pizza Palace")
session.add(first_restaurant)
session.commit()
session.query(Restaurant).all()

first_item = MenuItem(name='Cheese Pizza', description='Made with all natural ingredients nd fresh mozzarela',
                      course='Entry', price='8.99$', restaurant=first_restaurant)
session.add(first_item)
second_item = MenuItem(name='Pizza2', description='Made up', course='Entry', price='9.99$', restaurant=first_restaurant)
session.add(first_item)
session.commit()
session.query(MenuItem).all()

# read
first_query = session.query(Restaurant).first()
print(first_query.name)
second_query = session.query(MenuItem).filter_by(name='Cheese Pizza').one()
print(second_query.description)

# update
pizza = session.query(MenuItem).filter_by(name='Cheese Pizza').one()
pizza.price = '7.99$'
session.add(pizza)
session.commit()

# delete
pizza_to_delete = session.query(MenuItem).filter_by(name='Pizza2').one()
session.delete(pizza_to_delete)
session.commit()
