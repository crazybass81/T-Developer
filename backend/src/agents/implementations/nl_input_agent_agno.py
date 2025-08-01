"""
T-Developer NL Input Agent - Agno Framework 연결 버전
"""
from agno.agent import Agent
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import json

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

class NLInputAgentAgno:
    """Agno Framework 기반 자연어 입력 처리 에이전트"""
    
    def __init__(self):
        # Agno Agent 생성 (실제 모델 없이 테스트용)
        self.agent = Agent(
            name="T-Developer-NL-Processor",
            description="프로젝트 설명에서 핵심 요구사항을 추출하는 전문가",
            instructions=[
                "프로젝트 설명에서 핵심 요구사항을 추출",
                "기술적/비기술적 요구사항을 구분", 
                "프로젝트 유형과 규모를 파악",
                "선호 기술 스택과 제약사항을 식별"
            ]
        )
        
        print(f"✅ Agno Agent 생성 완료: {self.agent.agent_id}")
    
    async def process_description(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """자연어 프로젝트 설명 처리"""
        
        # 1. 기본 분석 (Agno 없이 규칙 기반으로 시작)
        project_type = self._detect_project_type(description)
        tech_requirements = self._extract_technical_requirements(description)
        non_functional = self._extract_non_functional_requirements(description)
        tech_preferences = self._extract_technology_preferences(description)
        constraints = self._extract_constraints(description)
        entities = self._extract_entities(description)
        
        # 2. 신뢰도 점수 계산
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
        
        # 실시간 기능
        if any(word in desc_lower for word in ['실시간', 'real-time', 'realtime', 'live']):
            requirements.append('실시간 데이터 처리')
        
        # 인증
        if any(word in desc_lower for word in ['로그인', 'login', 'auth', '인증']):
            requirements.append('사용자 인증 시스템')
        
        # 데이터베이스
        if any(word in desc_lower for word in ['저장', 'database', 'db', '데이터']):
            requirements.append('데이터 저장소')
        
        # 파일 업로드
        if any(word in desc_lower for word in ['업로드', 'upload', '파일']):
            requirements.append('파일 업로드 기능')
        
        # 검색
        if any(word in desc_lower for word in ['검색', 'search', '찾기']):
            requirements.append('검색 기능')
        
        return requirements
    
    def _extract_non_functional_requirements(self, description: str) -> List[str]:
        """비기능적 요구사항 추출"""
        requirements = []
        desc_lower = description.lower()
        
        # 성능
        if any(word in desc_lower for word in ['빠른', 'fast', 'quick', '성능']):
            requirements.append('고성능 처리')
        
        # 보안
        if any(word in desc_lower for word in ['보안', 'secure', 'security', '안전']):
            requirements.append('보안 강화')
        
        # 확장성
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
        
        # 간단한 키워드 추출
        words = description.split()
        for word in words:
            if len(word) > 2 and word.isalpha():
                entities['keywords'].append(word)
        
        return entities
    
    def _calculate_confidence(self, description: str, requirements: List[str]) -> float:
        """신뢰도 점수 계산"""
        base_score = 0.5
        
        # 설명 길이에 따른 가중치
        if len(description) > 50:
            base_score += 0.2
        
        # 추출된 요구사항 수에 따른 가중치
        if len(requirements) > 2:
            base_score += 0.2
        
        # 구체적인 기술 언급 시 가중치
        if any(tech in description.lower() for tech in ['react', 'vue', 'python', 'node']):
            base_score += 0.1
        
        return min(base_score, 1.0)

# 테스트 함수
async def test_nl_agent():
    """NL Agent 테스트"""
    agent = NLInputAgentAgno()
    
    test_description = "실시간 채팅 기능이 있는 웹 애플리케이션을 React로 만들고 싶습니다. 사용자 인증과 파일 업로드 기능도 필요합니다."
    
    result = await agent.process_description(test_description)
    
    print("🧪 NL Agent 테스트 결과:")
    print(f"프로젝트 타입: {result.project_type}")
    print(f"기술 요구사항: {result.technical_requirements}")
    print(f"기술 선호도: {result.technology_preferences}")
    print(f"신뢰도: {result.confidence_score:.2f}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_nl_agent())