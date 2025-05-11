# 更新日志

## [1.0.2] - 2025-05-11

### 变更

- 修改tag版本号为：v1.0.2
- 修改IP地址信息表数据-查询接口，禁用自动重定向（解决**308 重定向问题**）
- 添加在线Demo：https://kucsexuzxxdj.ap-northeast-1.clawcloudrun.com/  (用户名/密码：admin/123456)

## [0.2] - 2024-10-13

### 变更

- 修改`pear_admin\extensions\tasks\snmp_polling.py`文件OID字典的值类型为字符串
- 修改`port_type`值为列表，当需要`snmp`获取`port_type`值时，循环尝试列表中的元素，返回值为true时中断循环

---

## [0.2] - 2024-10-10

### 新增

- 添加`dockerfile`文件，用于构建镜像

### 变更

- 修改IP地址信息查询接口返回结果以`ip`字段升序
- 修改IP地址信息页面空IP行背景色为`#FFFACD`

### 修复

- 修复分组重命名的问题，在`pear_admin\apis\group.py`文件第`130`行添加 传递参数 `gid=None `
- 修复IP地址表数据中有IP地址，掩码，网段的值为None的行，导致在分组页面不能点击树组件子节点问题

---

## [0.2] - 2024-09-09

### 新增

- 添加日志记录到文件功能
- 添加`pear_admin/extensions/tasks/tasks.json` `snmp`轮询参数配置文件，可于应用配置页面修改写入
- 添加`generate_secret_key.py`文件，用于随机生成的32字节的 SECRET_KEY并写入configs.py配置文件
- 添加`waitress`作为`wsgi`启动flask
- 添加bat启动脚本启动flask
- 添加after_request函数用于还原waitress不显示的请求日志
- 添加离线安装包目录`whls`

### 变更

- `snmp`轮询参数的配置文件移动到`pear_admin/extensions/tasks/tasks.json`文件
- 修改日志界面显示内容
- 修改IP地址信息页面和日志页面的`defaultToolbar`导出功能为导出所有
- README文件变更说明

### 修复

- 修复IP地址表数据中有IP地址，掩码，网段的值为None的行，导致在分组页面不能点击树组件子节点问题

### 安全改进

- SECRET_KEY生成写入

---

## [0.2] - 2024-09-05

### 新增

- 添加CHANGELOG.md文件
- 添加requirements.txt
- 添加LICENSE文件
- 添加IP地址表数据页面及接口
- 添加分组数据页面及接口
- 添加定时任务页面及接口
- 添加IP分组修改页面及接口
- 添加应用配置页面
- 添加关于页面
- 添加用户密码修改显示页面及接口
- 添加API接口权限校验
- 添加普通用户注册接口

### 变更

- 修改favicon图标，title
- 修改login页面banner图片，缩放50%
- 修改login页面项目名称和描述
- 修改login页面默认用户名为admin
- 隐藏index框架消息中心
- 修改index框架头像右侧显示登陆用户名
- 修改首页显示内容
- 修改系统监控页面显示内容
- 修改`.flaskenv`文件，端口修改为`5666`
- 修改model字段属性（user字段非空要求）
- 权限新增页面：权限类型单选框原菜单修改为一级菜单，二级菜单
- 权限新增页面：类型列变更为一级菜单、二级菜单、路径、权限渲染显示
- 修改框架渲染左侧栏显示二级菜单缩进样式
- 修改login函数登陆成功返回的access_token中包含附加声明权限列表
- 修改使用pip包管理

### 删除

- 删除poetry相关文件

### 安全改进

- 添加API接口权限校验装饰器

---

