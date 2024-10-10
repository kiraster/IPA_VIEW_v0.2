import os
import platform
import re
import time
from datetime import datetime
import flask
import psutil
from cpuinfo import cpuinfo
from flask import Blueprint

from .http import success_api, fail_api, table_api

monitor_api = Blueprint("monitor", __name__, url_prefix="/monitor")

# 记录应用启动时间
flask_start = datetime.now()


# 系统监控
@monitor_api.get("/system-info")
def get_system_monitor():
    try:
        # 主机名称
        hostname = platform.node()
        # 系统版本
        system_version = platform.platform()

        cpu_info = cpuinfo.get_cpu_info()

        # CPU型号
        brand_raw = cpu_info['brand_raw']
        # CPU主频
        hz_actual_friendly = cpu_info['hz_actual_friendly']
        # CPU核心数
        count = cpu_info['count']
        # CPU架构
        arch = cpu_info['arch']
        # CPU是否64bits
        bits = cpu_info['bits']

        # 内存大小
        memory_information = psutil.virtual_memory()
        mem_total = memory_information.total
        # 转换为 GB，并保留两位小数
        mem_total_gb = mem_total / (1024 ** 3)
        mem_total = f"{mem_total_gb:.2f}"

        # 开机时间
        boot_time = datetime.fromtimestamp(psutil.boot_time()).replace(microsecond=0)

        # 计算开机时间
        up_time = datetime.now().replace(microsecond=0) - boot_time
        up_time_list = re.split(r':', str(up_time))

        # 格式化 boot_time datetime 对象和up_time
        boot_time = boot_time.strftime("%Y-%m-%d %H:%M:%S")
        up_time = " {} 小时 {} 分钟 {} 秒".format(up_time_list[0], up_time_list[1], up_time_list[2])

        # 计算总运行时间
        calc_time = datetime.now() - flask_start
        calc_time_list = re.split(r':', str(calc_time))
        flask_start_at = " {} 小时 {} 分钟 {} 秒".format(calc_time_list[0], calc_time_list[1], calc_time_list[2].split('.')[0])

        # python版本
        # python_version = platform.python_version()

        # Python版本
        python_version = cpu_info['python_version']

        # 获取 Flask 的版本号
        flask_version = flask.__version__

        data = {
            'hostname': hostname,
            'system_version': system_version,
            'cpu_brand': brand_raw,
            'cpu_frequency': hz_actual_friendly,
            'cpu_core': count,
            'cpu_arch': arch,
            'bits': bits,
            'mem_total': mem_total,
            'boot_time': boot_time,
            'up_time': up_time,
            'flask_start_at': flask_start_at,
            'python_version': python_version,
            'flask_version': flask_version
        }
        return success_api(message="获取系统信息成功", data=data)
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# 磁盘信息
@monitor_api.get("/disk-partition")
def get_disk_partition():
    try:
        data = []
        # 判断是否在容器中
        if not os.path.exists('/.dockerenv'):
            disk_partitions = psutil.disk_partitions()
            for i in disk_partitions:
                a = psutil.disk_usage(i.device)
                disk_partitions_dict = {
                    'device': i.device,
                    'fstype': i.fstype,
                    'total': round(a.total / (1024 * 1024* 1024), 2),
                    'used': round(a.used / (1024 * 1024* 1024), 2),
                    'free': round(a.free / (1024 * 1024* 1024), 2),
                    'percent': a.percent
                }
                data.append(disk_partitions_dict)

        return success_api(message="获取磁盘分区信息成功", data=data)
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# 获取CPU和内存利用率
@monitor_api.get("/utilization")
def polling_utilization():
    try:
        # 获取cpu使用率
        cpus_percent = psutil.cpu_percent(interval=0.1, percpu=False)  # percpu 获取主使用率
        # 获取内存使用率
        memory_information = psutil.virtual_memory()
        memory_usage = memory_information.percent
        time_now = time.strftime('%H:%M:%S ', time.localtime(time.time()))
        data = {'cups_percent': cpus_percent, 'memory_used': memory_usage, 'time_now': time_now}
        return success_api(message="获取CPU和内存使用率成功", data=data)
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# 网卡信息
@monitor_api.get("/network-load")
def polling_network_load():
    try:
        stats = psutil.net_io_counters()
        # 单位MB，保留两位小数
        bytes_sent = round(stats.bytes_sent / (1024 * 1024), 2)
        bytes_recv = round(stats.bytes_recv / (1024 * 1024), 2)
        time_now = time.strftime('%H:%M:%S ', time.localtime(time.time()))
        data = {'time_now': time_now, 'bytes_sent': bytes_sent, 'bytes_recv': bytes_recv}
        return success_api(message="获取系统网络负载信息成功", data=data)
    except Exception as e:
        return fail_api(message=f"{str(e)}")

