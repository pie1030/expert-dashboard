# 专家画像 Dashboard - Docker 镜像
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app/ ./app/
COPY static/ ./static/
COPY run.py .

# 创建上传目录
RUN mkdir -p uploads

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "8080"]
