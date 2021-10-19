from fastapi import FastAPI
from config import Config
from app.models import db

def create_app(config: Config):

    db.bind(**config.dbBind)
    db.generate_mapping(create_tables=config.createTables)

    app = FastAPI()

    from app.games.endpoints import router as gameRouter

    app.include_router(gameRouter)

    return app, db
