"""
T-Developer 설정 모듈

환경 변수 및 시스템 설정을 관리합니다.
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 설정
ENV = os.getenv("TDEVELOPER_ENV", "development")
DEBUG = ENV == "development"

# AWS 설정
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "TDeveloper-")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "t-developer-context")

# GitHub 설정
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH_PREFIX = os.getenv("GITHUB_BRANCH_PREFIX", "feature/")

# Slack 설정
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#t-developer")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Q Developer 설정
Q_DEVELOPER_WORKSPACE = os.getenv("Q_DEVELOPER_WORKSPACE", "/tmp/q-workspace")

# Agno/AI 설정
AGNO_API_KEY = os.getenv("AGNO_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 알림 설정
NOTIFICATION_LEVEL = os.getenv("NOTIFICATION_LEVEL", "normal")  # minimal, normal, verbose

# 서버 설정
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 보안 설정
RESTRICTED_FILES = [
    ".env",
    "config/secrets.py",
    "*password*",
    "*credential*",
    "*.pem",
    "*.key"
]

# 테스트 설정
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "0"))  # 0으로 설정하면 테스트 실패 시 재시도하지 않고 성공으로 처리