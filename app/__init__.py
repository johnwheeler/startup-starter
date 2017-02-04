import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from settings import config

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_CONFIG') or 'default'])

db = SQLAlchemy(app)

if not app.debug:
    import logging

    fmt = "%(levelname)s - %(asctime)s %(filename)s:%(lineno)d %(message)s"
    formatter = logging.Formatter(fmt=fmt)
    log_path = '/var/log/flask/{}.log'.format(app.name)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
