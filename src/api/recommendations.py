from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import numpy as np
import random
from src.api import checkout

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    dependencies=[Depends(auth.get_api_key)],
)

class Customer(BaseModel):
    name: str
    role: str

class CheckoutItem(BaseModel):
    item_sku: str
    qty: int

def cosine_distance(v1, v2):
    v1 = np.array(v1) * np.array([0.001, 1, 1])
    v2 = np.array(v2) * np.array([0.001, 1, 1])
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return 1-(dot_product / (norm_v1 * norm_v2))

@router.post("/recommend")
def recommend(customer:Customer, budget: int, enemy_element: str):
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

        id = connection.execute(sqlalchemy.text(sql), [{"name":customer.name.title(), "role":customer.role.title()}]).scalar()

        # if not, then create a new record and use THAT id .. 
        if id is None:
            sql = '''
            INSERT INTO customers (name, role) VALUES (:name, :role)
            returning id
            '''
            try:
                id = connection.execute(sqlalchemy.text(sql), [{"name":customer.name.title(), "role":customer.role.title()}]).scalar()
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

        if object_type == 1:
            w_budget = int(budget*0.5)
            a_budget = int(budget*0.25)
            m_budget = int(budget*0.25)
        elif object_type == 2:
            w_budget = int(budget*0.25)
            a_budget = int(budget*0.5)
            m_budget = int(budget*0.25)
        else:
            w_budget = int(budget*0.25)
            a_budget = int(budget*0.25)
            m_budget = int(budget*0.5)

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
        
        w_element = enemy_element_attack_map.get(enemy_element.upper(), 0)
        a_element = enemy_element_defense_map.get(enemy_element.upper(), 0)
        m_element = random.randint(0, 3)

        w_given_vec = [w_budget, w_element, 1]
        a_given_vec = [a_budget, a_element, 2]
        m_given_vec = [m_budget, m_element, 3]
        


        # Stores a list of all weapon item vectors that we have in our item plan where we have at least one of those items in stock
        w_item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            WHERE items_plan.type = :x
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""), [{"x":"weapon"}])
        total_price = 0
        # if w_item_vecs is not None:
        if w_item_vecs.rowcount > 0:
            # Set cosine distance is worst possible
            min_dist = 2
            # For each vector in our weapon inventory we will find the vector with the closest distance to the vector constructed with the user's info
            for row in w_item_vecs:
                if cosine_distance(row.item_vec, w_given_vec) < min_dist:
                    min_dist = cosine_distance(row.item_vec, w_given_vec)
                    w_rec_vec = row.item_vec
            info1 = connection.execute(sqlalchemy.text("""SELECT sku, price FROM items_plan 
                                                        WHERE item_vec = :x"""), [{"x":w_rec_vec}]).fetchone()
            rec_weapon_sku = info1[0]
            total_price += info1[1]
        else:
            rec_weapon_sku = "NA"
        
        # We repeat that process but for just the armor
        a_item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            WHERE items_plan.type = :x
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""), [{"x":"armor"}])
        # this is still running even when empty ... the comparison is not working
        # if a_item_vecs is not None:
        if a_item_vecs.rowcount > 0:
            min_dist = 2
            for row in a_item_vecs:
                # NOTE: this line is throwing an erro .. comparison between None and int
                if cosine_distance(row.item_vec, a_given_vec) < min_dist:
                    min_dist = cosine_distance(row.item_vec, a_given_vec)
                    a_rec_vec = row.item_vec
            info2 = connection.execute(sqlalchemy.text("""SELECT sku, price FROM items_plan 
                                                        WHERE item_vec = :x"""), [{"x":a_rec_vec}]).fetchone()
            rec_armor_sku = info2[0]
            total_price += info2[1]
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
            rec_other_sku = info3[0]
            total_price += info3[1]
        else:
            rec_other_sku = "NA"

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

    with db.engine.begin() as connection:
        # Accesses the sku and corresponding customer id for the items that the customer has currently in their inventory
        results = connection.execute(sqlalchemy.text("""SELECT item_sku, customer_id FROM items_ledger
                                                JOIN items_plan ON items_plan.sku = items_ledger.item_sku
                                                WHERE customer_id = (SELECT id FROM customers
                                                WHERE name = :x)
                                                GROUP BY item_sku, customer_id, items_plan.type
                                                HAVING SUM(qty_change) < 0
                                                ORDER BY items_plan.type ASC"""), [{"x":customer.name.title(), "y":"weapon"}]).fetchall()
        # Access the skus of the items we recommended to the user
        rec_skus = connection.execute(sqlalchemy.text("""SELECT recent_w_rec, recent_a_rec, recent_o_rec FROM customers 
                                               WHERE name = :x"""), [{"x":customer.name.title()}]).fetchone()
        if not rec_skus: 
                raise HTTPException(status_code=404, detail=f"No previous recommendations found for {customer.name.title()}")
        # If the customer wants to swap their weapon...
        if weapon and rec_skus[0] != "NA":
            if not results[2]:
                raise HTTPException(status_code=404, detail=f"No weapons found in the inventory for customer {customer.name.title()}")
            # Accesses the id and price from items_plan of the weapon that the customer has in their inventory
            details = connection.execute(sqlalchemy.text("""SELECT id, price FROM items_plan
                                                         WHERE sku = :x"""), [{"x":results[2][0]}]).fetchone()
            # Completes the return of the customer's weapon to Fallen Stars Armory
            connection.execute(sqlalchemy.text("""INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) 
                                               VALUES (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)"""), 
                                [{"qty_change":1, "item_id":details[0], "item_sku":results[2][0], "credit_change":-details[1], "customer_id":results[2][1]}])
            
            # Stages the recommended weapon to be checked out
            checkout_list.append(CheckoutItem(item_sku=rec_skus[0], qty=1))

        # If the customer wants to swap their armor...
        if armor and rec_skus[1] != "NA":
            if not results[0]:
                raise HTTPException(status_code=404, detail=f"No armor found in the inventory for customer {customer.name.title()}")
            # Accesses the id and price from items_plan of the armor that the customer has in their inventory
            details = connection.execute(sqlalchemy.text("""SELECT id, price FROM items_plan
                                                         WHERE sku = :x"""), [{"x":results[0][0]}]).fetchone()
            # Completes the return of the customer's armor to Fallen Stars Armory
            connection.execute(sqlalchemy.text("""INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) 
                                               VALUES (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)"""), 
                                [{"qty_change":1, "item_id":details[0], "item_sku":results[0][0], "credit_change":-details[1], "customer_id":results[0][1]}])
            
            # Stages the recommended armor to be checked out
            checkout_list.append(CheckoutItem(item_sku=rec_skus[1], qty=1))

        # If the customer wants to swap their "other item"...
        if other and rec_skus[2] != "NA":
            if not results[1]:
                raise HTTPException(status_code=404, detail=f"No misc. items found in the inventory for customer {customer.name.title()}")
            # Accesses the id and price from items_plan of the armor that the customer has in their inventory
            details = connection.execute(sqlalchemy.text("""SELECT id, price FROM items_plan
                                                         WHERE sku = :x"""), [{"x":results[1][0]}]).fetchone()
            # Completes the return of the customer's armor to Fallen Stars Armory
            connection.execute(sqlalchemy.text("""INSERT INTO items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) 
                                               VALUES (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)"""), 
                                [{"qty_change":1, "item_id":details[0], "item_sku":results[1][0], "credit_change":-details[1], "customer_id":results[1][1]}])
            
            # Stages the recommended other to be checked out
            checkout_list.append(CheckoutItem(item_sku=rec_skus[2], qty=1))

    # Performs a checkout on the new items
    try:
        checkout.checkout(customer, checkout_list)
    except:
        raise HTTPException(status_code=404, detail="Checkout failed, please contact Fallen Stars")
    
    return "OK"