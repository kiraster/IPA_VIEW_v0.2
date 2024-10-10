from flask import Flask
from flask_apscheduler import APScheduler

from .init_db import db, migrate
from .init_jwt import jwt
from .init_script import register_script


scheduler = APScheduler()


def register_extensions(app: Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    register_script(app)

    # 初始化调度器，添加判断是否已有scheduler在运行
    if not scheduler.running:
        scheduler.init_app(app)
        scheduler.start()
    # scheduler.init_app(app)
    # scheduler.start()

    # 导入任务函数
    from .tasks import tasks

    # 添加定时任务 触发器类型 interval，设置时间间隔，循环执行
    # scheduler.add_job(id='1',name='定时轮询网关ARP表和接入交换机mac地址表', func=tasks.job1,trigger='interval',seconds=10)
    # scheduler.add_job(id='2',name='定时更新没有轮询到ARP表项的IP地址状态', func=tasks.job2,trigger='interval',minutes=2)

    # 添加定时任务 触发器类型 date，指定固定时间，只执行一次
    # scheduler.add_job(id='3',name='触发器类型 date 任务示例',func=tasks.test,trigger='date',run_date='2024-9-23 00:10:10')

    # 添加定时任务 触发器类型 cron,周期内指定时间执行一次
    # scheduler.add_job(id='4',name='触发器类型 corn 任务示例',func=tasks.test,trigger='cron',day_of_week='mon-fri', hour=6,minute=00)


# 确保应用启动时从存储器中加载任务
def load_jobs_from_storage():
    if not scheduler.get_jobs():
        scheduler._load_jobs()