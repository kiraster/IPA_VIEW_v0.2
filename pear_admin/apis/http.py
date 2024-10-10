from flask import jsonify


def success_api(message: str = "成功", data=None, status_code: int = 200):
    """ 成功响应 默认值”成功“ """
    res = {
        'success': True,
        'message': message,
        'data': data,
        'status_code': status_code
    }
    return jsonify(res)


def fail_api(message: str = "失败", status_code: int = 500):
    """ 失败响应 默认值“失败” """
    res = {
        'success': False,
        'message': message,
        'status_code': status_code
    }
    return jsonify(res)


def table_api(message: str = "获取表格数据成功", count=0, data=None):
    """ 动态表格渲染响应 """
    res = {
        'message': message,
        'code': 0,
        'data': data,
        'count': count
    }
    return jsonify(res)
