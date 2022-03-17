from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from libretranslatepy import LibreTranslateAPI


"""
#######################################
Making the app
#######################################
"""
app = Flask(__name__)
app.config.from_object(Config)
app.debug = True


"""
#######################################
Making the db and all tables
#######################################
"""
db = SQLAlchemy(app)

"""
#######################################
Translation
#######################################
"""
lt = LibreTranslateAPI("http://localhost:5000/")
