import os,subprocess,datetime,requests,jwt
from uuid import uuid4
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q
from .BaseController import BaseController
from blacksheep.server.controllers import get, post
from blacksheep.server.authorization import auth
from blacksheep.server.bindings import FromForm, FromQuery,FromCookie
from blacksheep.server.responses import redirect
from guardpost.asynchronous.authentication import Identity
from passlib.hash import pbkdf2_sha256 as sha256
from models import *
from blacksheep.cookies import Cookie
from blacksheep import json,Response,Request,text
from typing import Optional

from .core.engine import GoaccessEngine
# from configuration import send_email

class FromFooCookie(FromCookie[str]):
    name = "As_X_auth"

class ModeCookie(FromCookie[str]):
    name = "modea"


class Dashboard(BaseController):
    @auth()
    @get("/")
    def home(self,req:Request):
        return "haii"
    
    @get("/as")
    def homes(foo: FromFooCookie) -> Response:
        return text(
            f"""
            Foo: {foo.value}
            """
        )

    
    @post("add-data")
    def add(self,data:FromForm[InputPath]):
        path = data.value.folder
        path_d = path.lstrip("/")


        path_ = os.path.join("/home/log",path_d)

        if not os.path.exists(path_):
            return "not found"
        
        exe = LogModel(filename=path,lastsize=0)
        exe.save()

        return "success"

    @get("test-docker")
    def docker_testing(self):

        req = requests.get("http://172.17.0.1:5005/dashboard")
        req = req.json()

        # req = json.load(req)
        return req['status']




