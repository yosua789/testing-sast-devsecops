import os, subprocess, datetime, requests, jwt, re, json
from uuid import uuid4
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q
from .BaseController import BaseController
from blacksheep.server.controllers import get, post
from blacksheep.server.authorization import auth
from blacksheep.server.bindings import FromForm, FromQuery, FromCookie
from blacksheep.server.responses import redirect
from guardpost.asynchronous.authentication import Identity
from passlib.hash import pbkdf2_sha256 as sha256
from models import *
from blacksheep.cookies import Cookie
from blacksheep import Response, Request, text, JSONContent
from typing import Optional
from bson import ObjectId
import inspect

from .core.engine import GoaccessEngine


class Analytic(BaseController):
    def formatModel(self, value, data,draw=1, start=1,length=10):
        # try:
            # start = 0 if page == 1 else (page - 1) * show
            end = start + length
            data_fix = data[value]["data"][start:end]
            
            if value == "os" or value == "browsers":
                data_fix = [{"hits":i['hits']['count'],
                            "visitor":i['visitors']['count'],
                            "data":i['data'],
                            } for i in data_fix]
            
            else:
                data_fix = [{"hits":i['hits']['count'],
                            "visitor":i['visitors']['count'],
                            "method":i['method'] ,
                            "data":i['data'],
                            "protocol":i['protocol'] ,
                            } for i in data_fix]
            
            return {
                "draw": draw,
                "recordsTotal": len(data[value]["data"]),
                "recordsFiltered": len(data[value]["data"]),
                "data": data_fix,
            }

            return {"data": data_fix, "page": page, "next": next, "prev": prev}

        # except Exception as e:
        #     return "Error"

    @auth()
    @get("/")
    def index(self, iden: Identity):
        cls_name, func_name = self.format_breadcrub(
            self.__class__.__name__, inspect.currentframe().f_code.co_name
        )
        # return model
        log = LogModel.objects.all()
        model = {"log": log, "breadcrub": [cls_name, func_name]}

        return self.view(model=model, iden=iden)

    @auth()
    @get("sub_log_detail/{id}")
    async def sub_log_detail(
        self, id: str, type: str,draw:int,start:int,length:int, logid: str = None
    ):
        if not ObjectId.is_valid(id):
            return {"status": 400, "message": "Id not valid"}

        ceklog = LogModel.objects.filter(id=id).first()

        if not ceklog:
            return {"status": 400, "message": "Data log not found"}

        if logid:
            datas = MetaModel.objects.filter(id=logid, filelog=ceklog).first()
        else:
            datas = (
                MetaModel.objects.filter(filelog=ceklog).order_by("-created_at").first()
            )

        if datas:
            data = json.loads(datas.data)

            return self.formatModel(data=data, value=type,draw=draw,start=start,length=length)
        else:
            return {"status": "400", "message": "not found"}

    @auth()
    @get("/log/{id}")
    def log(self, id: str, iden: Identity):

        if not ObjectId.is_valid(id):
            return {"status": 400, "message": "Id not valid"}

        ceklog = LogModel.objects.filter(id=id).first()

        if not ceklog:
            return {"status": 400, "message": "Data log not found"}

        cls_name, func_name = self.format_breadcrub(
            self.__class__.__name__, inspect.currentframe().f_code.co_name
        )

        datas = MetaModel.objects.filter(filelog=ceklog).order_by("-created_at").first()
        if datas:
            data = json.loads(datas.data)

            model = {
                "general": data["general"],
                "id": id,
                "filename": datas.filelog.filename,
                "create_at": datas.created_at,
                "service": datas.filelog.servicename,
                "breadcrub": [cls_name, func_name],
            }
        else:
            model = {"breadcrub": [cls_name, func_name]}

        return self.view(model=model, iden=iden)

    @auth()
    @get("/log-detail/{id}")
    def log_detail(
        self,
        id: str,
        type: str,
        subtype: str,
        iden: Identity,
        logid: str = None,
    ):
        if not type:
            return {"status": 400, "message": "Type not found"}

        if not type:
            return {"status": 400, "message": "Type not found"}

        if not ObjectId.is_valid(id):
            return {"status": 400, "message": "Id not valid"}

        ceklog = LogModel.objects.filter(id=id).first()

        if not ceklog:
            return {"status": 400, "message": "Data log not found"}

        if not logid:
            data = (
                MetaModel.objects.filter(filelog=ceklog).order_by("-created_at").first()
            )
            data = json.loads(data.data)
        else:
            if not ObjectId.is_valid(logid):
                return {"status": 400, "message": "Id not valid"}

            data = MetaModel.objects.filter(filelog=ceklog, id=logid).first()

            if data:
                data = json.loads(data.data)

        if data:
            if type not in data:
                return {"status": 400, "message": "Data type not valid"}

            valid = False
            index = None

            for _id, item in enumerate(data[type]["data"]):
                if item["data"] == subtype:
                    valid = True
                    break

            if valid:
                cls_name, func_name = self.format_breadcrub(
                    self.__class__.__name__, inspect.currentframe().f_code.co_name
                )

                model = {
                    "data": data[type]["data"][_id],
                    "item": data[type]["data"][_id]["items"],
                    "name": type,
                    "breadcrub": [cls_name, func_name],
                }

                # return model

                return self.view(model=model, iden=iden)

        return {"status": 400, "message": "Data not found"}

    @auth()
    @get("/log/filter/{id}")
    def filter_date(self, id: str, date: str, iden: Identity):
        if not date:
            return {"status": 400, "message": "Date not valid"}

        if not ObjectId.is_valid(id):
            return {"status": 400, "message": "Id not valid"}

        log = LogModel.objects.filter(id=id).first()

        if not log:
            return {"status": 400, "message": "Log not found"}

        try:
            date = datetime.strptime(date, "%Y-%m-%d")
            dateend = date + timedelta(hours=23, minutes=59)
        except:
            return {"status": 400, "message": "date format not valid"}

        meta = MetaModel.objects(
            filelog=log, created_at__gte=date, created_at__lt=dateend
        ).all()

        cls_name, func_name = self.format_breadcrub(
            self.__class__.__name__, inspect.currentframe().f_code.co_name
        )

        model = {"data": meta, "id": id, "breadcrub": [cls_name, func_name]}

        return self.view(model=model, iden=iden)

    @auth()
    @get("log/filter/{id}/{logid}")
    def filter_id(self, id: str, logid: str, iden: Identity):

        if not ObjectId.is_valid(id):
            return {"status": 400, "message": "Id not valid"}

        ceklog = LogModel.objects.filter(id=id).first()

        if not ceklog:
            return {"status": 400, "message": "Data log not found"}

        if not ObjectId.is_valid(logid):
            return {"status": 400, "message": "Id not valid"}
        cls_name, func_name = self.format_breadcrub(
            self.__class__.__name__, inspect.currentframe().f_code.co_name
        )

        datas = MetaModel.objects.filter(id=logid, filelog=ceklog).first()
        if datas:
            data = json.loads(datas.data)

            model = {
                "general": data["general"],
                "id": id,
                "filename": datas.filelog.filename,
                "create_at": datas.created_at,
                "logid": logid,
                "service": datas.filelog.servicename,
                "breadcrub": [cls_name, func_name],
            }
        else:
            model = {"breadcrub": [cls_name, func_name]}
            
        return self.view(model=model, iden=iden)
