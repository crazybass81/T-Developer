"""
User Story Generator Component
Task 4.22: 사용자 스토리 및 유스케이스 생성
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from aws_lambda_powertools import Logger

from .core import UserStory, ParsedRequirement, RequirementPriority

logger = Logger()


class UserStoryGenerator:
    """사용자 스토리 생성 컴포넌트"""
    
    def __init__(self):
        self._init_templates()
        self._init_personas()
        self._init_story_patterns()
    
    def _init_templates(self):
        """스토리 템플릿 초기화"""
        self.templates = {
            'standard': {
                'format': "As a {role}, I want {feature} so that {benefit}",
                'regex': r'as a (.+?), i want (.+?) so that (.+?)(?:\.|$)'
            },
            'extended': {
                'format': "As a {role}, I want {feature} so that {benefit}, given {context}",
                'regex': r'as a (.+?), i want (.+?) so that (.+?), given (.+?)(?:\.|$)'
            },
            'epic': {
                'format': "As {stakeholder}, we need {capability} to {objective}",
                'regex': r'as (.+?), we need (.+?) to (.+?)(?:\.|$)'
            },
            'job_story': {
                'format': "When {situation}, I want to {motivation}, so I can {outcome}",
                'regex': r'when (.+?), i want to (.+?), so i can (.+?)(?:\.|$)'
            }
        }
    
    def _init_personas(self):
        """사용자 페르소나 초기화"""
        self.personas = {
            'end_user': ['user', 'customer', 'client', 'visitor', 'member'],
            'admin': ['admin', 'administrator', 'manager', 'moderator'],
            'developer': ['developer', 'programmer', 'engineer', 'dev'],
            'business': ['stakeholder', 'owner', 'executive', 'business user'],
            'system': ['system', 'application', 'service', 'api']
        }
        
        self.persona_priorities = {
            'end_user': RequirementPriority.HIGH,
            'admin': RequirementPriority.HIGH,
            'developer': RequirementPriority.MEDIUM,
            'business': RequirementPriority.CRITICAL,
            'system': RequirementPriority.MEDIUM
        }
    
    def _init_story_patterns(self):
        """스토리 패턴 초기화"""
        self.action_verbs = {
            'create': ['create', 'add', 'generate', 'make', 'build'],
            'read': ['view', 'see', 'read', 'display', 'show', 'list'],
            'update': ['update', 'edit', 'modify', 'change', 'revise'],
            'delete': ['delete', 'remove', 'destroy', 'eliminate'],
            'search': ['search', 'find', 'filter', 'query', 'lookup'],
            'authenticate': ['login', 'logout', 'authenticate', 'sign in', 'sign up'],
            'manage': ['manage', 'control', 'configure', 'administer'],
            'communicate': ['send', 'receive', 'notify', 'message', 'email']
        }
        
        self.benefit_patterns = [
            'improve', 'enhance', 'optimize', 'streamline',
            'save time', 'increase efficiency', 'reduce errors',
            'better understand', 'make informed decisions',
            'maintain', 'ensure', 'comply with'
        ]
    
    async def generate_from_requirement(
        self,
        requirement: ParsedRequirement
    ) -> Optional[UserStory]:
        """요구사항에서 사용자 스토리 생성"""
        try:
            # 이미 스토리 형식인지 확인
            existing_story = self._extract_existing_story(requirement.description)
            if existing_story:
                return existing_story
            
            # 새 스토리 생성
            role = self._identify_role(requirement.description)
            feature = self._extract_feature(requirement.description)
            benefit = self._generate_benefit(requirement.description, feature)
            
            if not all([role, feature, benefit]):
                return None
            
            # 스토리 포인트 추정
            story_points = self._estimate_story_points(requirement)
            
            # 수용 기준 생성
            acceptance_criteria = self._generate_acceptance_criteria(
                requirement, feature
            )
            
            return UserStory(
                id=f"US_{requirement.id}",
                as_a=role,
                i_want=feature,
                so_that=benefit,
                acceptance_criteria=acceptance_criteria,
                story_points=story_points,
                priority=requirement.priority,
                dependencies=requirement.dependencies
            )
            
        except Exception as e:
            logger.error(f"Error generating user story: {e}")
            return None
    
    async def generate_additional_stories(
        self,
        project_info: Dict[str, Any]
    ) -> List[UserStory]:
        """추가 사용자 스토리 생성"""
        stories = []
        
        # 프로젝트 타입별 기본 스토리
        project_type = project_info.get('type', 'web-application')
        base_stories = self._get_base_stories_for_type(project_type)
        
        for story_data in base_stories:
            story = UserStory(
                id=f"US_BASE_{len(stories)+1}",
                as_a=story_data['role'],
                i_want=story_data['feature'],
                so_that=story_data['benefit'],
                acceptance_criteria=story_data.get('criteria', []),
                story_points=story_data.get('points', 3),
                priority=RequirementPriority(story_data.get('priority', 'medium'))
            )
            stories.append(story)
        
        # 보안 관련 스토리
        if project_info.get('requires_auth', True):
            stories.extend(self._generate_auth_stories())
        
        # 관리자 스토리
        if project_info.get('has_admin', True):
            stories.extend(self._generate_admin_stories())
        
        return stories
    
    def _extract_existing_story(self, text: str) -> Optional[UserStory]:
        """기존 스토리 형식 추출"""
        text_lower = text.lower()
        
        for template_name, template in self.templates.items():
            match = re.search(template['regex'], text_lower, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if template_name in ['standard', 'extended']:
                    return UserStory(
                        id=f"US_EXISTING_{hash(text) % 10000}",
                        as_a=groups[0].strip(),
                        i_want=groups[1].strip(),
                        so_that=groups[2].strip(),
                        acceptance_criteria=[],
                        story_points=None,
                        priority=RequirementPriority.MEDIUM
                    )
        
        return None
    
    def _identify_role(self, text: str) -> Optional[str]:
        """사용자 역할 식별"""
        text_lower = text.lower()
        
        # 명시적 역할 찾기
        role_pattern = r'(?:user|customer|admin|developer|manager|visitor) (?:can|should|must|wants)'
        match = re.search(role_pattern, text_lower)
        if match:
            role = match.group(0).split()[0]
            return self._normalize_role(role)
        
        # 페르소나 매핑
        for persona_type, keywords in self.personas.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return keyword
        
        # 기본값
        return "user"
    
    def _extract_feature(self, text: str) -> Optional[str]:
        """기능 추출"""
        text_lower = text.lower()
        
        # 동작 동사 찾기
        for action_type, verbs in self.action_verbs.items():
            for verb in verbs:
                pattern = f"{verb} (.+?)(?:\\.|,|$)"
                match = re.search(pattern, text_lower)
                if match:
                    feature = match.group(1).strip()
                    # 정제
                    feature = self._clean_feature_text(feature)
                    if len(feature) > 5:  # 의미있는 길이
                        return f"{verb} {feature}"
        
        # 기능 키워드 패턴
        feature_pattern = r'(?:ability|feature|functionality) to (.+?)(?:\.|,|$)'
        match = re.search(feature_pattern, text_lower)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _generate_benefit(self, text: str, feature: str) -> str:
        """이익/가치 생성"""
        text_lower = text.lower()
        
        # 명시적 이익 찾기
        benefit_pattern = r'(?:so that|in order to|to be able to) (.+?)(?:\.|,|$)'
        match = re.search(benefit_pattern, text_lower)
        if match:
            return match.group(1).strip()
        
        # 기능 기반 이익 추론
        if feature:
            feature_lower = feature.lower()
            
            if any(word in feature_lower for word in ['create', 'add', 'generate']):
                return "I can manage my data efficiently"
            elif any(word in feature_lower for word in ['view', 'see', 'display']):
                return "I can access the information I need"
            elif any(word in feature_lower for word in ['update', 'edit', 'modify']):
                return "I can keep information up to date"
            elif any(word in feature_lower for word in ['delete', 'remove']):
                return "I can maintain data cleanliness"
            elif any(word in feature_lower for word in ['search', 'find', 'filter']):
                return "I can quickly find what I'm looking for"
            elif any(word in feature_lower for word in ['login', 'authenticate']):
                return "I can securely access my account"
        
        # 일반적인 이익
        for pattern in self.benefit_patterns:
            if pattern in text_lower:
                return f"I can {pattern} my workflow"
        
        return "I can complete my tasks efficiently"
    
    def _estimate_story_points(self, requirement: ParsedRequirement) -> int:
        """스토리 포인트 추정"""
        points = 3  # 기본값
        
        # 복잡도 요소
        complexity_factors = {
            'simple': ['basic', 'simple', 'standard', 'typical'],
            'medium': ['moderate', 'normal', 'average'],
            'complex': ['complex', 'advanced', 'sophisticated', 'intricate']
        }
        
        text_lower = requirement.description.lower()
        
        # 복잡도 키워드 확인
        for level, keywords in complexity_factors.items():
            if any(keyword in text_lower for keyword in keywords):
                if level == 'simple':
                    points = 1
                elif level == 'medium':
                    points = 3
                elif level == 'complex':
                    points = 5
                break
        
        # 수용 기준 수에 따른 조정
        if len(requirement.acceptance_criteria) > 3:
            points += 2
        elif len(requirement.acceptance_criteria) > 1:
            points += 1
        
        # 의존성에 따른 조정
        if len(requirement.dependencies) > 2:
            points += 2
        elif len(requirement.dependencies) > 0:
            points += 1
        
        # 우선순위에 따른 조정
        if requirement.priority == RequirementPriority.CRITICAL:
            points = max(points, 5)  # 최소 5포인트
        
        return min(points, 13)  # 최대 13포인트 (피보나치)
    
    def _generate_acceptance_criteria(
        self,
        requirement: ParsedRequirement,
        feature: str
    ) -> List[str]:
        """수용 기준 생성"""
        criteria = []
        
        # 기존 수용 기준 사용
        if requirement.acceptance_criteria:
            criteria.extend(requirement.acceptance_criteria)
        
        # 기능 기반 기준 생성
        if feature:
            feature_lower = feature.lower()
            
            # CRUD 작업
            if 'create' in feature_lower or 'add' in feature_lower:
                criteria.extend([
                    "Given valid input data, when submitted, then the item is created successfully",
                    "Given invalid input data, when submitted, then appropriate error messages are displayed",
                    "After successful creation, the user is redirected to the appropriate page"
                ])
            elif 'update' in feature_lower or 'edit' in feature_lower:
                criteria.extend([
                    "Given an existing item, when edited with valid data, then changes are saved",
                    "Given an existing item, when edited with invalid data, then changes are rejected",
                    "The original data is displayed before editing"
                ])
            elif 'delete' in feature_lower or 'remove' in feature_lower:
                criteria.extend([
                    "Given an existing item, when deleted, then it is removed from the system",
                    "A confirmation dialog is shown before deletion",
                    "Deleted items cannot be accessed afterwards"
                ])
            elif 'search' in feature_lower or 'find' in feature_lower:
                criteria.extend([
                    "Search results are relevant to the query",
                    "Search is case-insensitive",
                    "Results are paginated if more than 10 items"
                ])
            elif 'login' in feature_lower or 'authenticate' in feature_lower:
                criteria.extend([
                    "Given valid credentials, when submitted, then user is logged in",
                    "Given invalid credentials, when submitted, then access is denied",
                    "Password is masked during input",
                    "Session expires after inactivity"
                ])
        
        # 제한: 최대 5개 기준
        return criteria[:5]
    
    def _normalize_role(self, role: str) -> str:
        """역할 정규화"""
        role_mappings = {
            'user': 'user',
            'customer': 'customer',
            'client': 'client',
            'admin': 'administrator',
            'administrator': 'administrator',
            'manager': 'manager',
            'developer': 'developer',
            'dev': 'developer',
            'visitor': 'visitor',
            'guest': 'visitor'
        }
        
        return role_mappings.get(role.lower(), role)
    
    def _clean_feature_text(self, text: str) -> str:
        """기능 텍스트 정제"""
        # 불필요한 단어 제거
        stopwords = ['the', 'a', 'an', 'and', 'or', 'but']
        words = text.split()
        cleaned = [w for w in words if w.lower() not in stopwords]
        
        # 재구성
        result = ' '.join(cleaned)
        
        # 길이 제한
        if len(result) > 100:
            result = result[:97] + '...'
        
        return result
    
    def _get_base_stories_for_type(self, project_type: str) -> List[Dict[str, Any]]:
        """프로젝트 타입별 기본 스토리"""
        base_stories = {
            'web-application': [
                {
                    'role': 'user',
                    'feature': 'register for an account',
                    'benefit': 'I can access personalized features',
                    'priority': 'high',
                    'points': 3
                },
                {
                    'role': 'user',
                    'feature': 'reset my password',
                    'benefit': 'I can regain access to my account',
                    'priority': 'high',
                    'points': 2
                },
                {
                    'role': 'user',
                    'feature': 'view my profile',
                    'benefit': 'I can see and manage my information',
                    'priority': 'medium',
                    'points': 1
                }
            ],
            'mobile-application': [
                {
                    'role': 'user',
                    'feature': 'use the app offline',
                    'benefit': 'I can access core features without internet',
                    'priority': 'high',
                    'points': 5
                },
                {
                    'role': 'user',
                    'feature': 'receive push notifications',
                    'benefit': 'I stay informed about important updates',
                    'priority': 'medium',
                    'points': 3
                }
            ],
            'backend-api': [
                {
                    'role': 'developer',
                    'feature': 'access API documentation',
                    'benefit': 'I can integrate the API correctly',
                    'priority': 'critical',
                    'points': 2
                },
                {
                    'role': 'system',
                    'feature': 'handle rate limiting',
                    'benefit': 'the API remains stable under load',
                    'priority': 'high',
                    'points': 3
                }
            ]
        }
        
        return base_stories.get(project_type, [])
    
    def _generate_auth_stories(self) -> List[UserStory]:
        """인증 관련 스토리 생성"""
        return [
            UserStory(
                id="US_AUTH_1",
                as_a="user",
                i_want="to log in with my credentials",
                so_that="I can access my personal data",
                acceptance_criteria=[
                    "Valid credentials grant access",
                    "Invalid credentials show error",
                    "Account locks after 5 failed attempts"
                ],
                story_points=3,
                priority=RequirementPriority.CRITICAL
            ),
            UserStory(
                id="US_AUTH_2",
                as_a="user",
                i_want="to log out securely",
                so_that="my account remains protected",
                acceptance_criteria=[
                    "Session is terminated on logout",
                    "Redirect to login page after logout"
                ],
                story_points=1,
                priority=RequirementPriority.HIGH
            )
        ]
    
    def _generate_admin_stories(self) -> List[UserStory]:
        """관리자 스토리 생성"""
        return [
            UserStory(
                id="US_ADMIN_1",
                as_a="administrator",
                i_want="to manage user accounts",
                so_that="I can maintain system security",
                acceptance_criteria=[
                    "View all user accounts",
                    "Activate/deactivate accounts",
                    "Reset user passwords"
                ],
                story_points=5,
                priority=RequirementPriority.HIGH
            ),
            UserStory(
                id="US_ADMIN_2",
                as_a="administrator",
                i_want="to view system logs",
                so_that="I can monitor system activity",
                acceptance_criteria=[
                    "Logs are searchable",
                    "Logs show timestamp and user",
                    "Export logs to CSV"
                ],
                story_points=3,
                priority=RequirementPriority.MEDIUM
            )
        ]