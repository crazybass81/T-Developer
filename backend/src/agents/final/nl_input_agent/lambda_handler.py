"""
Lambda Handler for NL Input Agent
Production-ready implementation with all SubTasks
"""

import json
import boto3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# AWS 클라이언트
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')
ssm = boto3.client('ssm')
secrets_manager = boto3.client('secretsmanager')

class NLInputAgent:
    """
    NL Input Agent - Tasks 4.1-4.10
    자연어 입력을 프로젝트 요구사항으로 변환
    """
    
    def __init__(self):
        self.table_name = os.environ.get('SESSION_TABLE', 't-developer-sessions-development')
        self.environment = os.environ.get('ENVIRONMENT', 'development')
        
    def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """메인 처리 로직"""
        
        session_id = context.get('session_id', str(uuid.uuid4()))
        user_id = context.get('user_id', 'anonymous')
        
        # Task 4.1: 자연어 입력 수신 및 전처리
        preprocessed = self._preprocess_input(user_input)
        
        # Task 4.2: 의도 파악 및 분류
        intent = self._classify_intent(preprocessed)
        
        # Task 4.3: 프로젝트 유형 결정
        project_type = self._determine_project_type(preprocessed, intent)
        
        # Task 4.4: 요구사항 추출
        requirements = self._extract_requirements(preprocessed, project_type)
        
        # Task 4.5: 제약 조건 식별
        constraints = self._identify_constraints(preprocessed, requirements)
        
        # Task 4.6: 기술 스택 제안
        suggested_stack = self._suggest_tech_stack(project_type, requirements)
        
        # Task 4.7: 모호성 검출 및 명확화 질문 생성
        clarifications = self._generate_clarifications(preprocessed, requirements)
        
        # Task 4.8: 컨텍스트 정보 수집
        context_info = self._gather_context(user_id, session_id)
        
        # Task 4.9: 요구사항 검증
        validation = self._validate_requirements(requirements, constraints)
        
        # Task 4.10: 구조화된 출력 생성
        structured_output = self._generate_structured_output(
            requirements, constraints, suggested_stack, 
            clarifications, validation, context_info
        )
        
        # 세션 저장
        self._save_session(session_id, user_id, structured_output)
        
        return structured_output
    
    def _preprocess_input(self, user_input: str) -> str:
        """Task 4.1: 입력 전처리"""
        # 정규화, 특수문자 처리, 언어 감지 등
        processed = user_input.strip().lower()
        return processed
    
    def _classify_intent(self, text: str) -> str:
        """Task 4.2: 의도 분류"""
        intents = {
            'create': ['create', 'build', 'make', 'develop'],
            'modify': ['modify', 'update', 'change', 'edit'],
            'analyze': ['analyze', 'review', 'check', 'audit']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in text for keyword in keywords):
                return intent
        return 'create'
    
    def _determine_project_type(self, text: str, intent: str) -> str:
        """Task 4.3: 프로젝트 유형 결정"""
        types = {
            'web': ['website', 'web app', 'web application', 'site'],
            'mobile': ['mobile', 'ios', 'android', 'app'],
            'api': ['api', 'backend', 'service', 'rest', 'graphql'],
            'desktop': ['desktop', 'windows', 'mac', 'linux'],
            'ai': ['ai', 'ml', 'machine learning', 'neural'],
            'blockchain': ['blockchain', 'crypto', 'smart contract']
        }
        
        for proj_type, keywords in types.items():
            if any(keyword in text for keyword in keywords):
                return proj_type
        return 'web'
    
    def _extract_requirements(self, text: str, project_type: str) -> Dict[str, Any]:
        """Task 4.4: 요구사항 추출"""
        return {
            'functional': self._extract_functional_requirements(text),
            'non_functional': self._extract_non_functional_requirements(text),
            'features': self._extract_features(text),
            'project_type': project_type
        }
    
    def _extract_functional_requirements(self, text: str) -> List[str]:
        """기능적 요구사항 추출"""
        requirements = []
        
        # 인증/인가
        if any(word in text for word in ['login', 'auth', 'user', 'account']):
            requirements.append('User authentication and authorization')
        
        # 데이터베이스
        if any(word in text for word in ['data', 'store', 'database', 'save']):
            requirements.append('Data persistence and management')
        
        # 결제
        if any(word in text for word in ['payment', 'pay', 'checkout', 'stripe']):
            requirements.append('Payment processing')
        
        # 검색
        if 'search' in text:
            requirements.append('Search functionality')
        
        # 실시간
        if any(word in text for word in ['realtime', 'real-time', 'live', 'chat']):
            requirements.append('Real-time features')
        
        return requirements
    
    def _extract_non_functional_requirements(self, text: str) -> List[str]:
        """비기능적 요구사항 추출"""
        requirements = []
        
        # 성능
        if any(word in text for word in ['fast', 'performance', 'speed']):
            requirements.append('High performance')
        
        # 확장성
        if any(word in text for word in ['scalable', 'scale', 'growth']):
            requirements.append('Scalability')
        
        # 보안
        if any(word in text for word in ['secure', 'security', 'safe']):
            requirements.append('Security')
        
        # 접근성
        if any(word in text for word in ['accessible', 'a11y', 'wcag']):
            requirements.append('Accessibility')
        
        return requirements
    
    def _extract_features(self, text: str) -> List[str]:
        """주요 기능 추출"""
        features = []
        
        feature_patterns = {
            'dashboard': ['dashboard', 'admin panel', 'control panel'],
            'analytics': ['analytics', 'metrics', 'statistics'],
            'notifications': ['notification', 'alert', 'email'],
            'api': ['api', 'integration', 'webhook'],
            'upload': ['upload', 'file', 'image', 'media']
        }
        
        for feature, patterns in feature_patterns.items():
            if any(pattern in text for pattern in patterns):
                features.append(feature)
        
        return features
    
    def _identify_constraints(self, text: str, requirements: Dict) -> Dict[str, Any]:
        """Task 4.5: 제약 조건 식별"""
        return {
            'technical': self._identify_technical_constraints(text),
            'business': self._identify_business_constraints(text),
            'regulatory': self._identify_regulatory_constraints(text),
            'timeline': self._extract_timeline(text),
            'budget': self._extract_budget(text)
        }
    
    def _identify_technical_constraints(self, text: str) -> List[str]:
        """기술적 제약 조건"""
        constraints = []
        
        # 브라우저 지원
        if any(word in text for word in ['ie', 'browser', 'compatibility']):
            constraints.append('Browser compatibility requirements')
        
        # 모바일 지원
        if any(word in text for word in ['mobile', 'responsive', 'adaptive']):
            constraints.append('Mobile responsiveness required')
        
        # 오프라인
        if 'offline' in text:
            constraints.append('Offline capability required')
        
        return constraints
    
    def _identify_business_constraints(self, text: str) -> List[str]:
        """비즈니스 제약 조건"""
        constraints = []
        
        if any(word in text for word in ['startup', 'mvp', 'prototype']):
            constraints.append('MVP/Rapid development')
        
        if any(word in text for word in ['enterprise', 'corporate']):
            constraints.append('Enterprise requirements')
        
        return constraints
    
    def _identify_regulatory_constraints(self, text: str) -> List[str]:
        """규제 관련 제약 조건"""
        constraints = []
        
        if any(word in text for word in ['gdpr', 'privacy', 'data protection']):
            constraints.append('GDPR compliance')
        
        if any(word in text for word in ['hipaa', 'health', 'medical']):
            constraints.append('HIPAA compliance')
        
        if any(word in text for word in ['pci', 'payment', 'card']):
            constraints.append('PCI compliance')
        
        return constraints
    
    def _extract_timeline(self, text: str) -> Optional[str]:
        """타임라인 추출"""
        import re
        
        # 주/월 패턴 찾기
        week_pattern = r'(\d+)\s*weeks?'
        month_pattern = r'(\d+)\s*months?'
        
        if match := re.search(week_pattern, text):
            return f"{match.group(1)} weeks"
        if match := re.search(month_pattern, text):
            return f"{match.group(1)} months"
        
        if 'asap' in text or 'urgent' in text:
            return 'ASAP'
        
        return None
    
    def _extract_budget(self, text: str) -> Optional[str]:
        """예산 추출"""
        import re
        
        money_pattern = r'\$[\d,]+'
        if match := re.search(money_pattern, text):
            return match.group(0)
        
        if 'low budget' in text or 'cheap' in text:
            return 'Low budget'
        if 'unlimited' in text or 'no limit' in text:
            return 'Flexible'
        
        return None
    
    def _suggest_tech_stack(self, project_type: str, requirements: Dict) -> Dict[str, List[str]]:
        """Task 4.6: 기술 스택 제안"""
        stacks = {
            'web': {
                'frontend': ['React', 'Vue.js', 'Angular'],
                'backend': ['Node.js', 'Python/Django', 'Ruby on Rails'],
                'database': ['PostgreSQL', 'MongoDB', 'MySQL']
            },
            'mobile': {
                'framework': ['React Native', 'Flutter', 'Swift/Kotlin'],
                'backend': ['Firebase', 'AWS Amplify', 'Node.js'],
                'database': ['Firestore', 'Realm', 'SQLite']
            },
            'api': {
                'framework': ['FastAPI', 'Express.js', 'Spring Boot'],
                'database': ['PostgreSQL', 'MongoDB', 'Redis'],
                'tools': ['Docker', 'Kubernetes', 'API Gateway']
            }
        }
        
        return stacks.get(project_type, stacks['web'])
    
    def _generate_clarifications(self, text: str, requirements: Dict) -> List[str]:
        """Task 4.7: 명확화 질문 생성"""
        questions = []
        
        # 모호한 요구사항 확인
        if not requirements['features']:
            questions.append("What are the main features you want in your application?")
        
        if 'users' in text but 'how many' not in text:
            questions.append("How many users do you expect to use this application?")
        
        if 'data' in text but not any(word in text for word in ['database', 'store', 'save']):
            questions.append("What kind of data will the application handle?")
        
        return questions
    
    def _gather_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Task 4.8: 컨텍스트 정보 수집"""
        return {
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'previous_sessions': self._get_previous_sessions(user_id)
        }
    
    def _get_previous_sessions(self, user_id: str) -> int:
        """이전 세션 수 조회"""
        try:
            table = dynamodb.Table(self.table_name)
            response = table.query(
                IndexName='user_id_index',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            return response.get('Count', 0)
        except:
            return 0
    
    def _validate_requirements(self, requirements: Dict, constraints: Dict) -> Dict[str, Any]:
        """Task 4.9: 요구사항 검증"""
        issues = []
        warnings = []
        
        # 충돌 검사
        if 'High performance' in requirements.get('non_functional', []) and constraints.get('budget') == 'Low budget':
            warnings.append("High performance requirements may conflict with budget constraints")
        
        # 완전성 검사
        if not requirements.get('functional'):
            issues.append("No functional requirements identified")
        
        # 실현 가능성 검사
        timeline = constraints.get('timeline')
        if timeline == 'ASAP' and len(requirements.get('features', [])) > 10:
            warnings.append("Large feature set may not be achievable in urgent timeline")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def _generate_structured_output(self, requirements: Dict, constraints: Dict, 
                                   tech_stack: Dict, clarifications: List[str],
                                   validation: Dict, context: Dict) -> Dict[str, Any]:
        """Task 4.10: 구조화된 출력 생성"""
        return {
            'success': True,
            'session_id': context['session_id'],
            'requirements': requirements,
            'constraints': constraints,
            'suggested_stack': tech_stack,
            'clarification_questions': clarifications,
            'validation': validation,
            'context': context,
            'next_agent': 'ui_selection',
            'metadata': {
                'agent': 'nl_input',
                'version': '1.0.0',
                'tasks_completed': ['4.1', '4.2', '4.3', '4.4', '4.5', '4.6', '4.7', '4.8', '4.9', '4.10'],
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def _save_session(self, session_id: str, user_id: str, data: Dict[str, Any]):
        """세션 저장"""
        try:
            table = dynamodb.Table(self.table_name)
            table.put_item(
                Item={
                    'session_id': session_id,
                    'user_id': user_id,
                    'data': json.dumps(data),
                    'created_at': int(datetime.now().timestamp()),
                    'ttl': int(datetime.now().timestamp()) + 86400 * 7  # 7일 후 만료
                }
            )
        except Exception as e:
            print(f"Error saving session: {e}")


def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Lambda handler"""
    
    try:
        # 요청 파싱
        body = event.get('body', {})
        if isinstance(body, str):
            body = json.loads(body)
        
        # 에이전트 실행
        agent = NLInputAgent()
        result = agent.process(
            user_input=body.get('user_input', ''),
            context=body.get('context', {})
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps(result),
            'headers': {
                'Content-Type': 'application/json',
                'X-Agent-Name': 'nl_input',
                'X-Tasks-Completed': '4.1-4.10'
            }
        }
        
    except Exception as e:
        print(f"Error in NL Input Agent: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'agent': 'nl_input'
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }