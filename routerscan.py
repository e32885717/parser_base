import csv
import db
import rsutils.sec
import re
import config

if config.use_orjson:
    import orjson as json
else:
    import json

std_struct = ['IP Address', 'Port', 'Time (ms)', 'Status', 'Authorization', 'Server name / Realm name / Device type', 'Radio Off', 'Hidden', 'BSSID', 'ESSID', 'Security', 'Key', 'WPS PIN', 'LAN IP Address', 'LAN Subnet Mask', 'WAN IP Address', 'WAN Subnet Mask', 'WAN Gateway', 'Domain Name Servers', 'Latitude', 'Longitude', 'Comments']
std_len = len(std_struct)

maria_str = " ON DUPLICATE KEY UPDATE time=current_timestamp()" if config.use_mariadb else ""
sqlite_str = "" if config.use_mariadb else "OR IGNORE "
insert_query = f"INSERT {sqlite_str}INTO rsdump (IP, Port, status, Authorization, name, RadioOff, Hidden, BSSID, ESSID, Security, WiFiKey, WPSPIN, LANIP, LANMask, WANIP, WANMask, WANGateway, DNS1, DNS2, DNS3, Comments) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?){maria_str};"

    
class ParsingOutput:
    def __init__(self, ok:bool=True, data:list=None, desc:str="") -> None:
        self.ok = ok
        self.data = data
        self.desc = desc
    ok:bool=True
    data:list=None
    desc:str=""

def check_rs_codes(st):
    if st == "<bridge>":
        return True
    return False

def ip2int(st):
    if check_rs_codes(st):
        return None
    d1 = st.split(".")
    d2 = [int(i).to_bytes(1) for i in d1]
    d3 = b"".join(d2)
    return int.from_bytes(d3, signed=True)


def bssid2int(bss):
    sys_val = 0xFFFFFFFFFFFF + 1
    if bss is None:
        return sys_val
    bss = str(bss)
    if bss == "<none>" or bss.strip() == "" or bss == "<no wireless>":
        return sys_val
    elif bss == "<access denied>":
        return sys_val + 1
    elif bss == "<not accessible>":
        return sys_val + 2
    elif bss == "<not implemented>":
        return sys_val + 3
    return int(bss.replace(":", ""), 16)

def dec2mac(n):
    he = hex(n)[2:]
    he = ("0" * (12 - len(he))) + he
    he = f"{he[0:2]}:{he[2:4]}:{he[4:6]}:{he[6:8]}:{he[8:10]}:{he[10:12]}"
    return he

def bssid2str(bssid):
    if bssid is None:
        return "<none>"
    sys_val = 0xFFFFFFFFFFFF + 1
    if bssid < sys_val:
        return dec2mac(bssid)
    elif bssid == sys_val:
        return "<none>"
    elif bssid == sys_val + 1:
        return "<access denied>"
    elif bssid == sys_val + 2:
        return "<not accessible>"
    elif bssid == sys_val + 3:
        return "<not implemented>"
    return "<unknown value>"

def wps2int(st):
    st = re.sub(r'\D+', "", st)
    if st == "":
        return None
    try:
        return int(st)
    except:
        return None

def parse_csv(dump_file):
    fr = True
    with open(dump_file, "r", encoding="windows-1251") as f:
        reader = csv.reader(f, delimiter=";")
        for row in reader:
            if fr:
                fr = False
                if row != std_struct:
                    return ParsingOutput(ok=False, desc="Bad structure")
                else:
                    continue
            if len(row) != std_len:
                return ParsingOutput(ok=False, desc="Wrong row len")
            if row[3] == "Can't load main page":
                continue
            if row[8] == "<no wireless>" and row[4] == "":
                continue
            if row[8] == "" and row[9] == "" and row[4] == "":
                continue
            psd_row = []
            psd_row.append(ip2int(row[0])) #IP
            psd_row.append(int(row[1])) #PORT
            psd_row.append(row[3] if row[3] != "" else None) #STATUS
            psd_row.append(row[4] if row[4] != "" else None) #AUTH
            psd_row.append(row[5] if row[5] != "" else None) #NAME
            psd_row.append(1 if row[6] == "[X]" else 0) #RADIOOFF
            psd_row.append(1 if row[7] == "[X]" else 0) #HIDDEN
            psd_row.append(bssid2int(row[8])) #BSSID
            psd_row.append(row[9] if row[9] != "" else "<none>") #SSID
            psd_row.append(rsutils.sec.str2sec(row[10])) #SECURITY
            psd_row.append(row[11] if row[11] != "" else "<none>") #KEY
            psd_row.append(wps2int(row[12]) if row[12] != "" else 0xFFFFFFFF) #WPS
            psd_row.append(ip2int(row[13]) if row[13] != "" else None) #LANIP
            psd_row.append(ip2int(row[14]) if row[14] != "" else None) #LANSUBNET
            psd_row.append(ip2int(row[15]) if row[15] != "" else None) #WANIP
            psd_row.append(ip2int(row[16]) if row[16] != "" else None) #WANSUB
            psd_row.append(ip2int(row[17]) if row[17] != "" else None) #WANGATE
            dns = []
            if row[18] != "":
                for i in row[18].split(" "):
                    if len(dns) >= 3:
                        break
                    dns.append(ip2int(i))
            for i in range(3):
                psd_row.append(dns[i] if i < len(dns) else None)
            psd_row.append(row[20] if row[20] != "" else None)
            write_sql_row(psd_row)
        db.database.commit()
    return ParsingOutput(ok=True)


def parse_json(data):
    try:
        data = json.loads(data).get("table")
    except:
        return ParsingOutput(ok=False, desc="JSON parse error")
    if data is None or data == {} or data == []:
        return ParsingOutput(ok=False, desc="Bad structure")
    for row in data:
        if not("ip" in row and "port" in row and "status" in row):
            return ParsingOutput(ok=False, desc="Bad row structure")
        if row["status"] == "Can't load main page":
            continue
        if row.get("bssid") == "<no wireless>" and not("auth" in row):
            continue
        if not("bssid" in row) and not("ssid" in row) and not("auth" in row):
            continue
        psd_row = []
        psd_row.append(ip2int(row["ip"])) #IP
        psd_row.append(int(row["port"])) #PORT
        psd_row.append(row["status"] if ("status" in row) else None) #STATUS
        psd_row.append(row["auth"] if ("auth" in row) else None) #AUTH
        psd_row.append(row["type"] if ("type" in row) else None) #NAME
        psd_row.append(1 if (row.get("radiooff") == True) else 0) #RADIOOFF
        psd_row.append(1 if (row.get("hidden") == True) else 0) #HIDDEN
        psd_row.append(bssid2int(row.get("bssid"))) #BSSID
        psd_row.append(row["ssid"] if ("ssid" in row) else "<none>") #SSID
        psd_row.append(rsutils.sec.str2sec(row.get("sec")) if "sec" in row else None) #SECURITY
        psd_row.append(row["key"] if ("key" in row) else "<none>") #KEY
        psd_row.append(wps2int(row.get("wps")) if ("wps" in row) else 0xFFFFFFFF) #WPS
        psd_row.append(ip2int(row.get("lanip")) if ("lanip" in row) else None) #LANIP
        psd_row.append(ip2int(row.get("lanmask")) if ("lanmask" in row) else None) #LANSUBNET
        psd_row.append(ip2int(row.get("wanip")) if ("wanip" in row) else None) #WANIP
        psd_row.append(ip2int(row.get("wanmask")) if ("wanmask" in row) else None) #WANSUB
        psd_row.append(ip2int(row.get("wangate")) if ("wangate" in row) else None) #WANGATE
        dns = []
        if "dns" in row:
            for i in row["dns"].split(" "):
                if len(dns) >= 3:
                    break
                dns.append(ip2int(i))
        for i in range(3):
            psd_row.append(dns[i] if i < len(dns) else None)
        psd_row.append(row["comment"] if ("comment" in row) else None)
        write_sql_row(psd_row)
    db.database.commit()
    return ParsingOutput(ok=True)

def write_sql_row(data):
    cur = db.database.cursor()
    cur.execute(insert_query, data)
    cur.close()
