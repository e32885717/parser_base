import re

SEC_AUTH_OPEN = 0x00
SEC_AUTH_PSK = 0x01
SEC_AUTH_EAP = 0x02
SEC_AUTH_WAPI = 0x03
SEC_WEP_NO = 0x00
SEC_WEP_YES = 0x01
SEC_SHARED_NO = 0x00
SEC_SHARED_YES = 0x01
SEC_8021X_NO = 0x00
SEC_8021X_YES = 0x01
SEC_WPA_NO = 0x00
SEC_WPA_1 = 0x01
SEC_WPA_2 = 0x02
SEC_WPA_BOTH = 0x03
SEC_DEFINED_NO = 0x00
SEC_DEFINED_YES = 0x01

def SECURITY_PACK(sec_auth, sec_wep, sec_shared, sec_8021x, sec_wpa, sec_def):
    sec = 0
    sec |= min(max(sec_auth, 0), 3)
    sec |= (min(max(sec_wep, 0), 1) << 2)
    sec |= (min(max(sec_shared, 0), 1) << 3)
    sec |= (min(max(sec_8021x, 0), 1) << 4)
    sec |= (min(max(sec_wpa, 0), 3) << 5)
    sec |= (min(max(sec_def, 0), 1) << 7)
    return sec

def SECURITY_UNPACK(sec):
    sec_auth = sec & 3
    sec_wep = (sec >> 2) & 1
    sec_shared = (sec >> 3) & 1
    sec_8021x = (sec >> 4) & 1
    sec_wpa = (sec >> 5) & 3
    sec_def = (sec >> 7) & 1
    return {'Auth': sec_auth, 'WEP': sec_wep, 'Shared': sec_shared, '8021X': sec_8021x, 'WPA': sec_wpa, 'Def': sec_def}

def str2sec(string):
    string = string.strip().upper()
    sec_auth = SEC_AUTH_OPEN
    sec_wep = SEC_WEP_NO
    sec_shared = SEC_SHARED_NO
    sec_8021x = SEC_8021X_NO
    sec_wpa = SEC_WPA_NO
    sec_def = SEC_DEFINED_NO
    if string == 'PSK':
        sec_auth = SEC_AUTH_PSK
    if string == 'EAP':
        sec_auth = SEC_AUTH_EAP
    if string == 'NONE':
        sec_auth = SEC_AUTH_OPEN
        sec_def = SEC_DEFINED_YES
    if re.match('.*802\.1X.*', string):
        sec_8021x = SEC_8021X_YES
        sec_def = SEC_DEFINED_YES
    if re.match('.*WEP.*', string):
        sec_wep = SEC_WEP_YES
        sec_def = SEC_DEFINED_YES
    if re.match('.*SHARED.*', string):
        sec_wep = SEC_WEP_YES
        sec_shared = SEC_SHARED_YES
        sec_def = SEC_DEFINED_YES
    if re.match('.*WPA.*', string):
        sec_auth = SEC_AUTH_PSK
        sec_def = SEC_DEFINED_YES
    if re.match('.*ENTERPRISE.*', string):
        sec_auth = SEC_AUTH_EAP
        sec_def = SEC_DEFINED_YES
    if re.match('WPA( |$)', string):
        sec_wpa = SEC_WPA_1
    if re.match('WPA2( |$)', string):
        sec_wpa = SEC_WPA_2
    if re.match('WPA/WPA2( |$)', string):
        sec_wpa = SEC_WPA_BOTH
    if re.match('.*WAPI.*', string):
        sec_auth = SEC_AUTH_WAPI
        sec_def = SEC_DEFINED_YES
    if string == 'WAPI':
        sec_wpa = SEC_WPA_1
    if string == 'WAPI-PSK':
        sec_wpa = SEC_WPA_2
    if string == 'WAPI/WAPI-PSK':
        sec_wpa = SEC_WPA_BOTH
    return SECURITY_PACK(sec_auth, sec_wep, sec_shared, sec_8021x, sec_wpa, sec_def)

def sec2str(sec):
    sec = SECURITY_UNPACK(int(sec))
    out = ''
    if sec['Def'] == SEC_DEFINED_NO:
        if sec['Auth'] == SEC_AUTH_OPEN:
            out = 'Unknown'
        elif sec['Auth'] == SEC_AUTH_PSK:
            out = 'PSK'
        elif sec['Auth'] == SEC_AUTH_EAP:
            out = 'EAP'
        elif sec['Auth'] == SEC_AUTH_WAPI:
            out = 'WAPI'
    else:
        if sec['Auth'] == SEC_AUTH_OPEN:
            if sec['WEP'] == SEC_WEP_NO and sec['8021X'] == SEC_8021X_NO:
                out = 'None'
            if sec['WEP'] == SEC_WEP_YES and sec['8021X'] == SEC_8021X_NO:
                out = 'WEP'
            if sec['WEP'] == SEC_WEP_NO and sec['8021X'] == SEC_8021X_YES:
                out = '802.1X'
            if sec['WEP'] == SEC_WEP_YES and sec['8021X'] == SEC_8021X_YES:
                out = '802.1X/WEP'
            if sec['Shared'] == SEC_SHARED_YES:
                out += ' Shared'
        elif sec['Auth'] == SEC_AUTH_PSK or sec['Auth'] == SEC_AUTH_EAP:
            if sec['WPA'] == SEC_WPA_1:
                out = 'WPA'
            if sec['WPA'] == SEC_WPA_2:
                out = 'WPA2'
            if sec['WPA'] == SEC_WPA_BOTH:
                out = 'WPA/WPA2'
            if sec['Auth'] == SEC_AUTH_EAP:
                out += ' Enterprise'
        elif sec['Auth'] == SEC_AUTH_WAPI:
            out = 'WAPI'
            if sec['WPA'] == SEC_WPA_2:
                out += '-PSK'
            if sec['WPA'] == SEC_WPA_BOTH:
                out += '/WAPI-PSK'
    return out
