import os
from datetime import timedelta
import logging
import logging.config


class BaseConfig:

    # 使用随机生成的32字节的 SECRET_KEY，运行项目根目录下的 generate_secret_key.py 脚本文件后自动写入以下SECRET_KEY
    SECRET_KEY = "ed8d8d3dec07b0fe6f0223f3b9e1f5bc5218f6ad482e0ce72d410bc532d93e87"

    SQLALCHEMY_DATABASE_URI = ""

    ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

    JWT_TOKEN_LOCATION = ["headers"]
    # 设置 token 有效期 7 days
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)


# APScheduler参数定义
class APSchedulerConfig:

    # 重新开始定时任务间隔时间，单位 秒
    # RESUME_TIME = 300

    # 配置 SCHEDULER_API_ENABLED = True 在 Flask 中启用 Flask-APScheduler 的 REST API，允许通过 HTTP 请求管理调度任务
    # 本代码中采用自定义接口处理定时任务的http请求，所以关闭此项
    SCHEDULER_API_ENABLED = False

    # 任务配置
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': True,  # True，任务堆积后，恢复运行的时候，会只执行一次
        'max_instances': 64,  # 同一个任务同一时间最多只能有5个实例在运行
        'misfire_grace_time': 1  # 任务错过执行的最大宽限时间（秒）
    }
    # 执行器
    SCHEDULER_EXECUTORS = {
        'default': {
            'type': 'threadpool',
            'max_workers': 20
        }
    }
    # 任务存储器
    # 前面已经定义过项目根目录，但是不想绕进多继承烧脑
    ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.path.join(ROOT_PATH,'instance/scheduler.db')

    SCHEDULER_JOBSTORAGE = 'sqlalchemy'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'  # 任务存储器数据库 URI
    SCHEDULER_JOBSTORAGE_OPTIONS = {
        'url': f'sqlite:///{DATABASE_PATH}'  # 存储器 URL
    }
    SCHEDULER_JOBSTORES = {
        'default': {
            'type': 'sqlalchemy',
            'url': f'sqlite:///{DATABASE_PATH}'
        }
    }
    SCHEDULER_JOB_TRIGGERS = {
        'interval': {
            'type': 'interval',
            'minutes': 1
        },
        'cron': {
            'type': 'cron',
            'minute': '*/5'
        }
    }
    SCHEDULER_TIMEZONE = 'UTC'


# SNMP轮询参数定义,转到pear_admin\extensions\tasks\tasks.json文件修改，或登陆到应用配置页面添加
# class SNMPConfig:
#
#     # 判断IP地址是否离线，当IP地址最后更新时间 < （当前时间 - 设定的值(单位 分钟)），判定IP地址离线
#     REFRESH_TIME = 30
#
#     # 网关设备snmp
#     SNMP_DATA_GW = [
#         {'snmp_host': '10.10.10.22', 'snmp_community': 'public'},
#         {'snmp_host': '10.10.10.11', 'snmp_community': 'public'},
#     ]
#     # 接入交换机或汇聚交换机snmp
#     SNMP_DATA_ACC = [
#         {'snmp_host': '10.10.10.11', 'snmp_community': 'public'},
#         {'snmp_host': '10.10.10.33', 'snmp_community': 'public'},
#         {'snmp_host': '10.10.10.44', 'snmp_community': 'public'},
#     ]


class DevelopmentConfig(BaseConfig, APSchedulerConfig):
    """开发配置"""

    DEBUG = True
    # 定义使用数据库，sqlite
    SQLALCHEMY_DATABASE_URI = "sqlite:///ipa_view.db"
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/ipa_view"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(BaseConfig, APSchedulerConfig):
    """测试配置"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # 内存数据库


class ProductionConfig(BaseConfig, APSchedulerConfig):
    """生产环境配置"""

    DEBUG = False
    # SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1:3306/ipa_view"
    SQLALCHEMY_DATABASE_URI = "sqlite:///ipa_view.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {"dev": DevelopmentConfig, "test": TestingConfig, "prod": ProductionConfig}


# 日志记录
class LogingConfig:

    # 前面已经定义过项目根目录，但是不想绕进多继承烧脑
    ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
    LOG_PATH = os.path.join(ROOT_PATH, 'log')

    # 如果不存在定义的日志目录就创建一个
    if not os.path.isdir(LOG_PATH):
        os.mkdir(LOG_PATH)
    # log文件的全路径
    logfile_path = os.path.join(LOG_PATH, 'log.log')

    # logging配置
    # 定义三种日志输出格式 开始
    standard_format = '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]' \
                      '[%(levelname)s][%(message)s]'  # 其中name为getlogger指定的名字
    simple_format = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
    id_simple_format = '[%(levelname)s][%(asctime)s] %(message)s'

    # 定义日志输出格式 结束

    # log配置字典
    LOGGING_DIC = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': standard_format
            },
            'simple': {
                'format': simple_format
            },
        },
        'filters': {},
        'handlers': {
            # 打印到终端的日志
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',  # 打印到屏幕
                'formatter': 'simple'
            },
            # 打印到文件的日志,收集info及以上的日志
            'default': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
                'formatter': 'standard',
                'filename': logfile_path,  # 日志文件
                'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                'backupCount': 5,
                'encoding': 'utf-8',  # 日志文件的编码
            },
        },
        'loggers': {
            # logging.getLogger(__name__)拿到的logger配置
            '': {
                'handlers': ['default',
                             'console'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
                'level': 'DEBUG',
                'propagate': True,  # 向上（更高level的logger）传递
            },
        },
    }


def get_logger(log_type):
    # 加载日志配置信息
    logging.config.dictConfig(LogingConfig().LOGGING_DIC)
    # 获取日志对象
    logger = logging.getLogger(log_type)
    return logger


