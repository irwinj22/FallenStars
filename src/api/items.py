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
    NEW LOGIC: 
    Buy so that we have 6 items of each type (weapon, armor, other)
    '''

    order = []

    credits_sql = '''
    SELECT COALESCE((SELECT SUM(items_ledger.credit_change) FROM items_ledger), 0) + 
           COALESCE((SELECT SUM(mods_ledger.credit_change) FROM mods_ledger), 0) AS credits
    '''

    items_sql = '''
    SELECT items_plan.type, SUM(qty_change)
    FROM items_ledger
    JOIN items_plan ON items_plan.id = items_ledger.item_id
    GROUP BY items_plan.type
    '''

    # NOTE: extra connection is necessary, as we can't buy items without knowing how much money we have
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text(credits_sql)).scalar()
        num_each_type = connection.execute(sqlalchemy.text(items_sql)).all()

    # storing the num of each type of item 
    # key: type
    # value: num we have
    type_dict = {}

    # convert query return from list of tuples to dict
    for value in num_each_type:
        type_dict[value[0]] = value[1]

    # fill in, just in case haven't bought item of certain type
    if "weapon" not in type_dict:
        type_dict["weapon"] = 0
    if "armor" not in type_dict:
        type_dict["armor"] = 0
    if "other" not in type_dict:
        type_dict["other"] = 0
  
    # iterate through each item being offered by Nurane, buy if we have fewer than 6
    for item in item_catalog: 
        # number we would want to buy, without restrains of price, num offered by Nurane
        num_wanted = min(6, abs(6 - type_dict[item.type]))
        num_can_afford = credits // item.price
        # now, introduce restraints
        num_possible = min(item.quantity, min(num_can_afford, num_wanted))
        # if, given restraints, we can buy something --> add it to order
        if num_possible > 0: 
            order.append(
                {
                    "sku": item.sku,
                    "type" : item.type, 
                    "price" : item.price,
                    "qty" : num_possible             
                }
            )
        # update credits
        credits -= num_possible * item.price
        # update num we have in dictionary (in case another item of same type offered later)
        type_dict[item.type] += num_possible

    # once we iterate through catalog, want to make insertion into ledger
 
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
