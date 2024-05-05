from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(auth.get_api_key)],
)
'''
class Item(BaseModel):
    id: int
    sku: str
    modifiers: list[int]
    name: setattr
'''
class Weapon (BaseModel):
    sku: str
    type: str
    damage: str
    price: int
    quantity: int

@router.post("/deliver_weapon")
def deliver_weapon(delivered_weapons: list[Weapon], order_id: int):
    with db.engine.begin() as connection:
        for weapon in delivered_weapons:
            weapon_id = connection.execute(sqlalchemy.text("SELECT id FROM weapon_inventory WHERE weapon_inventory.sku = :sku"),[{"sku": weapon.sku}]).scalar_one()
            connection.execute(sqlalchemy.text("INSERT INTO weapon_ledger (weapon_id, change) VALUES(:weapon_id, :change)"),[{"weapon_id": weapon_id, "change": weapon.quantity}])
    return "FUCK YEAH BABYGIRL"

@router.post("/weapon_plan")
def get_weapon_plan(weapon_catalog: list[Weapon]):
    json = []
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM credit_ledger")).scalar_one()
    for weapon in weapon_catalog:
        if weapon.type == "medium" and credits > weapon.price:
            json.append(
                {
                    "sku": weapon.sku,
                    "quantity": 1
                }
            )
    return json