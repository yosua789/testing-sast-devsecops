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
        pipeline = [
            {"$lookup": {
                "from": "log_file",  # The collection name for LogModel
                "localField": "filelog",  # The field in MetaModel that references LogModel
                "foreignField": "_id",  # The field in LogModel that we join on
                "as": "filelog_info"
            }},
            {"$unwind": "$filelog_info"},  # Flatten the lookup result
            {"$sort": {"created_at": -1}},  # Sort by created_at
            {"$group": {
                "_id": "$filelog_info.filename",  # Group by filename from LogModel
                "data": {"$first": "$data"},
                "created_at": {"$first": "$created_at"}
            }},
            {"$project": {
                "_id": 0,
                "filename": "$_id",  # Project the filename from the group
                "data": 1,
                "created_at": 1
            }}
        ]

        meta = MetaModel.objects.aggregate(*pipeline)
        meta = list(meta)
        
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




