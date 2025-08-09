"""
T-Developer MVP - Basic Entry Point (Skeleton)

⚠️  이 파일은 기본 스켈레톤입니다.
🚀 실제 프로덕션 API는 src/main_api.py를 사용하세요!

Features: 기본 health check만 제공
Production API: src/main_api.py (9-Agent Pipeline, Bedrock 통합)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(
    title="T-Developer MVP",
    description="AI Multi-Agent Development Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "T-Developer MVP Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )