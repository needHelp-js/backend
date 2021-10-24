import os
import dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
dotenv.load_dotenv(os.path.join(basedir, ".env"))


class Config:
    dbBind = {
        "provider": os.environ.get("db_provider") or "sqlite",
        "filename": os.environ.get("db_filename") or "db.sqlite",
        "create_db": os.environ.get("create_db") or True,
    }
    createTables = os.environ.get("create_tables") or True
