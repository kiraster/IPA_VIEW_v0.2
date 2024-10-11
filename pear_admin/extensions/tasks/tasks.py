import datetime

from .snmp_polling import poll_write
from .update_available import update_available
from configs import get_logger

task_logger = get_logger('task_log')


# 测试用
def test():
    # print(f'定时任务_test_{datetime.datetime.now()}')
    task_logger.info(f'定时任务_test_{datetime.datetime.now()}')


# 调用snmp_polling.py文件里的任务函数
def job1():
    try:
        from ... import create_app
        app = create_app()
        with app.app_context():
            poll_write()
            task_logger.info("已完成SNMP轮询任务")
            # print('已完成SNMP轮询任务')

    except Exception as e:
        task_logger.error('内部错误——定时任务函数job1' + str(e))
        # print(f"job1出现严重错误：{e}")


# 调用update_available.py文件里的任务函数
def job2():
    try:
        from ... import create_app
        app = create_app()
        with app.app_context():
            update_available()
            task_logger.info("已完成检测在线主机状态任务")
            # print('已完成检测在线主机状态任务')

    except Exception as e:
        task_logger.error('内部错误——定时任务函数job2' + str(e))
        # print(f"job2出现严重错误：{e}")
