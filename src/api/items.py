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

class Weapon (BaseModel):
    sku: str
    type: str
    damage: str
    price: int
    quantity: int

class Armor (BaseModel):
    sku: str
    type: str
    price: int
    quantity: int

class Item (BaseModel):
    sku: str
    type: str
    price: int
    quantity: int   

# TODO: this function is assuming that all weapons delivered will be in inventory 
# (ie: no new weapons ever?)
# YES! Because weapon_inventory dictates what you want to buy!!!
@router.post("/deliver_weapon")
def deliver_weapon(delivered_weapons: list[Weapon], order_id: int):
    '''
    Deliver purchased weapons.
    '''

    ''' NOTE:
    "weapon inventory" is spec of all weapons we are looking to purchase, 
    whereas weapon_log contains all the weapons that we have either bought or sold 
    TRUE
    '''
    with db.engine.begin() as connection:
        w_id = connection.execute(sqlalchemy.text("select id, sku from weapon_inventory"))
        w_id_dict = [w._asdict() for w in w_id]
        print(w_id_dict)
        dict_bulk = []
        cost = 0
        for weapon in delivered_weapons:
            dict_bulk += [{"w_id": next(w['id'] for w in w_id_dict if w['sku'] == weapon.sku), "type": weapon.type}] * weapon.quantity
            cost -= weapon.price*weapon.quantity
        connection.execute(sqlalchemy.insert(db.w_log), dict_bulk)
        connection.execute(sqlalchemy.text("insert into credit_ledger (change) values (:cost)"),[{"cost": cost}])
            
    return "OK"

@router.post("/deliver_armor")
def deliver_armor(delivered_armor: list[Armor], order_id: int):
    '''
    Deliver purchased armor.
    '''
    with db.engine.begin() as connection:
        a_id = connection.execute(sqlalchemy.text("select id, sku from armor_inventory"))
        a_id_dict = [a._asdict() for a in a_id]
        dict_bulk = []
        cost = 0
        for armor in delivered_armor:
            dict_bulk.append({"a_id": next(a['id'] for a in a_id_dict if a['sku'] == armor.sku), "type": armor.type})
            cost -= armor.price*armor.quantity
        connection.execute(sqlalchemy.insert(db.a_log), dict_bulk)
        connection.execute(sqlalchemy.text("insert into credit_ledger (change) values (:cost)"),[{"cost": cost}])         
    return "OK"

@router.post("/deliver_items")
def deliver_items(delivered_items: list[Item], order_id: int):
    '''
    Deliver purchased armor.
    '''
    with db.engine.begin() as connection:
        i_id = connection.execute(sqlalchemy.text("select id, sku from item_inventory"))
        i_id_dict = [i._asdict() for i in i_id]
        dict_bulk = []
        cost = 0
        for item in delivered_items:
            dict_bulk.append({"i_id": next(i['id'] for i in i_id_dict if i['sku'] == item.sku), "type": item.type})
            cost -= item.price*item.quantity
        connection.execute(sqlalchemy.insert(db.i_log), dict_bulk)
        connection.execute(sqlalchemy.text("insert into credit_ledger (change) values (:cost)"),[{"cost": cost}])         
    return "OK"

@router.post("/weapon_plan")
def get_weapon_plan(weapon_catalog: list[Weapon]):
    '''
    Plan to buy weapons.
    '''

    json = []

    # "credits" is purchasing power 
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM credit_ledger")).scalar_one()
    # per example flow, want to buy 2 laser pistols, so look for those in what is offered
    for weapon in weapon_catalog:
        if weapon.sku == "LASER_PISTOL" and credits > (2 * weapon.price):
            json.append(
                {
                    "sku": weapon.sku,
                    "quantity": 2
                }
            )
    return json

@router.post("/armor_plan")
def get_armor_plan(armor_catalog: list[Armor]):
    '''
    Plan to buy armor.
    '''

    json = []

    # "credits" is purchasing power 
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM credit_ledger")).scalar_one()    
    for armor in armor_catalog:
        if armor.sku == "STREET" and credits > armor.price:
            json.append(
                {
                    "sku": armor.sku,
                    "quantity": 1
                }
            )
    return json

@router.post("/item_plan")
def get_item_plan(item_catalog: list[Item]):
    '''
    Plan to buy misc items.
    '''

    json = []

    # "credits" is purchasing power 
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM credit_ledger")).scalar_one()
    # per example flow, want to buy 2 laser pistols, so look for those in what is offered
    for item in item_catalog:
        if item.sku == "COMPASS" and credits > item.price:
            json.append(
                {
                    "sku": item.sku,
                    "quantity": 1
                }
            )
    return json

if __name__ == "__main__":
    print(get_weapon_plan())