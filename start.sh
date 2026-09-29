#!/bin/bash
cd /opt/data/homework-grader

# 检查依赖
if ! python3 -c "import fastapi, uvicorn, reportlab"; then
    echo "安装依赖中..."
    pip install -r requirements.txt
fi

# 启动服务
uvicorn api.main:app --host 0.0.0.0 --port 8000
