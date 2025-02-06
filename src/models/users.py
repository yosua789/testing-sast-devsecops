import json, mongoengine as me

from dataclasses import dataclass
from datetime import datetime


class UserModel(me.Document):
    meta = {"collection" : "users"}

    name = me.StringField(max_length=150, required=True)
    email = me.StringField(max_length=150, required=True, unique=True)
    password = me.StringField(max_length=150, required=True)
    role = me.StringField(max_length=10, required=True)

    created_at = me.DateTimeField(required=True, default=datetime.now)


@dataclass
class usersForm:
    name:str
    email:str
    role:str
    password:str


@dataclass
class usersUpdate:
    name:str
    role:str
    password:str=None


@dataclass
class LoginUser:
    email:str
    password:str
 
# 