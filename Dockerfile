# 使用官方的 Python 镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 将当前目录的内容复制到容器的工作目录中
COPY . .

# 设置时区为 Asia/Shanghai
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone

# 安装所需的依赖
# 国内源
# RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
# 直通
RUN pip install -r requirements.txt

# 运行数据库初始化脚本
RUN flask init

# 运行`generate_secret_key.py`随机生成32 字节的 SECRET_KEY，然后自动写入configs.py文件
RUN python generate_secret_key.py

# 暴露应用使用的端口
# 只是一个标记指示，实际操作中使用其他端口并不影响
# 规范使用的话与实际使用的端口一致
EXPOSE 8080

# 运行 Flask 应用
CMD ["waitress-serve", "--call", "pear_admin:create_app"]
