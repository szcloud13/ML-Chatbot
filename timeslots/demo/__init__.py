# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask
from flask_cors import CORS
import timeslot_api


def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app)
    app.register_blueprint(
        timeslot_api.bp,
        url_prefix='/timeslot_api')
    return app

if __name__ == '__main__':
    create_app().run(debug=True, port=8082) # 8082 mapping