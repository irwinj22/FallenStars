from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import math

router = APIRouter(
    prefix="/recs",
    tags=["recs"],
    dependencies=[Depends(auth.get_api_key)],
)


class Point(BaseModel):
    radius: int
    angle: float
    z: float


@router.post("/recommend")
def recommend(budget: int, role: str, enemy_type: int):
    """
    Recommend items to customers

    NOTE: z-axis: type of item
          radius: price
          angle: modification

    Possible improvements:
     - Organize item_list by price and then if (item.price > budget) -> end for loop
    """
    with db.engine.begin() as connection:
        
        # Get all items we can offer
        item_list = connection.execute(sqlalchemy.text("SELECT * FROM items_plan"))

        # Create dictionary to store Cartesian distances
        dist_dict = {}
        
        # If the enemy is NOT a "basic" type:
        if enemy_type != 0:

            # change enemy_type to 1, 3, 5
            # Angle represents the modification that will make the item the strongest against the enemy type
            ideal_angle = (enemy_type * math.pi / 3) - (2 * math.pi / 3)
            ideal_radius = budget / 10
            if role == 'warrior':
                ideal_z = 10
            elif role == 'assassin':
                ideal_z = 7
            elif role == 'mage':
                ideal_z = 2
            elif role == 'scout':
                ideal_z = 0
            elif role == 'nexus':
                ideal_z = -10
            elif role == 'shifter':
                ideal_z = -7

            for item in item_list:
                if item.price < budget:
                    item_radius = item.price / 10
                    item_angle = item.mod * math.pi / 3
                    
                    if item.type == 'armor':
                        item_z = 10
                    elif item.type == 'misc':
                        item_z = 0
                    elif item.type == 'weapon':
                        item_z = -10

                    # Calculate polar distance between a customer's ideal item and an item we have in stock (does not incorporate item types) using the polar distance formula
                    polar_dist = math.sqrt((math.pow(item_radius, 2) + math.pow(ideal_radius, 2) - 2 * item_radius * ideal_radius * math.cos(item_angle - ideal_angle)))
                
                    # Calculate Cartesian distance between a customer's ideal item and an item we have in stock (to incorporate item types) using the Pythagorean Theorem
                    cartesian_dist = math.sqrt(math.pow(polar_dist, 2) + math.pow(ideal_z - item_z, 2))
                
                    dist_dict.insert(item.name, cartesian_dist)
        

        # NOTE: There is a lot of similarity between the above and below distance calculations. I
        #       kept the steps separate to make it clear that the calculations are done differently.


        # If the enemy IS a "basic" type:
        else:

            ideal_x = budget / 10

            if role == 'warrior':
                ideal_y = 10
            elif role == 'assassin':
                ideal_y = 7
            elif role == 'mage':
                ideal_y = 2
            elif role == 'scout':
                ideal_y = 0
            elif role == 'nexus':
                ideal_y = -10
            elif role == 'shifter':
                ideal_y = -7


            for item in item_list:
                if item.price < budget:
                    item_x = item.price / 10
                    if item.type == 'armor':
                        item_y = 10
                    elif item.type == 'misc':
                        item_y = 0
                    elif item.type == 'weapon':
                        item_y = -10

                    # Calculate distance between ideal item and a random item from our items_list
                    dist = math.sqrt(math.pow(item_x - ideal_x, 2) + math.pow(item_y - ideal_y, 2))
                
                    dist_dict.insert(item.name, dist)


        # Sort dist_dict and converts it to a list of keys
        sorted(dist_dict)

        # Order the top 3 items in order from most expensive to least expensive and put them into a tuple
        recommendations = (dist_dict.get(0), dist_dict.get(1), dist_dict.get(2))
        sorted(recommendations)

        # Return the tuple
        return recommendations


        