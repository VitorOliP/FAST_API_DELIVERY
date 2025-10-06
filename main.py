# Run API uvicorn main:app --reload
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

argon2_context = CryptContext(schemes=['argon2'], deprecated="auto")
oath2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login_form")

from routers.auth_routers import auth_router
from routers.order_routers import order_router

app.include_router(auth_router)
app.include_router(order_router)