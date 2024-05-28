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
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return 1-(dot_product / (norm_v1 * norm_v2))

@router.post("/recommend")
def recommend(budget: int, enemy_type: str, role: str):


    # Offensively speaking, water beats Fire
    # Earth beats Water
    # Fire beats Earth
    # 1 is associated with fire type objects, so if our enemy is of type earth we will want an attack object of fire type (1)
    # Similarly 2 is for water objects, 3 is for earth, and 4 is basic
    enemy_type_attack_map = {
    "FIRE": 2,
    "WATER": 3,
    "EARTH": 1,
    "BASIC": 4
                    }
    
    # Defensively speaking, each type defends the best against its own type
    # 1 for Fire, 2 for Water, 3 for Earth, 4 for Basic
    enemy_type_defense_map = {
    "FIRE": 1,
    "WATER": 2,
    "EARTH": 3,
    "BASIC": 4
                    }

    # The roles in our world fall into three categories: Attackers, Defenders, and Specialists
    # Attackers want weapons, which will be represented by 1
    # Defenders want armor, whcih will be represented by 2
    # Specialists want Misc. items, which will be represented by 3
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
    
    object_type = role_map.get(role.upper(),0)

    # Attackers get weapons that are strong against enemy type
    if object_type == 1:
        e_type = enemy_type_attack_map.get(enemy_type.upper(), 0)
    
    # Defender get armor of the same type as their enemy
    elif object_type == 2:
        e_type = enemy_type_defense_map.get(enemy_type.upper(), 0)
    
    # Misc. items are equally strong against all types, so specialists get a random type of misc. item
    else:
        e_type = random.randint(1, 4)
    


    with db.engine.begin() as connection:
        # Create our vector of given data
        given_vec = [budget, e_type, object_type]
        print(given_vec)
        # Stores a list of all item vectors that we have in our item plan where we have at least one of those items in stock
        item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan
                                                            JOIN items_ledger ON items_plan.id = items_ledger.item_id
                                                            GROUP BY item_vec
                                                            HAVING SUM(qty_change) > 0"""))
        # Set cosine distance is worst possible
        min_dist = 2

        # For each vector in our inventory we will find the vector with the closest distance to the vector given by the user
        for row in item_vecs:
            if cosine_distance(row.item_vec, given_vec) < min_dist:
                min_dist = cosine_distance(row.item_vec, given_vec)
                rec_vec = row.item_vec
        rec_item_sku = connection.execute(sqlalchemy.text("""SELECT sku FROM items_plan 
                                                      WHERE item_vec = :x"""), [{"x":rec_vec}]).fetchone()
    
    # Return the sku of the item with the "closest" vector as our recommendation

    return rec_item_sku[0]

