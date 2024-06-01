from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
import numpy as np
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

    return "OK"

@router.post("/million/", tags=["populate"])
def million():

    return "OK"