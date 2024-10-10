from flask import Blueprint, render_template, send_from_directory

ip_mgmt_bp = Blueprint("ip_mgmt", __name__)


@ip_mgmt_bp.route("/view/ip_mgmt/ips.html")
def ips_view():
    return render_template("view/ip_mgmt/ips.html")


@ip_mgmt_bp.route("/view/ip_mgmt/groups.html")
def group_view():
    return render_template("view/ip_mgmt/groups.html")
