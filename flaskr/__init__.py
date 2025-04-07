import os
from flask import Flask
from flask_cors import CORS
import shutil

BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
APP_DIR: str = os.path.join(BASE_DIR, 'app')
DATABASE_DIR: str = os.path.join(BASE_DIR, 'chroma_db')
DATA_DIR: str = os.path.join(BASE_DIR, 'flaskr/VDB_API/docs')

if not os.path.isdir(APP_DIR):
    os.mkdir(APP_DIR)

if os.path.isdir(DATABASE_DIR):
    shutil.rmtree(DATABASE_DIR)    
os.mkdir(DATABASE_DIR)

app = Flask(__name__, static_url_path='', static_folder=APP_DIR)

CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = 'development'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = False

from . import api_linebot

