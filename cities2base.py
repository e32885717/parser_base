import json
import math
import tqdm
import sqlite3
ext_mode = False
try:
    import db
except:
    ext_mode = True

if ext_mode:
    base_path = input("Укажите путь до базы данных: ")
    database = sqlite3.connect(base_path)
else:
    database = db.database

file_path = input("Укажите путь к файлу: ")

with open(file_path, "r", encoding="utf-8") as f:
    cities = json.load(f)

def from_geo_to_pixels(lat, long, projection, z):
    rho = math.pow(2, z + 8) / 2
    beta = lat * math.pi / 180
    phi = (1 - projection * math.sin(beta)) / (1 + projection * math.sin(beta))
    theta = math.tan(math.pi / 4 + beta / 2) * math.pow(phi, projection / 2)
    x_p = rho * (1 + long / 180)
    y_p = rho * (1 - math.log(theta) / math.pi)
    return [x_p // 256, y_p // 256]

def partition_rectangle_cnt(x, y, width, height, max_area):
    number = 0
    if width * height <= max_area:
        number += 1
    else:
        if width > height:
            half_width = width // 2
            number += partition_rectangle_cnt(x, y, half_width, height, max_area)
            number += partition_rectangle_cnt(x + half_width, y, width - half_width, height, max_area)
        else:
            half_height = height // 2
            number += partition_rectangle_cnt(x, y, width, half_height, max_area)
            number += partition_rectangle_cnt(x, y + half_height, width, height - half_height, max_area)
    return number

step = 20 # requests in subtask
max_area = 20 # max tiles in 1 request to 3wifi
projection = 0.0818191908426

many_tasks = len(cities) > 100
iter_obj = tqdm.tqdm(cities) if many_tasks else cities

for c in iter_obj:
    pixel_coords1 = from_geo_to_pixels(c["ma_x"], c["ma_y"], projection, 17)
    pixel_coords2 = from_geo_to_pixels(c["mi_x"], c["mi_y"], projection, 17)
    min_maxTileX = [int(min(pixel_coords1[0], pixel_coords2[0])), int(max(pixel_coords1[0], pixel_coords2[0]))]
    min_maxTileY = [int(min(pixel_coords1[1], pixel_coords2[1])), int(max(pixel_coords1[1], pixel_coords2[1]))]
    tiles_cnt = (min_maxTileX[1] - min_maxTileX[0] + 1) * (min_maxTileY[1] - min_maxTileY[0] + 1)
    print(f"Need to scan {tiles_cnt} tiles")
    x_len = min_maxTileX[1] - min_maxTileX[0] + 1
    y_len = min_maxTileY[1] - min_maxTileY[0] + 1
    reqs_len = partition_rectangle_cnt(min_maxTileX[0], min_maxTileY[0], x_len, y_len, max_area)
    cur = database.cursor()
    cur.execute("INSERT INTO tasks (min_maxTileX, min_maxTileY, max_area) VALUES (?,?,?);", (json.dumps(min_maxTileX), json.dumps(min_maxTileY), max_area))
    cur.execute("SELECT max(id) FROM tasks;")
    task_id = cur.fetchone()[0]
    iter_obj1 = range(0, reqs_len, step) if many_tasks else tqdm.tqdm(range(0, reqs_len, step))
    for i in iter_obj1:
        data = (f"[{min_maxTileX[0]},{min_maxTileX[1]}]", f"[{min_maxTileY[0]},{min_maxTileY[1]}]", max_area, f"[{i},{min(i + step, reqs_len)}]", task_id, c["name"])
        cur.execute("INSERT INTO subtasks (min_maxTileX, min_maxTileY, max_area, min_max_progress, parent_task, comment) VALUES (?,?,?,?,?,?)", data)
    cur.close()
    database.commit()