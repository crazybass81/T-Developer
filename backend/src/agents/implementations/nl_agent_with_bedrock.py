"""
T-Developer NL Input Agent - Agno + AWS Bedrock 완전 연결 버전
"""
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import os

@dataclass
class ProjectRequirements:
    description: str
    project_type: str
    technical_requirements: List[str]
    non_functional_requirements: List[str]
    technology_preferences: Dict[str, Any]
    constraints: List[str]
    extracted_entities: Dict[str, Any]
    confidence_score: float = 0.0

class NLInputAgentWithBedrock:
    """Agno Framework + AWS Bedrock 완전 연결 버전"""
    
    def __init__(self):
        # AWS 자격 증명 확인
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        try:
            # Agno + Bedrock Agent 생성
            self.agent = Agent(
                name="T-Developer-NL-Processor-Bedrock",
                model=AwsBedrock(
                    id="anthropic.claude-3-sonnet-20240229-v1:0",
                    region=aws_region
                ),
                role="Senior requirements analyst and technical architect",
                instructions=[
                    "프로젝트 설명에서 핵심 요구사항을 추출",
                    "기술적/비기술적 요구사항을 구분",
                    "프로젝트 유형과 규모를 파악", 
                    "선호 기술 스택과 제약사항을 식별",
                    "모호한 부분에 대해 명확화 질문 생성"
                ],
                description="자연어 프로젝트 설명을 분석하고 구조화된 요구사항으로 변환하는 전문가"
            )
            
            self.bedrock_available = True
            print(f"✅ Agno + Bedrock Agent 생성 완료: {self.agent.agent_id}")
            
        except Exception as e:
            print(f"⚠️ Bedrock 연결 실패, 로컬 모드로 전환: {e}")
            
            # Bedrock 없이 Agno만 사용
            self.agent = Agent(
                name="T-Developer-NL-Processor-Local",
                description="프로젝트 설명에서 핵심 요구사항을 추출하는 전문가",
                instructions=[
                    "프로젝트 설명에서 핵심 요구사항을 추출",
                    "기술적/비기술적 요구사항을 구분",
                    "프로젝트 유형과 규모를 파악"
                ]
            )
            
            self.bedrock_available = False
            print(f"✅ Agno Local Agent 생성 완료: {self.agent.agent_id}")
    
    async def process_description(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """자연어 프로젝트 설명 처리"""
        
        if self.bedrock_available:
            return await self._process_with_bedrock(description, context)
        else:
            return await self._process_locally(description, context)
    
    async def _process_with_bedrock(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """Bedrock을 사용한 고급 처리"""
        
        analysis_prompt = f"""
        다음 프로젝트 설명을 분석하고 JSON 형식으로 요구사항을 추출하세요:

        프로젝트 설명: {description}

        다음 형식으로 응답해주세요:
        {{
            "project_type": "프로젝트 유형 (web_application, mobile_application, api_service, cli_tool 중 하나)",
            "technical_requirements": ["기술적 요구사항 목록"],
            "non_functional_requirements": ["성능, 보안 등 비기능적 요구사항"],
            "technology_preferences": {{"frontend": ["선호 프론트엔드"], "backend": ["선호 백엔드"]}},
            "constraints": ["제약사항 목록"],
            "confidence_score": 0.95
        }}
        """
        
        try:
            # Agno Agent 실행
            response = await self.agent.arun(analysis_prompt)
            
            # JSON 파싱 시도
            import json
            try:
                parsed = json.loads(response.content)
                
                return ProjectRequirements(
                    description=description,
                    project_type=parsed.get('project_type', 'general_application'),
                    technical_requirements=parsed.get('technical_requirements', []),
                    non_functional_requirements=parsed.get('non_functional_requirements', []),
                    technology_preferences=parsed.get('technology_preferences', {}),
                    constraints=parsed.get('constraints', []),
                    extracted_entities={'raw_response': response.content},
                    confidence_score=parsed.get('confidence_score', 0.8)
                )
                
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 로컬 처리로 폴백
                print("⚠️ JSON 파싱 실패, 로컬 처리로 전환")
                return await self._process_locally(description, context)
                
        except Exception as e:
            print(f"⚠️ Bedrock 처리 실패: {e}")
            return await self._process_locally(description, context)
    
    async def _process_locally(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """로컬 규칙 기반 처리"""
        
        # 기본 분석 (이전 구현과 동일)
        project_type = self._detect_project_type(description)
        tech_requirements = self._extract_technical_requirements(description)
        non_functional = self._extract_non_functional_requirements(description)
        tech_preferences = self._extract_technology_preferences(description)
        constraints = self._extract_constraints(description)
        entities = self._extract_entities(description)
        confidence = self._calculate_confidence(description, tech_requirements)
        
        return ProjectRequirements(
            description=description,
            project_type=project_type,
            technical_requirements=tech_requirements,
            non_functional_requirements=non_functional,
            technology_preferences=tech_preferences,
            constraints=constraints,
            extracted_entities=entities,
            confidence_score=confidence
        )
    
    def _detect_project_type(self, description: str) -> str:
        """프로젝트 타입 감지"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['웹', 'web', 'website', '사이트']):
            return 'web_application'
        elif any(word in desc_lower for word in ['모바일', 'mobile', 'app', '앱']):
            return 'mobile_application'
        elif any(word in desc_lower for word in ['api', 'rest', 'graphql', '서버']):
            return 'api_service'
        elif any(word in desc_lower for word in ['cli', 'command', '명령어']):
            return 'cli_tool'
        else:
            return 'general_application'
    
    def _extract_technical_requirements(self, description: str) -> List[str]:
        """기술적 요구사항 추출"""
        requirements = []
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['실시간', 'real-time', 'realtime', 'live']):
            requirements.append('실시간 데이터 처리')
        
        if any(word in desc_lower for word in ['로그인', 'login', 'auth', '인증']):
            requirements.append('사용자 인증 시스템')
        
        if any(word in desc_lower for word in ['저장', 'database', 'db', '데이터']):
            requirements.append('데이터 저장소')
        
        if any(word in desc_lower for word in ['업로드', 'upload', '파일']):
            requirements.append('파일 업로드 기능')
        
        if any(word in desc_lower for word in ['검색', 'search', '찾기']):
            requirements.append('검색 기능')
        
        return requirements
    
    def _extract_non_functional_requirements(self, description: str) -> List[str]:
        """비기능적 요구사항 추출"""
        requirements = []
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['빠른', 'fast', 'quick', '성능']):
            requirements.append('고성능 처리')
        
        if any(word in desc_lower for word in ['보안', 'secure', 'security', '안전']):
            requirements.append('보안 강화')
        
        if any(word in desc_lower for word in ['확장', 'scalable', 'scale', '많은 사용자']):
            requirements.append('확장 가능한 아키텍처')
        
        return requirements
    
    def _extract_technology_preferences(self, description: str) -> Dict[str, Any]:
        """기술 스택 선호도 추출"""
        preferences = {}
        desc_lower = description.lower()
        
        # 프론트엔드
        frontend_techs = []
        if 'react' in desc_lower:
            frontend_techs.append('React')
        if 'vue' in desc_lower:
            frontend_techs.append('Vue.js')
        if 'angular' in desc_lower:
            frontend_techs.append('Angular')
        
        if frontend_techs:
            preferences['frontend'] = frontend_techs
        
        # 백엔드
        backend_techs = []
        if any(word in desc_lower for word in ['node', 'nodejs']):
            backend_techs.append('Node.js')
        if 'python' in desc_lower:
            backend_techs.append('Python')
        if 'java' in desc_lower:
            backend_techs.append('Java')
        
        if backend_techs:
            preferences['backend'] = backend_techs
        
        return preferences
    
    def _extract_constraints(self, description: str) -> List[str]:
        """제약사항 추출"""
        constraints = []
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['빠르게', 'urgent', '급하게']):
            constraints.append('짧은 개발 기간')
        
        if any(word in desc_lower for word in ['간단', 'simple', '쉽게']):
            constraints.append('단순한 구조 선호')
        
        return constraints
    
    def _extract_entities(self, description: str) -> Dict[str, Any]:
        """엔티티 추출"""
        entities = {
            'keywords': [],
            'technologies': [],
            'features': []
        }
        
        words = description.split()
        for word in words:
            if len(word) > 2 and word.isalpha():
                entities['keywords'].append(word)
        
        return entities
    
    def _calculate_confidence(self, description: str, requirements: List[str]) -> float:
        """신뢰도 점수 계산"""
        base_score = 0.5
        
        if len(description) > 50:
            base_score += 0.2
        
        if len(requirements) > 2:
            base_score += 0.2
        
        if any(tech in description.lower() for tech in ['react', 'vue', 'python', 'node']):
            base_score += 0.1
        
        return min(base_score, 1.0)

# 테스트 함수
async def test_bedrock_agent():
    """Bedrock 연결 테스트"""
    agent = NLInputAgentWithBedrock()
    
    test_cases = [
        "실시간 채팅 기능이 있는 React 웹 애플리케이션을 만들고 싶습니다. 사용자 인증과 파일 업로드 기능도 필요합니다.",
        "Python으로 REST API 서버를 개발하고 싶습니다. 데이터베이스 연동과 보안이 중요합니다.",
        "간단한 모바일 앱을 만들고 싶어요. 사용자가 사진을 업로드하고 공유할 수 있는 기능이 필요합니다."
    ]
    
    for i, description in enumerate(test_cases, 1):
        print(f"\n🧪 테스트 케이스 {i}:")
        print(f"입력: {description}")
        
        result = await agent.process_description(description)
        
        print(f"프로젝트 타입: {result.project_type}")
        print(f"기술 요구사항: {result.technical_requirements}")
        print(f"기술 선호도: {result.technology_preferences}")
        print(f"신뢰도: {result.confidence_score:.2f}")
        print(f"Bedrock 사용: {'✅' if agent.bedrock_available else '❌'}")

if __name__ == "__main__":
    asyncio.run(test_bedrock_agent())