FROM python:3.11-slim

WORKDIR /app

# uv 설치
RUN pip install uv

# 의존성 복사 및 설치
COPY backend/requirements.txt .
RUN uv pip install -r requirements.txt

# 소스 코드 복사
COPY backend/ .

EXPOSE 8000

CMD ["python", "main.py"]