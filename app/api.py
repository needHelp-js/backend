from app.exception_handlers import validation_exception_handler
from config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.models import db

origins = ["*"]


def create_app(config: Config):

    db.bind(**config.dbBind)
    db.generate_mapping(create_tables=config.createTables)

    app = FastAPI()

    from app.games.endpoints import router as gamesRouter

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(gamesRouter)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    return app, db
