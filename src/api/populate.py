from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import numpy as np
from sqlalchemy.exc import DBAPIError
from faker import Faker

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"],
    dependencies=[Depends(auth.get_api_key)],
)

router = APIRouter()
@router.post("/populate/", tags=["populate"])
def populate():
    '''
    Initital data needed to run properly.
    '''

    try:
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text('''
            INSERT INTO customers VALUES (0, now(), 'Fallen Stars', 'EXPERT');

            INSERT INTO mods_plan VALUES (0, 'BASIC', 'basic');
            INSERT INTO mods_plan VALUES (1, 'FIRE', 'fire');
            INSERT INTO mods_plan VALUES (2, 'EARTH', 'earth');
            INSERT INTO mods_plan VALUES (3, 'WATER', 'water');

            INSERT INTO items_plan VALUES (1, 'weapon', 30, 0, 'LONGSWORD', ARRAY[30, 0, 1]);
            INSERT INTO items_plan VALUES (2, 'weapon', 50, 1, 'FIRE_LONGSWORD', ARRAY[50, 1, 1]);
            INSERT INTO items_plan VALUES (3, 'weapon', 55, 2, 'EARTH_LONGSWORD', ARRAY[55, 2, 1]);
            INSERT INTO items_plan VALUES (4, 'weapon', 45, 3, 'WATER_LONGSWORD', ARRAY[45, 3, 1]);

            INSERT INTO items_plan VALUES (5, 'weapon', 25, 0, 'PISTOL', ARRAY[25, 0, 1]);
            INSERT INTO items_plan VALUES (6, 'weapon', 45, 1, 'FIRE_PISTOL', ARRAY[45, 1, 1]);
            INSERT INTO items_plan VALUES (7, 'weapon', 50, 2, 'EARTH_PISTOL', ARRAY[50, 2, 1]);
            INSERT INTO items_plan VALUES (8, 'weapon', 40, 3, 'WATER_PISTOL', ARRAY[40, 3, 1]);

            INSERT INTO items_plan VALUES (9, 'armor', 40, 0, 'SHIELD', ARRAY[40, 0, 2]);
            INSERT INTO items_plan VALUES (10, 'armor', 60, 1, 'FIRE_SHIELD', ARRAY[60, 1, 2]);
            INSERT INTO items_plan VALUES (11, 'armor', 65, 2, 'EARTH_SHIELD', ARRAY[65, 2, 2]);
            INSERT INTO items_plan VALUES (12, 'armor', 55, 3, 'WATER_SHIELD', ARRAY[55, 3, 2]);

            INSERT INTO items_plan VALUES (13, 'armor', 25, 0, 'HELMET', ARRAY[25, 0, 2]);
            INSERT INTO items_plan VALUES (14, 'armor', 45, 1, 'FIRE_HELMET', ARRAY[45, 1, 2]);
            INSERT INTO items_plan VALUES (15, 'armor', 50, 2, 'EARTH_HELMET', ARRAY[50, 2, 2]);
            INSERT INTO items_plan VALUES (16, 'armor', 40, 3, 'WATER_HELMET', ARRAY[40, 3, 2]);

            INSERT INTO items_plan VALUES (17, 'other', 35, 0, 'STAFF', ARRAY[35, 0, 3]);
            INSERT INTO items_plan VALUES (18, 'other', 55, 1, 'FIRE_STAFF', ARRAY[55, 1, 3]);
            INSERT INTO items_plan VALUES (19, 'other', 60, 2, 'EARTH_STAFF', ARRAY[60, 2, 3]);
            INSERT INTO items_plan VALUES (20, 'other', 50, 3, 'WATER_STAFF', ARRAY[50, 3, 3]);

            INSERT INTO items_plan VALUES (21, 'other', 30, 0, 'CHAINLINK', ARRAY[30, 0, 3]);
            INSERT INTO items_plan VALUES (22, 'other', 50, 1, 'FIRE_CHAINLINK', ARRAY[50, 1, 3]);
            INSERT INTO items_plan VALUES (23, 'other', 55, 2, 'EARTH_CHAINLINK', ARRAY[55, 2, 3]);
            INSERT INTO items_plan VALUES (24, 'other', 45, 3, 'WATER_CHAINLINK', ARRAY[45, 3, 3]);

            INSERT INTO mods_ledger VALUES (1, now(), 0, 0, 'NONE', 2000);
            '''))
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

    return "OK"

@router.post("/customer_population/", tags=["populate"])
def customer_population():
    dupe_num = 400000
    faker = Faker()
    np.random.seed(42)
    roles = ["WARRIOR", "SUNBLADE", "ASSASSIN", "NEXUS", "SHIFTER", "BUILDER", "EXPERT", "MAGGE", "SCOUT"]
    with db.engine.begin() as connection:
        items = connection.execute(sqlalchemy.text("select id, sku, price, mod_id, type from items_plan")).fetchall()
        cust_w = [i.sku for i in items if i.type == 'weapon'] + [None]
        cust_a = [i.sku for i in items if i.type == 'armor'] + [None]
        cust_o = [i.sku for i in items if i.type == 'other'] + [None]
        c_role = np.random.choice(roles, dupe_num//2)
        c_w = np.random.choice(cust_w, dupe_num//2)
        c_a = np.random.choice(cust_a, dupe_num//2)
        c_o = np.random.choice(cust_o, dupe_num//2)
            
        for i in range(dupe_num//2):
            print(i)
            name = faker.unique.name()
            connection.execute(sqlalchemy.text("""insert into customers (name, role, recent_w_rec, recent_a_rec, recent_o_rec) 
                                            values (:name, :role, :recent_w_rec, :recent_a_rec, :recent_o_rec)"""), 
                                            {"name": name, "role": c_role[i], "recent_w_rec": c_w[i], "recent_a_rec": c_a[i], "recent_o_rec": c_o[i]})
    
@router.post("/items_mods_population/", tags=["populate"])
def items_mods_population():
    dupe_num = 400000
    qty_changes = [1, 2, 3, 4, 5]
    c_check = True
    np.random.seed(42)
    randnum = np.random.random(size=dupe_num)
    with db.engine.begin() as connection:
        items = connection.execute(sqlalchemy.text("select id, sku, price, mod_id, type from items_plan")).fetchall()
        mods = connection.execute(sqlalchemy.text("select id, sku from mods_plan")).fetchall()
        possible_items = [[i.id, i.sku, i.price] for i in items]
        possible_mods = [[m.id, m.sku] for m in mods]
        q_i = np.random.choice(qty_changes, dupe_num)
        q_m = np.random.choice(qty_changes, dupe_num)
            
        c_ids = connection.execute(sqlalchemy.text("select id from customers")).fetchall()
        c_id_array = np.random.choice([i.id for i in c_ids], dupe_num)
        items_array = np.random.randint(len(possible_items), size=dupe_num)
        mods_array = np.random.randint(len(possible_mods), size=dupe_num)

    with db.engine.begin() as connection:
        for i in range(dupe_num):
            print(i)
            if c_check:
                '''
                connection.execute(sqlalchemy.text("""insert into items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) values
                                        (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)"""),
                                        {"qty_change": int(q_i[i]), "item_id": int(possible_items[items_array[i]][0]), 
                                        "item_sku": possible_items[items_array[i]][1], "credit_change": int(max(0,possible_items[items_array[i]][2]*q_i[i])),
                                        "customer_id": 0})
                '''
                connection.execute(sqlalchemy.text("""insert into mods_ledger (qty_change, mod_id, mod_sku, credit_change) values
                                               (:qty_change, :mod_id, :mod_sku, :credit_change)"""),
                                               {"qty_change": int(q_m[i]), "mod_id": int(possible_mods[mods_array[i]][0]), 
                                                "mod_sku": possible_mods[mods_array[i]][1], "credit_change": int(max(0,q_m[i]*20))})
                if randnum[i] >= 0.3:
                    c_check = False
                    int(c_id_array[i])
                    '''
                    connection.execute(sqlalchemy.text("""insert into items_ledger (qty_change, item_id, item_sku, credit_change, customer_id) values
                                        (:qty_change, :item_id, :item_sku, :credit_change, :customer_id)"""),
                                        {"qty_change": -1*int(q_i[i]), "item_id": int(possible_items[items_array[i]][0]), 
                                        "item_sku": possible_items[items_array[i]][1], "credit_change": int(max(0,possible_items[items_array[i]][2]*q_i[i])),
                                        "customer_id": int(c_id_array[i])})
                                        '''
                    connection.execute(sqlalchemy.text("""insert into mods_ledger (qty_change, mod_id, mod_sku, credit_change) values
                                               (:qty_change, :mod_id, :mod_sku, :credit_change)"""),
                                               {"qty_change": -1*int(q_m[i]), "mod_id": int(possible_mods[mods_array[i]][0]), 
                                                "mod_sku": possible_mods[mods_array[i]][1], "credit_change": int(max(0,q_m[i]*20))})

            else:
                c_check = True    
    return "OK"