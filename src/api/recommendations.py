from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from src.api import auth
import sqlalchemy
from src import database as db
import numpy as np
import random
from src.api import checkout
from typing import Literal

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
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
    qty: int= Field(gt=0, lt=20)

class CustomerSpecs(BaseModel):
    budget: int = Field(gt=0, lt=400)
    enemy_element: Literal["FIRE", "EARTH", "WATER"]

def cosine_distance(v1, v2):
    v1 = np.array(v1) * np.array([0.0001, 1, 1])
    v2 = np.array(v2) * np.array([0.0001, 1, 1])
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return 1-(dot_product / (norm_v1 * norm_v2))

# TODO: have to validate budget, enemy_element 
@router.post("/recommend")
def recommend(customer:Customer, specs:CustomerSpecs):
    total_price = 0
    '''
    Recommend purchases to customers. 
    '''
    with db.engine.begin() as connection:
        # check if customer record exists, get id
        sql = '''
        SELECT id
        FROM customers
        WHERE name = :name AND role = :role
        '''

        id = connection.execute(sqlalchemy.text(sql), [{"name":customer.name.title(), "role":customer.role.upper()}]).scalar()

        # if not, then create a new record and use THAT id .. 
        if id is None:
            sql = '''
            INSERT INTO customers (name, role) VALUES (:name, :role)
            returning id
            '''
            try:
                id = connection.execute(sqlalchemy.text(sql), [{"name":customer.name.title(), "role":customer.role.upper()}]).scalar()
            except sqlalchemy.exc.SQLAlchemyError as e: 
                raise HTTPException(status_code=400, detail="Invalid name")


    # The roles in our world fall into three categories: Attackers, Defenders, and Specialists
    # Attackers prioritize weapons, which will be represented by 1
    # Defenders prioritize armor, whcih will be represented by 2
    # Specialists prioritize Misc. items, which will be represented by 3
    
        role_map = {
        "WARRIOR": 1,
        "SUNBLADE": 1,
        "ASSASSIN": 1,
        "NEXUS": 2,
        "SHIFTER": 2,
        "BUILDER": 2,
        "EXPERT": 3,
        "MAGGE": 3,
        "SCOUT": 3
                        }
        
        object_type = role_map.get(customer.role.upper(),3)

        # Offensively speaking, water beats Fire
        # Earth beats Water
        # Fire beats Earth
        # 1 is associated with fire type objects, so if our enemy is of type earth we will want an attack object of fire type (1)
        # Similarly 2 is for water objects, 3 is for earth, and 4 is basic
        enemy_element_attack_map = {
        "FIRE": 3,
        "WATER": 2,
        "EARTH": 1,
        "BASIC": 0
                        }
        
        
        # Defensively speaking, each type defends the best against its own type
        # 1 for Fire, 2 for Water, 3 for Earth, 4 for Basic
        enemy_element_defense_map = {
        "FIRE": 1,
        "WATER": 3,
        "EARTH": 2,
        "BASIC": 0
                        }
        
        # Create the variables for the mapped element value
        # The misc (other) element value will be mapped dependent on the role of the customer
        w_element = enemy_element_attack_map.get(specs.enemy_element.upper(), 0)
        a_element = enemy_element_defense_map.get(specs.enemy_element.upper(), 0)

        # Allocate the budget uniquely depending on the priorities of the role of the customer
        if object_type == 1:
            w_budget = int(specs.budget*0.5)
            a_budget = int(specs.budget*0.25)
            m_budget = int(specs.budget*0.25)
            m_element = w_element
        elif object_type == 2:
            w_budget = int(specs.budget*0.25)
            a_budget = int(specs.budget*0.5)
            m_budget = int(specs.budget*0.25)
            m_element = a_element
        else:
            w_budget = int(specs.budget*0.25)
            a_budget = int(specs.budget*0.25)
            m_budget = int(specs.budget*0.5)
            m_element = 0

        w_given_vec = [w_budget, w_element, 1]
        a_given_vec = [a_budget, a_element, 2]
        m_given_vec = [m_budget, m_element, 3]


        # Stores a list of all weapon item vectors that we have in our item plan where we have at least one of those items in stock
        w_item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            WHERE items_plan.type = :x
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""), [{"x":"weapon"}])
        # if there are weapons in inventory, continue; else set the recommended weapon as NA:
        if w_item_vecs.rowcount > 0:
            # Set cosine distance is worst possible
            min_dist = 2
            # For each vector in our weapon inventory we will find the vector with the closest distance to the vector constructed with the user's info
            for row in w_item_vecs:
                if cosine_distance(row.item_vec, w_given_vec) < min_dist:
                    min_dist = cosine_distance(row.item_vec, w_given_vec)
                    w_rec_vec = row.item_vec
            # Get the info on the vector we are recommending
            info1 = connection.execute(sqlalchemy.text("""SELECT sku, price FROM items_plan 
                                                        WHERE item_vec = :x"""), [{"x":w_rec_vec}]).fetchone()
            rec_weapon_sku = info1.sku
            total_price += info1.price
        else:
            rec_weapon_sku = "NA"
        
        # We repeat that process but for just the armor
        a_item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            WHERE items_plan.type = :x
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""), [{"x":"armor"}])
        if a_item_vecs.rowcount > 0:
            min_dist = 2
            for row in a_item_vecs:
                # NOTE: this line is throwing an erro .. comparison between None and int
                if cosine_distance(row.item_vec, a_given_vec) < min_dist:
                    min_dist = cosine_distance(row.item_vec, a_given_vec)
                    a_rec_vec = row.item_vec
            info2 = connection.execute(sqlalchemy.text("""SELECT sku, price FROM items_plan 
                                                        WHERE item_vec = :x"""), [{"x":a_rec_vec}]).fetchone()
            rec_armor_sku = info2.sku
            total_price += info2.price
        else:
            rec_armor_sku = "NA"
        
        # Lastly we repeat that process but for misc. items
        m_item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            WHERE items_plan.type = :x
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""), [{"x":"other"}])
        # if m_item_vecs is not None:
        if m_item_vecs.rowcount > 0:
            min_dist = 2
            for row in m_item_vecs:
                if cosine_distance(row.item_vec, m_given_vec) < min_dist:
                    min_dist = cosine_distance(row.item_vec, m_given_vec)
                    m_rec_vec = row.item_vec
            info3 = connection.execute(sqlalchemy.text("""SELECT sku, price FROM items_plan 
                                                        WHERE item_vec = :x"""), [{"x":m_rec_vec}]).fetchone()
            rec_other_sku = info3.sku
            total_price += info3.price
        else:
            rec_other_sku = "NA"
        
        # Get a list of the customers inventory
        results = connection.execute(sqlalchemy.text("""SELECT item_sku, customer_id, items_plan.type AS type
                                                FROM items_ledger
                                                JOIN items_plan ON items_plan.sku = items_ledger.item_sku
                                                WHERE customer_id = (SELECT id FROM customers
                                                WHERE name = :x)
                                                GROUP BY item_sku, customer_id, items_plan.type
                                                HAVING SUM(qty_change) < 0
                                                ORDER BY items_plan.type ASC"""), [{"x":customer.name.title()}]).fetchall()
        # if the customer already has an item we recommend to them, then return NA for that item recommendation
        for row in results:
            if row.type == 'weapon' and row.item_sku == rec_weapon_sku:
                rec_weapon_sku = "NA"
                total_price -= info1.price
            if row.type == 'armor' and row.item_sku == rec_armor_sku:
                rec_armor_sku = "NA"
                total_price -= info2.price
            if row.type == 'other' and row.item_sku == rec_other_sku:
                rec_other_sku = "NA"
                total_price -= info3.price
        
        # Update the most recent recommendations for the customer
        connection.execute(sqlalchemy.text("""UPDATE customers SET recent_w_rec = :x, recent_a_rec = :y, recent_o_rec = :z
                                           WHERE name = :w"""), [{"x":rec_weapon_sku, "y": rec_armor_sku, "z":rec_other_sku, "w": customer.name.title()}])
        



        
    
    # Return a list of skus of the kit of wepaon, amror, and item with the respective "closest" vectors as our recommendation

    return {"Rec. Weapon": rec_weapon_sku, "Rec. Armor": rec_armor_sku, "Rec. Other": rec_other_sku, "Total Cost": total_price}


@router.post("/swap")
def swap(customer:Customer, weapon:bool, armor:bool, other:bool):
    '''
    Allow customer to swap their items for different ones. 
    '''

    # Initializing the list of items the customer will be "buying"
    checkout_list = []
    old = []
    new = []
    temp_weapon = False
    temp_armor = False
    temp_other = False

    with db.engine.begin() as connection:
        inventory = []
        # Accesses the sku and corresponding customer id for the items that the customer has currently in their inventory
        results = connection.execute(sqlalchemy.text("""SELECT item_sku, customer_id, items_plan.type AS type
                                                FROM items_ledger
                                                JOIN items_plan ON items_plan.sku = items_ledger.item_sku
                                                WHERE customer_id = (SELECT id FROM customers
                                                WHERE name = :x)
                                                GROUP BY item_sku, customer_id, items_plan.type
                                                HAVING SUM(qty_change) < 0
                                                ORDER BY items_plan.type ASC"""), [{"x":customer.name.title()}]).fetchall()
        if not results:
            raise HTTPException(status_code=404, detail=f"No items found in the inventory for customer {customer.name.title()}")
        
        # Handles the logic of whether or not the customer has items to be able to swap
        for row in results:
            if row.type == 'weapon' and temp_weapon == False:
                temp_weapon = True
                inventory.append([1, row.item_sku, row.customer_id])
            if row.type == 'armor'and temp_armor == False:
                temp_armor = True
                inventory.append([2, row.item_sku, row.customer_id])
            if row.type == 'other' and temp_other == False:
                temp_other = True
                inventory.append([3, row.item_sku, row.customer_id])
        if weapon == True:
            weapon = temp_weapon
        if armor == True:
            armor = temp_armor
        if other == True:
            other = temp_other

        inventory.sort(key=lambda x: x[0])

        # Access the skus of the items we recommended to the user
        rec_skus = connection.execute(sqlalchemy.text("""SELECT recent_w_rec, recent_a_rec, recent_o_rec FROM customers 
                                               WHERE name = :x"""), [{"x":customer.name.title()}]).fetchone()
        
        if rec_skus.recent_w_rec is None and rec_skus.recent_a_rec is None and rec_skus.recent_o_rec is None: 
                raise HTTPException(status_code=404, detail=f"No previous recommendations found for {customer.name.title()}")
        
        # If the customer wants to swap their weapon...
        if weapon and rec_skus.recent_w_rec != "NA" and inventory[0][1] != rec_skus.recent_w_rec:
            
            # Accesses the id and price from items_plan of the weapon that the customer has in their inventory
            details = connection.execute(sqlalchemy.text("""SELECT id, price FROM items_plan
                                                         WHERE sku = :x"""), [{"x":inventory[0][1]}]).fetchone()
            
            # Completes the return of the customer's weapon to Fallen Stars Armory
            connection.execute(sqlalchemy.text("""INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) 
                                               VALUES (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)"""), 
                                [{"qty_change":1, "item_id":details.id, "item_sku":inventory[0][1], "credit_change":-details.price, "customer_id":inventory[0][2]}])
            # Adds the customer's item that they are returning and their new item to respective lists to be referenced in the return statement
            old.append(inventory[0][1])
            new.append(rec_skus.recent_w_rec)        
            # Stages the recommended weapon to be checked out
            checkout_list.append(CheckoutItem(item_sku=rec_skus.recent_w_rec, qty=1))

        # If the customer wants to swap their armor...repeat a similar process as above
        if armor and rec_skus.recent_a_rec != "NA" and inventory[1][1] != rec_skus.recent_a_rec:
            
            # Accesses the id and price from items_plan of the armor that the customer has in their inventory
            details = connection.execute(sqlalchemy.text("""SELECT id, price FROM items_plan
                                                         WHERE sku = :x"""), [{"x":inventory[1][1]}]).fetchone()
            
            # Completes the return of the customer's armor to Fallen Stars Armory
            connection.execute(sqlalchemy.text("""INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) 
                                               VALUES (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)"""), 
                                [{"qty_change":1, "item_id":details.id, "item_sku":inventory[1][1], "credit_change":-details.price, "customer_id":inventory[1][2]}])
            old.append(inventory[1][1])
            new.append(rec_skus.recent_a_rec)
            # Stages the recommended armor to be checked out
            checkout_list.append(CheckoutItem(item_sku=rec_skus.recent_a_rec, qty=1))

        # If the customer wants to swap their "other item"...
        if other and rec_skus.recent_o_rec != "NA" and inventory[2][1] != rec_skus.recent_o_rec:
            
            # Accesses the id and price from items_plan of the armor that the customer has in their inventory
            details = connection.execute(sqlalchemy.text("""SELECT id, price FROM items_plan
                                                         WHERE sku = :x"""), [{"x":inventory[2][1]}]).fetchone()
            
            # Completes the return of the customer's armor to Fallen Stars Armory
            connection.execute(sqlalchemy.text("""INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) 
                                               VALUES (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)"""), 
                                [{"qty_change":1, "item_id":details.id, "item_sku":inventory[2][1], "credit_change":-details.price, "customer_id":inventory[2][2]}])
            old.append(inventory[2][1])
            new.append(rec_skus.recent_o_rec)
            # Stages the recommended other to be checked out
            checkout_list.append(CheckoutItem(item_sku=rec_skus.recent_o_rec, qty=1))

    # Performs a checkout on the new items
    try:
        checkout.checkout(customer, checkout_list)
    except:
        raise HTTPException(status_code=404, detail="Checkout failed, please contact Fallen Stars")
    if not old and not new:
        return {"Swapped": "Nothing"}
    # Returns what items are being swapped for which items
    result_string = ', '.join(old) + " for " + ', '.join(new)
    return {"Swapped": result_string}