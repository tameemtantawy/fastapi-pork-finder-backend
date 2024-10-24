# models.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String, nullable=False)
    name = Column(String, unique=True, index=True)
    contains_pork = Column(Boolean, default=False)
class Food2(Base):
    __tablename__ = "foods2"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_name = Column(String, nullable=False)
    name = Column(String, unique=True, index=True)
    contains_pork = Column(Boolean, default=False)