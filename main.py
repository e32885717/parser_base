import db
from fastapi import Depends, FastAPI, Header
from pydantic import BaseModel
from typing import Annotated, Union
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
import string
import utils
import config
import uvicorn
from fastapi.responses import HTMLResponse

if config.use_orjson:
    from fastapi.responses import ORJSONResponse as JSONResponse
else:
    from fastapi.responses import JSONResponse

app = FastAPI()

app.router.route_class = utils.GzipRoute
version = 20
tokens = []

def generate_token(user_id):
    global tokens
    usr_tkns = [i["token"] for i in tokens if i["user_id"] == user_id]
    if len(usr_tkns) > 0:
        tk = usr_tkns[0]
    else:
        tk = "".join(random.choices(string.ascii_letters, k=40))
        tokens.append({"user_id": user_id, "token": tk})
        if len(tokens) > 30:
            tokens = tokens[20:30]
    return tk

def check_token(token):
    eq_tokens = [i["user_id"] for i in tokens if i["token"] == token]
    return eq_tokens[0] if len(eq_tokens) > 0 else None

def check_ua(ua):
    return (ua.find("3wifiparser1.") != -1)

@app.get("/auth", response_class=JSONResponse)
def auth(credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())], user_agent: Annotated[Union[str, None], Header()] = None):
    if check_ua(user_agent):
        return JSONResponse({"ok": False, "desc": "old version"}, status_code=403)
    u = db.get_user(credentials.username, credentials.password)
    if not(not(u)):
        return JSONResponse({"ok": True, "token": generate_token(u), "version": version})
    else:
        return JSONResponse({"ok": False, "desc": "auth failed", "version": version}, status_code=401)

@app.get("/getFreeTask", response_class=JSONResponse)
def getFreeTask(user_agent: Annotated[Union[str, None], Header()] = None):
    if check_ua(user_agent):
        return JSONResponse({"ok": False, "desc": "old version"}, status_code=403)
    t = db.get_free_subtask()
    if not(t):
        return JSONResponse({"ok": False, "desc": "no more tasks"}, status_code=404)
    return JSONResponse(t)

@app.get("/privateTask", response_class=JSONResponse)
def getFreeTask(task_id: int, token: str):
    usid = check_token(token)
    if usid == None:
        return JSONResponse({"ok": False, "desc": "wrong token"}, status_code=401)
    return JSONResponse(db.private_task(task_id, usid))

@app.get("/pingTask", response_class=JSONResponse)
def pingTask(task_id: int, token: str):
    usid = check_token(token)
    if usid == None:
        return JSONResponse({"ok": False, "desc": "wrong token"}, status_code=401)
    return JSONResponse(db.ping_task(task_id, usid))

class networks(BaseModel):
    result: list
    task_id: int
    token: str

@app.post("/closeTask", response_class=JSONResponse)
def closeTask(item: networks):
    usid = check_token(item.token)
    if usid == None:
        return JSONResponse({"ok": False, "desc": "wrong token"}, status_code=400)
    if not(db.get_task(item.task_id)):
        return JSONResponse({"ok": False, "desc": "wrong task id"}, status_code=400)
    ans = db.close_task(item.task_id, usid)
    if ans["ok"] != False:
        ans = db.load_networks(item.result, item.task_id, usid)
    else:
        return JSONResponse(ans, status_code=400)
    return JSONResponse(ans)

class anondata(BaseModel):
    data: list

@app.post("/anonymousUpload", response_class=JSONResponse)
def anonymousUpload(item: anondata):
    return JSONResponse(db.load_anonymous(item.data))

@app.get("/stats", response_class=utils.PrettyJSONResponse)
def stats():
    if config.use_orjson:
        return JSONResponse(db.get_stats())
    else:
        return utils.PrettyJSONResponse(db.get_stats())

@app.get("/stats.html", response_class=utils.PrettyJSONResponse)
def statspg():
    with open("stats.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.host, port=config.port, log_level="info")