from fastapi import APIRouter, Depends, HTTPException
from src import database as db
from pydantic import BaseModel, Field
from src.api import auth
import sqlalchemy
from typing import Literal

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
    dependencies=[Depends(auth.get_api_key)],
)

class Customer(BaseModel):
    name: str = Field(regex=r"^[a-zA-Z0-9_ ]{1,20}$")
    role: Literal['WARRIOR','SUNBLADE','ASSASSIN','NEXUS','SHIFTER','BUILDER','EXPERT','MAGE','SCOUT']

class CheckoutItem(BaseModel):
    item_sku: Literal['LONGSWORD','FIRE_LONGSWORD','EARTH_LONGSWORD','WATER_LONGSWORD',
        'PISTOL','FIRE_PISTOL','EARTH_PISTOL','WATER_PISTOL',
        'SHIELD','FIRE_SHIELD','EARTH_SHIELD','WATER_SHIELD',
        'HELMET','FIRE_HELMET','EARTH_HELMET','WATER_HELMET',
        'STAFF','FIRE_STAFF','EARTH_STAFF','WATER_STAFF',
        'CHAINLINK','FIRE_CHAINLINK','EARTH_CHAINLINK','WATER_CHAINLINK']
    qty: int = Field(gt=0, lt=20)

# one Customer will call Checkout, and each Checkout will include one or more CheckoutItems

router = APIRouter()
@router.post("/checkout/", tags=["checkout"])
def checkout(customer:Customer, checkout_items: list[CheckoutItem]):
    '''
    Customer purchases item(s).
    '''

    print(checkout_items)

    # NOTE: have to create customer first, since foreign key reference in items_ledger
    with db.engine.begin() as connection:
        # check if customer record exists, get id
        sql = '''
        SELECT id
        FROM customers
        WHERE name = :name AND role = :role
        '''

        id = connection.execute(sqlalchemy.text(sql), [{"name":customer.name.title(), "role":customer.role.title()}]).scalar()

        # if not, then create a new record and use THAT id .. 
        if id is None:
            sql = '''
            INSERT INTO customers (name, role) VALUES (:name, :role)
            returning id
            '''
            id = connection.execute(sqlalchemy.text(sql), [{"name":customer.name.title(), "role":customer.role.title()}]).scalar()

    # NOW, make insertion into ledger for each type of item that was bought
    sql = '''
    SELECT items_plan.id AS "item_id", items_plan.price AS "total_price"
    FROM items_plan
    JOIN mods_plan ON mods_plan.id = items_plan.mod_id
    WHERE items_plan.sku = :item_sku
    '''

    item_sql = '''
    INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) VALUES (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)
    '''

    # NOTE: to make sure that we have enough inventory for purchase
    qty_sql = '''
    SELECT SUM(qty_change)
    FROM items_ledger
    WHERE item_id = :item_id
    '''

    with db.engine.begin() as connection:
        for item in checkout_items:
            print(item)
            # get the item_id, total_price for insertion
            info = connection.execute(sqlalchemy.text(sql), [{"item_sku":item.item_sku}]).fetchone()
            current_qty = connection.execute(sqlalchemy.text(qty_sql), [{"item_id":info.item_id}]).scalar()
            # input validation: make sure we have enough to sell to customer
            if item.qty > current_qty: 
                raise HTTPException(status_code=422, 
                                    detail="Transaction Failed (" + item.item_sku + "): Requested Quantity (" + str(item.qty) + ") Greater Than Inventory (" + str(current_qty) + ")")
            # make insertion into item_ledger
            connection.execute(sqlalchemy.text(item_sql), 
                                [{"qty_change":-item.qty, "item_id":info.item_id, "item_sku":item.item_sku, "credit_change":info.total_price, "customer_id":id}])

    return "OK"


