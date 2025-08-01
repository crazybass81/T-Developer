"""
T-Developer NL Input Agent - Bedrock 완전 작동 버전
"""
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
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

class TDeveloperNLAgentBedrock:
    """T-Developer NL Agent - AWS Bedrock 완전 연결"""
    
    def __init__(self):
        try:
            # Agno + Bedrock Agent 생성 (동기 방식)
            self.agent = Agent(
                name="T-Developer-NL-Bedrock",
                model=AwsBedrock(
                    id="anthropic.claude-3-5-sonnet-20241022-v2:0",  # 최신 Claude 3.5 Sonnet
                    aws_region="us-east-1",
                    temperature=0.3,
                    max_tokens=4000
                ),
                role="Senior requirements analyst and technical architect",
                instructions=[
                    "프로젝트 설명에서 핵심 요구사항을 추출",
                    "기술적/비기능적 요구사항을 구분",
                    "프로젝트 유형과 규모를 파악",
                    "JSON 형식으로 구조화된 응답 제공"
                ]
            )
            
            self.bedrock_available = True
            print(f"✅ T-Developer NL Agent (Bedrock) 생성 완료!")
            print(f"   Model: Claude 3.5 Sonnet v2")
            print(f"   Region: us-east-1")
            
        except Exception as e:
            print(f"❌ Bedrock 연결 실패: {e}")
            self.bedrock_available = False
            self.agent = None
    
    def analyze_project_description(self, description: str) -> ProjectRequirements:
        """프로젝트 설명 분석 (동기 방식)"""
        
        if not self.bedrock_available:
            return self._analyze_locally(description)
        
        analysis_prompt = f"""
다음 프로젝트 설명을 분석하고 구조화된 요구사항을 추출해주세요.

프로젝트 설명: {description}

다음 JSON 형식으로 정확히 응답해주세요:
{{
    "project_type": "web_application|mobile_application|api_service|cli_tool|desktop_application",
    "technical_requirements": [
        "구체적인 기술적 요구사항들"
    ],
    "non_functional_requirements": [
        "성능, 보안, 확장성 등 비기능적 요구사항들"
    ],
    "technology_preferences": {{
        "frontend": ["선호하는 프론트엔드 기술들"],
        "backend": ["선호하는 백엔드 기술들"],
        "database": ["선호하는 데이터베이스"]
    }},
    "constraints": [
        "시간, 예산, 기술적 제약사항들"
    ],
    "confidence_score": 0.95
}}

주의사항:
- 명시되지 않은 내용은 빈 배열로 두세요
- confidence_score는 0.0-1.0 사이의 값으로 설정하세요
- 한국어 설명의 경우 기술 용어는 영어로 변환하세요
"""
        
        try:
            print("🤖 Bedrock Claude로 분석 중...")
            
            # 동기 방식으로 실행
            response = self.agent.run(analysis_prompt)
            
            # 응답 텍스트 추출
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"📝 Bedrock 응답: {response_text[:200]}...")
            
            # JSON 파싱
            try:
                # JSON 블록 찾기
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    parsed = json.loads(json_text)
                    
                    print("✅ Bedrock 분석 완료!")
                    
                    return ProjectRequirements(
                        description=description,
                        project_type=parsed.get('project_type', 'general_application'),
                        technical_requirements=parsed.get('technical_requirements', []),
                        non_functional_requirements=parsed.get('non_functional_requirements', []),
                        technology_preferences=parsed.get('technology_preferences', {}),
                        constraints=parsed.get('constraints', []),
                        extracted_entities={'bedrock_response': response_text},
                        confidence_score=parsed.get('confidence_score', 0.8)
                    )
                else:
                    raise ValueError("JSON 블록을 찾을 수 없음")
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ JSON 파싱 실패: {e}")
                return self._analyze_locally(description)
                
        except Exception as e:
            print(f"⚠️ Bedrock 분석 실패: {e}")
            return self._analyze_locally(description)
    
    def _analyze_locally(self, description: str) -> ProjectRequirements:
        """로컬 분석 (폴백)"""
        print("🔧 로컬 분석으로 전환...")
        
        # 간단한 규칙 기반 분석
        project_type = 'web_application' if 'web' in description.lower() else 'general_application'
        
        tech_requirements = []
        if '실시간' in description or 'real-time' in description.lower():
            tech_requirements.append('실시간 데이터 처리')
        if '인증' in description or 'auth' in description.lower():
            tech_requirements.append('사용자 인증 시스템')
        
        tech_preferences = {}
        if 'react' in description.lower():
            tech_preferences['frontend'] = ['React']
        if 'python' in description.lower():
            tech_preferences['backend'] = ['Python']
        
        return ProjectRequirements(
            description=description,
            project_type=project_type,
            technical_requirements=tech_requirements,
            non_functional_requirements=[],
            technology_preferences=tech_preferences,
            constraints=[],
            extracted_entities={'method': 'local'},
            confidence_score=0.7
        )

def test_bedrock_connection():
    """Bedrock 연결 테스트"""
    print("🚀 T-Developer NL Agent Bedrock 연결 테스트\n")
    
    agent = TDeveloperNLAgentBedrock()
    
    if not agent.bedrock_available:
        print("❌ Bedrock 연결 실패")
        return
    
    test_cases = [
        "실시간 채팅 기능이 있는 React 웹 애플리케이션을 만들고 싶습니다. 사용자 인증과 파일 업로드가 필요합니다.",
        "Python FastAPI로 REST API를 개발하고 싶습니다. PostgreSQL 데이터베이스와 JWT 인증이 필요합니다."
    ]
    
    for i, description in enumerate(test_cases, 1):
        print(f"{'='*60}")
        print(f"🧪 테스트 케이스 {i}")
        print(f"{'='*60}")
        print(f"📝 입력: {description}")
        print()
        
        try:
            result = agent.analyze_project_description(description)
            
            print(f"📊 분석 결과:")
            print(f"   프로젝트 타입: {result.project_type}")
            print(f"   기술 요구사항: {result.technical_requirements}")
            print(f"   비기능 요구사항: {result.non_functional_requirements}")
            print(f"   기술 선호도: {result.technology_preferences}")
            print(f"   제약사항: {result.constraints}")
            print(f"   신뢰도: {result.confidence_score:.2f}")
            print(f"   Bedrock 사용: {'✅' if 'bedrock_response' in result.extracted_entities else '❌'}")
            
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
        
        print()
    
    print("🎉 테스트 완료!")

if __name__ == "__main__":
    test_bedrock_connection()