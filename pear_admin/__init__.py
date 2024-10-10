from datetime import datetime
from flask import Flask, render_template, request

from configs import config
from pear_admin.apis import register_apis
from pear_admin.extensions import register_extensions, load_jobs_from_storage
from pear_admin.orms import UserORM
from pear_admin.views import register_views
from pear_admin.apis.http import fail_api
from configs import get_logger

access_logger = get_logger('access_log')


# config_name 传入config.py文件里定义的配置（dev test prod, 开发，测试，生产）
def create_app(config_name="dev"):
    app = Flask("pear-admin-flask")

    app.config.from_object(config[config_name])

    register_extensions(app)
    register_apis(app)

    register_views(app)

    # 从存储器中加载任务
    load_jobs_from_storage()

    @app.errorhandler(403)
    def handle_403(e):
        """
        添加是否是ajax请求的逻辑判断
        对于 AJAX 请求：
            如果请求是 AJAX 请求（即 X-Requested-With 头为 XMLHttpRequest），返回 JSON 错误响应。
            这对前端处理 AJAX 错误特别有用，使得错误信息可以以 JSON 格式传递并在前端处理。
        对于非 AJAX 请求：
            如果请求不是 AJAX 请求，将返回 HTML 错误页面，这样用户可以看到友好的错误页面，而不是直接看到 JSON 错误信息。
        :param e:
        :return:
        """
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # 返回 JSON 错误响应
            return fail_api(message="权限不足，请联系管理员", status_code=403)
        else:
            # 返回 HTML 错误页面
            return render_template('error/403.html')
        # return render_template("error/403.html")

    @app.errorhandler(404)
    def handle_404(e):
        return render_template("error/404.html")

    @app.errorhandler(500)
    def handle_500(e):
        return render_template("error/500.html")

    @app.after_request
    def after_request(response):
        """
        waitress不显示每个请求的日志，只显示错误信息
        通过after_request还原日志记录
        使用 flask run 启动时注释此函数 ！！！
        :param response:    
        :return:
        """

        # 提取 HTTP 方法、路径、HTTP 版本和状态码
        method = request.method
        path = request.path
        http_version = request.environ.get('SERVER_PROTOCOL','HTTP/1.1')
        status_code = response.status_code
        remote_addr = request.remote_addr
        date_time = datetime.now().strftime('%d/%b/%Y %H:%M:%S')

        # 记录请求处理时间的日志
        access_logger.info(f'{remote_addr} - - [{date_time}] "{method} {path} {http_version}" {status_code} -')
        return response

    return app


__all__ = ["UserORM"]
