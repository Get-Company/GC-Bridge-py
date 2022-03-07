from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

# We need to create this here
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.debug = True

    db.init_app(app)

    return app
