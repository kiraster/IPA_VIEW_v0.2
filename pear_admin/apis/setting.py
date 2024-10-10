import os
import re
import json
from flask import Blueprint, request, jsonify

from .http import success_api, fail_api
from configs import BaseConfig, APSchedulerConfig
from pear_admin.extensions.comm import check_permission

setting_api = Blueprint("setting", __name__, url_prefix="/app-settings")

root_path = BaseConfig.ROOT_PATH
# 配置文件路径
config_path = os.path.join(root_path, 'configs.py')
# snmp配置文件路径， pear_admin\extensions\tasks\tasks.json
snmp_config_path = os.path.join(root_path, 'pear_admin', 'extensions', 'tasks', 'tasks.json')


# configs.py文件更新配置函数
def update_config_file(config_data):
    # root_path = BaseConfig.ROOT_PATH
    # config_path = os.path.join(root_path, 'configs.py')
    # 读取配置文件
    with open(config_path, 'r') as file:
        content = file.read()

    # 更新配置项
    for key, value in config_data.items():
        if key == 'JWT_ACCESS_TOKEN_EXPIRES':
            content = re.sub(r'(JWT_ACCESS_TOKEN_EXPIRES\s*=\s*timedelta\(days=\d+\))', 'JWT_ACCESS_TOKEN_EXPIRES = ' + value, content)

        # elif key.startswith('SCHEDULER_JOB_DEFAULTS_'):
        #     param = key.split('_', 3)[-1]  # Extract parameter name
        #     content = re.sub(rf"({param}': )\w+", r"\1" + str(value).lower(), content)
        # elif key == 'SNMP_DATA_GW':
        #     new_snmp_data_gw = json.dumps(value, indent=4)
        #     content = re.sub(r'(SNMP_DATA_GW\s*=\s*\[)[^\]]*\]', r'\1' + new_snmp_data_gw + ']', content)

    # 写回文件
    with open('config.py', 'w') as file:
        file.write(content)


# 转换写入tasks.json文件的格式
def parse_snmp_data(data):
    parsed_data = []
    for entry in data.split('\n'):
        if entry:
            host, community = entry.split(':')
            parsed_data.append({"snmp_host": host, "snmp_community": community})
    return parsed_data


# 应用配置-查询接口
@setting_api.get("/")
def get_app_settings():

    # 读取tasks.json文件提取信息
    with open(snmp_config_path,'r', encoding="utf-8") as f:
        snmp_config = json.load(f)

    # 构造字典
    data = {
        'token_time': BaseConfig.JWT_ACCESS_TOKEN_EXPIRES.days,
        'refresh_time': snmp_config['REFRESH_TIME'],
        'snmp_data_gw': snmp_config['SNMP_DATA_GW'],
        'snmp_data_acc': snmp_config['SNMP_DATA_ACC'],
        'coalesce': APSchedulerConfig.SCHEDULER_JOB_DEFAULTS['coalesce'],
        'max_instances': APSchedulerConfig.SCHEDULER_JOB_DEFAULTS['max_instances'],
        'misfire_grace_time': APSchedulerConfig.SCHEDULER_JOB_DEFAULTS['misfire_grace_time'],
    }

    return success_api(message="读取配置文件成功", data=data)


# 基本配置-更新接口
@setting_api.post('/base')
@check_permission("app_config:update")
def update_base_app_settings():
    # data = request.get_json()
    #
    # # 剔除token_time字段
    # data.pop('token_time',None)
    #
    # # 构造写入结构
    # update_data = {
    #     "logo": {
    #         "title": data['title']
    #     }
    # }
    #
    # # 读取当前的配置文件
    # with open(pear_config_json_path,'r', encoding="utf-8") as f:
    #     config = json.load(f)
    #
    # # 更新 logo 部分中的 title 字段
    # config['logo'].update(update_data['logo'])
    #
    # # 将更新后的内容写回文件
    # with open(pear_config_json_path,'w', encoding="utf-8") as f:
    #     json.dump(config,f, ensure_ascii=False, indent=2)

    return success_api(message="配置更新成功")


# snmp配置-更新接口
@setting_api.post('/snmp')
@check_permission("app_config:update")
def update_snmp_app_settings():
    try:
        data = request.get_json()

        if data is None:
            return fail_api(message="无效的SNMP配置", status_code=400)

        # 读取tasks.json文件提取信息
        with open(snmp_config_path, 'r', encoding="utf-8") as f:
            snmp_config = json.load(f)

        # 更新 REFRESH_TIME
        if 'refresh_time' in data:
            snmp_config['REFRESH_TIME'] = int(data['refresh_time'])

        # 更新 SNMP_DATA_GW
        if 'snmp_data_gw' in data:
            snmp_config['SNMP_DATA_GW'] = parse_snmp_data(data['snmp_data_gw'])

        # 更新 SNMP_DATA_ACC
        if 'snmp_data_acc' in data:
            snmp_config['SNMP_DATA_ACC'] = parse_snmp_data(data['snmp_data_acc'])

        # 将更新后的内容写回文件
        with open(snmp_config_path, 'w', encoding="utf-8") as f:
            json.dump(snmp_config, f, ensure_ascii=False, indent=2)

        return success_api(message="配置更新成功")

    except FileNotFoundError:
        return fail_api(message="配置文件未找到")
    except json.JSONDecodeError:
        return fail_api(message="配置文件格式错误")
    except Exception as e:
        return fail_api(message=str(e))
