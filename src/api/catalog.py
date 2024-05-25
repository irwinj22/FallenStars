from fastapi import APIRouter, Depends
from src import database as db
from src.api import auth
import sqlalchemy

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
    dependencies=[Depends(auth.get_api_key)],
)

# TODO: catalog only gets items, not mods ... but that makes sense because aren't selling mods individually, 
# only as attachments to items 

router = APIRouter()
@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    json = []

    sql = '''
    SELECT items_plan.id AS "item_id", items_plan.sku AS "item_sku", items_plan.type AS "type",
           mods_plan.id AS "mod_id", mods_plan.sku AS "mod_sku", (items_plan.price + mods_plan.markup) AS "price", 
           SUM(items_ledger.qty_change) AS "qty" 
    FROM items_plan
    JOIN items_ledger ON items_ledger.item_id = items_plan.id 
    JOIN mods_plan ON mods_plan.id = items_plan.mod_id
    WHERE (items_plan.price + mods_plan.markup) > 0
    GROUP BY items_plan.id, items_plan.sku, items_plan.type, mods_plan.id, mods_plan.sku
    '''
  
    with db.engine.begin() as connection:
        items_in_stock = connection.execute(sqlalchemy.text(sql)).fetchall() 

    for line_item in items_in_stock:
        json.append(
            {
                # "item_id" : line_item.item_id,
                "sku" : line_item.item_sku, 
                "type" : line_item.type,
                # "mod_id": line_item.mod_id,
                "mod" : line_item.mod_sku,
                "price" : line_item.price,
                "qty" : line_item.qty
            }      
        )

    return json


''' 
some other things that are worth taking note of: 

going to have a different entry in item_plan for every different combination of mod? is that true? 
if so, then I am going to have to take mods into account here ...


i think that mod_id being 0 means that there is no mod or something, otherwise how are we 
going to be able to make sure that the joins work and what not? 

mods_plan.compatibile should be defined as a list of text ... 


have to get "caught up" for some things to work, which seems kind of wild to me I don't understand 
I guess that's something that we will have to talk to Pierce about .. 

getting rid of the whole plan/deliver thing, which we didn't talk about but I think makese a lot of sense tbh .. 
'''
    
