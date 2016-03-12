global db
db = None

global root
root = None

global botname
botname = None
def set_db(settings):
    if hasattr(settings, 'db'):
        global db
        db = settings.db

def set_root(folder):
    global root
    root = folder

def set_name(name):
    global botname
    botname = name