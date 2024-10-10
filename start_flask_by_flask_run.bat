@echo off 
REM 确保脚本运行时的工作目录是批处理文件所在的目录 
cd /d %~dp0 
REM 激活conda虚拟环境 
call D:\miniconda3\Scripts\activate pear-admin-flask-base
REM 启动Flask应用
flask run