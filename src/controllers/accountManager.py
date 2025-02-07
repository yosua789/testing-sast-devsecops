import os
from uuid import uuid4
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q
from .BaseController import BaseController
from blacksheep.server.controllers import get, post
from blacksheep.messages import Request
from blacksheep.server.authorization import auth
from blacksheep.server.bindings import FromForm, FromQuery
from blacksheep.server.responses import redirect
from guardpost.asynchronous.authentication import Identity
from passlib.hash import pbkdf2_sha256 as sha256
from models import *
import inspect


class Account_Manager(BaseController):

    @auth()
    @get("/")
    async def index(self, iden:Identity):

        AllUsers = UserModel.objects.all()
        cls_name, func_name = self.format_breadcrub(
            self.__class__.__name__, inspect.currentframe().f_code.co_name
        )

        model = {
                "users": AllUsers,
                "breadcrub": [cls_name, func_name]
                }

        return self.view(model=model,iden=iden)

    @auth("admin")
    @get("/add-account")
    async def add_account(self, iden:Identity):
        cls_name, func_name = self.format_breadcrub(
            self.__class__.__name__, inspect.currentframe().f_code.co_name
        )

        model = {"breadcrub": [cls_name, func_name]}

        return self.view(model=model,iden=iden)

    @auth("admin")
    @post("/add-data")
    async def inserPro(self, user: Identity, data: FromForm[usersForm]):

        name = data.value.name
        password = sha256.encrypt(data.value.password)
        email = data.value.email
        role = data.value.role

        cekName = UserModel.objects.filter(name=name).first()

        if cekName:
            return {"status": 400, "message": "Name is taken"}

        cekEmail = UserModel.objects.filter(email=email).first()

        if cekEmail:
            return {"status": 400, "message": "Email is taken"}

        allowRole = ["admin", "viewer"]

        if not role in allowRole:
            return {"status": 400, "message": "Role is not valid"}

        user = UserModel(name=name, email=email, password=password, role=role)

        if user.save():
            return {"status": 200, "message": "Success"}

        else:
            return {"status": 400, "message": "Failed to save data"}

    @auth("admin")
    @get("/delete/{email}")
    async def delete(self, email: str, user: Identity, bs_message):
        user = UserModel.objects.filter(email=email).first()

        if not user:
            return {"status": 400, "message": "User not found"}

        user.delete()

        return redirect("/account-manager")
    
    @auth("admin")
    @post("/update/{email}")
    def update_exe(self,email:str,data: FromForm[usersUpdate],):
        name = data.value.name
        role = data.value.role  
        password = data.value.password
        
        cekEmail = UserModel.objects(email=email).first()
        
        if not cekEmail:
            return {"status": 400, "message": "Email not found"}
        
        if name != cekEmail.name:
            cekName = UserModel.objects(name=name).first()
            
            if cekName:
                return {"status": 400, "message": "Name is taken"}
            
        if password and password != "":
            password = sha256.encrypt(password)
            cekEmail.password = password
            
            
        allowRole = ["admin", "viewer"]
        if not role in allowRole:
            return {"status": 400, "message": "Role is not valid"}
            
        cekEmail.name = name
        cekEmail.role = role
        cekEmail.save()
        
        return {"status": 200, "message": "Success"}
    
    @auth("admin")
    @get("/update/{email}")
    def update(self,email:str,iden:Identity):
        cekEmail = UserModel.objects(email=email).first()
        
        if not cekEmail:
            return {"status": 400, "message": "User not found"}
        
        cls_name, func_name = self.format_breadcrub(
            self.__class__.__name__, inspect.currentframe().f_code.co_name
        )

        model = {
            "breadcrub": [cls_name, func_name],
            "email" : email,
            "data":cekEmail
            }
            
        return self.view(model=model,iden=iden)
        
        
        
            
        

        
        
            
