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
cd onii
pip install -r requirements.txt
python manage_dev.py migrate
python manage_dev.py init_security
python manage_dev.py runserver 8000
# 另一个终端
python manage_dev.py qcluster
```

### 2. Docker Compose 部署 (推荐)

```bash
cd onii
docker compose up -d
docker compose logs -f web
```

### 3. 单镜像部署

```bash
./build.sh 1.0.0
# 目标机
docker load < onii-1.0.0.tar
docker run -d -p 8000:8000 -v ./conf:/home/onii/conf onii:1.0.0
```

### 4. 裸机部署

```bash
cd onii
pip install -r requirements.txt
chmod +x start.sh
./start.sh
```

## 配置说明

配置文件位于 `onii/conf/` 目录：dev.yaml (开发) / prod.yaml (生产)。

### 数据库切换

```yaml
database:
  engine: sqlite    # sqlite / mysql / pgsql
  name: db.sqlite3
  host: 127.0.0.1
  port: 3306
  user: root
  password: ''
  db_name: onii
```

### 安全配置

```yaml
security:
  ip_whitelist_enabled: false
  api_sign_enabled: false
  api_sign_secret: 'your-secret'
  password_history_count: 5
  max_sessions: 3
```

### CORS 配置

```yaml
cors:
  allow_all: false
  allow_credentials: true
  allowed_origins:
    - https://your-domain.com
```

## API 文档

启动后访问：
- `/api/docs/` — Swagger UI
- `/api/redoc/` — ReDoc
- `/api/schema/` — OpenAPI 3.0 Schema

## API 接口总览

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login` | 登录 |
| GET | `/api/auth/info` | 当前用户信息 |
| POST | `/api/auth/change_password` | 修改密码 |
| POST | `/api/auth/logout` | 登出 |
| POST | `/api/auth/token/refresh` | 刷新 JWT |

### 用户管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/users` | 列表/创建 |
| PUT/DELETE | `/api/users/{id}` | 更新/禁用 |
| POST | `/api/users/{id}/reset-password` | 重置密码 |
| POST | `/api/users/{id}/assign-roles` | 分配角色 |

### 角色管理
| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/roles` | 角色增删改查 |

### 系统
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/monitor` | CPU/内存/磁盘/网络 |
| GET | `/api/health` | 健康检查(无需认证) |
| CRUD | `/api/configs` | 系统配置 KV |
| GET | `/api/configs/public` | 公开配置(无需认证) |

### 字典管理
| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/dict-types` | 字典类型 |
| CRUD | `/api/dict-data?type_code=xxx` | 字典数据 |

### 定时任务
| 方法 | 路径 | 说明 |
|------|------|------|
| CRUD | `/api/schedules` | Django-Q Schedule |

### 审计日志
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/audit-logs` | 审计日志 |
| GET | `/api/login-logs` | 登录日志 |

### Django Admin
`/admin/` — 用户/角色/配置/字典/日志管理

## 权限体系 (RBAC 三权分立)

| 角色 | 权限 |
|------|------|
| system_admin | 用户CRUD、系统配置、字典、监控、任务 |
| security_admin | 角色管理、权限分配、IP白名单、密码策略 |
| audit_admin | 审计日志、登录日志、监控 |
| user | 业务接口 |

## 安全特性

- JWT 认证 (access 2h / refresh 7d + token 黑名单)
- 登录失败锁定 (5次/30分钟)
- 密码策略 (大小写+数字+特殊字符，禁复用最近5次)
- 首次登录强改密码
- 会话并发控制 (超限自动踢)
- IP 白名单 (CIDR)
- API 限流 (匿名30/min，认证120/min)
- API 签名 (HMAC-SHA256 + nonce 防重放，可选)
- 审计日志 (自动记录写操作)
- 操作二次确认 (RequirePasswordConfirmation)
- 安全头 (X-Frame-Options / X-Content-Type-Options / XSS)
- 请求体限制 (10MB)

## 工具类

| 模块 | 功能 |
|------|------|
| `utils/soft_delete.py` | SoftDeleteMixin 软删除 |
| `utils/confirm_password.py` | 危险操作密码确认 |
| `utils/excel_util.py` | Excel/CSV 导入导出 |
| `utils/page_util.py` | 分页 |
| `utils/drf_util.py` | SuccessResponse/ErrorResponse |

## 项目结构

```
onii/
├── conf/                  # YAML 配置
├── onii/                  # Django 项目设置
├── app/
│   ├── admin.py           # Django Admin
│   ├── urls.py            # API 路由
│   ├── model/auth/        # 用户/角色/日志
│   ├── model/system/      # 配置/字典
│   ├── api/v1/auth/       # 认证 API
│   ├── api/v1/system/     # 监控/配置/字典 API
│   └── api/v1/task/       # 任务 API
├── middleware/             # 审计/IP白名单/签名
├── utils/                 # 工具类
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
