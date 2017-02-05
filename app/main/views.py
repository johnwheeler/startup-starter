from flask import render_template
from flask import current_app as app

from . import main
from .. import db


@main.route('/')
def index():
    app.logger.debug('DEBUG log message')
    app.logger.info('INFO log message')
    app.logger.warn('WARN log message')
    app.logger.error('ERROR log message')
    # Database connection test
    result = None
    try:
        result = db.engine.execute('select 1')
    except Exception as ex:
        pass

    return render_template('index.html', result=result)
