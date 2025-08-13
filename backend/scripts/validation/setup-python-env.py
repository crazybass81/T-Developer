#!/usr/bin/env python3
"""
Python 가상 환경 설정 스크립트
"""
import subprocess
import sys
import venv
import os


def create_virtual_env():
    """Python 가상 환경 생성"""
    venv_path = os.path.join(os.getcwd(), "venv")

    if not os.path.exists(venv_path):
        print("🔧 Python 가상 환경 생성 중...")
        venv.create(venv_path, with_pip=True)
        print("✅ 가상 환경 생성 완료")
    else:
        print("✅ 가상 환경이 이미 존재합니다")

    # 활성화 명령 출력
    if sys.platform == "win32":
        activate_cmd = f"{venv_path}\\Scripts\\activate"
    else:
        activate_cmd = f"source {venv_path}/bin/activate"

    print(f"\n📋 가상 환경 활성화 명령:")
    print(f"   {activate_cmd}")
    print(f"\n📋 의존성 설치 명령:")
    print(f"   pip install -r requirements.txt")

    return venv_path


def install_dependencies():
    """의존성 설치"""
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


if __name__ == "__main__":
    create_virtual_env()
    # 주의: 가상 환경 활성화 후 수동으로 설치 필요
