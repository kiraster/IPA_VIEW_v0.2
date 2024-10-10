from flask import Blueprint, Flask

from .department import department_api
from .passport import passport_api
from .rights import rights_api
from .role import role_api
from .user import user_api
from .ip import ip_api
from .group import group_api
from .monitor import monitor_api
from .task import task_api
from .setting import setting_api
from .log import log_api


def register_apis(app: Flask):
    apis = Blueprint("api", __name__, url_prefix="/api/v1")

    apis.register_blueprint(passport_api)
    apis.register_blueprint(rights_api)
    apis.register_blueprint(role_api)
    apis.register_blueprint(department_api)
    apis.register_blueprint(user_api)
    apis.register_blueprint(ip_api)
    apis.register_blueprint(group_api)
    apis.register_blueprint(monitor_api)
    apis.register_blueprint(task_api)
    apis.register_blueprint(setting_api)
    apis.register_blueprint(log_api)

    app.register_blueprint(apis)
