from fastapi import APIRouter, Depends
import sqlalchemy
from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
    dependencies=[Depends(auth.get_api_key)],
)

router = APIRouter()
@router.get("/catalog/", tags=["catalog"])
def get_weapon_catalog():
    with db.engine.begin as connection:
        in_stock = connection.execute(sqlalchemy.text("""SELECT sku, name, type, damage, modifier, price, COALESCE(SUM(change),0) AS total
                                                      FROM weapon_inventory
                                                      JOIN weapon_ledger ON weapon_inventory.id = weapon_id
                                                      GROUP BY sku, name, type, damage, modifier, price
                                                      """))

    json = []
    for row in in_stock:
        if row.total !=0:
            json.append(
                {
                    "sku": row.sku,
                    "name": row.name,
                    "type": row.type,
                    "damage": row.damage,
                    "modifier": row.modifier,
                    "price": row.price,
                    "quantity": row.total
                }
            )