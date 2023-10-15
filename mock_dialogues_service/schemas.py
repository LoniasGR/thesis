from pydantic import BaseModel

class Client(BaseModel):
    host: str

    class Config:
        from_attributes = True
    
class UserUtterance(BaseModel):
    intent: str
    description: str

    class Config:
        from_attributes = True
    
class Evaluation(BaseModel):
    user: list[UserUtterance]
    suggestion: str
    answer: bool

    class Config:
        from_attributes = True
