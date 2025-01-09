import os,jwt
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
from blacksheep import Application, Response, json
from blacksheep.cookies import Cookie

# from configuration import send_email

class Auth(BaseController):    
    @get('/')
    async def index(self):
        return os.getenv("MONGO_URI")

    # @get('/add-manual')
    # async def test(self):
        
    #     user = UserModel(name='admin',email='admin@app.com',password=sha256.encrypt('admin123'),role='Admin')
    #     if user.save() :
    #         return 'sukses'
    #     else:
    #         return 'gagal'
        
    
    @get('/login')
    async def login_page(self, user: Identity):
        cekUser = UserModel.objects.filter(email = "admin@app.com").first()

        if not cekUser:
            exe = UserModel(name='admin',email='admin@app.com',password=sha256.encrypt('admin123'),role='Admin')
            exe.save()

        if user:
            return redirect("/dashboard")

        return self.view()
    
    
    @post('/login')
    async def login_action(self, request: Request, data: FromForm[LoginUser],bs_message):
        getUser = UserModel.objects.filter(email=data.value.email).first()
        if not getUser:
            return {'status':400,'message':'Email not found'}

        secret = "dcd10e498fb0c76d1b41f7c748"

        if sha256.verify(data.value.password, getUser.password):
            beJwt = jwt.encode({"id":str(getUser.id),"name":getUser.name,"role":getUser.role}, secret, algorithm="HS256")
            response = json({'status':200,'message':'Success'})

            response.set_cookie(
                Cookie(
                    "Auth_AX",
                    beJwt,
                    http_only=True,
                    path="/",
                    expires=datetime.now() + timedelta(minutes=60),
                )
            )

            return response

        
        return {'status':400,'message':'Password not match'}
        

    # @auth('AuthUser')
    @get('/logout')
    async def logout(self,user:Identity,request: Request):
        response = json({'status':200,'message':'Success logout'})

        response.set_cookie(
                Cookie(
                    "Auth_AX",
                    "",
                    http_only=True,
                    path="/",
                    expires=datetime.now() + timedelta(minutes=60),
                )
            )

        return response

   