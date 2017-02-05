import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from settings import config


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config[os.getenv('FLASK_CONFIG') or 'default'])
    db.init_app(app)
    
    if not app.debug:
        import logging

        fmt = "%(levelname)s - %(asctime)s %(filename)s:%(lineno)d %(message)s"
        formatter = logging.Formatter(fmt=fmt)
        log_path = '/var/log/flask/{}.log'.format(app.name)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)

        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


    # Register app blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
