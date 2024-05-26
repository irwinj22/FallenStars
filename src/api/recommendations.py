from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import numpy as np

router = APIRouter(
    prefix="/recs",
    tags=["recs"],
    dependencies=[Depends(auth.get_api_key)],
)

def cosine_distance(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    return 1-(dot_product / (norm_v1 * norm_v2))

@router.post("/recommend")
def recommend(budget: int, enemy_type: str, role: str):
    enemy_type_map = {
    "FIRE": 1,
    "WATER": 2,
    "EARTH": 3,
    "BASIC": 4
                    }
    e_type = enemy_type_map.get(enemy_type.upper(), 0)

    with db.engine.begin() as connection:
        role = role.lower()
        sql_txt = """SELECT item_preference FROM characters WHERE role = :x"""
        object_type = connection.execute(sqlalchemy.text(sql_txt),[{"x":role}]).scalar()
    
        given_vec = [budget, e_type, object_type]

        item_vecs = connection.execute(sqlalchemy.text("""SELECT item_vec FROM items_plan"""))

        min_dist = 2
        for vec in item_vecs:
            qty = connection.execute(sqlalchemy.text("""SELECT COALESCE(SUM(qty_change),0) FROM items_ledger AS il
                                        JOIN items_plan AS ip ON ip.id = il.item_id
                                        WHERE ip.item_vec = :x
                                        GROUP BY item_vec"""),[{"x":vec}]).scalar()
            if cosine_distance(vec, given_vec) < min_dist and qty > 0:
                min_dist = cosine_distance(vec, given_vec)
                rec_vec = vec

        rec_item_sku = connection.execute(sqlalchemy.text("""SELECT sku FROM items_plan 
                                                      WHERE item_vec = :x"""), [{"x":rec_vec}]).fetchone()
    
    return rec_item_sku

