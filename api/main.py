"""
API 主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="家庭作业自动批改系统", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from api.v1.routers.homework import router as homework_router

# 注册路由
app.include_router(homework_router, prefix="/api/v1", tags=["API"])

@app.get("/")
def root():
    return {"message": "欢迎使用家庭作业自动批改系统", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
