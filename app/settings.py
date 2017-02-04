# config file inspired from flask-base
# https://github.com/hack4impact/flask-base/blob/master/config.py

import os
import urlparse

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Application name
    APP_NAME = os.environ.get('APP_NAME', 'Flask-App')

    # Secret key for http sessions
    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('/!\ Secret key should not be seen in production.')

    # SQLAlchemy configuration
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    db_host = os.environ.get('DB_HOST', 'db')
    db_name = os.environ.get('DB_NAME', 'vagrant')
    db_username = os.environ.get('DB_USERNAME', 'vagrant')
    db_password = os.environ.get('DB_PASSWORD', 'vagrant')

    SQLALCHEMY_DATABASE_URI = "postgres://{}:{}@{}:5432/{}".format(
        db_username,
        db_password,
        db_host,
        db_name,
    )

    # Mail service configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'password'
    ADMIN_EMAIL = os.environ.get(
        'ADMIN_EMAIL') or 'admin@example.com'
    EMAIL_SUBJECT_PREFIX = '[{}]'.format(APP_NAME)
    EMAIL_SENDER = '{app_name} Admin <{email}>'.format(
        app_name=APP_NAME, email=MAIL_USERNAME)

    # Redis configuration
    REDIS_URL = os.getenv('REDISTOGO_URL') or 'http://localhost:6379'

    # Parse the REDIS_URL to set RQ config variables
    urlparse.uses_netloc.append('redis')
    url = urlparse.urlparse(REDIS_URL)

    RQ_DEFAULT_HOST = url.hostname
    RQ_DEFAULT_PORT = url.port
    RQ_DEFAULT_PASSWORD = url.password
    RQ_DEFAULT_DB = 0

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SSL_DISABLE = (os.environ.get('SSL_DISABLE') or 'True') == 'True'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'heroku': HerokuConfig,
    'unix': UnixConfig
}
