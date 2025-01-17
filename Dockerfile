# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt


# 暴露 Streamlit 的默认端口
EXPOSE 8501

# 设置环境变量（可选）
ENV STREAMLIT_HIDE_WARNING=1

# 启动 Streamlit 应用
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]