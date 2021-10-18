from fastapi import FastAPI
from app.models import db
from app.games.endpoints import router as gameRouter

app = FastAPI()
app.include_router(gameRouter)

db.bind('sqlite', 'DataBase.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


@app.get("/")
async def root():
    return {"message": "Hello World"}