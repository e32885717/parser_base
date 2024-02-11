import sqlite3
import config
import json
from tqdm import tqdm

database = sqlite3.connect(config.sqlite_path, check_same_thread=False)

task_id = input("task_id: ")

cur = database.cursor()
cur.execute("SELECT * FROM tasks WHERE id=?", (task_id, ))
task = cur.fetchone()
cur.close()

if task == None:
    raise Exception("WRONG TASK ID")
min_maxTileX = json.loads(task[1])
min_maxTileY = json.loads(task[2])
tiles_cnt = (min_maxTileX[1] - min_maxTileX[0] + 1) * (min_maxTileY[1] - min_maxTileY[0] + 1)
print(f"{tiles_cnt} tiles")
for i in tqdm(range(0, tiles_cnt, 300)):
    database.execute("INSERT INTO subtasks (min_maxTileX, min_maxTileY, min_max_progress, parent_task) VALUES (?,?,?,?)", (task[1], task[2], json.dumps([i, min(i + 300, tiles_cnt)]), task_id))
database.commit()
input("a")