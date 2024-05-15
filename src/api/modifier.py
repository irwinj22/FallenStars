from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/modifier",
    tags=["modifier"],
    dependencies=[Depends(auth.get_api_key)],
)

class Modifier(BaseModel):
    sku: str
    name: str
    type: str
    quantity: int
    price: int  

@router.post("/deliver/{order_id}")
def post_deliver_modifiers(modifiers_delivered: list[Modifier], order_id: int):
    """ """
    print(f"mods delievered: {modifiers_delivered} order_id: {order_id}")
    with db.engine.begin() as connection:
        sku_list = []
        type_list = []
        mod_dict = []
        cost = 0
        for mod in modifiers_delivered:
            sku_list.append(mod.sku)
            type_list.append(mod.type)
        # query mod info for delivery and the weapon logs to link the mod to the weapon itself
        mod_list = connection.execute(sqlalchemy.text("""select sku, id as m_id, type 
                                                      from mod_inventory where sku in :sku_list"""),
                                                      [{"sku_list": tuple(sku_list)}])
        weapon_list = connection.execute(sqlalchemy.text("""select id as bw_id, m_id, type 
                                                         from w_log where m_id is null and type in :type_list"""),
                                                         [{"type_list": tuple(type_list)}])
        armor_list = connection.execute(sqlalchemy.text("""select id as bw_id, m_id, type 
                                                         from a_log where m_id is null and type in :type_list"""),
                                                         [{"type_list": tuple(type_list)}])
        item_list = connection.execute(sqlalchemy.text("""select id as bw_id, m_id, type 
                                                         from i_log where m_id is null and type in :type_list"""),
                                                         [{"type_list": tuple(type_list)}])
        thing_dict = [weapon._asdict() for weapon in weapon_list] + [armor._asdict() for armor in armor_list] + [item._asdict() for item in item_list]
        for mod in mod_list:
            q = next(m.quantity for m in modifiers_delivered if m.sku == mod.sku) # Quantity of mods to apply
            for thing in [t for t in thing_dict if t['type'] == mod.type]:
                thing['m_id'] = mod.m_id # Links all weapons queried such that the m_id column points to a modifier
                asdict = mod._asdict()
                asdict['attached'] = thing['bw_id']
                mod_dict.append(asdict) # Builds a list of dicts to add to the modifier logs that includes what it's attached to
                q -= 1 
                if q == 0: break # If you're out of mods to apply, stop!
            if q != 0:
                mod_dict += [mod._asdict()] * q
        if mod_dict != []:
            connection.execute(db.m_log.insert(), mod_dict)
        print(thing_dict)
        weapon_dict = [t for t in thing_dict if t['type'] in ['pistol', 'rifle', 'melee']]
        armor_dict = [t for t in thing_dict if t['type'] in ['street', 'combat', 'powered']]
        item_dict = [t for t in thing_dict if t['type'] in ['attack', 'defense', 'support']]
        if weapon_dict != []:
            connection.execute(db.w_log.update().where(sqlalchemy.and_(db.w_log.c.m_id == sqlalchemy.null(),db.w_log.c.id == sqlalchemy.bindparam('bw_id'))), weapon_dict) 
        if armor_dict != []:
            connection.execute(db.a_log.update().where(sqlalchemy.and_(db.a_log.c.m_id == sqlalchemy.null(),db.a_log.c.id == sqlalchemy.bindparam('bw_id'))), armor_dict) 
        if item_dict != []:
            connection.execute(db.w_log.update().where(sqlalchemy.and_(db.i_log.c.m_id == sqlalchemy.null(),db.i_log.c.id == sqlalchemy.bindparam('bw_id'))), item_dict) 
        for mod in modifiers_delivered:
            cost -= mod.quantity*mod.price
        connection.execute(sqlalchemy.text("insert into credit_ledger (change) values (:cost)"),[{"cost": cost}])


    return "OK"

@router.post("/plan")
def get_modify_plan(modifier_catalog: list[Modifier]):
    """
    Add modifiers to weapons
    """
    json = []
    for mod in modifier_catalog:
        with db.engine.begin() as connection:
            credits = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM credit_ledger")).scalar_one()
            weapon_list = connection.execute(sqlalchemy.text("select type, count(id) from w_log where m_id is null group by type order by type")).fetchall()
            armor_list = connection.execute(sqlalchemy.text("select type, count(id) from a_log where m_id is null group by type order by type")).fetchall()
            item_list = connection.execute(sqlalchemy.text("select type, count(id) from i_log where m_id is null group by type order by type")).fetchall()
            mod_list = connection.execute(sqlalchemy.text("select sku from mod_inventory")).fetchall()
            mod_filter = [m[0] for m in mod_list]
            all_types = weapon_list + armor_list + item_list
        for mod in modifier_catalog:
            qual = next((x for x in all_types if x[0] == mod.type), None)
            if qual != None and mod.price < credits and mod.sku in mod_filter:
                json.append(
                    {
                        "sku": mod.sku,
                        "quantity": min(qual[1], mod.quantity)
                    }
                )
                credits -= mod.price

    return json
    
    

if __name__ == "__main__":
    print(get_modify_plan())
