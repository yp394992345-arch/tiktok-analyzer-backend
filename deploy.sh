#!/bin/bash

# 这是一个简单的部署脚本
# 请在你的阿里云服务器上运行

echo "=== TikTok Analyzer 后端部署 ==="

# 1. 安装必要软件
echo "[1/4] 安装系统依赖..."
apt update && apt install -y python3 python3-pip git

# 2. 克隆代码
echo "[2/4] 下载后端代码..."
cd /root
git clone https://github.com/yp394992345-arch/tiktok-analyzer-backend.git
cd tiktok-analyzer-backend/app

# 3. 安装Python依赖
echo "[3/4] 安装Python依赖..."
pip3 install fastapi uvicorn python-multipart aliyun-python-sdk-core aliyun-python-sdk-vision-inverse

# 4. 配置环境变量
echo "[4/4] 启动服务..."
export TONGYI_QIANWEN_API_KEY="sk-cdfb23471e6145229e402b4b999c78d1"
export ALIYUN_VISION_ACCESS_KEY="LTAI5tCoJ7f2jBfs8fNp7M98"
export ALIYUN_VISION_SECRET_KEY="EZtKFXlFlJB5jndaYgURplVpdP1HlG"

# 启动后端
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /root/server.log 2>&1 &

echo "=== 部署完成 ==="
echo "检查服务: curl http://localhost:8000/docs"
