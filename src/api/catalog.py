from fastapi import APIRouter, Depends

from src import database as db
from src.api import auth
import sqlalchemy

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"],
    dependencies=[Depends(auth.get_api_key)],
)

router = APIRouter()
@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    '''
    Offer all possible items to customer.
    '''

    json = []

    sql = '''
    SELECT items_plan.id AS "item_id", items_plan.sku AS "item_sku", items_plan.type AS "type",
           mods_plan.id AS "mod_id", mods_plan.sku AS "mod_sku", (items_plan.price + mods_plan.markup) AS "price", 
           SUM(items_ledger.qty_change) AS "qty" 
    FROM items_plan
    JOIN items_ledger ON items_ledger.item_id = items_plan.id 
    JOIN mods_plan ON mods_plan.id = items_plan.mod_id
    GROUP BY items_plan.id, items_plan.sku, items_plan.type, mods_plan.id, mods_plan.sku
    HAVING SUM(items_ledger.qty_change) > 0
    '''
  
    # get all items in stock
    with db.engine.begin() as connection:
        items_in_stock = connection.execute(sqlalchemy.text(sql)).fetchall() 

    # offer each item in catalog 
    for line_item in items_in_stock:
        json.append(
            {
                "sku" : line_item.item_sku, 
                "type" : line_item.type,
                "mod" : line_item.mod_sku,
                "price" : line_item.price,
                "qty" : line_item.qty
            }      
        )

    return json
  