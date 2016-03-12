global db
db = None

global root
root = None
def set_db(settings):
    if hasattr(settings, 'db'):
        global db
        db = settings.db

def set_root(folder):
    global root
    root = folder