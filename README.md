# Onii 后台管理系统

基于 Django 5.2 LTS + DRF + Django-Q2 的通用后台管理系统。

## 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | Django 5.2 LTS + Django REST Framework |
| 认证 | JWT (simplejwt) |
| 异步任务 | Django-Q2 (ORM Broker) |
| 数据库 | SQLite / MySQL / PostgreSQL (YAML 配置切换) |
| API 文档 | drf-spectacular (Swagger / ReDoc) |
| 部署 | Docker / Docker Compose / 裸机 |

## 快速开始

### 1. 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage_dev.py migrate

# 初始化角色和管理员 (admin / Admin@123456)
python manage_dev.py init_security

# 启动开发服务
python manage_dev.py runserver 8000

# 启动任务队列 (另一个终端)
python manage_dev.py qcluster
```

### 2. Docker Compose 部署 (推荐)

```bash
# 启动所有服务 (web + worker + postgres)
docker compose up -d

# 查看日志
docker compose logs -f web
```

### 3. 单镜像部署

```bash
# 构建并导出
./build.sh 1.0.0

# 目标机导入
docker load < onii-1.0.0.tar
docker run -d -p 8000:8000 -v ./conf:/home/onii/conf onii:1.0.0
```

### 4. 裸机部署

```bash
pip install -r requirements.txt
chmod +x start.sh
./start.sh
```

## 配置说明

配置文件位于 `conf/` 目录：
- `conf/dev.yaml` — 开发环境
- `conf/prod.yaml` — 生产环境

### 数据库切换

```yaml
database:
  engine: sqlite    # sqlite / mysql / pgsql
  name: db.sqlite3  # SQLite 文件名
  host: 127.0.0.1   # MySQL/PG 主机
  port: 3306        # MySQL 3306 / PG 5432
  user: root
  password: ''
  db_name: onii
```

### 安全配置

```yaml
security:
  ip_whitelist_enabled: false    # IP 白名单
  api_sign_enabled: false        # API 签名验证
  api_sign_secret: 'your-secret' # HMAC 密钥
  password_history_count: 5      # 密码历史 (禁复用)
  max_sessions: 3                # 最大同时在线设备数
```

### CORS 配置

```yaml
cors:
  allow_all: false              # 开发环境可设 true
  allow_credentials: true
  allowed_origins:
    - https://your-domain.com
```

## API 文档

启动服务后访问：

| 地址 | 说明 |
|------|------|
| `/api/docs/` | Swagger UI 交互式文档 |
| `/api/redoc/` | ReDoc 阅读文档 |
| `/api/schema/` | OpenAPI 3.0 Schema |

## API 接口总览

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录 (返回 JWT + must_change_password) |
| GET | `/api/auth/info` | 当前用户信息 |
| POST | `/api/auth/change_password` | 修改密码 |
| POST | `/api/auth/logout` | 登出 (token 黑名单) |
| POST | `/api/auth/token/refresh` | 刷新 JWT |

### 用户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users` | 用户列表 |
| POST | `/api/users` | 创建用户 |
| PUT | `/api/users/{id}` | 更新用户 |
| DELETE | `/api/users/{id}` | 禁用用户 (软删除) |
| POST | `/api/users/{id}/reset-password` | 重置密码 (设 must_change_password) |
| POST | `/api/users/{id}/assign-roles` | 分配角色 |

### 角色管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/roles` | 角色列表 |
| POST | `/api/roles` | 创建角色 |
| PUT | `/api/roles/{id}` | 更新角色 |
| DELETE | `/api/roles/{id}` | 删除角色 (内置角色不可删) |

### 系统监控

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/monitor` | CPU/内存/磁盘/网络/系统信息 |
| GET | `/api/health` | 健康检查 (无需认证) |

### 系统配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/configs` | 配置列表 |
| POST | `/api/configs` | 创建配置 |
| PUT | `/api/configs/{id}` | 更新配置 |
| GET | `/api/configs/public` | 公开配置 (无需认证) |
| GET | `/api/configs/groups` | 配置分组列表 |

### 字典管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/dict-types` | 字典类型列表 |
| GET | `/api/dict-types/{id}` | 字典类型详情 (含数据) |
| POST | `/api/dict-types` | 创建字典类型 |
| GET | `/api/dict-data?type_code=xxx` | 按类型编码查询字典数据 |
| POST | `/api/dict-data` | 创建字典数据 |

### 定时任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schedules` | 定时任务列表 |
| POST | `/api/schedules` | 创建定时任务 |
| PUT | `/api/schedules/{id}` | 更新定时任务 |
| DELETE | `/api/schedules/{id}` | 删除定时任务 |

### 审计日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/audit-logs?start=&end=&username=` | 审计日志 |
| GET | `/api/login-logs?username=&success=` | 登录日志 |

### Django Admin

| 地址 | 说明 |
|------|------|
| `/admin/` | Django 后台管理 (用户/角色/配置/字典/日志) |

## 权限体系 (RBAC 三权分立)

| 角色 | 代码 | 权限 |
|------|------|------|
| 系统管理员 | `system_admin` | 用户 CRUD、系统配置、字典管理、监控、定时任务 |
| 安全管理员 | `security_admin` | 角色管理、权限分配、IP 白名单、密码策略 |
| 审计管理员 | `audit_admin` | 审计日志、登录日志、监控 |
| 普通用户 | `user` | 业务接口访问 |

## 安全特性

- **JWT 认证** — access 2h / refresh 7d，token 轮转 + 黑名单
- **登录失败锁定** — 5 次失败锁定 30 分钟
- **密码策略** — 大小写 + 数字 + 特殊字符，禁复用最近 5 次密码
- **首次登录强改密码** — 管理员重置后必须修改
- **会话并发控制** — 超过设备数自动踢掉最早设备
- **IP 白名单** — CIDR 支持
- **API 限流** — 匿名 30/min，认证用户 120/min
- **API 签名** — HMAC-SHA256 + 时间戳 + nonce 防重放 (可选)
- **审计日志** — 自动记录所有写操作
- **操作二次确认** — `RequirePasswordConfirmation` 权限类 (按需挂载)
- **安全头** — X-Frame-Options / X-Content-Type-Options / XSS Filter
- **请求体限制** — 10 MB

## 工具类

| 模块 | 功能 |
|------|------|
| `utils/soft_delete.py` | `SoftDeleteMixin` 软删除混入 |
| `utils/confirm_password.py` | `RequirePasswordConfirmation` 危险操作确认 |
| `utils/excel_util.py` | Excel/CSV 导入导出 |
| `utils/page_util.py` | 分页工具 |
| `utils/drf_util.py` | `SuccessResponse` / `ErrorResponse` 统一响应 |

## 项目结构

```
onii/
├── conf/                      # YAML 配置 (dev/prod)
├── onii/                      # Django 项目配置
│   ├── settings.py            # 生产配置
│   └── settings_dev.py        # 开发配置
├── app/
│   ├── admin.py               # Django Admin 注册
│   ├── urls.py                # API 路由
│   ├── model/
│   │   ├── auth/              # 用户/角色/日志/密码历史
│   │   └── system/            # 系统配置/字典
│   ├── api/v1/
│   │   ├── auth/              # 认证/用户/角色/日志 API
│   │   ├── system/            # 监控/健康/配置/字典 API
│   │   └── task/              # 定时任务 API
│   └── serializer/            # DRF 序列化器
├── middleware/                 # 中间件
│   ├── audit_middleware.py     # 审计日志
│   ├── ip_whitelist_middleware.py
│   └── api_sign_middleware.py  # API 签名验证
├── utils/                     # 工具类
├── jobs/                      # 定时任务定义
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
