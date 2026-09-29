# 家庭作业自动批改系统

孩子拍照上传数学作业，系统自动识别题目、判断对错、生成错题本。

## 技术栈
- 前端：Vue 3 + Vite
- 后端：FastAPI + Python
- 数据库：SQLite
- OCR：PaddleOCR

## 快速开始

```bash
cd homework-grader
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档
