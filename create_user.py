import db
import sys

def _gen_user(u, p):
    print(f"Generating user with\n    Login={u}\n    Password={p}")
    db.gen_user(u, p)
    print("Done. For exit press enter")
    input()

if __name__ == "__main__":
    if "-d" in sys.argv:
        username = "public"
        password = "public"
    elif "-u" in sys.argv and "-p" in sys.argv:
        username = sys.argv[sys.argv.index("-u") + 1]
        password = sys.argv[sys.argv.index("-p") + 1]
    else:
        username = input("Username: ")
        password = input("Password: ")
    _gen_user(username, password)