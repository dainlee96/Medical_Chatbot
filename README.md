# 🩺 Medical Chatbot RAG Architecture

본 프로젝트는 의료 도메인 특화 **RAG(검색 증강 생성)** 기반 챗봇 서비스의 아키텍처 템플릿입니다. 수강생들의 비동기 백엔드 구조 및 AI 모델 서빙의 이해를 돕기 목적으로 제작되었습니다.

## 🌟 Architecture Overview
- **Frontend**: HTML / Tailwind CSS / Vanilla JS (Glassmorphism 프리미엄 디자인 적용)
- **API Server**: FastAPI (메인 엔드포인트)
- **Message Broker**: Redis (세션 관리 및 대기 상태 큐)
- **Worker**: Celery (DB 검색 및 LLM 추론 전담 백그라운드 프로세서)
- **Vector DB**: ChromaDB (의학 문헌 임베딩 및 검색)
- **LLM**: OpenAI GPT-3.5-Turbo
- **Infrastructure**: Docker & Docker Compose

## 🚀 How to Run (Docker)
1. 프로젝트를 Clone 받습니다.
2. `docker-compose.yml`이 위치한 경로에서 아래 명령어를 통해 서버를 기동합니다.
   ```bash
   export OPENAI_API_KEY="본인의_API_KEY"
   docker-compose up -d --build
   ```
3. 브라우저에서 `http://localhost:8000/static/index.html` 에 접속하여 테스트합니다.

## 📚 멘토링/실습 포인트
해당 코드는 실습을 위해 초기 뼈대가 잡아진 가이드라인 템플릿입니다!
1. **[Vector DB 연동]** `rag.py` 내의 `dummy_docs` 배열을 지우고, Kaggle이나 실제 공공 의료 데이터를 판다스로 읽어들여 ChromaDB에 대량으로 주입(Bulk Insert)하는 코드로 확장해 보세요.
2. **[비동기 처리 관찰해보기]** 브라우저에서 다량의 채팅을 연달아 쳤을 때, FastAPI 서버가 멈추지 않고 스켈레톤 UI를 보여주며 Celery가 백그라운드에서 안전하게 결과값을 반환하는 과정을 확인해 보세요.
3. **[프롬프트 엔지니어링]** `prompt_template.txt`를 수정하여 다양한 페르소나(친절한 간호사, 냉철한 전문의 등)를 부여하고 환각 코너 케이스를 통제해 보세요.
