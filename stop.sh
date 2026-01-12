#!/bin/bash
echo "正在停止 xiaomusic-custom 容器..."
docker stop xiaomusic-custom

echo "正在删除 xiaomusic-custom 容器..."
docker rm xiaomusic-custom

echo "已停止并清理。"
