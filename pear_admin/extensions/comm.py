"""
通用函数
"""
from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import ipaddress
import json
from datetime import timedelta

from pear_admin.orms import UserORM, RoleORM, RightsORM
from pear_admin.apis.http import success_api, fail_api


def remove_duplicates_normal(lst):
    """去重普通列表并保持顺序"""
    seen = set()
    return [item for item in lst if not (item in seen or seen.add(item))]


def remove_duplicates_dict(lst):
    """去重字典列表并保持顺序，默认使用 'id' 作为唯一标识符"""
    seen = set()
    result = []
    for item in lst:
        # 默认使用 'id' 作为唯一标识符,数据中有ID为None的行，为没有IP地址，掩码，网段的行，不返回
        identifier = item.get('id')
        if identifier not in seen and item['id']:
            result.append(item)
            seen.add(identifier)
    return result


def convert_interval_to_seconds(data):
    # 检查触发器类型
    if data.get('trigger') == 'interval':
        # 如果已经有 seconds 字段，则直接返回数据
        if 'seconds' in data:
            return data

        # 提取时间单位和数值
        weeks = data.get('weeks',None)
        days = data.get('days',None)
        hours = data.get('hours',None)
        minutes = data.get('minutes',None)

        # 初始化秒数
        interval_in_seconds = 0

        # 根据提供的参数计算秒数
        if weeks is not None:
            interval_in_seconds += weeks * 7 * 24 * 3600  # 1周 = 7天 * 24小时 * 3600秒
        if days is not None:
            interval_in_seconds += days * 24 * 3600  # 1天 = 24小时 * 3600秒
        if hours is not None:
            interval_in_seconds += hours * 3600  # 1小时 = 3600秒
        if minutes is not None:
            interval_in_seconds += minutes * 60  # 1分钟 = 60秒

        # 如果没有任何时间单位，抛出错误
        if interval_in_seconds == 0:
            raise ValueError("No valid time unit provided for interval trigger.")

        # 更新字段值
        data['seconds'] = interval_in_seconds
        # 删除原有的时间单位字段
        data.pop('weeks',None)
        data.pop('days',None)
        data.pop('hours',None)
        data.pop('minutes',None)
    else:
        # 如果不是 interval 触发器，直接返回数据
        data['seconds'] = None

    return data


# 定义权限检查装饰器
def check_permission(permission):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = UserORM.query.get(user_id)
            jwt_claims = get_jwt()
            user_rights = jwt_claims.get('rights', [])
            if not user:
                return fail_api(message="用户不存在", status_code=404)

            if permission not in user_rights:
                return fail_api(message="用户没有权限操作", status_code=403)

            return func(*args, **kwargs)
        return wrapper
    return decorator


# 根据IP地址和子网掩码计算返回网段信息
def get_network_info(ip_address, subnet_mask):
    try:
        network = ipaddress.IPv4Network(ip_address + '/' + subnet_mask, strict=False)
        network_cidr = str(network)

        return network_cidr
    except ValueError:
        return None


# 判断IP地址是否属于网段
def ip_in_network(ip_address, network):
    ip = ipaddress.ip_address(ip_address)
    network = ipaddress.ip_network(network)

    if ip in network:
        return True
    else:
        return False


# 配置类转换字典
def class_to_dict(config_class):
    config_dict = {}
    for key in dir(config_class):
        # 过滤掉内置属性和方法
        if not key.startswith('__'):
            value = getattr(config_class, key)
            if isinstance(value, timedelta):
                value = value.days  # 只取天数
            elif isinstance(value, list):
                value = json.dumps(value)  # 将列表转为 JSON 字符串
            config_dict[key] = value
    return config_dict


if __name__ == '__main__':
    pass
