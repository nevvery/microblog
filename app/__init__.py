import os

from flask import Flask
from Config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
template_folder = os.path.join(basedir, 'templates')


def create_app(config_name=Config):
    app = Flask(__name__, template_folder=template_folder)
    app.config.from_object(config_name)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app
