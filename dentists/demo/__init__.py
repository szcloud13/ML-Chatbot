# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask
from flask_cors import CORS
import dentist_api


def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app)
    app.register_blueprint(
        dentist_api.bp,
        url_prefix='/dentist_api')
    return app

if __name__ == '__main__':
    create_app().run(debug=True, port=8081) # 8081 mapping