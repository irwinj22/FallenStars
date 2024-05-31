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
    qty: int

# one Customer will call Checkout, and each Checkout will include one or more CheckoutItems

router = APIRouter()
@router.post("/checkout/", tags=["checkout"])
def checkout(customer:Customer, checkout_items: list[CheckoutItem]):
    # NOTE: have to create customer first, since foreign key reference in items_ledger
    with db.engine.begin() as connection:
        # check if customer record exists, get id
        sql = '''
        SELECT id
        FROM customers
        WHERE name = :name AND role = :role
        '''

        id = connection.execute(sqlalchemy.text(sql), [{"name":customer.name, "role":customer.role}]).scalar()

        # if not, then create a new record and use THAT id .. 
        if id is None:
            sql = '''
            INSERT INTO customers (name, role) VALUES (:name, :role)
            returning id
            '''
            id = connection.execute(sqlalchemy.text(sql), [{"name":customer.name, "role":customer.role}]).scalar()

    # NOW, make insertion into ledger for each type of item that was bought
    sql = '''
    SELECT items_plan.id AS "item_id", items_plan.price + mods_plan.markup AS "total_price"
    FROM items_plan
    JOIN mods_plan ON mods_plan.id = items_plan.mod_id
    WHERE items_plan.sku = :item_sku
    '''

    item_sql = '''
    INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) VALUES (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)
    '''

    for item in checkout_items:
        print(item)
        with db.engine.begin() as connection:
            # get the item_id, total_price for insertion
            info = connection.execute(sqlalchemy.text(sql), [{"item_sku":item.item_sku}]).fetchone()
            # make insertion into item_ledger
            connection.execute(sqlalchemy.text(item_sql), 
                                [{"qty_change":-item.qty, "item_id":info.item_id, "item_sku":item.item_sku, "credit_change":info.total_price, "customer_id":id}])

    return "OK"

