"""
Gold Analysis Extend - FastAPI 主程式
投資組合管理、告警系統、回測系統、報告生成
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api import portfolios_router


app = FastAPI(
    title="Gold Analysis Extend API",
    description="黃金分析系統延伸功能 - 投資組合管理、告警、回測、報告",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境應限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(portfolios_router)


@app.get("/")
async def root():
    """根路徑"""
    return {
        "name": "Gold Analysis Extend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康檢查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
