import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '\x8f\xfdPC\xd3\xbf\x85a\xa3\x0c\xf5_\x90\xb9-J%1k\x90\x14i\x03\x9f'
    PG_CONFIG = dict(database=os.environ.get('RDS_DB_NAME'), user=os.environ.get('RDS_USERNAME'), password=os.environ.get('RDS_PASSWORD'), host=os.environ.get('RDS_HOSTNAME'))
    MONGO_CONNECTION_STRING = os.environ.get('MONGO_CONNECTION_STRING')
    FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN")
    FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
