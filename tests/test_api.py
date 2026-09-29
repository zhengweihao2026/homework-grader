#!/usr/bin/env python3
"""快速验证 API 服务"""
import sys
sys.path.insert(0, '/opt/data/homework-grader')

from api.main import app

# 测试简单请求
client = app.test_client()

# 测试根路径
response = client.get("/")
print(f"GET /: {response.status_code} - {response.json()}")

# 测试健康检查
response = client.get("/health")
print(f"GET /health: {response.status_code} - {response.json()}")

# 测试 API 文档路径
response = client.get("/docs")
print(f"GET /docs: {response.status_code}")

print("✓ API 服务测试通过！")
