import time
from flask import Blueprint, request, jsonify
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import func

from pear_admin.extensions import db
from pear_admin.orms import IPTableORM, IPGroupORM
from .http import success_api, fail_api, table_api
from pear_admin.extensions.comm import check_permission

ip_api = Blueprint("ip_table", __name__, url_prefix="/ips")


# IP地址信息表数据-查询接口
# @ip_api.get("/")
@ip_api.get("", strict_slashes=False)  # 关键修改--去掉 "/"，并禁用自动重定向
def get_ips():
    try:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("limit", default=10, type=int)

        # q = db.select(IPTableORM)
        # 构建查询对象，并按 'ip' 字段升序排序
        q = db.select(IPTableORM).order_by(db.asc(IPTableORM.ip))
        pages: Pagination = db.paginate(q, page=page, per_page=per_page)

        data = [item.json() for item in pages.items]

        return table_api(message="获取IP地址信息数据成功", data=data, count=pages.total)

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP地址信息表数据-搜索接口
@ip_api.get("/search")
def search_ips():
    # 与get_ip_table功能相似，前端表格重载数据，需要向后端请求，只不过多了过滤条件
    try:
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("limit", default=10, type=int)

        filter_condition = request.args.get('filter', default='', type=str)
        search_value = request.args.get('value', default='', type=str)

        # 添加判断
        if filter_condition == 'ip':
            query_obj = db.select(IPTableORM).where(IPTableORM.ip.like(f"%{search_value}%"))
        elif filter_condition == 'network':
            query_obj = db.select(IPTableORM).where(IPTableORM.network.like(f"%{search_value}%"))
        elif filter_condition == 'mac_add':
            query_obj = db.select(IPTableORM).where(IPTableORM.mac_add.like(f"%{search_value}%"))
        elif filter_condition == 'system_name':
            query_obj = db.select(IPTableORM).where(IPTableORM.system_name.like(f"%{search_value}%"))
        elif filter_condition == 'vlan':
            query_obj = db.select(IPTableORM).where(IPTableORM.vlan.like(f"%{search_value}%"))
        elif filter_condition == 'snmp_host':
            query_obj = db.select(IPTableORM).where(IPTableORM.snmp_host.like(f"%{search_value}%"))
        elif filter_condition == 'user':
            query_obj = db.select(IPTableORM).where(IPTableORM.user.like(f"%{search_value}%"))
        elif filter_condition == 'desc':
            query_obj = db.select(IPTableORM).where(IPTableORM.desc.like(f"%{search_value}%"))
        elif filter_condition == 'group_name':
            query_obj = db.select(IPGroupORM).where(IPGroupORM.group_name.like(f"%{search_value}%"))
            pages: Pagination = db.paginate(query_obj, page=page, per_page=per_page)
            # 无敌循环，自行烧脑
            data = [ip_table for item in pages.items for ip_table in item.json().get('ip_tables',[])]
            return table_api(message="获取IP地址信息搜索数据成功", data=data, count=pages.total)
        else:
            return fail_api(message="无效过滤条件", status_code=400)

        pages: Pagination = db.paginate(query_obj, page=page, per_page=per_page)
        data = [item.json() for item in pages.items]

        return table_api(message="获取IP地址信息搜索数据成功",data=data,count=pages.total)

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP地址信息表数据-更新接口
@ip_api.patch("/<uid>")
@check_permission("ip_table:update")
def update_ips(uid=None):
    try:
        data = request.get_json()
        uid = data.get("id")
        group_name = data.get("group_name")
        network = data.get("network")

        # 根据接收的group_name查询IPTableORM所有的行
        network_obj = IPTableORM.query.filter_by(network=network).all()

        # 根据接收的id查询IPTableORM对象
        row_obj = IPTableORM.query.get(uid)
        if row_obj is None:
            # 图一乐的判断
            return fail_api(message="没有查找到对应行", status_code=404)

        # 判断接收的group_name是否为空
        if not group_name:
            return fail_api(message="分组名称不能为空", status_code=400)

        # 根据接收的group_name查询IPGroupORM
        group_obj = IPGroupORM.query.filter_by(group_name=group_name).first()
        if group_obj is None:
            # 创建新的分组，将所有该网段加入到新分组（修改ip_group_id=new_group.id）
            new_group_obj = IPGroupORM(group_name=group_name)
            new_group_obj.save()
            new_group_id = new_group_obj.id

            # 保持数据一致性，将与所编辑行相同网络的行加入到新增的分组
            for row_by_network_obj in network_obj:
                row_by_network_obj.ip_group_id = new_group_id
                row_by_network_obj.save()

        else:
            # IPGroupORM已存在group_name记录
            # 保持数据一致性，将与所编辑行相同网络的行加入到修改后的分组
            group_obj_id = group_obj.id
            for row_by_network_obj in network_obj:
                row_by_network_obj.ip_group_id = group_obj_id
                row_by_network_obj.save()

        # 更新 IPTableORM 的其他字段
        for key, value in data.items():
            if key != "id" and key != "group_name" and key != "network":
                setattr(row_obj, key, value)

        row_obj.save()
        return success_api(message="更新IP地址信息数据成功")

    except Exception as e:
        db.session.rollback()
        return fail_api(message=f"{str(e)}")


# IP地址信息表数据-删除接口
@ip_api.delete("/")
@check_permission("ip_table:delete")
def delete_ips():
    try:
        # 解析请求的 JSON 数据
        request_data = request.get_json()

        if not request_data or 'ids' not in request_data:
            return fail_api(message='没有选中数据行或请求数据无效', status_code=400)

        ids_to_delete = request_data['ids']

        # 确保 ids_to_delete 是一个列表, 且不为空列表
        if not isinstance(ids_to_delete, list) or not ids_to_delete:
            return fail_api(message='ID 列表无效',status_code=400)

        # 执行删除操作
        for row_id in ids_to_delete:
            ip_table_obj = IPTableORM.query.get(row_id)
            ip_table_obj.delete()

        return success_api(message="删除IP地址信息数据成功")

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP地址信息表数据-获取统计信息接口-用于渲染首页第一栏
@ip_api.get("/statistics/overview")
def get_overview():
    try:
        # 统计ip_table表总行数
        total = db.select(IPTableORM)
        results = db.session.execute(total).scalars().all()
        total_count = len(results)

        # 获取在线状态-统计 query_obj = db.select(IPTableORM).where(IPTableORM.active == 1)
        online_status = db.select(IPTableORM).where(IPTableORM.available == 1)
        results = db.session.execute(online_status).scalars().all()
        online_status_count = len(results)

        # 获取离线状态-统计 query_obj = db.select(IPTableORM).where(IPTableORM.active == 0)
        offline_status = db.select(IPTableORM).where(IPTableORM.available == 0)
        results = db.session.execute(offline_status).scalars().all()
        offline_status_count = len(results)

        # 使用 SQLAlchemy 查询 distinct 的 network 值并统计其数量
        unique_network_count = db.session.query(func.count().label('unique_network_count')). \
            select_from(db.session.query(IPTableORM.network.distinct())).scalar()

        data = {
            'total_count': total_count,
            'online_status': online_status_count,
            'offline_status': offline_status_count,
            'unique_network_count': unique_network_count
        }

        return success_api(data=data)

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP地址信息表数据-获取IP在线和离线状态接口-用于渲染第二栏折线图
@ip_api.get("/statistics/status")
def polling_ip_status():
    # 在 SQLite 中，布尔值通常用 0 (表示 False) 和 1 (表示 True) 存储。
    # 在 Python 代码中，使用 True 和 False 来向 SQLite 数据库中写入布尔值
    # SQLAlchemy 会自动将这些布尔值转换为适当的整数值 (0 或 1) 存储在 SQLite 数据库中
    try:
        # 获取在线状态-统计 query_obj = db.select(IPTableORM).where(IPTableORM.active == 1)
        online_status = db.select(IPTableORM).where(IPTableORM.available == 1)
        # 执行查询
        results = db.session.execute(online_status).scalars().all()
        # 获取数据行数
        online_status_count = len(results)

        # 获取离线状态-统计 query_obj = db.select(IPTableORM).where(IPTableORM.active == 0)
        offline_status = db.select(IPTableORM).where(IPTableORM.available == 0)
        # 执行查询
        results = db.session.execute(offline_status).scalars().all()
        # 获取数据行数
        offline_status_count = len(results)

        time_now = time.strftime('%H:%M:%S ', time.localtime(time.time()))

        data = {'online_status': online_status_count, 'offline_status': offline_status_count, 'time_now': time_now}
        return success_api(data=data)

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# IP地址信息表数据-获取分组在线和离线状态接口-用于渲染第三栏柱形图
@ip_api.get("/statistics/group")
def polling_group_status():
    # 在 SQLite 中，布尔值通常用 0 (表示 False) 和 1 (表示 True) 存储。
    # 在 Python 代码中，使用 True 和 False 来向 SQLite 数据库中写入布尔值
    # SQLAlchemy 会自动将这些布尔值转换为适当的整数值 (0 或 1) 存储在 SQLite 数据库中
    try:
        ip_groups = IPGroupORM.query.all()

        true_counts = []
        false_counts = []
        remaining_counts = []

        result = []

        for ip_group in ip_groups:
            ip_tables = IPTableORM.query.filter_by(ip_group_id=ip_group.id).all()

            network_count = {}
            for ip_table in ip_tables:
                network = ip_table.network
                if network not in network_count:
                    network_count[network] = {'true': 0, 'false': 0}
                if ip_table.available:
                    network_count[network]['true'] += 1
                else:
                    network_count[network]['false'] += 1

            for network, counts in network_count.items():
                true_count = counts['true']
                false_count = counts['false']
                total_count = 254
                remaining_count = total_count - (true_count + false_count)

                result.append({
                    'group_name': ip_group.group_name,
                    'network': network
                })

                true_counts.append(str(true_count))
                false_counts.append(str(false_count))
                remaining_counts.append(str(remaining_count))

        data = {
            'result': result,
            'true_counts': true_counts,
            'false_counts': false_counts,
            'remaining_counts': remaining_counts
        }
        return success_api(data=data)

    except Exception as e:
        return fail_api(message=f"{str(e)}")