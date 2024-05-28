import os
import dotenv
import sqlalchemy
from sqlalchemy import create_engine

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)
metadata_obj = sqlalchemy.MetaData()
items_ledger = sqlalchemy.Table("items_ledger", metadata_obj, autoload_with=engine)
mods_ledger = sqlalchemy.Table("mods_ledger", metadata_obj, autoload_with=engine)