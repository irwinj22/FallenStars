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
def get_catalog():
    with db.engine.begin() as connection:
        # Set up stock for weapons, armor, and items separately
        weapons_in_stock = connection.execute(sqlalchemy.text("""SELECT weapon_inventory.id AS thing_id, weapon_inventory.sku, weapon_inventory.name, weapon_inventory.type, weapon_inventory.damage, mod_inventory.sku AS modifier, weapon_inventory.price
                                                      FROM weapon_inventory
                                                      LEFT JOIN w_log ON weapon_inventory.id = w_log.w_id
                                                      LEFT JOIN mod_inventory ON mod_inventory.id = w_log.m_id
                                                      """)).fetchall()
        
        armor_in_stock = connection.execute(sqlalchemy.text("""SELECT armor_inventory.id AS thing_id, armor_inventory.sku, armor_inventory.name, armor_inventory.type, mod_inventory.sku AS modifier, armor_inventory.price
                                                      FROM armor_inventory
                                                      LEFT JOIN a_log ON armor_inventory.id = a_log.a_id
                                                      LEFT JOIN mod_inventory ON mod_inventory.id = a_log.m_id
                                                      """)).fetchall()

        items_in_stock = connection.execute(sqlalchemy.text("""SELECT item_inventory.id AS thing_id, item_inventory.sku, item_inventory.name, item_inventory.type, mod_inventory.sku AS modifier, item_inventory.price
                                                      FROM item_inventory
                                                      LEFT JOIN i_log ON item_inventory.id = i_log.i_id
                                                      LEFT JOIN mod_inventory ON mod_inventory.id = i_log.m_id
                                                      """)).fetchall()

    json = []
    for row in weapons_in_stock:
        rental = False
        if row.thing_id <= 1:
            rental = True
        if row.total !=0:
            json.append(
                {
                    "thing_id": row.thing_id,
                    "sku": row.sku,
                    "name": row.name,
                    "type": row.type,
                    "damage": row.damage,
                    "modifier": row.modifier,
                    "price": row.price,
                    "rental": rental
                }
            )

    for row in armor_in_stock:
        rental = False
        if row.thing_id <= 1:
            rental = True
        if row.total !=0:
            json.append(
                {
                    "thing_id": row.thing_id,
                    "sku": row.sku,
                    "name": row.name,
                    "type": row.type,
                    "modifier": row.modifier,
                    "price": row.price,
                    "rental": rental
                }
            )
    
    for row in items_in_stock:
        rental = False
        if row.thing_id <= 1:
            rental = True
        if row.total !=0:
            json.append(
                {
                    "thing_id": row.thing_id,
                    "sku": row.sku,
                    "name": row.name,
                    "type": row.type,
                    "modifier": row.modifier,
                    "price": row.price,
                    "rental": rental
                }
            )
    
    return json