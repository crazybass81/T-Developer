"""
T-Developer NL Input Agent - Bedrock 최종 작동 버전
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

class TDeveloperNLAgentFinal:
    """T-Developer NL Agent - AWS Bedrock 최종 작동 버전"""
    
    def __init__(self):
        try:
            # 사용 가능한 Claude 3 Sonnet 모델 사용
            self.agent = Agent(
                name="T-Developer-NL-Final",
                model=AwsBedrock(
                    id="anthropic.claude-3-sonnet-20240229-v1:0",  # 작동하는 모델 ID
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
            print(f"✅ T-Developer NL Agent (Bedrock Final) 생성 완료!")
            print(f"   Model: Claude 3 Sonnet")
            print(f"   Region: us-east-1")
            
        except Exception as e:
            print(f"❌ Bedrock 연결 실패: {e}")
            self.bedrock_available = False
            self.agent = None
    
    def analyze_project_description(self, description: str) -> ProjectRequirements:
        """프로젝트 설명 분석"""
        
        if not self.bedrock_available:
            return self._analyze_locally(description)
        
        analysis_prompt = f"""
다음 프로젝트 설명을 분석하고 구조화된 요구사항을 추출해주세요.

프로젝트 설명: {description}

다음 JSON 형식으로 정확히 응답해주세요:
{{
    "project_type": "web_application",
    "technical_requirements": [
        "실시간 데이터 처리",
        "사용자 인증 시스템"
    ],
    "non_functional_requirements": [
        "고성능 처리",
        "보안 강화"
    ],
    "technology_preferences": {{
        "frontend": ["React"],
        "backend": ["Node.js"],
        "database": ["PostgreSQL"]
    }},
    "constraints": [
        "짧은 개발 기간"
    ],
    "confidence_score": 0.9
}}

주의사항:
- project_type은 web_application, mobile_application, api_service, cli_tool, desktop_application 중 하나
- 명시되지 않은 내용은 빈 배열로 두세요
- confidence_score는 0.0-1.0 사이의 값
"""
        
        try:
            print("🤖 Bedrock Claude 3 Sonnet으로 분석 중...")
            
            response = self.agent.run(analysis_prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            print(f"📝 Bedrock 응답 길이: {len(response_text)} 문자")
            
            # JSON 파싱
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    parsed = json.loads(json_text)
                    
                    print("✅ Bedrock 분석 성공!")
                    
                    return ProjectRequirements(
                        description=description,
                        project_type=parsed.get('project_type', 'general_application'),
                        technical_requirements=parsed.get('technical_requirements', []),
                        non_functional_requirements=parsed.get('non_functional_requirements', []),
                        technology_preferences=parsed.get('technology_preferences', {}),
                        constraints=parsed.get('constraints', []),
                        extracted_entities={'bedrock_response': json_text},
                        confidence_score=parsed.get('confidence_score', 0.8)
                    )
                else:
                    raise ValueError("JSON 블록을 찾을 수 없음")
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ JSON 파싱 실패: {e}")
                print(f"Raw response: {response_text[:300]}...")
                return self._analyze_locally(description)
                
        except Exception as e:
            print(f"⚠️ Bedrock 분석 실패: {e}")
            return self._analyze_locally(description)
    
    def _analyze_locally(self, description: str) -> ProjectRequirements:
        """로컬 분석 (폴백)"""
        print("🔧 로컬 분석으로 전환...")
        
        desc_lower = description.lower()
        
        # 프로젝트 타입
        if any(word in desc_lower for word in ['웹', 'web', 'website']):
            project_type = 'web_application'
        elif any(word in desc_lower for word in ['모바일', 'mobile', 'app']):
            project_type = 'mobile_application'
        elif any(word in desc_lower for word in ['api', 'rest', 'server']):
            project_type = 'api_service'
        else:
            project_type = 'general_application'
        
        # 기술 요구사항
        tech_requirements = []
        if any(word in desc_lower for word in ['실시간', 'real-time', 'live']):
            tech_requirements.append('실시간 데이터 처리')
        if any(word in desc_lower for word in ['인증', 'auth', 'login']):
            tech_requirements.append('사용자 인증 시스템')
        if any(word in desc_lower for word in ['파일', 'upload', '업로드']):
            tech_requirements.append('파일 업로드 기능')
        if any(word in desc_lower for word in ['채팅', 'chat', '메시지']):
            tech_requirements.append('메시징 시스템')
        
        # 기술 선호도
        tech_preferences = {}
        if 'react' in desc_lower:
            tech_preferences['frontend'] = ['React']
        if 'python' in desc_lower:
            tech_preferences['backend'] = ['Python']
        if 'fastapi' in desc_lower:
            tech_preferences['backend'] = ['Python', 'FastAPI']
        if 'postgresql' in desc_lower:
            tech_preferences['database'] = ['PostgreSQL']
        
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

def test_final_bedrock():
    """최종 Bedrock 테스트"""
    print("🚀 T-Developer NL Agent 최종 Bedrock 테스트\n")
    
    agent = TDeveloperNLAgentFinal()
    
    test_cases = [
        "실시간 채팅 기능이 있는 React 웹 애플리케이션을 만들고 싶습니다. 사용자 인증과 파일 업로드가 필요합니다.",
        "Python FastAPI로 REST API를 개발하고 싶습니다. PostgreSQL 데이터베이스와 JWT 인증이 필요합니다.",
        "간단한 모바일 앱을 만들고 싶어요. 사진 업로드와 소셜 기능이 필요합니다."
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
    
    print("🎉 최종 테스트 완료!")

if __name__ == "__main__":
    test_final_bedrock()