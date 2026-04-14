FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

WORKDIR /build

COPY requirements.txt .

# 安装编译依赖 + pip 依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libpq-dev default-libmysqlclient-dev pkg-config \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y gcc && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# ──────────── 运行阶段 ────────────
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 default-mysql-client curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash app

# 复制 pip 安装的包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /home/onii
COPY . .

RUN chmod +x entrypoint.sh start.sh \
    && chown -R app:app /home/onii

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -sf http://localhost:8000/api/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn.conf.py", "onii.wsgi:application"]