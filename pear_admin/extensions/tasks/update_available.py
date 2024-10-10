import os, json
from datetime import datetime,timedelta

from pear_admin.extensions import db
from pear_admin.orms import IPTableORM
from configs import get_logger, BaseConfig

task_logger = get_logger('task_log')


# 当超过REFRESH_TIME设置时间 没有updated_at值更新，则available值置为False
def update_available():

    try:
        root_path = BaseConfig.ROOT_PATH
        # pear_admin\extensions\tasks\tasks.json
        snmp_config_path = os.path.join(root_path,'pear_admin','extensions','tasks','tasks.json')
        # 读取tasks.json文件提取信息
        with open(snmp_config_path,'r',encoding="utf-8") as f:
            snmp_config = json.load(f)
        refresh_time = snmp_config['REFRESH_TIME']

        # 获取当前时间
        current_time = datetime.utcnow()

        # 计算时间阈值（30分钟之前的时间）
        threshold_time = current_time - timedelta(minutes=refresh_time)

        # 查询updated_at时间与当前时间相差30分钟以上的数据行
        ip_table_list = IPTableORM.query.filter(IPTableORM.updated_at < threshold_time).all()

        # 修改每一行的available值为False
        for ip_table in ip_table_list:
            ip_table.available = False

        # 提交修改到数据库中
        db.session.commit()
        return True
    except Exception as e:
        # print('内部错误——检测在线主机状态任务>>>' + str(e))
        task_logger.error('内部错误——检测在线主机状态任务' + str(e))
        db.session.rollback()
        return False
