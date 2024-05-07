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

class Modifier (BaseModel):
    sku: str
    type: str
    price: int
    quantity: int

class ModifierInventory(BaseModel):
    sku: str
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_modifiers(mods_delivered: list[ModifierInventory], order_id: int):
    """ 
    Deliver purchased modifications.
    """

    print(f"modifications delievered: {mods_delivered} order_id: {order_id}")

    for mod in mods_delivered:
        with db.engine.begin() as connection:
            mod_id = connection.execute(sqlalchemy.text("SELECT id FROM mod_inventory WHERE mod_inventory.sku = :sku"),[{"sku": mod.sku}]).scalar_one()
            connection.execute(sqlalchemy.text("INSERT INTO mod_ledger (mod_id, change) VALUES(:mod_id, :change)"),[{"mod_id": mod_id, "change": mod.quantity}])
            
    return "OK"

@router.post("/plan")
def get_modify_plan(modifier_catalog: list[Modifier]):
    """
    Plan to buy modifications.
    """

    json = []

    # "credits" is purchasing power 
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM credit_ledger")).scalar_one()


    # per example flow, want to buy calibration modifier ONLY
    for mod in modifier_catalog:
        if mod.sku == "CALIBRATION" and credits > (2 * mod.price):
            json.append(
                {
                    "sku": mod.sku,
                    "quantity": 1
                }
            )
    return json

            

if __name__ == "__main__":
    print(get_modify_plan())
