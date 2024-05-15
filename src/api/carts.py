from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
from src import database as db
import sqlalchemy
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

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
    # create new entry in carts table
    with db.engine.begin() as connection:
        new_id = connection.execute(sqlalchemy.text('''INSERT INTO carts (customer_name, class, level) VALUES (:customer_name, :class, :level) returning id'''),
                                    [{"customer_name" : new_cart.customer_name, "class":new_cart.character_class, "level":new_cart.level}]).scalar()
    
    return {"cart_id": new_id}

class CartItem(BaseModel):
    quantity: int

@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, type: str, thing_id: int, cart_item: CartItem):
    """ """
    # insert into item table
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text('''INSERT INTO cart_items (cart_id, type, thing_id, quantity) VALUES
                                           (:cart_id, :type, :thing_id, :quantity)'''), [{"cart_id":cart_id, "type":type, "thing_id":thing_id, "quantity":cart_item.quantity}])

    return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """ """
    num_purchases = 0
    total_credits = 0

    # NOTE: there are going to need to be base values in different tables

    # get all items being purchased by customer
    with db.engine.begin() as connection:

        cart_items = connection.execute(sqlalchemy.text("""SELECT cart_items.type, cart_items.thing_id, cart_items.quantity, catalog.rental 
                                                        FROM cart_items 
                                                        FULL JOIN catalog ON cart_items.thing_id = catalog.thing_id AND cart_items.type = catalog.type
                                                        WHERE cart_id = :cart_id"""), [{"cart_id":cart_id}]).all() 

        # create ledger entry for each thing being bought
        # item : [purchase_type, thing_id, quantity, rental]
        for item in cart_items:
            if item[3] == True:
                checkout = connection.execute(sqlalchemy.text("""INSERT INTO rentals (cart_id, rented_id, rented_type, returned) 
                                                VALUES (:y, :z, :w, :q)
                                                RETURNING checkout"""), [{"y":cart_id, "z":item[1], "w":item[0], "q": False}]).scalar()
                # timestamp_dt = datetime.fromisoformat(checkout)
                # two_hours = timedelta(hours=2)
                # new_timestamp = timestamp_dt + two_hours
                # iso_formatted_string = new_timestamp.isoformat()
                modified_timestamp = checkout + timedelta(hours=2)
                print(checkout)
                print(modified_timestamp)
                connection.execute(sqlalchemy.text("""UPDATE rentals SET checkin = :x"""), [{"x": modified_timestamp}])
            # if purchase is item
            if item[0] in ("attack", "defense", "support"):
                with db.engine.begin() as connection:
                    item_price = connection.execute(sqlalchemy.text("SELECT price FROM item_inventory WHERE id = :id"), [{"id":item[1]}]).scalar()
                    # create ledger entry for each individual item (ie, 3 entries if quantity 3)
                    for i in range(0, item[2]):
                        connection.execute(sqlalchemy.text('''INSERT INTO i_log (owner, i_id, m_id, type) VALUES (:name, :item, :mod, :type)'''), [{"name":cart_id, "item":item[1], "mod":None, "type":item[0]}])
            # if purchase is armor
            elif item[0] in ("melee", "rifle", "pistol"):
                with db.engine.begin() as connection:
                    item_price = connection.execute(sqlalchemy.text("SELECT price FROM weapon_inventory WHERE id = :id"), [{"id":item[1]}]).scalar()
                    # create ledger entry for each individual item (ie, 3 entries if quantity 3)
                    for i in range(0, item[2]):
                        connection.execute(sqlalchemy.text('''INSERT INTO w_log (owner, w_id, m_id, type) VALUES (:name, :weapon, :mod, :type)'''), [{"name":cart_id, "weapon":item[1], "mod":None, "type":item[0]}])      
            # if purchase is item
            elif item[0] in ("street", "combat", "powered"):
                with db.engine.begin() as connection:
                    item_price = connection.execute(sqlalchemy.text("SELECT price FROM armor_inventory WHERE id = :id"), [{"id":item[1]}]).scalar()
                    # create ledger entry for each individual item (ie, 3 entries if quantity 3)
                    for i in range(0, item[2]):
                        connection.execute(sqlalchemy.text('''INSERT INTO a_log (owner, a_id, m_id, type) VALUES (:name, :armor, :mod, :type)'''), [{"name":cart_id, "armor":item[1], "mod":None, "type":item[0]}])
            else:
                print("----------- ERROR ------------")
                print("CHECKOUT : UNEXPECTED ITEM TYPE")
            
            num_purchases += item[2]
            total_credits += (item_price * item[2])


    return {"total_purchases": num_purchases, "total_credits_paid": total_credits}

'''
the original idea was to have one cart that has both modifiers and rentals, but I am not sure if that's a good idea
yeah I think it makes more sense to do this twice, once with items and then another time with rentals, or something like 

so then there will be four tables that I have to add
purchase_carts
purchase_items
rental_carts
rental_items

and then I am going to have to add the correct INSERTs into respective tables, depending on what is being purchased

inventories are everything that we can POSSIBLY be holding
where as the logs are what we are actaully going to have in stock (ledgers)

could have five categories or something like that
id | cart_id | type | thing_id | quantity

type is the type of thing being purchased (item, weapon, armor)
while thing_id is the id of that thing within the log (this is making sense actually)

'''