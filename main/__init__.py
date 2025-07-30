from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from main.config import Config

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=naming_convention)

db = SQLAlchemy(metadata=metadata)


# We need to create this here
def create_app():
    app = Flask(__name__)
    CORS(app)
    CORS(app, origins=[
        'http://10.0.0.155:5000',  # Buchner
        'http://localhost:5000',  # Buchner local
        'http://10.0.0.205:5000',  # Bauer
        'http://10.0.0.210:5000',  # Angermeier
        'http://10.0.0.202:5000',  # Stadler
        'http://10.0.0.203:5000',  # Merkle
    ])
    app.config.from_object(Config)
    app.secret_key = 'super_secret_key'
    app.debug = True
    db.init_app(app)

    return app


