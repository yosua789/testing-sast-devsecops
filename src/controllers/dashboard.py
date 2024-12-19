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
        x = MetaModel.objects.all()

        if not x:
            return "empty"


        # exe = LogModel(filename="access.log")
        # exe.save()

        return len(x)
    
    @get("add-data")
    def add(self):
        cek = LogModel.objects.filter(filename="access.log").first()

        if cek:
          return "already add"

        a = LogModel(filename="access.log",lastsize=0)
        a.save()

        return "success"  

