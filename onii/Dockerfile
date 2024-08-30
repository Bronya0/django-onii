FROM python:3.8.16-alpine3.17

ENV PYTHONUNBUFFERED 1

ENV TZ Asia/Shanghai

# 创建项目目录
RUN mkdir /home/onii \
    && sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories

WORKDIR /home/onii

COPY ./requirements.txt .

RUN ls -l && pip3 install --no-cache-dir -U pip -i https://mirrors.aliyun.com/pypi/simple \
    && pip3 install --no-cache-dir --upgrade setuptools -i https://mirrors.aliyun.com/pypi/simple \
    && pip3 install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

RUN rm -rf /var/cache/apk/* \
    && rm -rf /root/.cache/pip/*

COPY . .

RUN chmod +x ./start.sh
CMD ["sh", "-c", "sh ./start.sh"]