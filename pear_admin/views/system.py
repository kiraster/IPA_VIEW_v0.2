from flask import Blueprint, render_template
from flask_jwt_extended import current_user, jwt_required

system_bp = Blueprint("system", __name__)


@system_bp.get("/system/<path1>/<path2>")
def system_view(path1, path2):
    return render_template(f"system/{path1}/{path2}")


@system_bp.get("/views/role.html")
def role_view():
    return render_template("system/role/index.html")


@system_bp.get("/views/department.html")
def department_view():
    return render_template("system/department/index.html")


@system_bp.get("/views/user.html")
def user_view():
    return render_template("system/user/index.html")


@system_bp.route("/view/system/app-scheduler.html")
def apscheduler_view():
    return render_template("view/system/app-scheduler.html")


@system_bp.route("/view/system/groups-setting.html")
def group_setting_view():
    return render_template("view/system/groups-setting.html")


@system_bp.route("/view/system/app-settings.html")
def app_setting_view():
    return render_template("view/system/app-settings.html")


@system_bp.route("/view/system/app-log.html")
def app_log_view():
    return render_template("view/system/app-log.html")


@system_bp.route("/view/system/app-about.html")
def app_about_view():
    return render_template("view/system/app-about.html")


@system_bp.route("/view/system/pwd-change.html")
def pwd_change_view():
    return render_template("view/system/pwd-change.html")
