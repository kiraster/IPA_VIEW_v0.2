@echo off
setlocal

:: 关闭 Flask 应用
:: 终止python进程
:: 使用 taskkill 命令终止
taskkill /F /IM python.exe

:: 结束
echo Flask application stopped.

endlocal
