这是一个基于 Django + DRF + APScheduler 的后端项目模板，结构比较简洁：

项目概览：

onii/onii/ — Django 配置（settings、urls）
app/api/v1/ — API views
app/model/ — 数据模型
app/service/ — 业务逻辑层
app/filter/ — DRF 过滤器
app/serializer/ — DRF 序列化器
jobs/ — 定时任务（APScheduler 独立进程）
utils/ — 工具类（分页、响应、Excel 等）
使用 APScheduler 做定时任务调度（独立进程，不随 Django 启动）
SQLite 数据库、gunicorn 部署