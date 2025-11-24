from flask import Flask
from dotenv import load_dotenv
from .config import Config
from .routes import register_routes
from .models import db
import os


load_dotenv()


def create_app(config_object=None):
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(Config)

    upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    db.init_app(app)

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app
