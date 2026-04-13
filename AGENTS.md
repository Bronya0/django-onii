这是一个基于 Django + DRF + Django-Q 的后端项目模板，结构比较简洁：

项目概览：

onii/onii/ — Django 配置（settings、urls）
app/api/v1/ — API views (目前只有 async_task)
app/model/ — 数据模型
app/service/ — 业务逻辑层
app/filter/ — DRF 过滤器
app/serializer/ — DRF 序列化器
jobs/ — 定时任务 & 异步任务
utils/ — 工具类（分页、响应、Excel 等）
使用 Django-Q (ORM 模式) 做异步任务队列
SQLite 数据库、gunicorn 部署