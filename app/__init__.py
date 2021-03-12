from flask import Flask 
from flask_login import LoginManager 
from flask_sqlalchemy import SQLAlchemy
import os, json,re

app = Flask(__name__)
# os.urandom(32)  
# b'\xc6^\xe13\xb31(\xc4\x9c\x00A\xa70\xe6J\xdd\xc6o<\xf9\x00~\x00\xaa\xc9\x87\xe6\x00W\xa3Q\xda'

# function to get the exact path of any file in app
def get_path(file):
    path = os.path.dirname(__file__)
    return os.path.join(path, str(file))

# loading JSON file - config.json
with open(get_path("config.json"), "r") as f:
   param = json.load(f) #json values are loaded and saved in python dictionary param

app.config["SQLALCHEMY_DATABASE_URI"] = param.get("db-uri")
# app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.secret_key = "\xc6^\xe13\xb31\xc4\x9c\x00A\xa70\xe6J\xdd\xc6o<\xf9\x00~\x00\xaa\xc9\x87\xe6\x00W\xa3Q\xda"

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.blueprint_login_views = {
"admin": "admin.admin_login",
"sub_cont": "team_login"
}

login_manager.login_message = "Login is required!"
login_manager.login_message_category = "danger"
# admin_login_manager =  LoginManager()

from app import view
from app.admin import admin as admin_bluprint
app.register_blueprint(admin_bluprint)

from app.contractor import sub_cont as contractor_bluprint
app.register_blueprint(contractor_bluprint)