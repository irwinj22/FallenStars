from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/purchase_carts",
    tags=["purchase_cart"],
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
        new_id = connection.execute(sqlalchemy.text('''INSERT INTO purchase_carts (customer_name, class, level) VALUES (:customer_name, :class, :level) returning id'''),
                                    [{"customer_name" : new_cart.customer_name, "class":new_cart.character_class, "level":new_cart.level}]).scalar()
    
    return {"cart_id": new_id}

class CartItem(BaseModel):
    quantity: int

# NOTE: need to make sure that the changed parameters work properly
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, purchase_type: str, type_id: int, cart_item: CartItem):
    """ """
    # insert into item table
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text('''INSERT INTO purchase_items (cart_id, purchase_type, type_id, quantity) VALUES
                                           (:cart_id, :pur_type, :type_id, :quantity)'''), [{"cart_id":cart_id, "pur_type":purchase_type, "type_id":type_id, "quantity":cart_item.quantity}])

    return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """ """
    # for entry into credit ledger
    num_purchases = 0
    total_credits = 0

    # TODO: not sure how to account for mods here ...
    # TODO: not doing anything with quantity, must be changed 
    # TODO: why is customer an int? 
    # --> FOR NOW just inserting the cart_id, which will have customer_name within it
    # NOTE: there are going to need to be base values in different tales in order for all of this to work (such as the different inventories)
    # --> those are going to depend on the sample flows though

    # get all items being purchased by customer
    with db.engine.begin() as connection:
        purchase_items = connection.execute(sqlalchemy.text("SELECT purchase_type, type_id, quantity FROM purchase_items WHERE cart_id = :cart_id"), [{"cart_id":cart_id}]).all() 
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
id | cart_id | type | type_id | quantity

type is the type of thing being purchased (item, weapon, armor)
while type_id is the id of that thing within the log (this is making sense actually)

'''