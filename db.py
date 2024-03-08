import time
import config
import hashlib
import random
import salt
if config.use_bcrypt:
    import bcrypt
import db_structure

if config.use_mariadb:
    import mariadb
    database = mariadb.connect(user=config.maria_creds["user"], password=config.maria_creds["password"], host=config.maria_creds["host"], port=config.maria_creds["port"])
    cur = database.cursor()
    act = db_structure.mariadb_initcmd.split(";")
    for i in act:
        if len(i) != 0:
            cur.execute(i)
    if config.allow_rsdump:
        cur.execute(db_structure.mariadb_rsdump)
    cur.close()
else:
    import sqlite3
    database = sqlite3.connect(config.sqlite_path, check_same_thread=False)
    cur = database.cursor()
    cur.executescript(db_structure.sqlite_initcmd)
    if config.allow_rsdump:
        cur.executescript(db_structure.sqlite_rsdump)
    cur.close()

def get_user(user: str, passw: str):
    try:
        cur = database.cursor()
        password_salt = (passw + salt.generate_user_salt(user + "@" + passw)).encode()
        passhash = hashlib.sha512(password_salt).digest()
        cur.execute("SELECT id,password FROM users WHERE login=?", (user, ))
        d = cur.fetchone()
        cur.close()
    except:
        return None
    if d == None:
        return None
    passfromdb = d[1].encode() if isinstance(d[1], str) else d[1]
    if config.use_bcrypt:
        password_eq = bcrypt.checkpw(passhash, passfromdb)
    else:
        password_eq = (passhash == passfromdb)
    if password_eq:
        return d[0]
    else:
        return None

def gen_user(user, passw):
    cur = database.cursor()
    passhash = hashlib.sha512((passw + salt.generate_user_salt(user + "@" + passw)).encode()).digest()
    hashed = bcrypt.hashpw(passhash, bcrypt.gensalt())
    sql_or = "" if config.use_mariadb else " OR"
    cur.execute(f"INSERT{sql_or} IGNORE INTO users VALUES (?,?,?)", (random.getrandbits(16), user, hashed))
    cur.close()
    database.commit()

def get_free_subtask():
    try:
        cur = database.cursor()
        close_dead_tasks(cur)
        database.commit()
        cur.execute("SELECT * FROM subtasks WHERE processing_by IS NULL LIMIT 1")
        d = cur.fetchone()
        cur.close()
    except:
        return {"ok": False, "desc": "database err"}
    if not(d):
        return d
    cd = db_structure.stdescription if config.use_mariadb else cur.description
    ans = {"ok": True, "data": dict(zip([i[0] for i in cd], d))}
    return ans

def get_task(task_id):
    try:
        cur = database.cursor()
        close_dead_tasks(cur)
        database.commit()
        cur.execute("SELECT * FROM subtasks WHERE id=?", (task_id, ))
        d = cur.fetchone()
        cur.close()
    except:
        return {"ok": False, "desc": "database err"}
    if not(d):
        return d
    cd = db_structure.stdescription if config.use_mariadb else cur.description
    ans = dict(zip([i[0] for i in cd], d))
    ans["ok"] = True
    return ans

def private_task(task_id, user_id):
    task = get_task(task_id)
    if not(task):
        return {"ok": False, "desc": "invalid task id"}
    if task["processing_by"] != None:
        return {"ok": False, "desc": "task privated"}
    try:
        cur = database.cursor()
        cur.execute("UPDATE subtasks SET processing_by=?, last_ping=?, progress=0 WHERE id=?", (user_id, int(time.time()), task_id))
        cur.close()
        database.commit()
    except:
        return {"ok": False, "desc": "database err"}
    return {"ok": True}

def ping_task(task_id, user_id):
    cur = database.cursor()
    close_dead_tasks(cur)
    task = get_task(task_id)
    if not(task):
        return {"ok": False, "desc": "invalid task id"}
    if task["processing_by"] == None:
        return {"ok": False, "desc": "task is free"}
    if int(task["processing_by"]) != int(user_id):
        return {"ok": False, "desc": "no rights"}
    if int(task["last_ping"]) == -1:
        return {"ok": False, "desc": "task completed"}
    try:
        cur.execute("UPDATE subtasks SET last_ping=? WHERE id=?", (int(time.time()), task_id))
        cur.close()
        database.commit()
    except:
        cur.close()
        return {"ok": False, "desc": "database err"}
    return {"ok": True}

def close_task(task_id, user_id):
    task = get_task(task_id)
    if not(task):
        return {"ok": False, "desc": "invalid task id"}
    if task["processing_by"] == None or task["progress"] == -1:
        return {"ok": False, "desc": "task is free"}
    if int(task["processing_by"]) != int(user_id):
        return {"ok": False, "desc": "no rights"}
    try:
        cur = database.cursor()
        cur.execute("UPDATE subtasks SET last_ping=-1, progress=-1 WHERE id=?", (task_id, ))
        cur.close()
        database.commit()
    except:
        return {"ok": False, "desc": "database err"}
    return {"ok": True}

def load_networks(networks: list, task_id: int, user_id: int):
    if len(networks) > 0:
        if len(networks[0]) != 9:
            return {"ok": False, "desc": "wrong arr length"}
    try:
        cur = database.cursor()
        user_id = int(user_id)
        task_id = int(task_id)
        cur.executemany(f"INSERT INTO networks VALUES (?,?,?,?,?,?,?,?,?,{task_id},{user_id},{int(time.time())})", networks)
        cur.close()
        database.commit()
    except:
        return {"ok": False, "desc": "database err"}
    return {"ok": True}

def load_anonymous(networks: list):
    if len(networks) > 0:
        if len(networks[0]) != 9:
            return {"ok": False, "desc": "wrong arr length"}
    try:
        cur = database.cursor()
        cur.executemany(f"INSERT INTO anonymous_data VALUES (?,?,?,?,?,?,?,?,?,{int(time.time())})", networks)
        cur.close()
        database.commit()
    except:
        return {"ok": False, "desc": "database err"}
    return {"ok": True}

def close_dead_tasks(cur=None):
    with_cur = (cur is None)
    if with_cur:
        cur = database.cursor()
    cur.execute("UPDATE subtasks SET processing_by=NULL, last_ping=NULL, progress=NULL WHERE last_ping IS NOT NULL AND last_ping!=-1 AND last_ping < (?)", (int(time.time()) - config.task_delete_timeout, ))
    if with_cur:
        cur.close()
        database.commit()

stats_cache = None
stats_cache_time = 0

def get_stats():
    global stats_cache, stats_cache_time
    if time.time() - stats_cache_time < 10:
        return stats_cache
    cur = database.cursor()
    cur.execute("SELECT count(*) FROM networks;")
    nets = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM subtasks;")
    subtasks = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM subtasks WHERE last_ping=-1;")
    completed_subtasks = cur.fetchone()[0]
    cur = cur.close()
    percent = (completed_subtasks * 10000 // subtasks) / 100 if subtasks != 0 else 0
    stats_cache = {
        "networks": nets,
        "subtasks": subtasks,
        "completed": completed_subtasks,
        "percent": percent
    }
    if config.user_stats:
        stats_cache["users"] = get_user_stats()
    stats_cache_time = time.time()
    return stats_cache

ustats_cache = None
ustats_cache_time = 0

def get_user_stats():
    global ustats_cache, ustats_cache_time
    if time.time() - ustats_cache_time < 60:
        return ustats_cache
    cur = database.cursor()
    cur.execute("SELECT id,login FROM users;")
    users = cur.fetchall()
    ustats_cache = {}
    for user in users:
        cur.execute("SELECT count(*) FROM networks WHERE scanned_by=?", (user[0], ))
        ustats_cache[user[1]] = cur.fetchone()[0]
    cur.close()
    ustats_cache_time = time.time()
    return ustats_cache