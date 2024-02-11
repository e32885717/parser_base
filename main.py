import db
from fastapi import Depends, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Annotated
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
import string
import zlib
from typing import Callable
from fastapi.routing import APIRoute

app = FastAPI()


class GzipRequest(Request):
    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = await super().body()
            if "gzip" in self.headers.getlist("Content-Encoding"):
                body = zlib.decompress(body)
            self._body = body
        return self._body


class GzipRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request = GzipRequest(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler

app.router.route_class = GzipRoute

security = HTTPBasic()
tokens = []

def generate_token(user_id):
    global tokens
    tk = ''.join(random.choices(string.ascii_letters, k=40))
    tokens.append({"user_id": user_id, "token": tk})
    if len(tokens) > 30:
        tokens = tokens[20:30]
    return tk

def check_token(token):
    for i in tokens:
        if i["token"] == token:
            return i["user_id"]
    return None

@app.get("/auth", response_class=JSONResponse)
def auth(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    u = db.get_user(credentials.username, credentials.password)
    if not(not(u)):
        return JSONResponse({"ok": True, "token": generate_token(u)})
    else:
        return JSONResponse({"ok": False, "desc": "auth failed"})
    

@app.get("/getFreeTask", response_class=JSONResponse)
def getFreeTask():
    t = db.get_free_subtask()
    if not(t):
        return JSONResponse({"ok": False, "desc": "no more tasks"})
    return JSONResponse({"ok": True, "data": t})

@app.get("/privateTask", response_class=JSONResponse)
def getFreeTask(task_id: int, token: str):
    usid = check_token(token)
    if usid == None:
        return JSONResponse({"ok": False, "desc": "wrong token"})
    return JSONResponse(db.private_task(task_id, usid))

@app.get("/pingTask", response_class=JSONResponse)
def pingTask(task_id: int, token: str, progress: int):
    usid = check_token(token)
    if usid == None:
        return JSONResponse({"ok": False, "desc": "wrong token"})
    return JSONResponse(db.ping_task(task_id, usid, progress))

class networks(BaseModel):
    result: list
    task_id: int
    token: str


@app.post("/closeTask", response_class=JSONResponse)
def closeTask(item: networks):
    usid = check_token(item.token)
    if usid == None:
        return JSONResponse({"ok": False, "desc": "wrong token"})
    if not(db.get_task(item.task_id)):
        return JSONResponse({"ok": False, "desc": "wrong task id"})
    ans = db.close_task(item.task_id, usid)
    if ans["ok"] != False:
        db.load_networks(item.result, item.task_id, usid)
    return JSONResponse(ans)