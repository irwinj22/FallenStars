import os
import dotenv
import sqlalchemy
def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = sqlalchemy.create_engine(database_connection_url(), pool_pre_ping=True)
metadata_obj = sqlalchemy.MetaData()
w_log = sqlalchemy.Table("w_log", metadata_obj, autoload_with=engine)
a_log = sqlalchemy.Table("a_log", metadata_obj, autoload_with=engine)
i_log = sqlalchemy.Table("i_log", metadata_obj, autoload_with=engine)
m_log = sqlalchemy.Table("m_log", metadata_obj, autoload_with=engine)