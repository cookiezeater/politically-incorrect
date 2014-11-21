import os
import logging
from flask import Flask, Response
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
db = SQLAlchemy(app)

handler = logging.FileHandler("pol.log")
handler.setLevel(logging.DEBUG)

app.logger.addHandler(handler)

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.DEBUG)
werkzeug_logger.addHandler(handler)

@app.errorhandler(500)
def internal_error(exception):
    app.logger.exception(exception)
    return Response("Shiiiiiiiiiiiit")
