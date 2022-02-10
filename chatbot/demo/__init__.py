# -*- coding: utf-8 -*-
from __future__ import absolute_import

from flask import Flask
from flask_cors import CORS
import MLChatBot


def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app)
    app.register_blueprint(
        MLChatBot.bp,
        url_prefix='/MLChatBot')
    return app

if __name__ == '__main__':
    create_app().run(debug=True, port=8080) # 8080 port mapping