import os
import asyncio
from controllers import *
from typing import Optional, Any
from blacksheep import Application, Request, Response, JSONContent
from blacksheep.server.authorization import Policy
from guardpost.asynchronous.authentication import AuthenticationHandler, Identity
from guardpost.common import AuthenticatedRequirement
from guardpost.authorization import AuthorizationContext, UnauthorizedError
from guardpost.synchronous.authorization import Requirement
from blacksheep.server.responses import redirect
from blacksheep.server.templating import use_templates
from jinja2 import FileSystemLoader
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from models import *

from controllers.core.engine import GoaccessEngine

# from sdk.engine import *
if not os.getenv('PRODUCTION'):
    app = Application(show_error_details=True, debug=True)
    print('LOAD DEVELOPMENT')
else:
    app = Application()
    print('LOAD PRODUCTION')

    
app.serve_files("UI/assets")
app.use_sessions(os.urandom(32), session_cookie="kecilin_web")
use_templates(app, loader=FileSystemLoader("UI/views"))
scheduler = AsyncIOScheduler()


@app.router.get("/")
def index():
    return redirect("/auth/login")

redirect_url = "/"

class AuthHandler(AuthenticationHandler):
    def __init__(self):
        pass

    async def authenticate(self, context: Request) -> Optional[Identity]:
        def iden_none():
            redirect_url = "/auth/login"
            context.identity = None

        global redirect_url
        try:
            jwtVal = context.cookies['Auth_AX']
            secret = "dcd10e498fb0c76d1b41f7c748"
            if jwtVal:
                jwtDec = jwt.decode(jwtVal, secret, algorithms=["HS256"])
                cekId = UserModel.objects.filter(id=jwtDec['id']).first()
                if not cekId:
                    iden_none()
                else:
                    if cekId.name != jwtDec['name']:
                        iden_none()
                    else:
                        context.identity = Identity({"name" : jwtDec['name'],  "id" : jwtDec['id'], "role" : jwtDec['role']}, "KecilinKloud")
            else:
                iden_none()
        except Exception as e:
            iden_none()
        
        return context.identity

class AuthChecker(Requirement):
     def handle(self, context: AuthorizationContext):
        global redirect_url
        identity = context.identity

        if identity is not None:
            context.succeed(self)
        

class VerifiedPolicy(Policy):
    def __init__(self):
        super().__init__("AuthUser", AuthChecker())


async def handle_unauthorized(app: Any, request: Request, http_exception: UnauthorizedError) -> Response:
    global redirect_url
    return redirect(redirect_url)

async def handle_404(app: Any, request: Request, http_exception: 404) -> Response:
    return Response(404, content=JSONContent({"status": 404, "message" : "404 not found"}))

async def start_app(application: Application) -> None:
    print("Scheduler read log is start")
    go  = GoaccessEngine()
    scheduler.add_job(go.run, 'interval', seconds=go.duration)
    scheduler.start()

async def stop_app(application: Application) -> None:
    print("Scheduler Stop")
    scheduler.shutdown(wait=True)

async def add_path(application:Application)-> None:
    print("Start add path docker yaml")
    go = GoaccessEngine()
    go.insertDockerYAMLPath()


app.use_authentication().add(AuthHandler())
app.use_authorization().add(Policy("authenticated", AuthenticatedRequirement())).add(VerifiedPolicy())
app.exceptions_handlers[UnauthorizedError] = handle_unauthorized
app.exceptions_handlers[404] = handle_404

app.on_start += add_path
app.on_start += start_app
app.on_stop += stop_app



