from sqlalchemy import Engine
from fastapi import FastAPI

from app import address, models
from .database import engine
from .logger import logger

# start app
app = FastAPI()

# create database table
models.Base.metadata.create_all(bind=engine)

# include address router
app.include_router(address.router, tags=["Addresses"], prefix="/api/addresses")


# health checker
@app.get("/")
async def root():
    logger.info("Hello World")
    return {"message": "Hello World"}
