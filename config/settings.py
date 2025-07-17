"""
T-Developer 시스템 설정 파일
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 기본 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 환경 설정
ENV = os.getenv("TDEVELOPER_ENV", "development")
DEBUG = ENV == "development"

# AWS 설정
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_PREFIX = os.getenv("DYNAMODB_TABLE_PREFIX", "TDeveloper-")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "t-developer-context")

# 컨텍스트 저장소 설정
CONTEXT_STORAGE = {
    "dynamo": {
        "task_table": f"{DYNAMODB_TABLE_PREFIX}TaskContext",
        "knowledge_table": f"{DYNAMODB_TABLE_PREFIX}Knowledge",
    },
    "s3": {
        "bucket": S3_BUCKET_NAME,
        "prefixes": {
            "plans": "plans/",
            "logs": "logs/",
            "artifacts": "artifacts/",
            "knowledge": "knowledge/",
        }
    }
}

# GitHub 설정
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_BRANCH_PREFIX = os.getenv("GITHUB_BRANCH_PREFIX", "feature/")

# Slack 설정
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#t-developer")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# AI 모델 설정
AGNO_API_KEY = os.getenv("AGNO_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Q Developer 설정
Q_DEVELOPER_WORKSPACE = os.getenv("Q_DEVELOPER_WORKSPACE", "/tmp/q-workspace")

# 작업 설정
MAX_FILES_PER_TASK = 5
MAX_RETRIES = 3
NOTIFICATION_LEVEL = os.getenv("NOTIFICATION_LEVEL", "normal")  # minimal, normal, verbose

# 보안 설정
RESTRICTED_FILES = [
    ".env",
    "config/secrets.py",
    "**/password*",
    "**/credential*",
]