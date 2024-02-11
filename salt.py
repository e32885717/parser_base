import hashlib
from base64 import b32encode, b64encode

def generate_user_salt(username):
    username = b32encode(username.encode())
    return b64encode(hashlib.sha512(username).digest())[0:20]