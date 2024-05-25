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

@router.post("/rental")
def rental_assign():
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""UPDATE i_log SET rental = :x
                                           WHERE id = (SELECT MIN(id) 
                                           FROM i_log
                                           WHERE Owner IS NULL AND rental = :y)"""), [{"x": True, "y": False}])
        connection.execute(sqlalchemy.text("""UPDATE w_log SET rental = :x
                                           WHERE id = (SELECT MIN(id) 
                                           FROM w_log
                                           WHERE Owner IS NULL AND rental = :y)"""), [{"x": True, "y": False}])
        connection.execute(sqlalchemy.text("""UPDATE a_log SET rental = :x
                                           WHERE id = (SELECT MIN(id) 
                                           FROM a_log
                                           WHERE Owner IS NULL AND rental = :y)"""), [{"x": True, "y": False}])
    return "OK"

@router.post("/rental_return")
def rental_return(cart_id: int):
    """
    Share current time.
    """
    with db.engine.begin() as connection:
        results = connection.execute(sqlalchemy.text("""SELECT checkin, rented_id, rented_type FROM rentals 
                                                          WHERE cart_id = :x AND returned = :y"""), [{"x":cart_id, "y": False}]).all() 
        current_utc_timestamptz = datetime.now(timezone.utc)
        for row in results:
            if current_utc_timestamptz > row[0]:
                connection.execute(sqlalchemy.text("""UPDATE rentals SET returned = :x"""), [{"x": True}])
                if row[2] in ("attack", "defense", "support"):
                    connection.execute(sqlalchemy.text("""UPDATE i_log 
                                                       SET owner = :x 
                                                       WHERE i_log.i_id = :y"""), [{"x": None, "y": row[1]}])
                elif row[2] in ("melee", "rifle", "pistol"):
                    connection.execute(sqlalchemy.text("""UPDATE w_log 
                                                       SET owner = :x 
                                                       WHERE w_log.w_id = :y"""), [{"x": None, "y": row[1]}])
                elif row[2] in ("street", "combat", "powered"):
                    connection.execute(sqlalchemy.text("""UPDATE a_log 
                                                       SET owner = :x 
                                                       WHERE a_log.a_id = :y"""), [{"x": None, "y": row[1]}])
            #iso_formatted_string = timestamp_dt.isoformat()
            
    return "OK"

