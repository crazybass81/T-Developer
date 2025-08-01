from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.nl_agent_api import router as nl_basic_router
from src.api.nl_advanced_api import router as nl_advanced_router

app = FastAPI(
    title="T-Developer NL Input Agent",
    description="AI-powered natural language processing for project requirements",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(nl_basic_router)
app.include_router(nl_advanced_router)

@app.get("/")
async def root():
    return {
        "message": "T-Developer NL Input Agent API",
        "version": "1.0.0",
        "features": [
            "Basic NL processing",
            "Multimodal input support",
            "Domain-specific analysis",
            "Intent analysis",
            "Requirement prioritization",
            "Performance optimization"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nl-input-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)