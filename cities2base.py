import json
import math
import tqdm
import sqlite3

base_path = input("Укажите путь до базы данных: ")

database = sqlite3.connect(base_path)

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

def partition_rectangle(x, y, width, height, max_area, rects=None):
    if rects is None:
        rects = []
    if width * height <= max_area:
        rects.append((x, y, x + width, y + height))
    else:
        if width > height:
            half_width = width // 2
            partition_rectangle(x, y, half_width, height, max_area, rects)
            partition_rectangle(x + half_width, y, width - half_width, height, max_area, rects)
        else:
            half_height = height // 2
            partition_rectangle(x, y, width, half_height, max_area, rects)
            partition_rectangle(x, y + half_height, width, height - half_height, max_area, rects)
    return rects

step = 20 # requests in subtask
max_area = 20 # max tiles in 1 request
projection = 0.0818191908426

many_tasks = len(cities) > 100
iter_obj = tqdm.tqdm(cities) if many_tasks else cities

for city in iter_obj:
    c = cities[city]
    pixel_coords1 = from_geo_to_pixels(c["ma_x"], c["ma_y"], projection, 17)
    pixel_coords2 = from_geo_to_pixels(c["mi_x"], c["mi_y"], projection, 17)
    min_maxTileX = [int(min(pixel_coords1[0], pixel_coords2[0])), int(max(pixel_coords1[0], pixel_coords2[0]))]
    min_maxTileY = [int(min(pixel_coords1[1], pixel_coords2[1])), int(max(pixel_coords1[1], pixel_coords2[1]))]
    tiles_cnt = (min_maxTileX[1] - min_maxTileX[0] + 1) * (min_maxTileY[1] - min_maxTileY[0] + 1)
    print(f"Need to scan {tiles_cnt} tiles")
    x_len = min_maxTileX[1] - min_maxTileX[0] + 1
    y_len = min_maxTileY[1] - min_maxTileY[0] + 1
    reqs = partition_rectangle(min_maxTileX[0], min_maxTileY[0], x_len, y_len, max_area)
    cur = database.cursor()
    cur.execute("SELECT max(id) FROM tasks")
    task_id = cur.fetchone() + 1
    cur.close()
    database.execute("INSERT INTO tasks (min_maxTileX, min_maxTileY, max_area) VALUES (?,?,?)", (json.dumps(min_maxTileX), json.dumps(min_maxTileY), max_area))
    reqs_len = len(reqs)
    iter_obj1 = range(0, reqs_len, step) if many_tasks else tqdm.tqdm(range(0, reqs_len, step))
    for i in iter_obj1:
        data = (json.dumps(min_maxTileX), json.dumps(min_maxTileY), max_area, json.dumps([i, min(i + step, reqs_len)]), task_id[0], c["name"])
        database.execute("INSERT INTO subtasks (min_maxTileX, min_maxTileY, max_area, min_max_progress, parent_task, comment) VALUES (?,?,?,?,?,?)", data)
    database.commit()