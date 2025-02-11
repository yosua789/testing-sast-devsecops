import os,subprocess,datetime,requests,jwt,re
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
from blacksheep import json,Response,Request,text,JSONContent
from typing import Optional
import inspect

from .core.engine import GoaccessEngine
# from configuration import send_email



class Dashboard(BaseController):
    @auth()
    @get("/")
    def index(self,req:Request,iden:Identity):
        # return iden.claims.get("name")
        getLog = LogModel.objects.all()
        meta = []
        
        if getLog:
            for i in getLog:
                a = MetaModel.objects.filter(filelog=i).order_by("-created_at").first()
                
                if a:
                    meta.append(a)
        
        cls_name,func_name = self.format_breadcrub(self.__class__.__name__,inspect.currentframe().f_code.co_name)
        
        
        model = {
            "res":meta,
            "breadcrub":[cls_name,func_name],
        }

        return self.view(model=model,iden=iden)

    @get("test-docker")
    def docker_testing(self):

        go = GoaccessEngine()
        # a = go.editYaml("/home/gozilla/project/web_logger/log4","/home/log/test4","delete")
        a = go.run()
        return a




