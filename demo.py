"""
T-Developer 데모 스크립트

이 스크립트는 T-Developer 시스템의 기본 기능을 시연합니다.
"""
import logging
import sys
import time
from typing import Dict, Any

from core.mao import MAO
from core.task import Task, TaskStatus

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_demo():
    """
    T-Developer 데모 실행
    """
    logger.info("Starting T-Developer demo")
    
    # MAO 인스턴스 생성
    mao = MAO()
    
    # 데모 작업 요청
    request = "Add a simple JWT authentication endpoint to the API"
    user_id = "demo_user"
    
    logger.info(f"Submitting task request: {request}")
    
    # 작업 처리 요청
    task_id = mao.process_request(request, user_id)
    
    logger.info(f"Task created with ID: {task_id}")
    
    # 작업 상태 모니터링
    monitor_task(mao, task_id)
    
    logger.info("Demo completed")

def monitor_task(mao: MAO, task_id: str, poll_interval: int = 5, max_polls: int = 60):
    """
    작업 상태 모니터링
    
    Args:
        mao: MAO 인스턴스
        task_id: 모니터링할 작업 ID
        poll_interval: 폴링 간격 (초)
        max_polls: 최대 폴링 횟수
    """
    logger.info(f"Monitoring task {task_id}")
    
    polls = 0
    completed_statuses = [TaskStatus.COMPLETED, TaskStatus.ERROR]
    
    while polls < max_polls:
        # 작업 상태 조회
        task = mao.task_store.get_task(task_id)
        
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        logger.info(f"Task {task_id} status: {task.status}")
        
        # 작업 완료 확인
        if task.status in completed_statuses:
            if task.status == TaskStatus.ERROR:
                logger.error(f"Task failed: {task.error}")
            else:
                logger.info("Task completed successfully")
            
            # 작업 결과 출력
            print_task_summary(task)
            return
        
        # 대기
        time.sleep(poll_interval)
        polls += 1
    
    logger.warning(f"Monitoring timed out after {max_polls * poll_interval} seconds")

def print_task_summary(task: Task):
    """
    작업 요약 출력
    
    Args:
        task: 작업 객체
    """
    print("\n" + "=" * 50)
    print(f"Task Summary: {task.task_id}")
    print("=" * 50)
    print(f"Request: {task.request}")
    print(f"Status: {task.status}")
    print(f"Created: {task.created_at}")
    
    if task.completed_at:
        print(f"Completed: {task.completed_at}")
    
    if task.plan_summary:
        print(f"\nPlan: {task.plan_summary}")
    
    if task.modified_files or task.created_files:
        print("\nCode Changes:")
        if task.modified_files:
            print(f"  Modified files: {', '.join(task.modified_files)}")
        if task.created_files:
            print(f"  Created files: {', '.join(task.created_files)}")
    
    if task.branch_name:
        print(f"\nGit Branch: {task.branch_name}")
    
    if task.commit_hash:
        print(f"Commit: {task.commit_hash}")
    
    if task.pr_url:
        print(f"Pull Request: {task.pr_url}")
    
    if task.deployed_url:
        print(f"Deployed at: {task.deployed_url}")
    
    if task.error:
        print(f"\nError: {task.error}")
    
    print("=" * 50)

if __name__ == "__main__":
    run_demo()