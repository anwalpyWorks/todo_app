import datetime
from fastapi import FastAPI
from model.models import Employee, User
from mongoengine import connect
import json

app = FastAPI()
connect(db="hrms", host="localhost", port=27017)


# @app.get("/")
# def home():
#   return {"message":"Hello world"}

@app.get("/get_all_employees")
def get_all_employees():
    employees = json.loads(Employee.objects().to_json())
    return {"employees": employees}


from fastapi import Path


@app.get("/get_employee/{emp_id}")
def get_employee(emp_id: int = Path(..., gt=0)):
    employee = Employee.objects.get(emp_id=emp_id)
    employee_dict = {
        "emp_id": employee.emp_id,
        "name": employee.name,
        "age": employee.age,
        "teams": employee.teams
    }
    return employee_dict


from fastapi import Query
from mongoengine.queryset.visitor import Q


@app.get("/search_employees")
def search_employees(name: str, age: int = Query(None, gt=18)):
    employees = json.loads(Employee.objects.filter(Q(name__icontains=name) | Q(age=age)).to_json())
    return {"employees": employees}


from pydantic import BaseModel
from fastapi import Body

class NewEmployee(BaseModel):
    emp_id: int
    name: str
    age: int = Body(None, gt=18)
    teams: list


@app.post("/add_employee")
def add_employee(employee: NewEmployee):
    new_employee = Employee(emp_id=employee.emp_id,
                            name=employee.name,
                            age=employee.age,
                            teams=employee.teams)

    new_employee.save()

    return {"message": "employee has added successfully"}











class NewUser(BaseModel):
    username: str
    password: str


from passlib.context import CryptContext

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
from jose import jwt

def create_access_token(data: dict, expires_delta: timedelta, SECRET_KEY=None, ALGORITHM=None):
    to_encode = data.copy()

    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp":expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if authenticate_user(username, password):
        access_token = create_access_token(data={"sub": username}, expires_delta=timedelta(minutes=30))

        return {"access_token": username, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=400, detail=" incorrect user name or password")


@app.get("/")
def home(token: str = Depends(oauth2_scheme)):
    return {"token": token}
