from flask import Blueprint, render_template, send_from_directory

index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index():
    return render_template("view/index.html")


@index_bp.route("/view/login.html")
def login():
    return render_template("view/login.html")


@index_bp.route("/view/register.html")
def register():
    return render_template("view/register.html")


# @index_bp.route("/view/console/index.html")
# def console1():
#     return render_template("view/console/index.html")


# @index_bp.route("/view/system/person.html")
# def person():
#     return render_template("view/system/person.html")

@index_bp.route("/favicon.ico")
def fav_icon():
    return send_from_directory(directory="static", path="favicon.ico")


@index_bp.route("/view/start/index.html")
def index_page_view():
    return render_template("view/start/index.html")


@index_bp.route("/view/start/monitor.html")
def monitor_view():
    return render_template("view/start/monitor.html")



