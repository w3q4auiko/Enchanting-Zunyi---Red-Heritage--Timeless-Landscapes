# -----------------------------------------------------------------------------
# 后端服务镜像构建脚本
# 用于构建旅游信息系统 API 的运行镜像，强调依赖可移植与镜像体积可控，
# 以便在多环境部署中保持一致的性能与安全基线。
# -----------------------------------------------------------------------------

FROM python:3.11-slim

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# 系统级构建依赖与数据库客户端支持，保障 Python 扩展与 MySQL 驱动可用。
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    pkg-config \
    default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

# 依赖层单独拷贝，保持镜像缓存命中以缩短构建时间。
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
