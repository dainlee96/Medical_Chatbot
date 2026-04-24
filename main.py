from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from celery.result import AsyncResult
from worker import celery_app, process_chat_message
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Medical AI Chatbot API", description="의료 RAG 챗봇 데모 API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프론트엔드 정적 파일 서빙
# frontend 디렉토리가 있을 때만 마운트하도록 예외 처리 (로컬 개발용)
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend", html=True), name="static")

class ChatRequest(BaseModel):
    user_id: str
    message: str

class TaskResponse(BaseModel):
    task_id: str

class ChatStatusResponse(BaseModel):
    status: str
    result: Optional[str] = None

@app.post("/api/chat", response_model=TaskResponse)
async def submit_chat(request: ChatRequest):
    """
    사용자의 메시지를 받아 백그라운드 Worker(Celery)에 추론(RAG 검색+LLM 생성)을 요청합니다.
    """
    # delay()를 통해 비동기로 함수를 백그라운드 워커에 전달
    task = process_chat_message.delay(request.user_id, request.message)
    return {"task_id": task.id}

@app.get("/api/chat/{task_id}", response_model=ChatStatusResponse)
async def get_chat_status(task_id: str):
    """
    Celery Worker의 작업 상태와 완료된 답변을 반환합니다. 클라이언트는 이 API를 폴링하여 결과를 받습니다.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.state == 'PENDING':
        return {"status": "processing"}
    elif task_result.state == 'SUCCESS':
        return {"status": "completed", "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"status": "failed", "result": str(task_result.info)}
    else:
        return {"status": task_result.state}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
