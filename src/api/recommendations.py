from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import numpy as np
import random

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    dependencies=[Depends(auth.get_api_key)],
)

def cosine_distance(v1, v2):
    v1 = np.array(v1) * np.array([0.001, 1, 1])
    v2 = np.array(v2) * np.array([0.001, 1, 1])
    print("v1", v1)
    print("v2", v2)
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return 1-(dot_product / (norm_v1 * norm_v2))

@router.post("/recommend")
def recommend(budget: int, enemy_element: str, role: str):

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
    
    object_type = role_map.get(role.upper(),3)

    if object_type == 1:
        w_budget = int(budget*0.4)
        a_budget = int(budget*0.3)
        m_budget = int(budget*0.3)
    elif object_type == 2:
        w_budget = int(budget*0.3)
        a_budget = int(budget*0.4)
        m_budget = int(budget*0.3)
    else:
        w_budget = int(budget*0.3)
        a_budget = int(budget*0.3)
        m_budget = int(budget*0.4)

    # Offensively speaking, water beats Fire
    # Earth beats Water
    # Fire beats Earth
    # 1 is associated with fire type objects, so if our enemy is of type earth we will want an attack object of fire type (1)
    # Similarly 2 is for water objects, 3 is for earth, and 4 is basic
    enemy_element_attack_map = {
    "FIRE": 2,
    "WATER": 3,
    "EARTH": 1,
    "BASIC": 4
                    }
    
    
    # Defensively speaking, each type defends the best against its own type
    # 1 for Fire, 2 for Water, 3 for Earth, 4 for Basic
    enemy_element_defense_map = {
    "FIRE": 1,
    "WATER": 2,
    "EARTH": 3,
    "BASIC": 4
                    }
    
    w_element = enemy_element_attack_map.get(enemy_element.upper(), 4)
    a_element = enemy_element_defense_map.get(enemy_element.upper(), 4)
    m_element = random.randint(1, 4)

    w_given_vec = [w_budget, w_element, 1]
    a_given_vec = [a_budget, a_element, 2]
    m_given_vec = [m_budget, m_element, 3]
    


    with db.engine.begin() as connection:
        # Stores a list of all weapon item vectors that we have in our item plan where we have at least one of those items in stock
        w_item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            WHERE items_plan.type = :x
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""), [{"x":"weapon"}])
        # Set cosine distance is worst possible
        min_dist = 2
        # For each vector in our weapon inventory we will find the vector with the closest distance to the vector constructed with the user's info
        for row in w_item_vecs:
            if cosine_distance(row.item_vec, w_given_vec) < min_dist:
                min_dist = cosine_distance(row.item_vec, w_given_vec)
                print("MIN", min_dist)
                w_rec_vec = row.item_vec
        rec_weapon_sku = connection.execute(sqlalchemy.text("""SELECT sku FROM items_plan 
                                                      WHERE item_vec = :x"""), [{"x":w_rec_vec}]).fetchone()
        
        # We repeat that process but for just the armor
        a_item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            WHERE items_plan.type = :x
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""), [{"x":"armor"}])
        min_dist = 2
        for row in a_item_vecs:
            if cosine_distance(row.item_vec, a_given_vec) < min_dist:
                min_dist = cosine_distance(row.item_vec, a_given_vec)
                a_rec_vec = row.item_vec
        rec_armor_sku = connection.execute(sqlalchemy.text("""SELECT sku FROM items_plan 
                                                      WHERE item_vec = :x"""), [{"x":a_rec_vec}]).fetchone()
        
        # Lastly we repeat that process but for misc. items
        m_item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            WHERE items_plan.type = :x
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""), [{"x":"misc"}])
        min_dist = 2
        for row in m_item_vecs:
            if cosine_distance(row.item_vec, m_given_vec) < min_dist:
                min_dist = cosine_distance(row.item_vec, m_given_vec)
                m_rec_vec = row.item_vec
        rec_misc_sku = connection.execute(sqlalchemy.text("""SELECT sku FROM items_plan 
                                                      WHERE item_vec = :x"""), [{"x":m_rec_vec}]).fetchone()

        
    
    # Return a list of skus of the kit of wepaon, amror, and item with the respective "closest" vectors as our recommendation

    return [rec_weapon_sku[0],rec_armor_sku[0], rec_misc_sku[0]]



# , curr_weapon:str, curr_armor:str, curr_misc:str