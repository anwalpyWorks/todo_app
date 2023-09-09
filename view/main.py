import json
from pydantic import BaseModel
from fastapi import Body
from fastapi import FastAPI
from mongoengine import connect
from model.models import Employee

app = FastAPI()
connect(db="hrms", host="localhost", port=27017)

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

