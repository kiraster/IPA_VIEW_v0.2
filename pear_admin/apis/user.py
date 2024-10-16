from datetime import datetime
from flask import Blueprint, request
from flask_jwt_extended import current_user, jwt_required
from flask_sqlalchemy.pagination import Pagination

from pear_admin.extensions import db
from pear_admin.orms import RoleORM, UserORM
from .http import success_api, fail_api

user_api = Blueprint("user", __name__, url_prefix="/user")


@user_api.get("/")
def user_list():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("limit", default=10, type=int)
    q = db.select(UserORM)

    pages: Pagination = db.paginate(q, page=page, per_page=per_page)

    return {
        "code": 0,
        "msg": "获取用户数据成功",
        "data": [item.json() for item in pages.items],
        "count": pages.total,
    }


@user_api.post("/")
def create_user():
    data = request.get_json()
    if data["id"]:
        del data["id"]
    role = UserORM(**data)
    create_at = data["create_at"]
    if create_at:
        role.create_at = datetime.strptime(create_at, "%Y-%m-%d %H:%M:%S")
    role.password = "123456"
    role.save()
    return {"code": 0, "msg": "新增用户成功"}


@user_api.post("/register")
def register_user():
    try:
        # force=True 参数强制将请求体当作 JSON 来处理
        data = request.get_json(force=True)
        nickname = data.get("nickname")
        new_username = data.get("username")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # 检查用户名和密码是否为空或全为空格
        if not new_username or new_username.isspace():
            return fail_api(message="用户名不能为空")
        if not password or password.isspace():
            return fail_api(message="密码不能为空")

        user_obj = UserORM.query.filter_by(username=new_username).first()
        # 查询用户名是否已存在
        if user_obj:
            return fail_api(message="用户名已存在")

        # 比对两次输入的新密码是否一致
        if password != confirm_password:
            return fail_api(message="新密码和确认新密码不一致")

        # 创建用户实例
        new_user = UserORM(username=new_username, nickname=nickname)
        new_user.password = data.get("password")

        # 查询默认角色
        default_role = RoleORM.query.get(3)
        if default_role:
            # 将默认角色添加到用户的角色列表中
            new_user.role_list.append(default_role)
        else:
            raise ValueError("默认角色不存在")

        new_user.save()

        return success_api(message="注册用户成功，正在跳转登陆页")
    except Exception as e:
        return fail_api(message=f"{str(e)}")


@user_api.put("/<int:uid>")
@user_api.put("/")
def change_user(uid=None):
    data = request.get_json()
    uid = data["id"]
    del data["id"]

    user_obj = UserORM.query.get(uid)
    for key, value in data.items():
        if key == "create_at":
            value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        setattr(user_obj, key, value)
    user_obj.save()
    return {"code": 0, "msg": "修改用户信息成功"}


@user_api.delete("/<int:rid>")
def del_user(rid):
    user_obj = UserORM.query.get(rid)
    user_obj.delete()
    return {"code": 0, "msg": "删除用户成功"}


@user_api.get("/user_role/<int:uid>")
def get_user_role(uid):
    user: UserORM = db.session.execute(
        db.select(UserORM).where(UserORM.id == uid)
    ).scalar()

    wn_role_list = [r.id for r in user.role_list]

    return {
        "code": 0,
        "msg": "返回角色权限数据成功",
        "data": wn_role_list,
    }


@user_api.put("/user_role/<int:rid>")
def change_user_role(rid):
    role_ids = request.json.get("rights_ids", "")
    role_list = role_ids.split(",")

    user: UserORM = db.session.execute(
        db.select(UserORM).where(UserORM.id == rid)
    ).scalar()
    role_obj_list = db.session.execute(
        db.select(RoleORM).where(RoleORM.id.in_(role_list))
    ).all()
    user.role_list = [r[0] for r in role_obj_list]
    user.save()
    return {"code": 0, "msg": "授权成功"}


@user_api.get("/profile")
@jwt_required()
def user_profile():
    return {
        "code": 0,
        "msg": "获取个人数据成功",
        "data": current_user.json(),
    }


@user_api.patch("/pwd")
@jwt_required()
def update_pwd():
    try:
        # force=True 参数强制将请求体当作 JSON 来处理
        data = request.get_json(force=True)
        # 比对两次输入的新密码是否一致
        if data.get("new_password") == '':
            return fail_api(message="新密码不得为空")
        if data.get("new_password") != data.get("confirm_password"):
            return fail_api(message="新密码和确认新密码不一致")

        user = current_user
        # 查数据库，校验输入的旧密码hash与数据库中存在的hash值是否一致
        # UserORM模型中自定义的 方法：check_password， 属性：password

        is_right = user.check_password(data.get("old_password"))
        if not is_right:
            return fail_api(message="旧密码错误")

        # 设置密码为新密码
        user.password = data.get("new_password")
        # 存它
        user.save()

        return success_api(message="修改用户密码成功")

    except Exception as e:
        return fail_api(message=f"{str(e)}")
