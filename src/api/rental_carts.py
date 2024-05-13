from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/rental_carts",
    tags=["rental_cart"],
    dependencies=[Depends(auth.get_api_key)],
)

# our customer has the same attributes
class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the armory today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    """ """
    # create new entry in purchase_carts table
    with db.engine.begin() as connection:
        new_id = connection.execute(sqlalchemy.text('''INSERT INTO rental_carts (renter_name, class, level) VALUES (:renter_name, :class, :level) returning id'''),
                                    [{"renter_name" : new_cart.customer_name, "class":new_cart.character_class, "level":new_cart.level}]).scalar()
    
    return {"cart_id": new_id}

class CartItem(BaseModel):
    quantity: int

# NOTE: need to make sure that the changed parameters work properly
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, type: str, type_id: int, cart_item: CartItem):
    """ """
    # insert into item table
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text('''INSERT INTO rental_items (cart_id, type, type_id, quantity) VALUES
                                           (:cart_id, :type, :type_id, :quantity)'''), [{"cart_id":cart_id, "type":type, "type_id":type_id, "quantity":cart_item.quantity}])

    return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """ """
    # for entry into credit ledger
    num_rentals = 0
    total_credits = 0

    # TODO: is logging going to be any different for rentals vs purchases?
    # How are we going to be able to differentiate between the two on logs?

    # get all items being purchased by customer
    with db.engine.begin() as connection:
        purchase_items = connection.execute(sqlalchemy.text("SELECT type, type_id, quantity FROM rental_items WHERE cart_id = :cart_id"), [{"cart_id":cart_id}]).all() 
        # customer_name = connection.execute(sqlalchemy.text("SELECT customer_name FROM purchase_carts WHERE id = :cart_id"), [{"cart_id":cart_id}]).scalar()

    # CREATE LEDGER ENTRY for each distinct item that is bought
    # item --> [purchase_type, type_id, quantity]
    for item in purchase_items:
        # there are only three possibilities for type: "item", "weapon", and "armor"
        if item[0] == "item":
            with db.engine.begin() as connection:
                item_price = connection.execute(sqlalchemy.text("SELECT price FROM item_inventory WHERE id = :id"), [{"id":item[1]}]).scalar()
                connection.execute(sqlalchemy.text('''INSERT INTO i_log (owner, i_id, m_id, type) VALUES (:name, :item, :mod, :type)'''), [{"name":cart_id, "item":item[1], "mod":-1, "type":item[0]}])
        elif item[0] == "weapon":
            with db.engine.begin() as connection:
                item_price = connection.execute(sqlalchemy.text("SELECT price FROM weapon_inventory WHERE id = :id"), [{"id":item[1]}]).scalar()
                connection.execute(sqlalchemy.text('''INSERT INTO w_log (owner, w_id, m_id, type) VALUES (:name, :weapon, :mod, :type)'''), [{"name":cart_id, "weapon":item[1], "mod":-1, "type":item[0]}])      
        elif item[0] == "armor":
            with db.engine.begin() as connection:
                item_price = connection.execute(sqlalchemy.text("SELECT price FROM armor_inventory WHERE id = :id"), [{"id":item[1]}]).scalar()
                connection.execute(sqlalchemy.text('''INSERT INTO a_log (owner, a_id, m_id, type) VALUES (:name, :armor, :mod, :type)'''), [{"name":cart_id, "armor":item[1], "mod":-1, "type":item[0]}])
        else:
            print("----------- ERROR ------------")
            print("CHECKOUT : UNEXPECTED ITEM TYPE")
        num_rentals += item[2]
        total_credits += (item_price * item[2])


    return {"total_rentals": num_rentals, "total_credits_paid": total_credits}