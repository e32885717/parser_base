import json
import math
import tqdm
import sqlite3

database = sqlite3.connect("main.db")

with open("cities.json", "r", encoding="utf-8") as f:
    cities = json.load(f)

def from_geo_to_pixels(lat, long, projection, z):
    rho = math.pow(2, z + 8) / 2
    beta = lat * math.pi / 180
    phi = (1 - projection * math.sin(beta)) / (1 + projection * math.sin(beta))
    theta = math.tan(math.pi / 4 + beta / 2) * math.pow(phi, projection / 2)
    x_p = rho * (1 + long / 180)
    y_p = rho * (1 - math.log(theta) / math.pi)
    return [x_p // 256, y_p // 256]

for city in cities:
    c = cities[city]
    projection = 0.0818191908426
    pixel_coords1 = from_geo_to_pixels(c["ma_x"], c["ma_y"], projection, 17)
    pixel_coords2 = from_geo_to_pixels(c["mi_x"], c["mi_y"], projection, 17)
    min_maxTileX = [int(min(pixel_coords1[0], pixel_coords2[0])), int(max(pixel_coords1[0], pixel_coords2[0]))]
    min_maxTileY = [int(min(pixel_coords1[1], pixel_coords2[1])), int(max(pixel_coords1[1], pixel_coords2[1]))]
    tiles_cnt = (min_maxTileX[1] - min_maxTileX[0] + 1) * (min_maxTileY[1] - min_maxTileY[0] + 1)
    print(f"Need to scan {tiles_cnt} tiles")
    database.execute("INSERT INTO tasks (min_maxTileX, min_maxTileY) VALUES (?,?)", (json.dumps(min_maxTileX), json.dumps(min_maxTileY)))
    database.commit()
    cur = database.cursor()
    cur.execute("SELECT max(id) FROM tasks")
    task_id = cur.fetchone()
    cur.close()
    for i in tqdm.tqdm(range(0, tiles_cnt, 300)):
        database.execute("INSERT INTO subtasks (min_maxTileX, min_maxTileY, min_max_progress, parent_task, comment) VALUES (?,?,?,?,?)", (json.dumps(min_maxTileX), json.dumps(min_maxTileY), json.dumps([i, min(i + 300, tiles_cnt)]), task_id[0], c["name"]))
    database.commit()