import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = ""
    UPLOAD_EXTENSIONS = ['mp3', 'wav', 'ogg', 'flac']


class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "music_app.sqlite3")
    DEBUG = True
    SECRET_KEY = 'your_secret_key_here'
    UPLOAD_FOLDER = os.path.join(basedir, "../static/songs")
