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

class Item(BaseModel):
    sku: str
    type: str
    price: int
    quantity: int

@router.post("/purchase/items")
def purchase_items(item_catalog: list[Item]):
    '''
    Nurane gives list of items, we buy inventory accordingly. 
    '''

    '''
    Current logic: 
    buy 5 PISTOL, if possible (could be restrained by credits or num offered)
    --> if can't buy 5, just buy as many as possible 
    '''

    order = []

    credits_sql = '''
    SELECT COALESCE((SELECT SUM(items_ledger.credit_change) FROM items_ledger), 0) + 
           COALESCE((SELECT SUM(mods_ledger.credit_change) FROM mods_ledger), 0) AS credits
    '''

    # NOTE: extra connection is necessary, as we can't buy items without knowing how much money we have
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text(credits_sql)).scalar()

    # iterate through each item being offered by Nurane, buy according to logic specified above
    for item in item_catalog: 
        if item.sku == "PISTOL":
            num_can_afford = credits // item.price 
            num_possibile = min(5, min(num_can_afford, item.quantity))
            # if possible for us to buy more than one, then add to order
            if num_possibile > 0:
                order.append(
                    {
                        "sku": item.sku,
                        "type" : item.type, 
                        "price" : item.price,
                        "qty" : num_possibile
                    }
                )

    # to get id from items_plan    
    id_sql = '''
    SELECT id 
    FROM items_plan 
    WHERE sku = :sku 
    '''
    
    # to make insertion into items_ledger
    pur_sql = '''
    INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change) VALUES (:qty, :item_id, :item_sku, :credit_change)
    '''

    # once the order has been created, run through and make the appropriate inserts
    with db.engine.begin() as connection:
        for line_item in order:
            print(line_item)
            id = connection.execute(sqlalchemy.text(id_sql), [{"sku":line_item['sku']}]).scalar()
            connection.execute(sqlalchemy.text(pur_sql), [{"qty":line_item['qty'], "item_id":id, "item_sku":line_item['sku'], "credit_change": -line_item['price'] * line_item['qty']}])

    return order
