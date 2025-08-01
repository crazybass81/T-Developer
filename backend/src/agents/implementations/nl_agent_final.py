"""
T-Developer NL Input Agent - 최종 완성 버전 (Agno + Bedrock)
"""
from agno.agent import Agent
from agno.models.aws import AwsBedrock
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import os
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

class TDeveloperNLAgent:
    """T-Developer 자연어 입력 처리 에이전트 - 최종 버전"""
    
    def __init__(self):
        # AWS 설정
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        try:
            # Agno + Bedrock Agent 생성 (올바른 파라미터 사용)
            self.agent = Agent(
                name="T-Developer-NL-Agent",
                model=AwsBedrock(
                    id="anthropic.claude-3-sonnet-20240229-v1:0",
                    aws_region=aws_region,  # region 대신 aws_region 사용
                    temperature=0.3
                ),
                role="Senior requirements analyst and technical architect",
                instructions=[
                    "프로젝트 설명에서 핵심 요구사항을 추출",
                    "기술적/비기술적 요구사항을 구분",
                    "프로젝트 유형과 규모를 파악",
                    "선호 기술 스택과 제약사항을 식별",
                    "JSON 형식으로 구조화된 응답 제공"
                ],
                description="자연어 프로젝트 설명을 분석하고 구조화된 요구사항으로 변환"
            )
            
            self.bedrock_available = True
            print(f"✅ T-Developer NL Agent (Agno + Bedrock) 생성 완료!")
            print(f"   Agent ID: {self.agent.agent_id}")
            print(f"   Model: Claude 3 Sonnet")
            print(f"   Region: {aws_region}")
            
        except Exception as e:
            print(f"⚠️ Bedrock 연결 실패, 로컬 모드로 전환: {e}")
            
            # Bedrock 없이 Agno만 사용
            self.agent = Agent(
                name="T-Developer-NL-Agent-Local",
                description="프로젝트 설명에서 핵심 요구사항을 추출하는 전문가",
                instructions=[
                    "프로젝트 설명에서 핵심 요구사항을 추출",
                    "기술적/비기술적 요구사항을 구분",
                    "프로젝트 유형과 규모를 파악"
                ]
            )
            
            self.bedrock_available = False
            print(f"✅ T-Developer NL Agent (Local) 생성 완료!")
            print(f"   Agent ID: {self.agent.agent_id}")
    
    async def analyze_project_description(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """
        프로젝트 설명 분석 - 메인 API
        
        Args:
            description: 자연어 프로젝트 설명
            context: 추가 컨텍스트 정보
            
        Returns:
            ProjectRequirements: 구조화된 요구사항
        """
        
        if self.bedrock_available:
            return await self._analyze_with_bedrock(description, context)
        else:
            return await self._analyze_locally(description, context)
    
    async def _analyze_with_bedrock(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """Bedrock Claude를 사용한 고급 분석"""
        
        analysis_prompt = f"""
        다음 프로젝트 설명을 분석하고 구조화된 요구사항을 추출해주세요.

        프로젝트 설명:
        {description}

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
                "database": ["선호하는 데이터베이스"],
                "deployment": ["선호하는 배포 방식"]
            }},
            "constraints": [
                "시간, 예산, 기술적 제약사항들"
            ],
            "confidence_score": 0.95
        }}

        주의사항:
        - 명시되지 않은 내용은 추측하지 말고 빈 배열로 두세요
        - confidence_score는 0.0-1.0 사이의 값으로 설정하세요
        - 한국어 설명의 경우 기술 용어는 영어로 변환하세요
        """
        
        try:
            # Agno Agent 실행
            print("🤖 Bedrock Claude로 분석 중...")
            response = await self.agent.arun(analysis_prompt)
            
            # 응답에서 JSON 추출
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # JSON 파싱 시도
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
                print(f"Raw response: {response_text[:200]}...")
                return await self._analyze_locally(description, context)
                
        except Exception as e:
            print(f"⚠️ Bedrock 분석 실패: {e}")
            return await self._analyze_locally(description, context)
    
    async def _analyze_locally(self, description: str, context: Optional[Dict] = None) -> ProjectRequirements:
        """로컬 규칙 기반 분석 (폴백)"""
        
        print("🔧 로컬 규칙 기반 분석 중...")
        
        # 프로젝트 타입 감지
        project_type = self._detect_project_type(description)
        
        # 기술적 요구사항 추출
        tech_requirements = self._extract_technical_requirements(description)
        
        # 비기능적 요구사항 추출
        non_functional = self._extract_non_functional_requirements(description)
        
        # 기술 선호도 추출
        tech_preferences = self._extract_technology_preferences(description)
        
        # 제약사항 추출
        constraints = self._extract_constraints(description)
        
        # 엔티티 추출
        entities = self._extract_entities(description)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(description, tech_requirements)
        
        print("✅ 로컬 분석 완료!")
        
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
        
        # 웹 애플리케이션
        if any(word in desc_lower for word in ['웹', 'web', 'website', '사이트', 'html', 'css']):
            return 'web_application'
        
        # 모바일 애플리케이션
        elif any(word in desc_lower for word in ['모바일', 'mobile', 'app', '앱', 'ios', 'android']):
            return 'mobile_application'
        
        # API 서비스
        elif any(word in desc_lower for word in ['api', 'rest', 'graphql', '서버', 'server', 'backend']):
            return 'api_service'
        
        # CLI 도구
        elif any(word in desc_lower for word in ['cli', 'command', '명령어', 'terminal', 'console']):
            return 'cli_tool'
        
        # 데스크톱 애플리케이션
        elif any(word in desc_lower for word in ['desktop', '데스크톱', 'gui', 'window']):
            return 'desktop_application'
        
        else:
            return 'general_application'
    
    def _extract_technical_requirements(self, description: str) -> List[str]:
        """기술적 요구사항 추출"""
        requirements = []
        desc_lower = description.lower()
        
        # 실시간 기능
        if any(word in desc_lower for word in ['실시간', 'real-time', 'realtime', 'live', '라이브']):
            requirements.append('실시간 데이터 처리')
        
        # 사용자 인증
        if any(word in desc_lower for word in ['로그인', 'login', 'auth', '인증', 'signin', '회원']):
            requirements.append('사용자 인증 시스템')
        
        # 데이터 저장
        if any(word in desc_lower for word in ['저장', 'database', 'db', '데이터', 'data', '보관']):
            requirements.append('데이터 저장소')
        
        # 파일 처리
        if any(word in desc_lower for word in ['업로드', 'upload', '파일', 'file', '첨부']):
            requirements.append('파일 업로드 기능')
        
        # 검색 기능
        if any(word in desc_lower for word in ['검색', 'search', '찾기', 'find', '조회']):
            requirements.append('검색 기능')
        
        # 채팅/메시징
        if any(word in desc_lower for word in ['채팅', 'chat', '메시지', 'message', '대화']):
            requirements.append('메시징 시스템')
        
        # 알림 기능
        if any(word in desc_lower for word in ['알림', 'notification', 'push', '푸시']):
            requirements.append('알림 시스템')
        
        return requirements
    
    def _extract_non_functional_requirements(self, description: str) -> List[str]:
        """비기능적 요구사항 추출"""
        requirements = []
        desc_lower = description.lower()
        
        # 성능
        if any(word in desc_lower for word in ['빠른', 'fast', 'quick', '성능', 'performance', '속도']):
            requirements.append('고성능 처리')
        
        # 보안
        if any(word in desc_lower for word in ['보안', 'secure', 'security', '안전', 'safe']):
            requirements.append('보안 강화')
        
        # 확장성
        if any(word in desc_lower for word in ['확장', 'scalable', 'scale', '많은 사용자', '대용량']):
            requirements.append('확장 가능한 아키텍처')
        
        # 가용성
        if any(word in desc_lower for word in ['안정', 'stable', 'reliable', '신뢰', '24시간']):
            requirements.append('높은 가용성')
        
        return requirements
    
    def _extract_technology_preferences(self, description: str) -> Dict[str, Any]:
        """기술 스택 선호도 추출"""
        preferences = {}
        desc_lower = description.lower()
        
        # 프론트엔드 기술
        frontend_techs = []
        if 'react' in desc_lower:
            frontend_techs.append('React')
        if 'vue' in desc_lower:
            frontend_techs.append('Vue.js')
        if 'angular' in desc_lower:
            frontend_techs.append('Angular')
        if 'svelte' in desc_lower:
            frontend_techs.append('Svelte')
        
        if frontend_techs:
            preferences['frontend'] = frontend_techs
        
        # 백엔드 기술
        backend_techs = []
        if any(word in desc_lower for word in ['node', 'nodejs']):
            backend_techs.append('Node.js')
        if 'python' in desc_lower:
            backend_techs.append('Python')
        if 'java' in desc_lower:
            backend_techs.append('Java')
        if 'go' in desc_lower:
            backend_techs.append('Go')
        if 'rust' in desc_lower:
            backend_techs.append('Rust')
        
        if backend_techs:
            preferences['backend'] = backend_techs
        
        # 데이터베이스
        database_techs = []
        if any(word in desc_lower for word in ['mysql', 'postgresql', 'postgres']):
            database_techs.append('PostgreSQL' if 'postgres' in desc_lower else 'MySQL')
        if 'mongodb' in desc_lower:
            database_techs.append('MongoDB')
        if 'redis' in desc_lower:
            database_techs.append('Redis')
        
        if database_techs:
            preferences['database'] = database_techs
        
        return preferences
    
    def _extract_constraints(self, description: str) -> List[str]:
        """제약사항 추출"""
        constraints = []
        desc_lower = description.lower()
        
        # 시간 제약
        if any(word in desc_lower for word in ['빠르게', 'urgent', '급하게', '빨리', 'asap']):
            constraints.append('짧은 개발 기간')
        
        # 복잡도 제약
        if any(word in desc_lower for word in ['간단', 'simple', '쉽게', 'easy', '단순']):
            constraints.append('단순한 구조 선호')
        
        # 예산 제약
        if any(word in desc_lower for word in ['저렴', 'cheap', '비용', 'cost', '예산']):
            constraints.append('예산 제약')
        
        return constraints
    
    def _extract_entities(self, description: str) -> Dict[str, Any]:
        """엔티티 추출"""
        entities = {
            'keywords': [],
            'technologies': [],
            'features': [],
            'domain': None
        }
        
        # 키워드 추출
        words = description.split()
        for word in words:
            if len(word) > 2 and word.isalpha():
                entities['keywords'].append(word)
        
        # 도메인 감지
        desc_lower = description.lower()
        if any(word in desc_lower for word in ['쇼핑', 'shop', 'ecommerce', '상거래']):
            entities['domain'] = 'ecommerce'
        elif any(word in desc_lower for word in ['소셜', 'social', 'sns']):
            entities['domain'] = 'social'
        elif any(word in desc_lower for word in ['교육', 'education', '학습']):
            entities['domain'] = 'education'
        
        return entities
    
    def _calculate_confidence(self, description: str, requirements: List[str]) -> float:
        """신뢰도 점수 계산"""
        base_score = 0.5
        
        # 설명 길이에 따른 가중치
        if len(description) > 100:
            base_score += 0.2
        elif len(description) > 50:
            base_score += 0.1
        
        # 추출된 요구사항 수에 따른 가중치
        if len(requirements) > 3:
            base_score += 0.2
        elif len(requirements) > 1:
            base_score += 0.1
        
        # 구체적인 기술 언급 시 가중치
        tech_keywords = ['react', 'vue', 'python', 'node', 'java', 'mysql', 'mongodb']
        if any(tech in description.lower() for tech in tech_keywords):
            base_score += 0.1
        
        return min(base_score, 1.0)

# 종합 테스트 함수
async def comprehensive_test():
    """종합 테스트"""
    print("🚀 T-Developer NL Agent 종합 테스트 시작\n")
    
    agent = TDeveloperNLAgent()
    
    test_cases = [
        {
            "name": "웹 애플리케이션",
            "description": "실시간 채팅 기능이 있는 React 웹 애플리케이션을 만들고 싶습니다. 사용자 인증과 파일 업로드 기능도 필요하고, 성능이 중요합니다."
        },
        {
            "name": "API 서비스", 
            "description": "Python FastAPI로 REST API 서버를 개발하고 싶습니다. PostgreSQL 데이터베이스 연동과 JWT 인증, 보안이 중요합니다."
        },
        {
            "name": "모바일 앱",
            "description": "간단한 소셜 미디어 모바일 앱을 만들고 싶어요. 사용자가 사진을 업로드하고 공유할 수 있고, 푸시 알림 기능이 필요합니다."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{'='*60}")
        print(f"🧪 테스트 케이스 {i}: {test_case['name']}")
        print(f"{'='*60}")
        print(f"📝 입력: {test_case['description']}")
        print()
        
        try:
            result = await agent.analyze_project_description(test_case['description'])
            
            print(f"📊 분석 결과:")
            print(f"   프로젝트 타입: {result.project_type}")
            print(f"   기술 요구사항: {result.technical_requirements}")
            print(f"   비기능 요구사항: {result.non_functional_requirements}")
            print(f"   기술 선호도: {result.technology_preferences}")
            print(f"   제약사항: {result.constraints}")
            print(f"   신뢰도: {result.confidence_score:.2f}")
            print(f"   Bedrock 사용: {'✅' if agent.bedrock_available else '❌'}")
            
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
        
        print()
    
    print("🎉 종합 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(comprehensive_test())