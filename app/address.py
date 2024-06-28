from . import schemas, models
from .logger import logger
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from .database import get_db

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_address(payload: schemas.AddressBase, db: Session = Depends(get_db)):
    new_address = models.Address(**payload.model_dump())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    logger.info("Successfully added new address")
    return {"status": "success", "address": new_address}
