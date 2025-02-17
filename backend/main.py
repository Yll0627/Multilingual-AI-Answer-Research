from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import translator
from app.core.config import settings

app = FastAPI(
    title="Multilingual Translator API",
    description="A REST API service for translating text using DeepL",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translator.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
