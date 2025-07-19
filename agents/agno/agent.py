"""
Agno Agent - T-Developer의 계획 수립 에이전트

이 모듈은 Agno 프레임워크를 사용하여 계획 수립, 지식 검색 등을 수행하는 에이전트를 구현합니다.
"""
import logging
import json
import os
from typing import Dict, List, Any, Optional

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

class AgnoAgent:
    """
    Agno 기반 계획 수립 에이전트
    
    계획 수립, 지식 검색 등을 담당합니다.
    """
    
    def __init__(self):
        """Agno 에이전트 초기화"""
        self.api_key = settings.AGNO_API_KEY
        self.openai_api_key = settings.OPENAI_API_KEY
        
        # Agno 에이전트 초기화 (실제 구현에서는 Agno 프레임워크 사용)
        logger.info("Agno Agent initialized")
        
        # 실제 Agno 에이전트 초기화 코드 (주석 처리)
        # try:
        #     from agno import Agent
        #     self.agent = Agent(model="gpt-4", api_key=self.openai_api_key)
        #     logger.info("Agno Agent initialized with GPT-4")
        # except ImportError:
        #     logger.warning("Agno package not found, using mock implementation")
        #     self.agent = None
    
    def _build_planning_prompt(self, request: str, context: Dict[str, Any]) -> str:
        """
        계획 수립 프롬프트 생성
        
        Args:
            request: 요청 내용
            context: 컨텍스트 정보
            
        Returns:
            프롬프트 문자열
        """
        # 글로벌 컨텍스트 추출
        global_context = context.get("global_context", {})
        framework = global_context.get("framework", "FastAPI")
        coding_style = global_context.get("coding_style", "PEP8")
        test_framework = global_context.get("test_framework", "pytest")
        
        # 관련 작업 추출
        related_tasks = context.get("related_tasks", [])
        related_tasks_text = ""
        if related_tasks:
            related_tasks_text = "## Related Tasks\n"
            for task in related_tasks:
                related_tasks_text += f"- Task {task.get('task_id')}: {task.get('request')}\n"
                if task.get('plan_summary'):
                    related_tasks_text += f"  Summary: {task.get('plan_summary')}\n"
        
        # 관련 파일 추출
        related_files = context.get("related_files", [])
        related_files_text = ""
        if related_files:
            related_files_text = "## Related Files\n"
            for file in related_files:
                related_files_text += f"- {file.get('path')}: {file.get('description')}\n"
        
        # 프롬프트 구성
        prompt = f"""
        # Planning Task
        
        You are a senior software architect tasked with creating a detailed implementation plan for a feature request.
        
        ## Feature Request
        {request}
        
        ## Project Context
        - Framework: {framework}
        - Coding Style: {coding_style}
        - Test Framework: {test_framework}
        
        {related_tasks_text}
        
        {related_files_text}
        
        ## Instructions
        1. Analyze the feature request and create a detailed implementation plan.
        2. Break down the implementation into clear, logical steps.
        3. Define acceptance criteria for the feature.
        4. Identify any potential challenges or considerations.
        
        ## Output Format
        Provide your response as a JSON object with the following structure:
        ```json
        {{
            "summary": "Brief summary of the implementation plan",
            "steps": [
                "Step 1: Description of the first implementation step",
                "Step 2: Description of the second implementation step",
                ...
            ],
            "acceptance_criteria": [
                "Criterion 1: Description of the first acceptance criterion",
                "Criterion 2: Description of the second acceptance criterion",
                ...
            ],
            "considerations": [
                "Consideration 1: Description of the first consideration",
                "Consideration 2: Description of the second consideration",
                ...
            ]
        }}
        ```
        
        Ensure your plan is detailed, practical, and follows the project's coding style and framework conventions.
        """
        
        return prompt
    
    def _build_qa_prompt(self, question: str, context: Dict[str, Any]) -> str:
        """
        질문 응답 프롬프트 생성
        
        Args:
            question: 질문 내용
            context: 컨텍스트 정보
            
        Returns:
            프롬프트 문자열
        """
        # 글로벌 컨텍스트 추출
        global_context = context.get("global_context", {})
        framework = global_context.get("framework", "FastAPI")
        
        # 관련 지식 추출
        knowledge = context.get("knowledge", [])
        knowledge_text = ""
        if knowledge:
            knowledge_text = "## Relevant Knowledge\n"
            for item in knowledge:
                knowledge_text += f"- {item}\n"
        
        # 프롬프트 구성
        prompt = f"""
        # Question Answering Task
        
        You are a technical expert assisting with a software development project.
        
        ## Question
        {question}
        
        ## Project Context
        - Framework: {framework}
        
        {knowledge_text}
        
        ## Instructions
        1. Answer the question based on the provided context.
        2. If you don't have enough information, state what additional information would be helpful.
        3. Provide code examples when relevant.
        
        Be concise, accurate, and helpful in your response.
        """
        
        return prompt
    
    def create_plan(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        계획 수립
        
        Args:
            request: 요청 내용
            context: 컨텍스트 정보
            
        Returns:
            계획 정보
        """
        logger.info(f"Creating plan for request: {request}")
        logger.info(f"OpenAI API Key 존재 여부: {bool(settings.OPENAI_API_KEY)}")
        logger.info(f"Agno API Key 존재 여부: {bool(settings.AGNO_API_KEY)}")
        
        # 프롬프트 생성
        prompt = self._build_planning_prompt(request, context)
        
        try:
            # OpenAI API 호출 (실제 구현)
            if settings.OPENAI_API_KEY:
                import openai
                
                openai.api_key = settings.OPENAI_API_KEY
                
                # API 호출
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # 응답을 구조화된 JSON으로 파싱
                plan_text = response.choices[0].message.content
                
                try:
                    # JSON 파싱 시도
                    plan = json.loads(plan_text)
                    logger.info(f"Plan created with {len(plan.get('steps', []))} steps from OpenAI")
                    return plan
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 텍스트에서 계획 추출 시도
                    logger.warning("Failed to parse OpenAI response as JSON, using fallback")
                    # 임시 구현: 가상의 계획 반환
                    plan = self._mock_plan_generation(request, context)
                    return plan
            else:
                # OpenAI API 키가 없는 경우 가상의 계획 반환
                logger.warning("OpenAI API key not provided, using mock implementation")
                plan = self._mock_plan_generation(request, context)
                return plan
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            # 오류 발생 시 가상의 계획 반환
            plan = self._mock_plan_generation(request, context)
            return plan
    
    def _mock_plan_generation(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        가상의 계획 생성 (테스트용)
        
        Args:
            request: 요청 내용
            context: 컨텍스트 정보
            
        Returns:
            계획 정보
        """
        # 요청 내용에 따라 다른 계획 반환
        if "auth" in request.lower() or "authentication" in request.lower():
            return {
                "summary": "JWT 인증 기능 구현 계획",
                "steps": [
                    "JWT 유틸리티 모듈 구현 (토큰 생성, 검증)",
                    "사용자 인증 엔드포인트 구현 (/api/auth)",
                    "미들웨어 구현 (토큰 검증)",
                    "보호된 엔드포인트에 미들웨어 적용",
                    "단위 테스트 작성"
                ],
                "acceptance_criteria": [
                    "유효한 자격 증명으로 로그인하면 JWT 토큰이 발급됨",
                    "유효한 토큰으로 보호된 엔드포인트에 접근 가능",
                    "유효하지 않은 토큰으로는 접근 불가",
                    "모든 테스트가 통과함"
                ],
                "considerations": [
                    "토큰 만료 시간 설정",
                    "환경 변수로 시크릿 키 관리",
                    "CORS 설정 확인"
                ]
            }
        elif "api" in request.lower() or "endpoint" in request.lower():
            return {
                "summary": "새로운 API 엔드포인트 구현 계획",
                "steps": [
                    "데이터 모델 정의",
                    "서비스 레이어 구현",
                    "API 엔드포인트 구현",
                    "입력 유효성 검사 추가",
                    "단위 테스트 작성"
                ],
                "acceptance_criteria": [
                    "API가 올바른 응답 형식을 반환함",
                    "유효하지 않은 입력에 대해 적절한 오류 응답을 반환함",
                    "모든 테스트가 통과함"
                ],
                "considerations": [
                    "API 문서화 (Swagger/OpenAPI)",
                    "성능 최적화",
                    "에러 처리 일관성"
                ]
            }
        elif "database" in request.lower() or "db" in request.lower():
            return {
                "summary": "데이터베이스 연동 기능 구현 계획",
                "steps": [
                    "데이터베이스 연결 설정",
                    "모델 스키마 정의",
                    "CRUD 작업 구현",
                    "마이그레이션 스크립트 작성",
                    "단위 테스트 작성"
                ],
                "acceptance_criteria": [
                    "데이터베이스 연결이 성공적으로 이루어짐",
                    "CRUD 작업이 정상적으로 동작함",
                    "마이그레이션이 오류 없이 실행됨",
                    "모든 테스트가 통과함"
                ],
                "considerations": [
                    "데이터베이스 자격 증명 보안",
                    "인덱싱 전략",
                    "트랜잭션 관리"
                ]
            }
        else:
            # 기본 계획
            return {
                "summary": "요청된 기능 구현 계획",
                "steps": [
                    "요구사항 분석",
                    "설계 및 아키텍처 결정",
                    "코드 구현",
                    "단위 테스트 작성",
                    "통합 테스트 수행"
                ],
                "acceptance_criteria": [
                    "기능이 요구사항에 맞게 동작함",
                    "코드가 프로젝트 스타일 가이드를 준수함",
                    "모든 테스트가 통과함"
                ],
                "considerations": [
                    "성능 최적화",
                    "보안 고려사항",
                    "유지보수성"
                ]
            }
    
    def answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """
        질문 응답
        
        Args:
            question: 질문 내용
            context: 컨텍스트 정보
            
        Returns:
            응답 내용
        """
        logger.info(f"Answering question: {question}")
        
        # 프롬프트 생성
        prompt = self._build_qa_prompt(question, context)
        
        # 실제 구현에서는 OpenAI API 호출
        # 임시 구현: 가상의 응답 반환
        if "framework" in question.lower():
            return "이 프로젝트는 FastAPI 프레임워크를 사용합니다. FastAPI는 Python 기반의 고성능 웹 프레임워크로, 자동 문서화, 타입 힌트 기반의 유효성 검사 등의 기능을 제공합니다."
        elif "database" in question.lower():
            return "이 프로젝트는 PostgreSQL 데이터베이스를 사용하며, SQLAlchemy ORM을 통해 데이터베이스와 상호작용합니다."
        elif "test" in question.lower():
            return "이 프로젝트는 pytest를 사용하여 단위 테스트와 통합 테스트를 수행합니다. 테스트 파일은 tests/ 디렉토리에 위치하며, 'test_'로 시작하는 파일명과 함수명을 사용합니다."
        else:
            return "질문에 대한 정확한 정보를 찾을 수 없습니다. 더 구체적인 질문을 해주시면 도움을 드릴 수 있습니다."
    
    def search_knowledge(self, query: str, context: Dict[str, Any]) -> List[str]:
        """
        지식 검색
        
        Args:
            query: 검색어
            context: 컨텍스트 정보
            
        Returns:
            검색 결과 목록
        """
        logger.info(f"Searching knowledge for: {query}")
        
        # 실제 구현에서는 벡터 데이터베이스 등을 사용한 검색
        # 임시 구현: 가상의 검색 결과 반환
        if "auth" in query.lower():
            return [
                "JWT 인증은 JSON Web Token을 사용한 인증 방식입니다.",
                "인증 토큰은 Header, Payload, Signature로 구성됩니다.",
                "FastAPI에서는 OAuth2PasswordBearer를 사용하여 JWT 인증을 구현할 수 있습니다."
            ]
        elif "api" in query.lower():
            return [
                "RESTful API는 HTTP 메서드를 사용하여 리소스를 조작하는 아키텍처 스타일입니다.",
                "FastAPI에서는 @app.get(), @app.post() 등의 데코레이터를 사용하여 엔드포인트를 정의합니다.",
                "Pydantic 모델을 사용하여 요청 및 응답 스키마를 정의할 수 있습니다."
            ]
        elif "database" in query.lower():
            return [
                "SQLAlchemy는 Python용 SQL 툴킷 및 ORM입니다.",
                "데이터베이스 마이그레이션은 Alembic을 사용하여 관리할 수 있습니다.",
                "FastAPI에서는 Depends를 사용하여 데이터베이스 세션을 주입할 수 있습니다."
            ]
        else:
            return []