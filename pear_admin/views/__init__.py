from flask import Flask

from .index import index_bp
from .system import system_bp
from .ip_mgmt import ip_mgmt_bp


def register_views(app: Flask):
    app.register_blueprint(index_bp)
    app.register_blueprint(system_bp)
    app.register_blueprint(ip_mgmt_bp)

