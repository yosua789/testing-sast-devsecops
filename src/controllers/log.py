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
from blacksheep import Response,Request,text,JSONContent
from typing import Optional
import inspect

from .core.engine import GoaccessEngine

class Logfile(BaseController):
    @auth()
    @get("/")
    def index(self,iden:Identity):
        
        log = LogModel.objects.all()
        cls_name,func_name = self.format_breadcrub(self.__class__.__name__,inspect.currentframe().f_code.co_name)
        
        model = {
            "log":log,
            "breadcrub":[cls_name,func_name]
        }
        return self.view(model=model,iden=iden)
    
    @auth("admin")
    @get("add-filelog")
    def add_filelog(self,iden:Identity):
        log = PathModel.objects.all()
        cls_name,func_name = self.format_breadcrub(self.__class__.__name__,inspect.currentframe().f_code.co_name)
        
        model = {
            "log":log,
            "breadcrub":[cls_name,func_name]
        }
        return self.view(model=model,iden=iden)
    
    @auth("admin")
    @post("add-filelog")
    def add_fileexe(self,data:FromForm[AddLog]):
        go = GoaccessEngine()
        log = data.value.filename
        service = data.value.service
        # return str(data.value.path)
        path = PathModel.objects.filter(id=str(data.value.path)).first()
        
        if not path:
            return {"status": 400, "message" : "Path not found"}
        
        log = os.path.join(path.docker_path,log)

        # return log
        if not os.path.isfile(log):
            return {"status": 400, "message" : "file not found"}
        
        cekfile = LogModel.objects.filter(filename = log).first()

        if cekfile:
            return {"status": 400, "message" : "Data already exists"}
        
        cekService = LogModel.objects.filter(servicename=service).first()
        
        if cekService:
            return {"status": 400, "message" : "Service name already taken"}
            
        status,val = go.readLogLine(log)

        if not status:
            return {"status": 400, "message" : "Error while read filelog"}
        
        val = go.getLogDate(val)

        if not val:
            return {"status": 400, "message" : "Error while read datetime on log"}
        
        dateformat = go.convertDateFormat(val)
        
        if not dateformat:
            return {"status": 400, "message" : "Error convert datetime"}
        
        ignore = go.getIgnore()
        
        status,msg= go.exe(log,dateformat,ignore)
        if not status:
            return {"status": 400, "message" : "Format not valid"}
        
        size = os.path.getsize(log)

        respone_file,respone_path = go.filenameRespone(log)

        with open(respone_file,"r") as file:
            go_json = json.load(file)
        
        exe = LogModel(filename=log,dateformat=dateformat,path=path,servicename=service)
        exe.save()

        exeMeta = MetaModel(filelog=exe,data=json.dumps(go_json))
        exeMeta.save()

        exe.lastsize = size
        exe.save()
        
        return {"status": 200, "message" : "Success"}

    @auth("admin")
    @get("/delete/{id}")
    def delete(self,id:str):
        try:
            cek = LogModel.objects.filter(id=id).first()

            if not cek:
                return {"status": 400, "message" : "Not Found"}
            
            delMeta = MetaModel.objects(filelog = cek).delete()
            
            cek.delete()

            return redirect("/logfile")

        except Exception as e:
            return {"status": 500, "message" : "Error"}