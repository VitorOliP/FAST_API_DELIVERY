from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
db = create_engine(DATABASE_URL, echo=True)

'''
create migration: alembic revision --autogenerate -m "mensage"
execute migration: alembic upgrade head
'''

# link do db
# db = create_engine("sqlite:///data.db")

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    email = Column("email", String, nullable=False)
    password = Column("password", String)
    activated = Column("activated", Boolean)
    admin = Column("admin", Boolean, default=False)
    
    def __init__(self, name, email, password, activated=True, admin=False):
        self.name = name
        self.email = email
        self.password = password
        self.activated = activated
        self.admin = admin
        
class Order(Base):
    __tablename__ = "orders"
    
    orders_status = (
        ("pending", "pending"),
        ("canceled", "canceled"),
        ("completed", "completed")
    )
    
    id = Column("id", Integer, primary_key=True, autoincrement=True) 
    user = Column("user", ForeignKey("users.id"))
    status = Column("status", String) #pending, canceled, completed
    price = Column("price", Float)
    itens = relationship("OrderItens", cascade="all, delete")
    
    def __init__(self, user, status="pending", price=0):
        self.user = user
        self.status = status
        self.price = price
        
    def calculate_price(self):
        self.price = sum(item.unit_price * item.quantity for item in self.itens)
        
class OrderItens(Base):
    __tablename__ = "order_itens"
    
    id = Column("id", Integer, primary_key=True, autoincrement=True) 
    quantity = Column("quantity", Integer) 
    flavor = Column("flavor", String)
    size = Column("size", String)
    unit_price = Column("unit_price", Float) 
    order = Column("order", ForeignKey("orders.id"))
    
    def __init__(self, quantity, flavor, size, unit_price, order): 
        self.quantity = quantity
        self.flavor = flavor
        self.size = size
        self.unit_price = unit_price
        self.order = order
        
