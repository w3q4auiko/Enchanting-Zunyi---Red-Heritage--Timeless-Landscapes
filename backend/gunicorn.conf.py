"""Gunicorn 生产运行配置模块。

本模块为旅游信息系统的后端 API 服务提供进程模型与日志配置。
默认 worker 数量遵循经验公式并设定上限，以适配 I/O 密集型服务在
高并发访问下的稳定性与资源成本控制。
"""

import multiprocessing
import os

bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:5000")

cpu_count = multiprocessing.cpu_count() or 1
default_workers = max(2, min(cpu_count * 2 + 1, 12))
workers = int(os.environ.get("GUNICORN_WORKERS", default_workers))
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "gevent")

timeout = int(os.environ.get("GUNICORN_TIMEOUT", 60))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", 30))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", 5))

accesslog = os.environ.get("GUNICORN_ACCESS_LOG", "-")
errorlog = os.environ.get("GUNICORN_ERROR_LOG", "-")
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
