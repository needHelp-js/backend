from fastapi import FastAPI
from config import Config
from app.models import db
from app.games.endpoints import router as gamesRouter

def create_app(config: Config):

    db.bind(**config.dbBind)
    db.generate_mapping(create_tables=config.createTables)

    app = FastAPI()
    app.include_router(gamesRouter)

    return app, db
