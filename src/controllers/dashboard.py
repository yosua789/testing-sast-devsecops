import os,subprocess,json,datetime
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
from .core.engine import GoaccessEngine
# from configuration import send_email

class Dashboard(BaseController):
    # @auth()
    @get("/")
    def index(self):
        x = MetaModel.objects.filter(name="/test/access.log").all()
        y = MetaModel.objects.filter(name="/test2/access.log").all()
        z = MetaModel.objects.filter(name="/test3/access.log").all()


        if not x:
            return "empty"


        # exe = LogModel(filename="access.log")
        # exe.save()
        res = {"test":len(x),"test2":len(y),"test3":len(z)}
        return res

        # a = GoaccessEngine()
        # p = a.run()

        # return p
    
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

