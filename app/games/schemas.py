from pydantic import BaseModel


class CreateGameSchema(BaseModel):
    gameName: str
    hostNickname: str
