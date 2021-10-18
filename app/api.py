from fastapi import FastAPI, responses
from app.models import *
from random import randint
from app.games.endpoints import router as gamesRouter

app = FastAPI()

db.bind('sqlite', 'DataBase.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(gamesRouter)