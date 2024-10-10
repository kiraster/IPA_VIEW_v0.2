from datetime import datetime
from flask import Blueprint, request, render_template
from flask_apscheduler.utils import job_to_dict
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

from configs import APSchedulerConfig
from pear_admin.extensions.tasks import tasks
from pear_admin.extensions import scheduler
from ..apis.http import success_api, fail_api, table_api
from pear_admin.extensions.comm import check_permission
from configs import get_logger

task_logger = get_logger('task_log')

task_api = Blueprint("task", __name__, url_prefix="/scheduler")


# 获取jobs
@task_api.get('/jobs')
def get_jobs():
    try:
        jobs = scheduler.get_jobs()
        data = []
        for job in jobs:
            data.append(job_to_dict(job))
        return table_api(message="获取job成功",data=data,count=len(data))

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# 新增job
@task_api.post("/jobs")
@check_permission("jobs:add")
def add_job():
    try:
        # 获取请求中的 JSON 数据
        data = request.get_json()
        job_id = data.get('id')
        name = data.get('name')
        func = data.get('func')
        next_run_time = data.get('next_run_time')
        trigger_type = data.get('trigger_type')
        seconds = data.get('seconds')
        # cron_data = data.get('cron_data')
        run_date_str = data.get('run_date')

        # 判断next_run_time，当值为真将当前时间转换格式后赋值,否则设为None
        if next_run_time:
            # 获取当前 UTC 时间
            utc_now = datetime.utcnow()
            # 转换为指定的时间格式
            formatted_utc_time = utc_now.strftime("%Y-%m-%d %H:%M:%S")
            next_run_time = formatted_utc_time

        else:
            next_run_time = None

        # 处理max_instances不是字符型数字的情况
        try:
            max_instances = int(data.get('max_instances'))
        except (TypeError, ValueError):
            max_instances = APSchedulerConfig.SCHEDULER_JOB_DEFAULTS.get('max_instances')

        # 处理misfire_grace_time不是字符型数字的情况
        try:
            misfire_grace_time = int(data.get('misfire_grace_time'))
        except (TypeError, ValueError):
            misfire_grace_time = APSchedulerConfig.SCHEDULER_JOB_DEFAULTS.get('misfire_grace_time')

        # 解析时间字段
        run_date = datetime.strptime(run_date_str,"%Y-%m-%d %H:%M:%S") if run_date_str else None

        if trigger_type == 'date':
            next_run_time = run_date
            trigger = DateTrigger(run_date=run_date)
        elif trigger_type == 'interval':
            trigger = IntervalTrigger(seconds=int(seconds))
        # elif trigger_type == 'cron':
        #     # CronTrigger 需要更多的字段配置，这里我不想玩
        #     pass
        else:
            return fail_api(message="无效触发器类型")

        # 添加任务
        scheduler.add_job(
            id=job_id,
            func=getattr(tasks, func),
            name=name,
            next_run_time=next_run_time,
            trigger=trigger,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time)

        return success_api(message="添加job成功")

    except Exception as e:
        return fail_api(message=f"{str(e)}")


# 更新job
@task_api.patch("/jobs/<job_id>")
@check_permission("jobs:update")
def update_job(job_id=None):
    try:
        data = request.get_json()
        job_id = data.get('id')
        name = data.get('name')
        func = data.get('func')
        next_run_time = data.get('next_run_time')
        trigger_type = data.get('trigger_type')

        # cron_data = data.get('cron_data')
        run_date_str = data.get('run_date')

        # 判断next_run_time，当值为真将当前时间转换格式后赋值,否则设为None
        if next_run_time:
            # 获取当前 UTC 时间
            utc_now = datetime.utcnow()
            # 转换为指定的时间格式
            formatted_utc_time = utc_now.strftime("%Y-%m-%d %H:%M:%S")
            next_run_time = formatted_utc_time
        else:
            next_run_time = None

        # 处理max_instances不是字符型数字的情况
        try:
            max_instances = int(data.get('max_instances'))
        except (TypeError,ValueError):
            max_instances = APSchedulerConfig.SCHEDULER_JOB_DEFAULTS.get('max_instances')

        # 处理misfire_grace_time不是字符型数字的情况
        try:
            misfire_grace_time = int(data.get('misfire_grace_time'))
        except (TypeError,ValueError):
            misfire_grace_time = APSchedulerConfig.SCHEDULER_JOB_DEFAULTS.get('misfire_grace_time')

        # 解析时间字段
        run_date = datetime.strptime(run_date_str,"%Y-%m-%d %H:%M:%S") if run_date_str else None

        if trigger_type == 'date':
            next_run_time = run_date
            # trigger = DateTrigger(run_date=run_date)
            # modify_job
            scheduler.modify_job(
                id=job_id,
                func=getattr(tasks,func),
                name=name,
                run_date=run_date,
                next_run_time=next_run_time,
                trigger=trigger_type,
                max_instances=max_instances,
                misfire_grace_time=misfire_grace_time,
            )
        elif trigger_type == 'interval':
            seconds = data.get('seconds')
            # trigger = IntervalTrigger(seconds=int(seconds))
            # modify_job
            scheduler.modify_job(
                id=job_id,
                func=getattr(tasks,func),
                name=name,
                next_run_time=next_run_time,
                seconds=int(seconds),
                trigger=trigger_type,
                max_instances=max_instances,
                misfire_grace_time=misfire_grace_time,
            )
        # elif trigger_type == 'cron':
        #     # CronTrigger 需要更多的字段配置，这里我不想玩
        #     pass
        else:
            return fail_api(message="无效触发器类型")

        return success_api(message="更新job成功")
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# 删除job
@task_api.delete('/jobs')
@check_permission("jobs:delete")
def delete_job():
    try:
        # 解析请求的 JSON 数据
        request_data = request.get_json()

        if not request_data or 'ids' not in request_data:
            return fail_api(message='没有选中数据行或请求数据无效', status_code=400)

        ids_to_delete = request_data['ids']

        # 确保 ids_to_delete 是一个列表, 且不为空列表
        if not isinstance(ids_to_delete,list) or not ids_to_delete:
            return fail_api(message='ID 列表无效',status_code=400)

        # 删除
        for row_id in ids_to_delete:
            scheduler.remove_job(str(row_id))

        return success_api(message="删除job成功")
    except Exception as e:
        return fail_api(message=f"{str(e)}")


# 恢复job
@task_api.patch('/jobs/<job_id>/resume')
@check_permission("jobs:update")
def resume_job(job_id=None):
    job_id = request.json.get('id')
    # print(f"启用任务，ID为{job_id}")
    task_logger.info(f"启用任务，ID为{job_id}")
    if job_id:
        scheduler.resume_job(str(job_id))
        return success_api(message="启动成功")
    return fail_api(message="数据错误")


# 暂停job
@task_api.patch('/jobs/<job_id>/pause')
@check_permission("jobs:update")
def pause_job(job_id=None):
    job_id = request.json.get('id')
    # print(f"暂停任务，ID为{job_id}")
    task_logger.info(f"暂停任务，ID为{job_id}")
    if job_id:
        scheduler.pause_job(str(job_id))
        return success_api(message="暂停成功")
    return fail_api(message="数据错误")
