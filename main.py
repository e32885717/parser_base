import db
from fastapi import Depends, FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Annotated, Union
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
import string
import utils

app = FastAPI()

app.router.route_class = utils.GzipRoute

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

def check_ua(ua):
    return (ua.find("3wifiparser1.") != -1)

@app.get("/auth", response_class=JSONResponse)
def auth(credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())], user_agent: Annotated[Union[str, None], Header()] = None):
    if check_ua(user_agent):
        return {"ok": False, "desc": "old version"}
    u = db.get_user(credentials.username, credentials.password)
    if not(not(u)):
        return JSONResponse({"ok": True, "token": generate_token(u)})
    else:
        return JSONResponse({"ok": False, "desc": "auth failed"})
    

@app.get("/getFreeTask", response_class=JSONResponse)
def getFreeTask(user_agent: Annotated[Union[str, None], Header()] = None):
    if check_ua(user_agent):
        return {"ok": False, "desc": "old version"}
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

class anondata(BaseModel):
    data: list

@app.post("/anonymousUpload", response_class=JSONResponse)
def anonymousUpload(item: anondata):
    db.load_anonymous(item.data)
    return JSONResponse({"ok": True})

@app.get("/stats", response_class=utils.PrettyJSONResponse)
def stats():
    return utils.PrettyJSONResponse(db.get_stats())