from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/mods",
    tags=["mods"],
    dependencies=[Depends(auth.get_api_key)],
)

class Mod(BaseModel):
    sku: str
    type: str
    price: int
    quantity: int
    compatible: list[str]

@router.post("/attach/mods")
def attach_mods(mod_catalog: list[Mod]):
    with db.engine.begin() as connection:
        base_items = connection.execute(sqlalchemy.text("""select item_id, item_sku, type, sum(qty_change) as qty_change from items_ledger
                                           join items_plan on items_ledger.item_id = items_plan.id
                                           where items_plan.mod_id = 0
                                           group by item_id, item_sku, type
                                           having sum(qty_change) > 0"""))
        planned_items = connection.execute(sqlalchemy.text("select * from items_plan where not mod_id = 0"))

        base_items_dict = [row._asdict() for row in base_items.fetchall()] # Rows saved as dictionaries of all items eligible to be modded
        planned_items_dict = [row._asdict() for row in planned_items.fetchall()] # All possible planned items saved as dictionaries

        final_items = []
        used_items_dict = []
        for mod in mod_catalog:
            quantity = mod.quantity
            for item in base_items_dict:
                if item["type"] in mod.compatible and quantity != 0: # If there are mods that are available and we have weapons to mod, add them!
                    used_item = item
                    used_item["qty_change"] = -1*min(item["qty_change"], mod.quantity) # Attach until we run out of weapons or mods.
                    used_item["credit_change"] = 0 
                    final_items += [{"qty_change": -1*used_item["qty_change"], 
                                     "item_id": next(i["id"] for i in planned_items_dict if i["sku"] == mod.sku + "_" + item["item_sku"]),
                                     "item_sku": mod.sku + "_" + item["item_sku"],
                                     "credit_change": 0}] # Dictionary row to add to the ledger
                    used_items_dict += [used_item] # Dictionary row to add to the ledger, subtracts base item
                    quantity += used_item["qty_change"] # The quantity variable keeps track of how many mods are left to use.
        if used_items_dict and final_items:
            connection.execute(sqlalchemy.text("""insert into items_ledger (qty_change, item_id, item_sku, credit_change) 
                                               values (:qty_change, :item_id, :item_sku, :credit_change)"""), used_items_dict + final_items) # Insert all changes (Base items removed), modded versions added
            return "Your mods are now attached. You're welcome!"
        else:
            return "No mods attached. No items to attach to, or you put in 0 mods!"

@router.post("/purchase/mods")
def purchase_mods(mod_catalog: list[Mod]):
    '''
    Nurane gives list of mods, we buy inventory accordingly. 
    '''

    '''
    Current logic: 
    buy 3 FLAMING_BLADE, if possible (could be restrained by credits or num offered)
    --> if can't buy 3, just buy as many as possible 
    '''

    order = []

    credits_sql = '''
    SELECT (SELECT SUM(items_ledger.credit_change) FROM items_ledger) + 
           (SELECT SUM(mods_ledger.credit_change) FROM mods_ledger) AS credits
    '''

    # NOTE: this will return None if there are no entries in either of the ledgers ... 
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text(credits_sql)).scalar()

    # iterate through each item being offered by Nurane, buy according to logic specified above
    for mod in mod_catalog: 
        if mod.sku == "FLAMING_BLADE":
            num_can_afford = credits // mod.price 
            num_possibile = min(3, min(num_can_afford, mod.quantity))
            # if possible for us to buy more than one, then add to order
            if num_possibile > 0:
                order.append(
                    {
                        "sku": mod.sku,
                        "type" : mod.type, 
                        "price" : mod.price,
                        "qty" : num_possibile
                    }
                )

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
    for line_item in order:
        print(line_item)
        with db.engine.begin() as connection:
            id = connection.execute(sqlalchemy.text(id_sql), [{"sku":line_item['sku']}]).scalar()
            connection.execute(sqlalchemy.text(pur_sql), [{"qty":line_item['qty'], "mod_id":id, "mod_sku":line_item['sku'], "credit_change": -line_item['price'] * line_item['qty']}])

    # TODO: implement the logic of attaching mods to items!!

    return order



