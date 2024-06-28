from typing import List
from pydantic import BaseModel


class AddressBase(BaseModel):
    street: str
    city: str
    state: str
    country: str
    zipcode: int
    latitude: float
    longitude: float

    class Config:
        orm_mode = True


class ListNoteResponse(BaseModel):
    status: str
    results: int
    notes: List[AddressBase]
