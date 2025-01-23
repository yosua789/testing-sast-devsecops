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

from .core.engine import GoaccessEngine

class Path(BaseController):
    @auth()
    @get("/")
    def index(self):
        path = PathModel.objects.all()
        model = {
            "path" : path
        }
        return self.view(model=model)
    @auth()
    @get("/add-path")
    def add_path(self):
        return self.view()
    
    @auth()
    @post("add-path")
    def add(self,context:Request,data:FromForm[InputPath]):
        go = GoaccessEngine()
        host_path = data.value.host
        docker_path = data.value.docker

        docker_path = docker_path.lstrip("/")

        docker_path = os.path.join(os.getenv("LOG_PATH"),docker_path)
        
        header = context.cookies['Auth_AX']
        
        status,msg = go.CheckHostPath(host_path,header)

        if not status:
            return {"status": 400, "message" : msg}
        
        status,msg = go.AddPath(host_path,docker_path,header)

        if not status:
            return {"status": 400, "message" : msg}
        
    @auth()
    @get("/delete/{id}")
    def delete_path(self,context:Request,id:str):
        go = GoaccessEngine()
        
        cekPath = PathModel.objects.filter(id=id).first()

        if not cekPath:
            return {"status": 400, "message" : "Data not found from db"}
        
        
        endpoint_cek = go.endpoint_service + "/service/restart-docker"
        docker_filename = go.docker_filename
        header = context.cookies['Auth_AX']
        
        status,msg = go.CheckHostPath(docker_filename,header)

        if not status:
            return {"status": 400, "message" : msg}

        data_to_send = {
            "path":docker_filename
        }

        headers = {
            "Auth_AX":header
        }

        status,msg = go.editYaml(cekPath.host_path,cekPath.docker_path,"delete")
        if not status:
            return {"status": 400, "message" : msg}

        try:
            
            deleted_log = LogModel.objects(path=cekPath).delete()
            cekPath.delete()
            
            res = requests.post(endpoint_cek,json=data_to_send,headers=headers)
            if res.status_code == 200:
                return True
            
            return {"status": 400, "message" : "Failed to send"}

        except Exception as e:
            return {"status": 400, "message" : "Docker reset service is not active"}

       


