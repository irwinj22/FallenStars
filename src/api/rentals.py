from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
from src import database as db
import sqlalchemy
from datetime import datetime, timedelta, timezone


router = APIRouter(
    prefix="/rentals",
    tags=["rentals"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/rental_return")
def rental_return(cart_id: int):
    """
    Share current time.
    """
    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("""SELECT checkin, rented_id, rented_type FROM rentals 
                                                          WHERE cart_id = :x"""), [{"x":cart_id}]).all() 
        timestamp_dt = datetime.now(timezone.utc)
        for row in results:
            checkin_dt = datetime.fromisoformat(row[0])
            if timestamp_dt < checkin_dt:
                connection.execute(sqlalchemy.text("""UPDATE rentals SET returned = :x""", [{"x": True}]))
                if row[2] in ("attack", "defense", "support"):
                    connection.execute(sqlalchemy.text("""UPDATE i_log SET owner = :x""", [{"x": None}]))
                elif row[2] in ("melee", "rifle", "pistol"):
                    connection.execute(sqlalchemy.text("""UPDATE w_log SET owner = :x""", [{"x": None}]))
                elif row[2] in ("street", "combat", "powered"):
                    connection.execute(sqlalchemy.text("""UPDATE a_log SET owner = :x""", [{"x": None}]))

            #iso_formatted_string = timestamp_dt.isoformat()
            
    return "OK"

