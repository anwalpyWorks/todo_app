import datetime
from fastapi import FastAPI
from model.models import Employee, User
from mongoengine import connect
import json
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
connect(db="hrms", host="localhost", port=27017)

templates = Jinja2Templates(directory="templates")

@app.get("/")
def view():
    return




class NewUser(BaseModel):
    username: str
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@app.post("/sign_up")
def sign_up(new_user: NewUser):
    user = User(username=new_user.username,
                password=get_password_hash(new_user.password))  # pip3 install passlib[bcrypt]
    user.save()
    return {"message": "New user created successfully"}


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username, password):
    try:
        user = json.loads(User.objects.get(username=username).to_json())
        password_check = pwd_context.verify(password, user['password'])
        return password_check
    except User.DoesNotExist:
        return False


from datetime import timedelta, datetime
from jose.constants import ALGORITHMS
import jose.jwt

SECRET_KEY = "066244f09392a2ac8cfe0fb887e85492e316dae5c6f7969ad460ba4f040e5cd5"


ALGORITHMS = "HS256"

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jose.jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHMS)
    return encoded_jwt

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if authenticate_user(username, password):
        access_token = create_access_token(
            data={"sub": username}, expires_delta=timedelta(minutes=30))
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail=" incorrect user name or password")



@app.get("/")
def home(token: str = Depends(oauth2_scheme)):
    return {"token": token}
