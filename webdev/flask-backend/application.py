import os
from app import create_app
from flask import g

application = create_app(os.environ.get('FLASK_CONFIG') or 'default')

@application.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
    mongo = getattr(g, '_mongo', None)
    if mongo is not None:
        mongo.close()    

if __name__ == '__main__':
    application.run()
