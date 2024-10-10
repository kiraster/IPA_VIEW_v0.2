import os
import re
from flask import Blueprint, request

from .http import fail_api, table_api
from configs import BaseConfig
from pear_admin.extensions.comm import check_permission

log_api = Blueprint("log", __name__, url_prefix="/logs")

root_path = BaseConfig.ROOT_PATH
# log文件路径，log\log.log
log_file_path = os.path.join(root_path, 'log', 'log.log')


# 读取日志文件函数
def read_and_parse_log(file_path):
    try:
        with open(file_path,'r',encoding='utf-8') as file:
            lines = file.readlines()

        lines.reverse()  # 倒序排列
        logs = []

        # 正则表达式匹配日志格式，提取所有中括号内的内容
        log_pattern = re.compile(
            r'\[(.*?)\]\[(.*?):(\d+)\]\[task_id:(.*?)\]\[(.*?):(\d+)\]\[(.*?)\]\[(.*)\]')

        for line in lines:
            match = log_pattern.match(line)
            if match:
                timestamp = match.group(1)
                thread = f"{match.group(2)}:{match.group(3)}"
                task_id = match.group(4)
                file_name = f"{match.group(5)}:{match.group(6)}"
                level = match.group(7)
                # 取最后一个中括号的内容作为消息
                message = match.group(8).strip()

                log_entry = {
                    'timestamp': timestamp,
                    'thread': thread,
                    'task_id': task_id,
                    'file_name': file_name,
                    'level': level,
                    'message': message
                }
                logs.append(log_entry)

        return logs
    except Exception as e:
        return fail_api(message=f"读取log文件错误，{str(e)}")


# 日志-查询接口
@log_api.get("/")
def get_logs():
    try:
        page = int(request.args.get('page',1))
        page_size = int(request.args.get('limit',20))

        # log_file_path 日志文件路径
        all_logs = read_and_parse_log(log_file_path)
        # 计算行数
        total_count = len(all_logs)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        # 分页
        paged_logs = all_logs[start_index:end_index]

        return table_api(message="获取日志数据成功", data=paged_logs, count=total_count)
    except Exception as e:
        return fail_api(message=f"{str(e)}")