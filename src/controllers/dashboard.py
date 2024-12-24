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

        if not x:
            return "empty"


        # exe = LogModel(filename="access.log")
        # exe.save()
        res = {"test":len(x),"test2":len(y)}
        return res

        # a = GoaccessEngine()
        # p = a.run()

        # return p
    
    @get("add-data")
    def add(self):
        cek = LogModel.objects.filter(filename="/test2/access.log").first()
        

        if cek:
          return "already add"

        a = LogModel(filename="/test/access.log",lastsize=0)
        a.save()

        b = LogModel(filename="/test2/access.log",lastsize=0)
        b.save()
        return "success"  

