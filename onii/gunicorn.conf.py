import multiprocessing

# 工作进程数, 通常设置为 2 * CPU 核心数 + 1，上限 16
workers = min(multiprocessing.cpu_count() * 2 + 1, 16)
# 指定每个工作者的线程数
threads = 4
# 监听端口
bind = '0.0.0.0:8000'
# 请求超时
timeout = 120
# 优雅关闭超时
graceful_timeout = 30
# Keep-Alive 连接等待时间
keepalive = 5
# 日志输出到 stdout/stderr（Docker 友好）
accesslog = '-'
errorlog = '-'
loglevel = 'info'
# 使用多线程 worker
worker_class = 'gthread'
# 预加载应用（节省内存）
preload_app = True
# worker 回收：处理指定请求数后重启（防止内存泄漏）
max_requests = 2000
max_requests_jitter = 200
