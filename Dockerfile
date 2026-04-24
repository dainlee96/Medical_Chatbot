FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 라이브러리 설치 (필요시)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# 패키지 요구사항 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 복사
COPY . .

# 포트 개방
EXPOSE 8000
