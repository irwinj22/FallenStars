from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/mods",
    tags=["mods"],
    dependencies=[Depends(auth.get_api_key)],
)

class Mod(BaseModel):
    sku: str
    type: str
    price: int
    quantity: int
    compatible: list[str]

@router.post("/purchase/mods")
def purchase_mods(mod_catalog: list[Mod]):
    '''
    Nurane gives list of mods, we buy inventory accordingly. 
    '''

    '''
    Current logic: 
    buy 3 FLAMING_BLADE, if possible (could be restrained by credits or num offered)
    --> if can't buy 3, just buy as many as possible 
    '''

    order = []

    credits_sql = '''
    SELECT (SELECT SUM(items_ledger.credit_change) FROM items_ledger) + 
           (SELECT SUM(mods_ledger.credit_change) FROM mods_ledger) AS credits
    '''

    # NOTE: this will return None if there are no entries in either of the ledgers ... 
    with db.engine.begin() as connection:
        credits = connection.execute(sqlalchemy.text(credits_sql)).scalar()

    # iterate through each item being offered by Nurane, buy according to logic specified above
    for mod in mod_catalog: 
        if mod.sku == "FLAMING_BLADE":
            num_can_afford = credits // mod.price 
            num_possibile = min(3, min(num_can_afford, mod.quantity))
            # if possible for us to buy more than one, then add to order
            if num_possibile > 0:
                order.append(
                    {
                        "sku": mod.sku,
                        "type" : mod.type, 
                        "price" : mod.price,
                        "qty" : num_possibile
                    }
                )

    # to get id from mods_plan    
    id_sql = '''
    SELECT id 
    FROM mods_plan 
    WHERE sku = :sku 
    '''
    
    # to make insertion into mods_ledger
    pur_sql = '''
    INSERT INTO mods_ledger (qty_change, mod_id, mod_sku, credit_change) VALUES (:qty, :mod_id, :mod_sku, :credit_change)
    '''

    # once the order has been created, run through and make the appropriate inserts
    for line_item in order:
        print(line_item)
        with db.engine.begin() as connection:
            id = connection.execute(sqlalchemy.text(id_sql), [{"sku":line_item['sku']}]).scalar()
            connection.execute(sqlalchemy.text(pur_sql), [{"qty":line_item['qty'], "mod_id":id, "mod_sku":line_item['sku'], "credit_change": -line_item['price'] * line_item['qty']}])

    # TODO: implement the logic of attaching mods to items!!

    return order



