import os
from celery import Celery
from rag import get_medical_answer

# Redis 브로커 설정 (환경변수 또는 로컬)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Celery 앱 초기화
celery_app = Celery(
    "medical_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

@celery_app.task(name="process_chat_message")
def process_chat_message(user_id: str, message: str):
    """
    무거운 RAG 검색 및 LLM 추론을 담당하는 비동기 워커 태스크.
    메인 FastAPI 스레드를 블로킹하지 않도록 백그라운드 프로세스로 실행됩니다.
    """
    try:
        # 실제 환경에서는 user_id를 바탕으로 대화 기록(Session)을 조회해 컨텍스트에 추가할 수 있습니다.
        answer = get_medical_answer(message)
        return answer
    except Exception as e:
        return f"죄송합니다. 의료 정보를 분석하는 중 오류가 발생했습니다: {str(e)}"
