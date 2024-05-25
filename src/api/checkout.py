from fastapi import APIRouter, Depends
from src import database as db
from pydantic import BaseModel
from src.api import auth
import sqlalchemy

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
    dependencies=[Depends(auth.get_api_key)],
)

class Customer(BaseModel):
    name: str
    role: str

class CheckoutItem(BaseModel):
    item_sku: str
    mod_sku: str
    qty: int

# one Customer will call Checkout, and each Checkout will include one or more CheckoutItems

router = APIRouter()
@router.post("/checkout/", tags=["checkout"])
def checkout(customer:Customer, checkout_items: list[CheckoutItem]):
    
    # insert new customer in customers 
    # NOTE: this will allow for repeat customers, which we don't want
    # however, do we really want to uniquely identify customers by name? that doesn't make much sense to me either tbh ...
    
    sql = '''
    INSERT INTO customers (name, role) VALUES (:name, :role)
    '''

    # TODO: really, the insertion into customers and item_ledger should occur atomically (under the same with statement)
    with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(sql), [{"name":customer.name, "role":customer.role}])


    sql = '''
    SELECT items_plan.id AS "item_id", items_plan.price + mods_plan.markup AS "total_price"
    FROM items_plan
    JOIN mods_plan ON mods_plan.id = items_plan.mod_id
    WHERE items_plan.sku = :item_sku
    AND mods_plan.sku = :mod_sku
    '''

    item_sql = '''
    INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change) VALUES (:qty_change, :item_id, :item_sku, :credit_change)
    '''

    # iterate through each item being purchased, make insertion into items_ledger
    for item in checkout_items:
        print(item)
        with db.engine.begin() as connection:
            # get the item_id, total_price for insertion
            info = connection.execute(sqlalchemy.text(sql), [{"item_sku":item.item_sku, "mod_sku":item.mod_sku}]).fetchone()
            # make insertion into item_ledger
            connection.execute(sqlalchemy.text(item_sql), [{"qty_change":-item.qty, "item_id":info.item_id, "item_sku":item.item_sku, "credit_change":info.total_price}])

    return "OK"

# TODO: items_ledger needs to have a customer_id, that needs to be included with all of this