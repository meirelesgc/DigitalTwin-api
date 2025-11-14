from http import HTTPStatus

from fastapi import FastAPI

from api.routers import auth, users, estaccionamento
from api.schemas import Message

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(estaccionamento.router)


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Olá Mundo!"}
