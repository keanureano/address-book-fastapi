from . import schemas, models
from .logger import logger
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response, Query
from .database import get_db
from geopy.distance import distance as geopy_distance

router = APIRouter()


@router.get("/")
def get_addresses(
    latitude: float = Query(0.0, description="Latitude of the center point"),
    longitude: float = Query(0.0, description="Longitude of the center point"),
    distance: float = Query(
        None, description="Distance in kilometers (default: infinite)"
    ),
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Limit the number of results"),
    page: int = Query(1, description="Page number"),
):
    try:
        skip = (page - 1) * limit

        addresses = db.query(models.Address).limit(limit).offset(skip).all()

        if distance is None:
            # if no distance specified, return all addresses
            logger.info("Returning all addresses as no distance is specified.")
            return {"status": "success", "results": len(addresses), "notes": addresses}
        else:
            # filter addresses by distance using geopy's great_circle function
            filtered_addresses = []
            center_point = (latitude, longitude)

            for address in addresses:
                address_point = (float(address.latitude), float(address.longitude))
                distance_km = geopy_distance(center_point, address_point).kilometers
                if distance is None or distance_km <= distance:
                    filtered_addresses.append(address)

            logger.info(f"Returning addresses within {distance} km.")
            return {
                "status": "success",
                "results": len(filtered_addresses),
                "addresses": filtered_addresses,
            }

    except Exception as e:
        logger.error(f"Error getting addresses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_address(payload: schemas.AddressBase, db: Session = Depends(get_db)):

    # validate coordinates
    if not (-90 <= payload.latitude <= 90) or not (-180 <= payload.longitude <= 180):
        logger.warning(
            "Address can not be saved due to incorrect coordinates as input."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid coordinates"
        )

    try:
        new_address = models.Address(**payload.model_dump())
        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        logger.info("Successfully added new address")
        return {"status": "success", "address": new_address}

    except Exception as e:
        logger.error(f"Error creating address: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put("/{address_id}")
def update_address(
    address_id: int, payload: schemas.AddressBase, db: Session = Depends(get_db)
):
    # validate coordinates
    if not (-90 <= payload.latitude <= 90) or not (-180 <= payload.longitude <= 180):
        logger.warning(
            "Address can not be saved due to incorrect coordinates as input."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid coordinates"
        )

    try:
        address_query = db.query(models.Address).filter(models.Address.id == address_id)
        db_address = address_query.first()
        if not db_address:
            logger.warning(f"No address found with id {address_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address id {address_id} not found",
            )

        # update the address fields
        update_data = payload.model_dump(exclude_unset=True)
        address_query.filter(models.Address.id == address_id).update(
            update_data, synchronize_session=False
        )

        db.commit()
        db.refresh(db_address)
        logger.info(f"Address with id {address_id} updated successfully")
        return {"message": "Address updated successfully"}

    except Exception as e:
        logger.error(f"Error updating address: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    try:
        db_address = (
            db.query(models.Address).filter(models.Address.id == address_id).first()
        )
        if not db_address:
            logger.warning(f"No address found with id {address_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address id {address_id} not found",
            )

        db.delete(db_address)
        db.commit()
        logger.info(f"Address with id {address_id} deleted successfully")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        logger.error(f"Error deleting address: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
