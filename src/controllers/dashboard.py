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
        a = GoaccessEngine()
        
        sts,msg = a.exe("/home/log/access.log")

        print(f"{sts} - {msg}")


        # exe = LogModel(filename="access.log")
        # exe.save()

        return "hai"


