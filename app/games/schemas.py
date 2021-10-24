from pydantic import BaseModel

class AvailableGameSchema(BaseModel):
    id: int
    name: str
    playerCount: int