global db
db = None
def set_db(settings):
    if hasattr(settings, 'db'):
        global db
        db = settings.db