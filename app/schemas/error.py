from pydantic import BaseModel


class ErrorOut(BaseModel):
    error: str
    message: str
    status_code: int
