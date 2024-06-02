from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from src.api import auth
import sqlalchemy
from src import database as db
from typing import Literal
from sqlalchemy.exc import DBAPIError

router = APIRouter(
    prefix="/mods",
    tags=["mods"],
    dependencies=[Depends(auth.get_api_key)],
)

class Mod(BaseModel):
    sku: Literal["FIRE", "EARTH", "WATER"]
    type: Literal["fire", "earth", "water"]
    price: int = Field(gt=0, lt=200)
    quantity: int = Field(gt=0, lt=20)

@router.post("/attach/mods")
def attach_mods():
    '''
    Attaching mods to items. 
    '''
     
    # TODO: this function does not work properly ... 
    # attaching even after it runs out of items to attach to 
    try: 
        with db.engine.begin() as connection:
            base_items = connection.execute(sqlalchemy.text("""SELECT item_id, item_sku, type, SUM(qty_change) AS qty_change FROM items_ledger
                                            JOIN items_plan ON items_ledger.item_id = items_plan.id
                                            WHERE items_plan.mod_id = 0 and items_ledger.customer_id = 0
                                            GROUP BY item_id, item_sku, type
                                            HAVING SUM(qty_change) > 0"""))
            
            planned_items = connection.execute(sqlalchemy.text("SELECT * FROM items_plan WHERE NOT mod_id = 0"))

            mod_catalog = connection.execute(sqlalchemy.text("""SELECT mods_plan.id, mods_plan.sku, mods_plan.type, sum(qty_change) AS quantity 
                                                            FROM mods_ledger JOIN mods_plan ON mods_ledger.mod_id = mods_plan.id 
                                                            GROUP BY mods_plan.id, mods_plan.sku, mods_plan.type"""))
        
            # Rows saved as dictionaries of all items eligible to be modded
            base_items_dict = [row._asdict() for row in base_items.fetchall()] 
            # All possible planned items saved as dictionaries
            planned_items_dict = [row._asdict() for row in planned_items.fetchall()] 

            final_items = []
            used_items_dict = []
            mod_catalog_dict = []

            for mod in mod_catalog:
                quantity = mod.quantity
                for item in base_items_dict:
                    # If there are mods that are available and we have weapons to mod, add them!
                    if quantity != 0: 
                        used_item = item
                        # Attach until we run out of weapons or mods.
                        used_item["qty_change"] = -1*min(abs(item["qty_change"]), abs(mod.quantity)) 
                        used_item["credit_change"] = 0 
                        # Dictionary row to add to the ledger
                        final_items += [{"qty_change": -1*used_item["qty_change"], 
                                        "item_id": next(i["id"] for i in planned_items_dict if i["sku"] == mod.sku + "_" + item["item_sku"]),
                                        "item_sku": mod.sku + "_" + item["item_sku"],
                                        "credit_change": 0,
                                        "customer_change": 0}]
                        # Dictionary row to add to the ledger, subtracts base item
                        used_items_dict += [used_item] 
                        # The quantity variable keeps track of how many mods are left to use
                        quantity += used_item["qty_change"] 

                # only want to add to mod ledger if there is quantity change
                if quantity - mod.quantity != 0:
                    mod_catalog_dict += [{"qty_change": quantity - mod.quantity, "mod_id": mod.id, "mod_sku": mod.sku, "credit_change": 0}]
            
            if used_items_dict and final_items:
                connection.execute(sqlalchemy.text("""INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change) 
                                                VALUES (:qty_change, :item_id, :item_sku, :credit_change)"""), used_items_dict + final_items) # Insert all changes (Base items removed), modded versions added
                connection.execute(sqlalchemy.text("INSERT INTO mods_ledger (qty_change, mod_id, mod_sku, credit_change) VALUES (:qty_change, :mod_id, :mod_sku, :credit_change)"), mod_catalog_dict)
                return "OK"
            else:
                return "ERROR: mods could not be attached. No items to attach to, or 0 mods available."
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

@router.post("/purchase/mods")
def purchase_mods(mod_catalog: list[Mod]):
    '''
    Nurane gives list of mods, we buy inventory accordingly. 
    '''

    '''
    NEW logic: buy up to four of each kind of mod, depending on what we have in inventory 
    (as in, what we haven't attached ...)
    '''

    order = []

    credits_sql = '''
    SELECT COALESCE((SELECT SUM(items_ledger.credit_change) FROM items_ledger), 0) + 
           COALESCE((SELECT SUM(mods_ledger.credit_change) FROM mods_ledger), 0) AS credits
    '''

    mods_sql = '''
    SELECT mod_sku, SUM(qty_change)
    FROM mods_ledger
    GROUP BY mod_sku
    '''

    # NOTE: this will return None if there are no entries in either of the ledgers ... 
    try:
        with db.engine.begin() as connection:
            credits = connection.execute(sqlalchemy.text(credits_sql)).scalar()
            num_each_type = connection.execute(sqlalchemy.text(mods_sql)).all()
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    # storing the num of each type of item 
    # key: type
    # value: num we have
    type_dict = {}

    # convert query return from list of tuples to dict
    for value in num_each_type:
        # don't want to include 
        if value[0] != "NONE":
            type_dict[value[0]] = value[1]

    # fill in, just in case haven't bought item of certain type
    if "FIRE" not in type_dict:
        type_dict["FIRE"] = 0
    if "EARTH" not in type_dict:
        type_dict["EARTH"] = 0
    if "WATER" not in type_dict:
        type_dict["WATER"] = 0

    # iterate through each item being offered by Nurane, buy according to logic specified above
    for mod in mod_catalog: 
        # input validation: the sku has to match the type
        if mod.sku.lower() != mod.type: 
            raise HTTPException(status_code=422, detail="Transaction Failed: Mod SKU Does Not Match Mod Type")
       
        # NOTE: we only want to buy if we have fewer than 4 and price is "reasonable"
        if type_dict[mod.sku] < 4 and mod.price <= 20:
            # number we would want to buy, without restrains of price, num offered by Nurane
            # maybe we could just do a check or something, i am not sure what the best to do this is tbh
            num_wanted = min(4, 4 - type_dict[mod.sku])
            num_can_afford = credits // mod.price
            # now, introduce restraints
            num_possible = min(mod.quantity, min(num_can_afford, num_wanted))
            # if, given restraints, we can buy something --> add it to order
            if num_possible > 0: 
                order.append(
                    {
                        "sku": mod.sku,
                        "type" : mod.type, 
                        "price" : mod.price,
                        "qty" : num_possible             
                    }
                )
            # update credits
            credits -= num_possible * mod.price
            # update num we have in dictionary
            type_dict[mod.sku] += num_possible

    # to get id from mods_plan    
    id_sql = '''
    SELECT id 
    FROM mods_plan 
    WHERE sku = :sku 
    '''
    
    # to make insertion into mods_ledger
    pur_sql = '''
    INSERT INTO mods_ledger (qty_change, mod_id, mod_sku, credit_change) VALUES (:qty, :mod_id, :mod_sku, :credit_change)
    '''

    # once the order has been created, run through and make the appropriate inserts
    try:
        with db.engine.begin() as connection:
            for line_item in order:
                print(line_item)
                id = connection.execute(sqlalchemy.text(id_sql), [{"sku":line_item['sku']}]).scalar()
                connection.execute(sqlalchemy.text(pur_sql), [{"qty":line_item['qty'], "mod_id":id, "mod_sku":line_item['sku'], "credit_change": -line_item['price'] * line_item['qty']}])
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
        
    return order