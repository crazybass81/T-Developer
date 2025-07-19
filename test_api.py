#!/usr/bin/env python3
"""
T-Developer API 테스트 스크립트

백엔드 API를 테스트하고 에이전트 호출 여부를 확인합니다.
"""
import requests
import json
import time
import sys

# API 기본 URL
BASE_URL = "http://localhost:9000"

def test_health():
    """헬스 체크 API 테스트"""
    print("헬스 체크 API 테스트 중...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

def test_create_task():
    """작업 생성 API 테스트"""
    print("\n작업 생성 API 테스트 중...")
    try:
        data = {
            "request": "사용자가 질문을 입력하면 관련된 정부 지원사업을 검색하여 추천하는 기능을 추가해줘.",
            "user_id": "test-user",
            "project_id": "test-project"
        }
        response = requests.post(f"{BASE_URL}/api/tasks", json=data)
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {response.json()}")
        
        if response.status_code == 200:
            task_id = response.json().get("task_id")
            print(f"생성된 작업 ID: {task_id}")
            return task_id
        return None
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def test_get_task(task_id):
    """작업 조회 API 테스트"""
    print(f"\n작업 조회 API 테스트 중... (ID: {task_id})")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

def monitor_task(task_id, max_attempts=20):  # Increased from 10 to 20 attempts
    """작업 상태 모니터링"""
    print(f"\n작업 상태 모니터링 중... (ID: {task_id})")
    attempts = 0
    
    while attempts < max_attempts:
        try:
            response = requests.get(f"{BASE_URL}/api/tasks/{task_id}")
            if response.status_code == 200:
                task_data = response.json()
                status = task_data.get("status")
                print(f"현재 상태: {status}")
                
                # 작업이 완료되었거나 오류가 발생한 경우
                if status in ["completed", "deployed", "tested", "error"]:  # Added 'tested' as a completion state
                    print(f"최종 상태: {status}")
                    print(f"상세 정보: {json.dumps(task_data, indent=2, ensure_ascii=False)}")
                    return True
            else:
                print(f"API 오류: {response.status_code}")
        except Exception as e:
            print(f"모니터링 오류: {e}")
        
        attempts += 1
        print(f"5초 후 다시 확인합니다... ({attempts}/{max_attempts})")
        time.sleep(5)
    
    print("최대 시도 횟수 초과")
    return False

def main():
    """메인 테스트 함수"""
    print("T-Developer API 테스트 시작")
    
    # 헬스 체크
    if not test_health():
        print("헬스 체크 실패. 서버가 실행 중인지 확인하세요.")
        sys.exit(1)
    
    # 작업 생성
    task_id = test_create_task()
    if not task_id:
        print("작업 생성 실패.")
        sys.exit(1)
    
    # 작업 조회
    if not test_get_task(task_id):
        print("작업 조회 실패.")
        sys.exit(1)
    
    # 작업 모니터링
    monitor_task(task_id)
    
    print("\n테스트 완료")

if __name__ == "__main__":
    main()