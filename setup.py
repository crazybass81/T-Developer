"""
T-Developer 설치 스크립트
"""
from setuptools import setup, find_packages

setup(
    name="t-developer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.23.2",
        "python-dotenv==1.0.0",
        "boto3==1.28.62",
        "slack-sdk==3.23.0",
        "requests==2.31.0",
        "pydantic==2.4.2",
        "openai==1.2.4"
    ],
    python_requires=">=3.8",
    author="T-Developer Team",
    author_email="example@example.com",
    description="T-Developer - AI-powered development automation system",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)