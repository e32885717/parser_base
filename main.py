import db
from fastapi import Depends, FastAPI, Header
from pydantic import BaseModel
#from typing import Annotated, Union
from typing import Tuple, Union
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
import string
import utils
import config
import uvicorn
from fastapi.responses import HTMLResponse
from coords import settasks


if config.allow_rsdump:
    from fastapi import File, UploadFile, Form
    import routerscan
    import zlib
    import os

if config.use_orjson:
    from fastapi.responses import ORJSONResponse as JSONResponse
else:
    from fastapi.responses import JSONResponse

app = FastAPI()

app.router.route_class = utils.GzipRoute
version = 20
security = HTTPBasic()
tokens = []

def random_str(n:int=40):
    return "".join(random.choices(string.ascii_letters, k=n))

def generate_token(user_id):
    global tokens
    usr_tkns = [i["token"] for i in tokens if i["user_id"] == user_id]
    if len(usr_tkns) > 0:
        tk = usr_tkns[0]
    else:
        tk = random_str()
        tokens.append({"user_id": user_id, "token": tk})
        if len(tokens) > 30:
            tokens = tokens[20:30]
    return tk

def check_token(token):
    eq_tokens = [i["user_id"] for i in tokens if i["token"] == token]
    return eq_tokens[0] if len(eq_tokens) > 0 else None

def check_ua(ua):
    if ua is not None:
        return (ua.find("3wifiparser1.") != -1)
    return False
###
@app.post("/register", response_class=JSONResponse)
async def register(username: str, password: str):
    # Перевірка чи існує користувач з таким ім'ям
    if db.get_user(username, password):
        raise BaseException(status_code=400, detail="Username already exists")

    # Реєстрація нового користувача
    db.gen_user(username, password)
    return JSONResponse({"ok": True, "message": "Registration successful"})
###

@app.get("/auth", response_class=JSONResponse)
def auth(credentials: HTTPBasicCredentials = Depends(security), user_agent: Union[str, None] = Header(default=None)):
#def auth(credentials: Annotated[HTTPBasicCredentials, Depends(HTTPBasic())], user_agent: Annotated[Union[str, None], Header()] = None):
    if check_ua(user_agent):
        return JSONResponse({"ok": False, "desc": "old version", "version": version}, status_code=403)
    u = db.get_user(credentials.username, credentials.password)
    if not(not(u)):
        return JSONResponse({"ok": True, "token": generate_token(u), "version": version})
    else:
        return JSONResponse({"ok": False, "desc": "auth failed", "version": version}, status_code=401)

@app.get("/getFreeTask", response_class=JSONResponse)
def getFreeTask(user_agent: Union[str, None] = None):
#def getFreeTask(user_agent: Annotated[Union[str, None], Header()] = None):
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

@app.get("/stats.html", response_class=HTMLResponse)
def statspg():
    with open("stats.html", "r", encoding="utf-8") as f:
        return f.read()

if config.allow_rsdump:
    @app.post("/routerscan", response_class=JSONResponse)
    async def routerscanpost(ftype:str = Form(media_type="multipart/form-data"), data:UploadFile=File(...), content_length: Annotated[Union[int, None], Header()] = None):
        if content_length > 1024 * 1024:
            return JSONResponse({"ok": False, "desc": "too big file"}, status_code=400)
        if ftype not in ["csv", "json"]:
            return JSONResponse({"ok": False, "desc": "wrong format"}, status_code=400)
        fname = f"tmp_{random_str(20)}.{ftype}"
        try:
            if ftype == "json":
                with open("temp/gzip/" +  fname + ".gz", "wb") as gzf:
                    content = await data.read()
                    gzf.write(zlib.compress(content, level=5, wbits=31))
            else:
                with open("temp/" + fname, "wb") as f:
                    with open("temp/gzip/" +  fname + ".gz", "wb") as gzf:
                        content = await data.read()
                        f.write(content)
                        gzf.write(zlib.compress(content, level=5, wbits=31))
                        #while content := await data.read(1024 * 64):
                        #    f.write(content)
        except:
            return JSONResponse({"ok": False, "desc": "file write server error"}, status_code=500)
        if ftype == "csv":
            res = routerscan.parse_csv("temp/" + fname)
            os.remove("temp/" + fname)
        elif ftype == "json":
            res = routerscan.parse_json(content)
        if res.ok:
            return JSONResponse({"ok": True})
        else:
            return JSONResponse({"ok": False, "desc": res.desc}, status_code=400)
else:
    @app.post("/routerscan", response_class=JSONResponse)
    async def routerscanpost():
        return JSONResponse({"ok": False, "desc": "Forbidden"}, status_code=403)

@app.get("/routerscan.html", response_class=HTMLResponse)
def routerscanpg():
    if not(config.allow_rsdump):
        return JSONResponse({"ok": False, "desc": "Forbidden"}, status_code=403)
    with open("routerscan.html", "r", encoding="utf-8") as f:
        return f.read()

###

@app.get("/coords.html", response_class=utils.PrettyJSONResponse)
def coords():
    with open("coords.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())



class Coords(BaseModel):
    token: str
    pos1: str
    pos2: str

@app.post("/setcoords", response_class=JSONResponse)
async def handle_data(item: Coords):
    # Отримання даних з моделі item
    token = item.token
    pos1 = item.pos1
    pos2 = item.pos2
    
    usid = check_token(token)
    if usid == None:
        return JSONResponse({"ok": False, "desc": "wrong token"}, status_code=401)
    #
    settasks(pos1, pos2)
  
    req = {"ok": True, "message": "Coordinates received successfully", "token": token, "pos1": pos1, "pos2": pos2}
    #print(req)
    return JSONResponse(req)
    
###
if __name__ == "__main__":
    uvicorn.run("main:app", host=config.host, port=config.port, log_level="info")
