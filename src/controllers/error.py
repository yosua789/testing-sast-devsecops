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



class Error(BaseController):
    @get("/404")
    def page_404(self):
        return self.view()
    
    @get("/403")
    def page_403(self):
        return self.view()

    




