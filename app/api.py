from fastapi import FastAPI
from app.models import db

app = FastAPI()

db.bind('sqlite', 'DataBase.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


@app.get("/")
async def root():
    return {"message": "Hello World"}