import os

from flask import Flask
from flask_jwt_extended import JWTManager

from app.views.users import users_bp
from app.views.parcels import parcels_bp
from config import app_config



def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    jwt=JWTManager(app)
    app.register_blueprint(users_bp)
    app.register_blueprint(parcels_bp)

    return app