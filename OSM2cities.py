import json
import tqdm

osm_file = input("Укажите путь до файлика с ответом от overpass api: ")

with open(osm_file, 'r', encoding="utf-8") as inFile:
    j = json.load(inFile)

places = {}
ids = {}
relations = {}

for i, elem in enumerate(j['elements']):
    ids[str(elem['id'])] = i
    if 'tags' in elem and 'place' in elem['tags'] and elem['tags']['place'] in ['city', 'town', 'village']:
        pop = 0
        if 'population' in elem['tags']:
            try:
                pop = int(elem['tags'].get('population'))
            except:
                try:
                    pop = int(elem['tags'].get('population').split()[0])
                except:
                    try:
                        pop = int(elem['tags'].get('population').split()[1])
                    except:
                        pop = 0
        else:
            pop = 0
        rel_id = elem['id'] if 'members' in elem else None
        if 'members' in elem:
            relations[str(elem['id'])] = elem
        if elem.get("type") == "way":
            rel_id = "way" + str(elem['id'])
            relations[str(elem['id'])] = elem["nodes"]
        places[str(elem['id'])] = {
            'name': elem['tags'].get('name', ''),
            'relation_id': rel_id,
            'population': pop,
            'ma_x': 0,
            'ma_y': 0,
            'mi_x': 180,
            'mi_y': 180
        }


for place_id, place in places.items():
    if place['relation_id'] is None:
        continue
    ma_x, mi_x, ma_y, mi_y = 0, 180, 0, 180
    if str(place['relation_id']).startswith("way"):
        elem1 = relations[str(place['relation_id'][3:])]
    else:
        for i in relations[str(place['relation_id'])]['members']:
            if i['type'] == 'way' and i['role'] == 'outer':
                elem1 = j['elements'][ids[str(i['ref'])]]['nodes']
    for node_in in elem1:
        try:
            elem2 = j['elements'][ids[str(node_in)]]
            ma_x = max(ma_x, elem2['lat'])
            mi_x = min(mi_x, elem2['lat'])
            ma_y = max(ma_y, elem2['lon'])
            mi_y = min(mi_y, elem2['lon'])
        except:
            pass      
    place['ma_x'] = ma_x
    place['mi_x'] = mi_x
    place['ma_y'] = ma_y
    place['mi_y'] = mi_y
    print(f"Найден - {place['name']}")

def is_invalid(entry):
    return (
        len(entry["name"]) == 0 or
        entry.get("ma_x", 0) == 0 or
        entry.get("ma_y", 0) == 0 or
        entry.get("mi_x", 0) == 180 or
        entry.get("mi_y", 0) == 180
    )

with open('parsed_osm.json', 'w', encoding="utf-8") as outFile:
    places = [value for key, value in places.items() if not is_invalid(value)]
    places.sort(key=lambda x: x["population"], reverse=True)
    json.dump(places, outFile, indent=4, ensure_ascii=False)
    print("Сохраненно в parsed_osm.json")
    print("Чтобы добавить получившиеся задания в базу используйте скрипт cities2base.py")
input("End")