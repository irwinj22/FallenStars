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
def set_item_quantity(cart_id: int, type: str, object_id: int, cart_item: CartItem):
    """ """
    # insert into item table
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text('''INSERT INTO cart_items (cart_id, type, object_id, quantity) VALUES
                                           (:cart_id, :type, :object_id, :quantity)'''), [{"cart_id":cart_id, "type":type, "object_id":object_id, "quantity":cart_item.quantity}])

    return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """ """
    num_purchases = 0
    total_credits = 0

    # NOTE: there are going to need to be base values in different tables

    # get all items being purchased by customer
    # List of items for each kind of object (item, weapon, armor)
    # Storing the object type, its respective LOG id, quantity of that item, and whether or not it's a rental
    with db.engine.begin() as connection:
        i_cart_items = connection.execute(sqlalchemy.text("""SELECT cart_items.type, cart_items.object_id, cart_items.quantity, i_log.rental, i_log.i_id 
                                                        FROM cart_items 
                                                        RIGHT JOIN i_log ON cart_items.object_id = i_log.id AND cart_items.type = i_log.type
                                                        WHERE cart_id = :cart_id"""), [{"cart_id":cart_id}]).all() 
        w_cart_items = connection.execute(sqlalchemy.text("""SELECT cart_items.type, cart_items.object_id, cart_items.quantity, w_log.rental, w_log.w_id  
                                                        FROM cart_items 
                                                        RIGHT JOIN w_log ON cart_items.object_id = w_log.id AND cart_items.type = w_log.type
                                                        WHERE cart_id = :cart_id"""), [{"cart_id":cart_id}]).all() 
        a_cart_items = connection.execute(sqlalchemy.text("""SELECT cart_items.type, cart_items.object_id, cart_items.quantity, a_log.rental, a_log.a_id 
                                                        FROM cart_items 
                                                        RIGHT JOIN a_log ON cart_items.object_id = a_log.id AND cart_items.type = a_log.type
                                                        WHERE cart_id = :cart_id"""), [{"cart_id":cart_id}]).all() 

        # create ledger entry for each thing being bought
        # item : [purchase_type, thing_id, quantity, rental]
        # Looping through each of the three lists
        # First checking if item is a rental; if it is, then it inserts it into our rental table and assigns a checkin time to be two hours later
        for item in i_cart_items:
            if item[3] == True:
                checkout = connection.execute(sqlalchemy.text("""INSERT INTO rentals (cart_id, rented_id, rented_type, returned) 
                                                VALUES (:y, :z, :w, :q)
                                                RETURNING checkout"""), [{"y":cart_id, "z":item[1], "w":item[0], "q": False}]).scalar()
                modified_timestamp = checkout + timedelta(hours=2)
                connection.execute(sqlalchemy.text("""UPDATE rentals SET checkin = :x"""), [{"x": modified_timestamp}])
                
            # Acquire the price of specific ITEM 
            item_price = connection.execute(sqlalchemy.text("SELECT price FROM item_inventory WHERE id = :id"), [{"id":item[4]}]).scalar()
            
            # create ledger entry for each individual item (ie, 3 entries if quantity 3)
            for i in range(0, item[2]):
                connection.execute(sqlalchemy.text('''INSERT INTO i_log (owner, i_id, m_id, type) VALUES (:name, :item, :mod, :type)'''), [{"name":cart_id, "item":item[4], "mod":None, "type":item[0]}])
            
            # Update credit ledger
            connection.execute(sqlalchemy.text("INSERT INTO credit_ledger (change) VALUES (:change)"), [{"change":item_price*item[2]}]) 
            
            # Update counts of purchases and credits spent in this cart
            num_purchases += item[2]
            total_credits += (item_price * item[2])
        
        for item in w_cart_items:
            if item[3] == True:
                checkout = connection.execute(sqlalchemy.text("""INSERT INTO rentals (cart_id, rented_id, rented_type, returned) 
                                                VALUES (:y, :z, :w, :q)
                                                RETURNING checkout"""), [{"y":cart_id, "z":item[1], "w":item[0], "q": False}]).scalar()
                modified_timestamp = checkout + timedelta(hours=2)
                connection.execute(sqlalchemy.text("""UPDATE rentals SET checkin = :x"""), [{"x": modified_timestamp}])

             # Acquire the price of specific WEAPON    
            item_price = connection.execute(sqlalchemy.text("SELECT price FROM weapon_inventory WHERE id = :id"), [{"id":item[4]}]).scalar()

            # create ledger entry for each individual item (ie, 3 entries if quantity 3)
            for i in range(0, item[2]):
                connection.execute(sqlalchemy.text('''INSERT INTO w_log (owner, w_id, m_id, type) VALUES (:name, :item, :mod, :type)'''), [{"name":cart_id, "item":item[4], "mod":None, "type":item[0]}])
            
            # Update credit ledger
            connection.execute(sqlalchemy.text("INSERT INTO credit_ledger (change) VALUES (:change)"), [{"change":item_price*item[2]}]) 
            
            # Update counts of purchases and credits spent in this cart
            num_purchases += item[2]
            total_credits += (item_price * item[2])
        
        for item in a_cart_items:
            if item[3] == True:
                checkout = connection.execute(sqlalchemy.text("""INSERT INTO rentals (cart_id, rented_id, rented_type, returned) 
                                                VALUES (:y, :z, :w, :q)
                                                RETURNING checkout"""), [{"y":cart_id, "z":item[1], "w":item[0], "q": False}]).scalar()
                modified_timestamp = checkout + timedelta(hours=2)
                connection.execute(sqlalchemy.text("""UPDATE rentals SET checkin = :x"""), [{"x": modified_timestamp}])

            item_price = connection.execute(sqlalchemy.text("SELECT price FROM armor_inventory WHERE id = :id"), [{"id":item[4]}]).scalar()
            # create ledger entry for each individual item (ie, 3 entries if quantity 3)
            for i in range(0, item[2]):
                connection.execute(sqlalchemy.text('''INSERT INTO a_log (owner, a_id, m_id, type) VALUES (:name, :item, :mod, :type)'''), [{"name":cart_id, "item":item[4], "mod":None, "type":item[0]}])
            
            # Update credit ledger
            connection.execute(sqlalchemy.text("INSERT INTO credit_ledger (change) VALUES (:change)"), [{"change":item_price*item[2]}]) 
            
            # Update counts of purchases and credits spent in this cart
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