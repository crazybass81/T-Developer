"""
MAO (Multi-Agent Orchestrator) - T-Developer의 중앙 오케스트레이터

이 모듈은 T-Developer 시스템의 핵심 컴포넌트로, 사용자 요청을 처리하고
Agno와 Q Developer 에이전트 간의 작업 흐름을 조정합니다.
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from config import settings
from core.task import Task, TaskStatus
from agents.agno.agent import AgnoAgent
from agents.q_developer.agent import QDeveloperAgent
from context.dynamo.task_store import TaskStore
from context.s3.artifact_store import ArtifactStore
from tools.git.github import GitHubTool
from slack.notifier import SlackNotifier

# 로깅 설정
logger = logging.getLogger(__name__)

class MAO:
    """
    Multi-Agent Orchestrator (MAO) 클래스
    
    사용자 요청을 받아 작업을 계획하고, 적절한 에이전트에 위임하며,
    결과를 통합하고 사용자에게 알림을 보내는 역할을 담당합니다.
    """
    
    def __init__(self):
        """MAO 초기화"""
        self.task_store = TaskStore()
        self.artifact_store = ArtifactStore()
        self.agno_agent = AgnoAgent()
        self.q_developer = QDeveloperAgent()
        self.github_tool = GitHubTool()
        self.slack = SlackNotifier()
        
    def process_request(self, request_text: str, user_id: str) -> str:
        """
        사용자 요청을 처리하는 메인 함수
        
        Args:
            request_text: 사용자가 요청한 텍스트
            user_id: 요청한 사용자의 ID
            
        Returns:
            생성된 작업 ID
        """
        # 작업 ID 생성 (TASK-날짜-일련번호 형식)
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # 작업 생성 및 저장
        task = Task(
            task_id=task_id,
            request=request_text,
            user_id=user_id,
            status=TaskStatus.RECEIVED,
            created_at=datetime.now().isoformat()
        )
        self.task_store.save_task(task)
        
        # Slack에 작업 접수 알림
        self.slack.send_acknowledgment(task)
        
        # 비동기로 작업 처리 시작 (실제 구현에서는 비동기 처리)
        # 여기서는 동기식으로 처리
        self._execute_task(task)
        
        return task_id
    
    def _execute_task(self, task: Task) -> None:
        """
        작업을 실행하는 내부 함수
        
        Args:
            task: 실행할 작업 객체
        """
        try:
            # 1. 작업 분석 및 계획 수립
            self._analyze_and_plan(task)
            
            # 2. 코드 구현
            if task.status != TaskStatus.ERROR:
                self._implement_code(task)
            
            # 3. 테스트 실행
            if task.status != TaskStatus.ERROR:
                self._run_tests(task)
            
            # 4. 배포 (필요시)
            if task.status != TaskStatus.ERROR and self._should_deploy(task):
                self._deploy(task)
            
            # 작업 완료 처리
            if task.status != TaskStatus.ERROR:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now().isoformat()
                self.task_store.update_task(task)
                self.slack.send_completion(task)
        
        except Exception as e:
            # 오류 발생 시 처리
            logger.error(f"Task {task.task_id} failed: {str(e)}", exc_info=True)
            task.status = TaskStatus.ERROR
            task.error = str(e)
            self.task_store.update_task(task)
            self.slack.send_error(task)
    
    def _analyze_and_plan(self, task: Task) -> None:
        """
        Agno 에이전트를 사용하여 작업을 분석하고 계획을 수립
        
        Args:
            task: 계획을 수립할 작업 객체
        """
        logger.info(f"Planning task {task.task_id}")
        task.status = TaskStatus.PLANNING
        self.task_store.update_task(task)
        self.slack.send_planning_started(task)
        
        # 관련 컨텍스트 수집
        context = self._gather_context(task)
        
        # Agno에 계획 요청
        try:
            plan_result = self.agno_agent.create_plan(task.request, context)
            
            # 계획 저장
            plan_summary = self._extract_plan_summary(plan_result)
            plan_s3_key = f"plans/{task.task_id}.json"
            self.artifact_store.save_artifact(plan_s3_key, json.dumps(plan_result))
            
            # 작업 업데이트
            task.plan_summary = plan_summary
            task.plan_s3_key = plan_s3_key
            task.status = TaskStatus.PLANNED
            self.task_store.update_task(task)
            
            # Slack에 계획 알림
            self.slack.send_plan_created(task, plan_summary)
            
        except Exception as e:
            logger.error(f"Planning failed for task {task.task_id}: {str(e)}", exc_info=True)
            task.status = TaskStatus.ERROR
            task.error = f"Planning failed: {str(e)}"
            self.task_store.update_task(task)
            self.slack.send_error(task)
    
    def _implement_code(self, task: Task) -> None:
        """
        Q Developer를 사용하여 코드 구현
        
        Args:
            task: 구현할 작업 객체
        """
        logger.info(f"Implementing code for task {task.task_id}")
        task.status = TaskStatus.CODING
        self.task_store.update_task(task)
        self.slack.send_coding_started(task)
        
        # 계획 및 컨텍스트 로드
        plan = json.loads(self.artifact_store.get_artifact(task.plan_s3_key))
        context = self._gather_context(task)
        
        # GitHub 브랜치 생성
        branch_name = f"{settings.GITHUB_BRANCH_PREFIX}{task.task_id}"
        self.github_tool.create_branch(branch_name)
        
        # Q Developer에 작업 지시
        try:
            # 작업 지시 생성
            instruction = self._create_q_developer_instruction(task, plan, context)
            
            # Q Developer 실행
            result = self.q_developer.execute_task(instruction)
            
            # 결과 저장
            diff_s3_key = f"artifacts/{task.task_id}-diff.patch"
            self.artifact_store.save_artifact(diff_s3_key, result.get("diff", ""))
            
            # 변경사항 커밋
            commit_message = f"feat: {task.request} [Task {task.task_id}]"
            commit_hash = self.github_tool.commit_changes(branch_name, commit_message)
            
            # 작업 업데이트
            task.branch_name = branch_name
            task.commit_hash = commit_hash
            task.modified_files = result.get("modified_files", [])
            task.created_files = result.get("created_files", [])
            task.diff_s3_key = diff_s3_key
            task.status = TaskStatus.CODED
            self.task_store.update_task(task)
            
            # Slack에 코딩 완료 알림
            self.slack.send_coding_completed(task)
            
        except Exception as e:
            logger.error(f"Code implementation failed for task {task.task_id}: {str(e)}", exc_info=True)
            task.status = TaskStatus.ERROR
            task.error = f"Code implementation failed: {str(e)}"
            self.task_store.update_task(task)
            self.slack.send_error(task)
    
    def _run_tests(self, task: Task) -> None:
        """
        구현된 코드에 대한 테스트 실행
        
        Args:
            task: 테스트할 작업 객체
        """
        logger.info(f"Running tests for task {task.task_id}")
        task.status = TaskStatus.TESTING
        self.task_store.update_task(task)
        self.slack.send_testing_started(task)
        
        try:
            # Q Developer에 테스트 실행 요청
            test_result = self.q_developer.run_tests()
            
            # 테스트 결과 저장
            test_log_s3_key = f"logs/{task.task_id}-test.log"
            self.artifact_store.save_artifact(test_log_s3_key, test_result.get("log", ""))
            
            # 테스트 결과 처리
            if test_result.get("success", False):
                # 테스트 성공
                task.test_success = True
                task.test_log_s3_key = test_log_s3_key
                task.status = TaskStatus.TESTED
                self.task_store.update_task(task)
                self.slack.send_tests_passed(task)
            else:
                # 테스트 실패 - 수정 시도
                retry_count = 0
                while retry_count < settings.MAX_RETRIES:
                    retry_count += 1
                    self.slack.send_test_fix_attempt(task, retry_count)
                    
                    # Q Developer에 수정 요청
                    fix_result = self.q_developer.fix_test_failures(test_result.get("failures", []))
                    
                    # 수정 후 다시 테스트
                    test_result = self.q_developer.run_tests()
                    
                    # 수정된 결과 저장
                    self.artifact_store.save_artifact(test_log_s3_key, test_result.get("log", ""))
                    
                    # 변경사항 커밋
                    commit_message = f"fix: test failures in {task.task_id} (attempt {retry_count})"
                    commit_hash = self.github_tool.commit_changes(task.branch_name, commit_message)
                    
                    # 테스트 성공 시 종료
                    if test_result.get("success", False):
                        task.test_success = True
                        task.test_log_s3_key = test_log_s3_key
                        task.status = TaskStatus.TESTED
                        self.task_store.update_task(task)
                        self.slack.send_tests_passed(task)
                        break
                
                # 최대 재시도 후에도 실패하면 오류 처리
                if not test_result.get("success", False):
                    task.test_success = False
                    task.test_log_s3_key = test_log_s3_key
                    task.status = TaskStatus.ERROR
                    task.error = "Tests failed after maximum retry attempts"
                    self.task_store.update_task(task)
                    self.slack.send_test_failure(task)
        
        except Exception as e:
            logger.error(f"Testing failed for task {task.task_id}: {str(e)}", exc_info=True)
            task.status = TaskStatus.ERROR
            task.error = f"Testing failed: {str(e)}"
            self.task_store.update_task(task)
            self.slack.send_error(task)
    
    def _deploy(self, task: Task) -> None:
        """
        구현된 코드 배포
        
        Args:
            task: 배포할 작업 객체
        """
        logger.info(f"Deploying task {task.task_id}")
        task.status = TaskStatus.DEPLOYING
        self.task_store.update_task(task)
        self.slack.send_deploying(task)
        
        try:
            # GitHub PR 생성 및 머지
            pr_title = f"Feature: {task.request} [Task {task.task_id}]"
            pr_body = self._generate_pr_description(task)
            pr_url = self.github_tool.create_pull_request(task.branch_name, "main", pr_title, pr_body)
            
            # PR 자동 머지 (설정에 따라)
            merge_result = self.github_tool.merge_pull_request(pr_url)
            
            # 배포 결과 저장
            task.pr_url = pr_url
            task.deployed = merge_result.get("merged", False)
            task.deployed_version = merge_result.get("version", "")
            task.deployed_url = merge_result.get("url", "")
            task.status = TaskStatus.DEPLOYED if task.deployed else TaskStatus.ERROR
            
            if not task.deployed:
                task.error = "Deployment failed: " + merge_result.get("message", "Unknown error")
            
            self.task_store.update_task(task)
            
            # Slack에 배포 결과 알림
            if task.deployed:
                self.slack.send_deployment_success(task)
            else:
                self.slack.send_deployment_failure(task)
        
        except Exception as e:
            logger.error(f"Deployment failed for task {task.task_id}: {str(e)}", exc_info=True)
            task.status = TaskStatus.ERROR
            task.error = f"Deployment failed: {str(e)}"
            self.task_store.update_task(task)
            self.slack.send_error(task)
    
    def _gather_context(self, task: Task) -> Dict[str, Any]:
        """
        작업에 필요한 컨텍스트 수집
        
        Args:
            task: 컨텍스트를 수집할 작업 객체
            
        Returns:
            수집된 컨텍스트 정보
        """
        # 기본 컨텍스트
        context = {
            "task_id": task.task_id,
            "request": task.request,
        }
        
        # 글로벌 컨텍스트 (프로젝트 가이드라인 등)
        global_context = self.task_store.get_global_context()
        if global_context:
            context["global"] = global_context
        
        # 관련 작업 검색 (키워드 기반)
        related_tasks = self.task_store.find_related_tasks(task.request)
        if related_tasks:
            context["related_tasks"] = related_tasks
        
        # 코드베이스 관련 파일 검색 (키워드 기반)
        # 실제 구현에서는 코드 검색 도구 사용
        related_files = self.github_tool.find_related_files(task.request)
        if related_files:
            context["related_files"] = related_files
        
        return context
    
    def _extract_plan_summary(self, plan_result: Dict[str, Any]) -> str:
        """
        계획 결과에서 요약 추출
        
        Args:
            plan_result: Agno가 생성한 계획 결과
            
        Returns:
            계획 요약 문자열
        """
        # 계획에 steps가 있으면 그 개수와 간략한 설명 반환
        if "steps" in plan_result and isinstance(plan_result["steps"], list):
            steps = plan_result["steps"]
            summary = f"{len(steps)} steps: "
            summary += ", ".join([step[:50] + "..." if len(step) > 50 else step 
                                for step in steps[:3]])
            if len(steps) > 3:
                summary += f", and {len(steps) - 3} more steps"
            return summary
        
        # 그렇지 않으면 계획 자체의 요약 반환
        return plan_result.get("summary", "Plan created (details in S3)")
    
    def _create_q_developer_instruction(self, task: Task, plan: Dict[str, Any], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Q Developer에 전달할 작업 지시 생성
        
        Args:
            task: 작업 객체
            plan: Agno가 생성한 계획
            context: 수집된 컨텍스트
            
        Returns:
            Q Developer에 전달할 작업 지시 JSON
        """
        # 기본 지시 구조
        instruction = {
            "task_id": task.task_id,
            "feature_name": task.request[:50],  # 간략한 제목
            "description": task.request,
            "requirements": [],
            "context": {
                "existing_modules": [],
                "framework": context.get("global", {}).get("framework", ""),
                "related_commit": None,
                "notes": ""
            },
            "acceptance_criteria": [],
            "deliverables": [],
            "tools_allowed": ["Run: pytest", "Access files in repository"],
            "session_context": "",
            "priority": "HIGH",
            "status": "open"
        }
        
        # 계획에서 요구사항 추출
        if "steps" in plan:
            instruction["requirements"] = plan["steps"]
        
        # 컨텍스트에서 기존 모듈 정보 추출
        if "related_files" in context:
            for file_info in context["related_files"]:
                module_info = {
                    "name": file_info.get("name", ""),
                    "description": file_info.get("description", ""),
                    "location": file_info.get("path", "")
                }
                instruction["context"]["existing_modules"].append(module_info)
        
        # 계획에서 수락 기준 추출
        if "acceptance_criteria" in plan:
            instruction["acceptance_criteria"] = plan["acceptance_criteria"]
        else:
            # 기본 수락 기준
            instruction["acceptance_criteria"] = [
                "All tests pass",
                "Code follows project style guidelines",
                "Functionality meets the requirements"
            ]
        
        # 계획에서 산출물 추출
        if "deliverables" in plan:
            instruction["deliverables"] = plan["deliverables"]
        else:
            # 기본 산출물
            instruction["deliverables"] = [
                "Implemented code files",
                "Unit tests"
            ]
        
        return instruction
    
    def _generate_pr_description(self, task: Task) -> str:
        """
        GitHub PR 설명 생성
        
        Args:
            task: PR을 생성할 작업 객체
            
        Returns:
            PR 설명 문자열
        """
        description = f"## Feature: {task.request}\n\n"
        description += f"Task ID: {task.task_id}\n\n"
        
        # 계획 요약 추가
        if task.plan_summary:
            description += f"### Plan\n{task.plan_summary}\n\n"
        
        # 변경된 파일 목록 추가
        if task.modified_files:
            description += "### Modified Files\n"
            for file in task.modified_files:
                description += f"- {file}\n"
            description += "\n"
        
        # 생성된 파일 목록 추가
        if task.created_files:
            description += "### Created Files\n"
            for file in task.created_files:
                description += f"- {file}\n"
            description += "\n"
        
        # 테스트 결과 추가
        if task.test_success:
            description += "### Tests\n✅ All tests passed\n\n"
        
        description += "Generated by T-Developer"
        
        return description
    
    def _should_deploy(self, task: Task) -> bool:
        """
        작업을 배포해야 하는지 결정
        
        Args:
            task: 결정할 작업 객체
            
        Returns:
            배포 여부
        """
        # 테스트가 성공했고, 코드가 구현되었으면 배포
        return task.status == TaskStatus.TESTED and task.test_success