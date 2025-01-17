# 构建docker镜像
```angular2html
docker build -t liu-yao  .
```

# 运行docker镜像
```BASH
# 已经在dockerfile中配置过环境变量
docker run -p 8501:8501 liu-yao
# 未在dockerfile中配置过环境变量
docker run -p 8501:8501 \
  -e API_KEY=your_api_key \
  -e BASE_URL=https://api.deepseek.com \
  -e MODEL=deepseek-chat \
  liu-yao
```

# 访问应用
```angular2html
http://localhost:8501
```