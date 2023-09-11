from mongoengine import Document, StringField, IntField, ListField
from pydantic import BaseModel


class Todo(BaseModel):
    name: str
    description: str


class Employee(Document):
    emp_id = IntField()
    name = StringField(max_length=100)
    age = IntField()
    teams = ListField()


class User(Document):
    username = StringField()
    password = StringField()
