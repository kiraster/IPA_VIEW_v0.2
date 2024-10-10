from flask import Blueprint, request, jsonify
from flask_sqlalchemy.pagination import Pagination

from pear_admin.extensions import db
from pear_admin.orms import IPTableORM, IPGroupORM
from ..extensions.comm import remove_duplicates_normal
from ..extensions.comm import remove_duplicates_dict
from .http import success_api, fail_api, table_api
from pear_admin.extensions.comm import check_permission

group_api = Blueprint("ip_group", __name__, url_prefix="/groups")


# 分组页面-IP分组信息表数据-数组件渲染接口
@group_api.get("/tree")
def get_tree_groups():
    try:
        # 查询所有顶层 IP 组
        group_obj = IPGroupORM.query.all()

        # 构造结果数据
        data = []
        for idx, group in enumerate(group_obj, start=1):

            # 引入去重函数，去重相同的network值
            # from ..extensions.comm import remove_duplicates_dict
            networks = [ip_table.json_for_tree() for ip_table in group.ip_tables]
            unique_networks = remove_duplicates_dict(networks)

            # 父级数据，id为从1开始的自增数字
            group_data = {
                "id": idx,
                "title": group.group_name,
                'spread': 1,  # 定义spread属性，使分组目录默认为展开模式
                # 子级数据
                # "children": [ip_table.json_for_tree() for ip_table in group.ip_tables]
                "children": unique_networks
            }
            data.append(group_data)

        return success_api(message="获取IP分组信息数据成功",data=data)

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# 分组页面-IP分组信息表数据-饼图数据和分组IP地址表请求接口
@group_api.get("/pie")
def get_pie_groups(network=None):
    try:
        network = request.args.get("id", default='192.168.1.0/24')
        ip_tables = IPTableORM.query.filter_by(network=network).all()

        # 获取第一个对象的group_name，因为同一网段只能属于同一个分组
        group_name = ip_tables[0].json()['group_name']

        # 获取IPTableORM所有数据传递给分组页面表格渲染
        group_data = []

        ip_available = []
        for data_row in ip_tables:
            group_data.append(data_row.json())
            ip_available.append({'ip': data_row.ip, 'available': data_row.available})

        # 统计available字段
        len_count = len(ip_tables)  # 统计查询到的数据行
        available_count = len([ip_table for ip_table in ip_tables if ip_table.available])
        unavailable_count = len(ip_tables) - available_count

        res = {
            'network': network,
            'group_name': group_name,
            'group_data': group_data,
            'ip_available': ip_available,
            'count': {'len_count': len_count, 'available_count': available_count, 'unavailable_count': unavailable_count},
        }
        return success_api(message="获取IP分组信息数据成功",data=res)

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP分组修改页面-IP分组信息表数据-搜索接口
@group_api.get("/search")
def search_groups():
    try:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("limit", default=10, type=int)

        search_value = request.args.get('value', default='', type=str)
        query_obj = db.select(IPGroupORM).where(IPGroupORM.group_name.like(f"%{search_value}%"))

        pages: Pagination = db.paginate(query_obj, page=page, per_page=per_page)
        data = [item.json_for_setting() for item in pages.items]

        return table_api(message="获取分组地址信息搜索数据成功",data=data,count=pages.total)
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP分组修改页面-IP分组信息表数据-新增接口
@group_api.post("/")
@check_permission("group_table:add")
def add_groups():
    try:
        data = request.get_json()
        group_name = data.get("group_name")

        # 查询分组名称是否已存在
        existing_group = IPGroupORM.query.filter_by(group_name=group_name).first()
        if existing_group:
            return fail_api(message="分组名称已存在", status_code=400)

        # 修改数据行中的group_name
        if not group_name:
            return fail_api(message="分组名称为空值",status_code=400)

        row_obj = IPGroupORM(**data)
        row_obj.save()

        return success_api(message="新增IP分组信息数据成功")

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP分组修改页面-IP分组信息表数据-更新接口
@group_api.patch("/<gid>")
@check_permission("group_table:update")
def update_groups(gid=None):
    try:
        data = request.get_json()
        gid = data.get("id")
        group_name = data.get("group_name")

        # 查找 IPGroupORM 对象
        row_obj = IPGroupORM.query.get(gid)
        if row_obj is None:
            # 图一乐的判断
            return fail_api(message="没有查找到对应行", status_code=404)

        # Check if the group_name already exists for another row
        existing_group = IPGroupORM.query.filter_by(group_name=group_name).first()
        if existing_group and existing_group.id != gid:
            return fail_api(message="分组名称已存在",status_code=400)

        # 修改数据行中的group_name
        if not group_name:
            return fail_api(message="分组名称不能为空",status_code=400)

        row_obj.group_name = group_name
        # db.session.commit()
        row_obj.save()

        return success_api(message="更新IP分组信息数据成功")
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP分组修改页面-IP分组信息表数据-删除接口
@group_api.delete("/")
@check_permission("group_table:delete")
def delete_groups():
    try:
        # 解析请求的 JSON 数据
        request_data = request.get_json()

        if not request_data or 'ids' not in request_data:
            return fail_api(message="没有选中数据行或请求数据无效",status_code=400)

        ids_to_delete = request_data['ids']

        # 确保 ids_to_delete 是一个列表, 且不为空列表
        if not isinstance(ids_to_delete, list) or not ids_to_delete:
            return fail_api(message="ID 列表无效",status_code=400)

        # 判断列表中的ID存在1，即默认组ID时，提示不可删除
        if 1 in ids_to_delete:
            return fail_api(message="ID 列表中不能包含默认组ID",status_code=403)

        # 删除前将该分组下网段即置为默认组
        for row_id in ids_to_delete:
            # 更新所有引用了要删除的 IPGroupORM 的 IPTableORM 实例, 即置为默认组
            IPTableORM.query.filter_by(ip_group_id=row_id).update({IPTableORM.ip_group_id: 1})
            db.session.commit()

        # 执行删除操作
        for row_id in ids_to_delete:
            group_table_obj = IPGroupORM.query.get(row_id)
            group_table_obj.delete()

        return success_api(message="删除IP分组信息数据成功")
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP分组修改页面-IP分组信息表数据-查询接口
@group_api.get("/setting")
def get_setting_groups():
    try:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("limit", default=10, type=int)

        # 查询所有顶层 IP 组
        q = db.select(IPGroupORM)

        pages: Pagination = db.paginate(q, page=page, per_page=per_page)
        data = [item.json_for_setting() for item in pages.items]

        return table_api(message="获取分组信息数据成功",data=data,count=pages.total)
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP分组修改页面-IP分组信息表数据-穿梭框数据请求接口
@group_api.get("/transfer")
def get_transfer_groups():
    try:
        gid = request.args.get("id")
        group_name = request.args.get("group_name")

        # 定义列表装载
        gid_list = []
        all_list = []

        # 获取根据gid查询到的所有网段，列表形式 去重
        row_gid_obj = IPTableORM.query.filter_by(ip_group_id=gid).all()
        for data_row in row_gid_obj:
            gid_list.append(data_row.json_for_transfer()['network'])

        # gid_list去重
        gid_list = remove_duplicates_normal(gid_list)

        # 获取所有网段，列表形式，去重
        row_all_obj = IPTableORM.query.all()
        for data_row in row_all_obj:
            all_list.append(data_row.json_for_transfer()['network'])

        # gid_list去重
        all_list = remove_duplicates_normal(all_list)
        # 使用列表推导式将每个元素转换为字典
        col_left = [{"id": item, "network": item} for item in all_list]

        # 构造穿梭框数据格式
        col_right = gid_list

        data = {
            'gid': {'gid': gid},
            'col_left': col_left,
            'col_right': col_right,
        }
        return success_api(message="获取分组信息穿梭框数据成功", data=data)
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP分组修改页面-IP分组信息表数据-加组操作接口
@group_api.patch("/join")
@check_permission("group_table:update")
def join_groups():
    # 加组逻辑：获取穿梭框右侧列组ID，然后将加组的网段的groupID置为穿梭框右侧列组ID
    try:
        data = request.get_json()
        gid = data[0]['gid']
        for value in data[1]:
            network = value['value']
            rows_obj = IPTableORM.query.filter_by(network=network).all()
            for row_obj in rows_obj:
                row_obj.ip_group_id = gid
                row_obj.save()
        return success_api(message="网段加入分组成功")
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP分组修改页面-IP分组信息表数据-离组操作接口
@group_api.patch("/leave")
@check_permission("group_table:update")
def leave_groups():
    # 离组逻辑：将分组加入ID为1的默认组
    try:
        data = request.get_json()
        for value in data:
            network = value['value']
            rows_obj = IPTableORM.query.filter_by(network=network).all()
            for row_obj in rows_obj:
                row_obj.ip_group_id = 1
                row_obj.save()
        return success_api(message="网段离开分组成功")
    except Exception as e:
        return fail_api(message=f"{str(e)}")

