import os,subprocess,datetime,requests,jwt,re,json
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
from blacksheep import Response,Request,text,JSONContent
from typing import Optional

from .core.engine import GoaccessEngine

class Analytic(BaseController):
    @get("/")
    def index(self):
        log = LogModel.objects.all()
        model = {
            "log":log
        }

        return self.view(model=model)
    

    @get("/log/{id}")
    def log(self,id:str):
        def formatModel(value,data):
            try:
                return data[value]
            except Exception as e:
                return None
            
        ceklog = LogModel.objects.filter(id=id).first()

        if not ceklog:
            return {"status":400,"message":"Data log not found"}
 
        data = MetaModel.objects.filter(filelog=ceklog).order_by("-created_at").first()
        data = json.loads(data.data)
        
        # return data

        # return data['requests']
        # tes = PathModel.objects.all()
        model = {
            "requests":formatModel('requests',data),
            "browser":formatModel('browsers',data),
            "not_found":formatModel('not_found',data),
            "ref_site":formatModel('referring_sites',data),
            "os":formatModel('os',data),
            "general":data["general"],
            "static_req":formatModel('static_requests',data),
            "id":id,

        }
        
        return self.view(model=model)

    @get("/log/{id}/{type}/{subtype}")
    def log_detail(self,id:str,type:str,subtype:str):

        ceklog = LogModel.objects.filter(id=id).first()

        if not ceklog:
            return {"status":400,"message":"Data log not found"}
 
        data = MetaModel.objects.filter(filelog=ceklog).order_by("-created_at").first()
        data = json.loads(data.data)
        
        # return data
        
        if type not in data:
            return {"status":400,"message":"Data type not valid"}
        
        valid = False
        index = None
        
        for _id,item in enumerate(data[type]['data']):
            if item['data'] == subtype:
                valid = True
                break
        
        if valid:
            model ={
                "data":data[type]['data'][_id],
                "item":data[type]['data'][_id]['items'],
                "name":type
            }

            # return model

            return self.view(model=model)

        
        return {"status":400,"message":"Data not found"}

