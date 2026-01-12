#!/bin/bash

# 1. 构建 Docker 镜像
echo "正在构建 Docker 镜像..."
docker build -t xiaomusic-netease .

# 2. 停止并删除旧容器（如果存在）
echo "清理旧容器..."
docker stop xiaomusic-custom 2>/dev/null
docker rm xiaomusic-custom 2>/dev/null

# 3. 运行新容器
# -p 8080:8080: 将宿主机的 8080 端口映射到容器的 8080 端口
# -e XIAOMUSIC_PORT=8080: 告诉应用程序监听 8080 端口
# -v $(pwd)/music:/app/music: 挂载音乐目录
# -v $(pwd)/conf:/app/conf: 挂载配置目录
echo "启动新容器..."
docker run -d \
  --name xiaomusic-custom \
  --restart unless-stopped \
  -p 8080:8080 \
  -e XIAOMUSIC_PORT=8080 \
  -v "$(pwd)/music:/app/music" \
  -v "$(pwd)/conf:/app/conf" \
  xiaomusic-netease

echo "部署完成！"
echo "服务已运行在: http://localhost:8080"
