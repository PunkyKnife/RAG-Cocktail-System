from pydantic import BaseModel


class Question(BaseModel):
    msg: str
