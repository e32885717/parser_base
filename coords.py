import sqlite3
import os
import json
import math


script_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_directory)

sqlite_path = "main.db"
database = sqlite3.connect(sqlite_path, check_same_thread=False)


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

def settasks(pos1, pos2):
  
    border1 = pos1.split(",")
    border1[0] = float(border1[0])
    border1[1] = float(border1[1])
    border2 = pos2.split(",")
    border2[0] = float(border2[0])
    border2[1] = float(border2[1])
    z = 17
    
    comment = ""

    projection = 0.0818191908426

    pixel_coords1 = from_geo_to_pixels(border1[0], border1[1], projection, z)
    pixel_coords2 = from_geo_to_pixels(border2[0], border2[1], projection, z)
    min_maxTileX = [int(min(pixel_coords1[0], pixel_coords2[0])), int(max(pixel_coords1[0], pixel_coords2[0]))]
    min_maxTileY = [int(min(pixel_coords1[1], pixel_coords2[1])), int(max(pixel_coords1[1], pixel_coords2[1]))]

    max_area = 25

    x_len = min_maxTileX[1] - min_maxTileX[0] + 1
    y_len = min_maxTileY[1] - min_maxTileY[0] + 1
    if x_len * y_len > 100000:
      ram_safe = True
    reqs_len = partition_rectangle_cnt(min_maxTileX[0], min_maxTileY[0], x_len, y_len, max_area)
    cur = database.cursor()
    cur.execute("INSERT INTO tasks (min_maxTileX, min_maxTileY, max_area) VALUES ((?),(?),(?))", (json.dumps(min_maxTileX), json.dumps(min_maxTileY), max_area))
    #
    cur.execute("SELECT max(id) FROM tasks")
    task_id = cur.fetchone()[0]

    database.commit()

    tiles_cnt = (min_maxTileX[1] - min_maxTileX[0] + 1) * (min_maxTileY[1] - min_maxTileY[0] + 1)
    print(f"{tiles_cnt} tiles")
    #
    step = 25
    
    for i in range(0, reqs_len, step):
      cur.execute("INSERT INTO subtasks (min_maxTileX, min_maxTileY, max_area, min_max_progress, parent_task, comment) VALUES (?,?,?,?,?,?)", (json.dumps(min_maxTileX), json.dumps(min_maxTileY), max_area, json.dumps([i, min(i + step, reqs_len)]), task_id, comment))
    cur.close()
    database.commit()

