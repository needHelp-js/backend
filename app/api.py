from fastapi import FastAPI
from config import Config
from app.models import db

from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]


def create_app(config: Config):

    db.bind(**config.dbBind)
    db.generate_mapping(create_tables=config.createTables)

    app = FastAPI()

    from app.games.endpoints import router as gameRouter

    app.include_router(gameRouter)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app, db
