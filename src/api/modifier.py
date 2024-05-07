from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/modifier",
    tags=["modifier"],
    dependencies=[Depends(auth.get_api_key)],
)

class WeaponInventory(BaseModel):
    sku: str
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_modifiers(weapons_delivered: list[WeaponInventory], order_id: int):
    """ """
    print(f"potions delievered: {weapons_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        for weapon in weapons_delivered:
            connection.execute(sqlalchemy.text("""INSERT INTO weapon_ledger (sku, change, description) 
                                           VALUES (:x, :y, :z)"""),
                                           [{"x": weapon.sku, "y": 1, "z": "Modifier Added"}])
            connection.execute(sqlalchemy.text("""INSERT INTO weapon_ledger (sku, change, description) 
                                           VALUES (:x, :y, :z)"""),
                                           [{"x": weapon.sku.split("_")[0], "y": 1, "z": "Modifier Added"}])
            connection.execute(sqlalchemy.text("""INSERT INTO modifier_ledger (sku, change, description) 
                                           VALUES (:x, :y, :z)"""),
                                           [{"x": weapon.sku.split("_")[1], "y": -1, "z": "Modifier Added"}])

    return "OK"

@router.post("/plan")
def get_modify_plan():
    """
    Add modifiers to weapons
    """
    with db.engine.begin() as connection:
        num_whet = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS num_modifiers
                                                     FROM modifier_ledger
                                                    WHERE sku = :x"""),[{"x": "WHET_STONE"}]).scalar_one()
        num_kat = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(change), 0) AS num_katanas
                                                     FROM weapon_ledger
                                                    WHERE sku = :x"""),[{"x": "KATANA"}]).scalar_one()
        if num_whet > 0 and num_kat > 0:
            return
        [{
                "sku": "KATANA_SHARP",
                "quantity": 1
            }
            ]
            

    return []
    
    

if __name__ == "__main__":
    print(get_modify_plan())
