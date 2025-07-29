#!/usr/bin/env python3
# scripts/test-python-deps.py

def test_python_dependencies():
    """Python 의존성 설치 확인"""
    print("🔍 Python 의존성 테스트 중...\n")
    
    dependencies = [
        ("boto3", "AWS SDK"),
        ("botocore", "AWS Core"),
        ("python-dotenv", "Environment Variables"),
        ("requests", "HTTP Client"),
        ("pydantic", "Data Validation"),
        ("fastapi", "Web Framework"),
        ("uvicorn", "ASGI Server"),
        ("pytest", "Testing Framework"),
        ("black", "Code Formatter"),
        ("flake8", "Code Linter"),
        ("mypy", "Type Checker")
    ]
    
    success_count = 0
    
    for package, description in dependencies:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package:<15} - {description}")
            success_count += 1
        except ImportError:
            print(f"❌ {package:<15} - {description} (설치되지 않음)")
    
    print(f"\n📊 결과: {success_count}/{len(dependencies)} 패키지 설치됨")
    
    if success_count == len(dependencies):
        print("🎉 모든 Python 의존성이 정상적으로 설치되었습니다!")
        return True
    else:
        print("⚠️  일부 패키지가 설치되지 않았습니다.")
        return False

if __name__ == "__main__":
    success = test_python_dependencies()
    exit(0 if success else 1)