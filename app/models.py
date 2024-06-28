from sqlalchemy import Column, Integer, String, Float
from .database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    street = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    zipcode = Column(Integer)
    latitude = Column(Float, index=True)
    longitude = Column(Float, index=True)
