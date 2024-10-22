## 项目简介

**版本:** 0.2

**发布日期:** 2024-09-05

**代码框架:** 基于[pear-admin-flask](https://gitee.com/pear-admin/pear-admin-flask) Python后台管理系统进行二次开发

**功能描述:** 基于SNMP轮询的IP地址管理检测

**实现逻辑:** 通过SNMP协议轮询交换机设备，获取ARP，MAC地址，端口类型，端口索引，系统名称，子网掩码等信息后进行逻辑判断处理

**感谢:** [pear-admin-flask](https://gitee.com/pear-admin/pear-admin-flask) Python 后台管理系统开源项目及其贡献者

## 安装使用

### 下载源码

git clone 或 Download ZIP

### 手搓安装

#### 配置虚拟环境

使用虚拟环境并不是必须的，考虑到可能会冲突或干扰你本机的Python环境，建议使用虚拟环境

- 本项目开发环境：Windows+Python 3.10+Miniconda
- Conda是软件包管理系统和环境管理系统，**Miniconda** 是一个更加轻量级的选项
- 使用任意虚拟环境，不挑食

```
# 使用venv
# 创建虚拟环境
python -m venv venv
#  进入虚拟环境
.\venv\Scripts\activate

# 使用miniconda3
# 创建一个虚拟环境（指定Python版本3.10）
conda create -n ipa_base python=3.10 -y
# 激活虚拟环境
conda activate ipa_base
```

#### 安装库

##### 在线安装

```
pip install -r requirements.txt

# 网络不行用下面这两之一

pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/  -r requirements.txt
或
pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

##### 离线安装

点击右侧`Releases`，已上传使用通过 `pip download -r requirements.txt -d whls` 下载的离线依赖包，也可自行使用该命令下载离线依赖包

windows系统

```
pip install --no-index --find-links=whls-windows -r requirements.txt 
```

linux系统

```
pip install --no-index --find-links=whls-linux -r requirements.txt 
```

#### 配置SECRET_KEY

运行`generate_secret_key.py`随机生成32 字节的 SECRET_KEY，然后自动写入configs.py文件

SECRET_KEY用于加密和签名会话 cookies 和其他重要数据, 帮助保护数据的完整性，防止篡改。

```
python generate_secret_key.py
Generated SECRET_KEY: fa0f839b85803b1e40163f6621643b0fb284cbfb8e9d02e8376e58d1b6d44ad3
```

#### 修改配置

1、修改启动配置`.flaskenv`（**flask run命令启动使用，调试阶段使用，正常运行后选择使用waitress**）

- `FLASK_DEBUG`：正常运行后建议修改为False（使用waitress启动，需要在配置文件修改）
- `FLASK_RUN_PORT`：设置端口不与本机其它监听端口冲突
- `FLASK_RUN_HOST`：如不为4个0，可设置具体本机网卡IP地址

```
FLASK_DEBUG=True                # 开启调试模式
FLASK_RUN_PORT=5666             # 设置运行的端口
FLASK_RUN_HOST=0.0.0.0          # 设置监听的 ip
FLASK_APP="pear_admin:create_app()"   # 运行程序
```

2、修改`configs.py`文件（按照注释说明按需修改，正常使用默认值即可）

3、修改`pear_admin/extensions/tasks/tasks.json`文件（snmp的轮询参数，替换为实际使用，或通过web页面-系统设置-应用配置中的SNMP参数配置修改提交）

```
{
  "REFRESH_TIME": 30,
  "SNMP_DATA_GW": [
    {
      "snmp_host": "1.1.1.1",
      "snmp_community": "public"
    }
  ],
  "SNMP_DATA_ACC": [
    {
      "snmp_host": "1.1.1.2",
      "snmp_community": "public"
    }
  ]
}
```

#### 初始化写入数据

1、按需修改`static\data`路径下的csv初始化数据

- `static\data\ums_user.csv`: 添加或修改初始登陆用户和密码（密码是经过计算后的hash值，最终储存在数据库）,
- `static\data\ip_group.csv`: 添加需要创建的分组名称
- `static\data\ip_table.csv`:（可选）添加测试数据

2、执行初始化数据库

```
flask init
```

#### 启动Flask

方式一（flask启动，使用内置类wsgi）

```
flask run
```

方式二（flask启动脚本，使用前如有虚拟环境需修改激活虚拟环境命令）

```
双击start_flask_by_flask_run.bat脚本
```

方式三（waitress启动，设置参数，使用waitress）

```
waitress-serve --port 5666  --call  pear_admin:create_app
```

方式三（waitress启动脚本，设置参数，使用前如有虚拟环境需修改激活虚拟环境命令）

```
双击start_flask_by_waitress.bat脚本
```

### docker安装

**如需修改代码内容，如修改dockerfile文件、修改配置、修改初始化数据等，需在构建镜像步骤前完成**

#### 构建镜像

在项目根目录下执行

```
docker build -t ipa-view:v0.2 .
```

#### 创建并运行 Docker 容器

在项目根目录下执行

```
docker run -d --restart always -p 5666:8080 ipa-view:v0.2
```

这里贴上将代码进行docker容器化的笔记提供参考：https://kiraster.github.io/posts/297bc3bd.html

## 关于定时任务

使用flask-apscheduler的API接口管理定时任务，预先在`pear_admin\extensions\tasks\tasks.py`文件里编写功能函数代码，然后在`定时任务`页面通过添加功能设置ID，名称，函数，间隔时间等参数提交即可

本项目中定义了两个功能函数和测试函数

- job1：定时轮询网关ARP表和接入交换机mac地址表任务
- job2：定时更新没有轮询到ARP表项的IP地址状态任务
- test：定时控制台打印测试内容

## 项目功能

本项目中各个页面详细功能说明，运行代码后，在`系统设置` -->> `关于`查看

## API和路由

（仅列出本代码创建的API和路由，原  [pear-admin-flask](https://gitee.com/pear-admin/pear-admin-flask)  内容请移步到源码仓库浏览）

| Endpoint                             | Methods | Rule                                   | Description                  |
| ------------------------------------ | ------- | -------------------------------------- | ---------------------------- |
| api.ip_group.add_groups              | POST    | /api/v1/groups/                        | 增加分组                     |
| api.ip_group.delete_groups           | DELETE  | /api/v1/groups/                        | 删除分组                     |
| api.ip_group.get_pie_groups          | GET     | /api/v1/groups/pie                     | 获取饼图渲染数据             |
| api.ip_group.get_setting_groups      | GET     | /api/v1/groups/setting                 | 获取分组表格渲染数据         |
| api.ip_group.get_transfer_groups     | GET     | /api/v1/groups/transfer                | 获取分组穿梭框渲染数据       |
| api.ip_group.get_tree_groups         | GET     | /api/v1/groups/tree                    | 获取分组数组件渲染数据       |
| api.ip_group.join_groups             | PATCH   | /api/v1/groups/join                    | 网段加组                     |
| api.ip_group.leave_groups            | PATCH   | /api/v1/groups/leave                   | 网段离组                     |
| api.ip_group.search_groups           | GET     | /api/v1/groups/search                  | 搜索分组                     |
| api.ip_group.update_groups           | PATCH   | /api/v1/groups/<gid>                   | 更新分组                     |
| api.ip_table.delete_ips              | DELETE  | /api/v1/ips/                           | 删除IP地址                   |
| api.ip_table.get_ips                 | GET     | /api/v1/ips/                           | 获取IP地址表                 |
| api.ip_table.get_overview            | GET     | /api/v1/ips/statistics/overview        | 获取IP统计信息               |
| api.ip_table.polling_group_status    | GET     | /api/v1/ips/statistics/group           | 获取分组柱形图渲染数据       |
| api.ip_table.polling_ip_status       | GET     | /api/v1/ips/statistics/status          | 获取IP地址状态折线图渲染数据 |
| api.ip_table.search_ips              | GET     | /api/v1/ips/search                     | 搜索IP地址                   |
| api.ip_table.update_ips              | PATCH   | /api/v1/ips/<uid>                      | 更新IP地址                   |
| api.log.get_logs                     | GET     | /api/v1/logs/                          | 获取日志                     |
| api.monitor.get_disk_partition       | GET     | /api/v1/monitor/disk-partition         | 获取主机分区信息             |
| api.monitor.get_system_monitor       | GET     | /api/v1/monitor/system-info            | 获取主机系统信息             |
| api.monitor.polling_network_load     | GET     | /api/v1/monitor/network-load           | 获取主机网络负载             |
| api.monitor.polling_utilization      | GET     | /api/v1/monitor/utilization            | 获取主机CPU和内存利用率      |
| api.setting.get_app_settings         | GET     | /api/v1/app-settings/                  | 获取flask应用配置            |
| api.setting.update_base_app_settings | POST    | /api/v1/app-settings/base              | 更新flask基本配置            |
| api.setting.update_snmp_app_settings | POST    | /api/v1/app-settings/snmp              | 更新snmp轮询参数配置         |
| api.task.add_job                     | POST    | /api/v1/scheduler/jobs                 | 增加任务                     |
| api.task.delete_job                  | DELETE  | /api/v1/scheduler/jobs                 | 删除任务                     |
| api.task.get_jobs                    | GET     | /api/v1/scheduler/jobs                 | 获取任务列表                 |
| api.task.pause_job                   | PATCH   | /api/v1/scheduler/jobs/<job_id>/pause  | 暂停任务                     |
| api.task.resume_job                  | PATCH   | /api/v1/scheduler/jobs/<job_id>/resume | 恢复任务                     |
| api.task.update_job                  | PATCH   | /api/v1/scheduler/jobs/<job_id>        | 更新任务                     |
| api.user.update_pwd                  | PATCH   | /api/v1/user/pwd                       | 更新用户密码                 |
| index.index_page_view                | GET     | /view/start/index.html                 | 首页页面路由                 |
| index.monitor_view                   | GET     | /view/start/monitor.html               | 系统监控页面路由             |
| ip_mgmt.group_view                   | GET     | /view/ip_mgmt/groups.html              | 分组页面路由                 |
| ip_mgmt.ips_view                     | GET     | /view/ip_mgmt/ips.html                 | IP地址页面路由               |
| system.app_about_view                | GET     | /view/system/app-about.html            | 关于页面路由                 |
| system.app_setting_view              | GET     | /view/system/app-settings.html         | 应用设置页面路由             |
| system.apscheduler_view              | GET     | /view/system/app-scheduler.html        | 定时任务页面路由             |
| system.group_setting_view            | GET     | /view/system/groups-setting.html       | 分组修改页面路由             |
| system.pwd_change_view               | GET     | /view/system/pwd-change.html           | 更新用户密码页面路由         |

## 项目结构

```
│  .flaskenv
│  CHANGELOG.md  # 更新日志
│  configs.py  # 配置文件
│  Dockerfile  # Dockerfile文件
|  generate_secret_key.py  # 生成SECRET_KEY并写入configs.py的脚本文件
│  LICENSE  # license
│  README.md
│  requirements.txt  # 安装库
│  start_flask_by_flask_run.bat  # flask run 方式启动flask的bat脚本
│  start_flask_by_waitress.bat  # waitress 方式启动flask的bat脚本
│  stop_flask.bat  # 关闭Python进程，顺带关闭flask的bat脚本
│
├─instance
│      ipa_view.db  # 业务数据库
│      scheduler.db  # 定时任务存储数据
├─log
│      log.log  # 日志文件
│
├─pear_admin
│  │  __init__.py  # flask应用 入口工厂函数
│  │
│  ├─apis
│  │      department.py
│  │      group.py  # 分组相关接口
│  │      http.py
│  │      ip.py  # IP地址相关接口
│  │      log.py  # 日志文件获取接口
│  │      monitor.py  # 系统监控相关接口
│  │      passport.py
│  │      rights.py
│  │      role.py
│  │      setting.py  # 应用设置相关接口
│  │      task.py  # 定时任务相关接口
│  │      user.py
│  │      __init__.py
│  │
│  ├─extensions
│  │  │  comm.py  # 通用可复用函数
│  │  │  init_apscheduler.py
│  │  │  init_db.py
│  │  │  init_jwt.py
│  │  │  init_script.py
│  │  │  __init__.py
│  │  │
│  │  └─tasks
│  │          snmp_polling.py  # job1被调用函数
│  │          tasks.json  # 定时任务配置文件
│  │          tasks.py  # apscheduler定时任务入口
│  │          update_available.py  # job2被调用函数
│  │
│  ├─orms
│  │      department.py
│  │      ipgroup.py  # IP分组信息数据模型类
│  │      iptable.py  # IP地址信息数据模型类
│  │      rights.py
│  │      role.py
│  │      user.py
│  │      _base.py
│  │      __init__.py
│  │
│  └─views
│          index.py  # 开始页面路由
│          ip_mgmt.py # IP地址使用页面路由
│          system.py # 系统设置页面路由
│          __init__.py
│
├─static
│  │  favicon.ico
│  │
│  ├─admin
│  │  ├─css
│  │  │  │  admin.css
│  │  │  │  admin.dark.css
│  │  │  │  reset.css
│  │  │  │  variables.css
│  │  │  │
│  │  │  └─other
│  │  │          analysis.css
│  │  │          console.css
│  │  │          console2.css
│  │  │          exception.css
│  │  │          login.css
│  │  │          profile.css
│  │  │          result.css
│  │  │
│  │  ├─data
│  │  │      menu.json
│  │  │      message.json
│  │  │      table.json
│  │  │
│  │  └─images
│  │          avatar.jpg
│  │          background.svg
│  │          banner.png
│  │          banner2.png
│  │          banner2.svg
│  │          blog.jpg
│  │          captcha.gif
│  │          ip_group_ref.png
│  │          logo.png
│  │          user_right_ref.png
│  │
│  ├─component
│  │  ├─layui
│  │  │  │  layui.js
│  │  │  │
│  │  │  ├─css
│  │  │  │      layui.css
│  │  │  │
│  │  │  └─font
│  │  │          iconfont.eot
│  │  │          iconfont.svg
│  │  │          iconfont.ttf
│  │  │          iconfont.woff
│  │  │          iconfont.woff2
│  │  │
│  │  └─pear
│  │      │  pear.js
│  │      │
│  │      ├─css
│  │      │  │  pear.css
│  │      │  │
│  │      │  └─module
│  │      │          global.css
│  │      │          menu.css
│  │      │          menuSearch.css
│  │      │          messageCenter.css
│  │      │          nprogress.css
│  │      │          page.css
│  │      │          tabPage.css
│  │      │          toast.css
│  │      │
│  │      ├─font
│  │      │      iconfont.css
│  │      │      iconfont.js
│  │      │      iconfont.json
│  │      │      iconfont.ttf
│  │      │      iconfont.woff
│  │      │      iconfont.woff2
│  │      │
│  │      └─module
│  │          │  admin.js
│  │          │  button.js
│  │          │  fullscreen.js
│  │          │  menu.js
│  │          │  menuSearch.js
│  │          │  messageCenter.js
│  │          │  page.js
│  │          │  tabPage.js
│  │          │  tools.js
│  │          │
│  │          └─extends
│  │                  count.js
│  │                  echarts.js
│  │                  echartsTheme.js
│  │                  nprogress.js
│  │                  popup.js
│  │                  toast.js
│  │                  yaml.js
│  │
│  ├─config
│  │      pear.config.json
│  │
│  ├─data
│  │      databases.sql
│  │      ip_group.csv  # IP分组信息导入数据
│  │      ip_table.csv  # IP地址信息导入数据
│  │      ums_department.csv
│  │      ums_rights.csv
│  │      ums_role.csv
│  │      ums_user.csv
│  │
│  └─js
│          moment.min.js
│          pear_admin_flask.js
│
└─templates
   ├─error
   │      403.html
   │      404.html
   │      500.html
   │      
   ├─system
   │  ├─department
   │  │      index.html
   │  │      
   │  ├─rights
   │  │      index.html
   │  │      
   │  ├─role
   │  │      index.html
   │  │      
   │  └─user
   │          index.html
   │
   └─view
      │  index.html
      │  login.html
      │  register.html
      │  
      │─ip_mgmt
      │     groups.html  # 分组页面模板
      │     ips.html  # IP地址信息页面模板
      │     
      │─start
      │      index.html  # 首页模板
      │      monitor.html  # 系统监控页面模板
      │      
      └─system
               app-about.html  # 关于页面模板
               app-log.html  # 日志页面模板
               app-scheduler.html  # 定时任务页面模板
               app-settings.html  # 应用设置页面模板
               groups-setting.html  # IP分组修改页面模板
               pwd-change.html  # 密码修改页面模板
```

## 预览

高清大图看这：https://kiraster.github.io/gallery/IPA_VIEW_v0.2/

![ScreenCaputure1314](https://s2.loli.net/2024/09/05/9ITPRYf1zLnGF7S.jpg)

![ScreenCaputure1320](https://s2.loli.net/2024/09/05/pWmb6NkjAiaZVPo.jpg)

![ScreenCaputure1002](https://s2.loli.net/2024/09/05/oxJPzlD2C59y8kg.jpg)

![ScreenCaputure1024](https://s2.loli.net/2024/09/05/tyvBxP4XSf8MaoL.jpg)

![ScreenCaputure1034](https://s2.loli.net/2024/09/05/DAUMrSmL9fWVdEk.jpg)

![ScreenCaputure1048](https://s2.loli.net/2024/09/05/M2DSuJlwQy4hFOX.jpg)

![ScreenCaputure1123](https://s2.loli.net/2024/09/05/1QdrTvIeKwZcoEm.jpg)

![ScreenCaputure1129](https://s2.loli.net/2024/09/05/KbI6FLyTg3OJV1e.jpg)

![ScreenCaputure1136](https://s2.loli.net/2024/09/05/t1dwSlQjhPaypes.jpg)

![ScreenCaputure1141](https://s2.loli.net/2024/09/05/Jruy1hIDbEVZFwj.jpg)

![ScreenCaputure1151](https://s2.loli.net/2024/09/05/q9pXZmtuohdF2WT.jpg)

![ScreenCaputure1205](https://s2.loli.net/2024/09/05/6Et3hdmPpXS4IfC.jpg)

![ScreenCaputure1222](https://s2.loli.net/2024/09/05/hBea8MQrO5pC6jF.jpg)

![ScreenCaputure1229](https://s2.loli.net/2024/09/05/B6jaXfFCIvbdM7N.jpg)

![ScreenCaputure4014](https://s2.loli.net/2024/09/06/P34mJrfnsOvI6lT.jpg)

![ScreenCaputure1235](https://s2.loli.net/2024/09/05/KyH4eF3Ct1gp9sr.jpg)

![ScreenCaputure1239](https://s2.loli.net/2024/09/05/zDsTL4KQIY7fZwl.jpg)
