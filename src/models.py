import uuid
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key = True)
    created_at = Column(TIMESTAMP, server_default = func.now())

    categories = relationship('Category', back_populates = 'user')
    receipts = relationship('Receipt', back_populates = 'user')

class Category(Base):
    __tablename__ = 'categories'

    id = Column(String, primary_key = True, default = lambda : str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'))
    category_name = Column(String(30), nullable = False)
    budget = Column(Numeric, default = None)

    user = relationship('User', back_populates = 'categories')
    receipts = relationship('Receipt', back_populates = 'category')

class Receipt(Base):
    __tablename__ = 'receipts'

    id = Column(String, primary_key = True, default = lambda : str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'))
    category_id = Column(String, ForeignKey('categories.id'))
    expense_date = Column(TIMESTAMP, server_default = func.now())
    amount = Column(Numeric, nullable = False)
    description = Column(String(50))

    user = relationship('User', back_populates = 'receipts')
    category = relationship('Category', back_populates = 'receipts')