from typing import Dict, List, Any
import re

class UserStoryGenerator:
    """사용자 스토리 생성기"""

    def __init__(self):
        self.story_templates = self._load_story_templates()
        self.persona_patterns = self._load_persona_patterns()

    def _load_story_templates(self) -> Dict[str, str]:
        """스토리 템플릿 로드"""
        return {
            'basic': "As a {persona}, I want to {action} so that {benefit}",
            'detailed': "As a {persona}, I want to {action} {object} so that I can {benefit} and {additional_value}",
            'acceptance': "Given {precondition}, when I {action}, then {expected_result}"
        }

    def _load_persona_patterns(self) -> Dict[str, List[str]]:
        """페르소나 패턴 로드"""
        return {
            'user': ['user', 'customer', 'visitor', 'person'],
            'admin': ['admin', 'administrator', 'manager', 'moderator'],
            'developer': ['developer', 'programmer', 'engineer'],
            'system': ['system', 'application', 'service']
        }

    async def generate(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """사용자 스토리 생성"""
        user_stories = []
        features = base_structure.get('key_features', [])
        target_users = base_structure.get('target_users', ['user'])

        for feature in features:
            stories = await self._generate_stories_for_feature(feature, target_users)
            user_stories.extend(stories)

        return user_stories

    async def _generate_stories_for_feature(
        self, 
        feature: str, 
        target_users: List[str]
    ) -> List[Dict[str, Any]]:
        """기능별 사용자 스토리 생성"""
        stories = []

        for user_type in target_users:
            persona = self._determine_persona(user_type)
            action = self._extract_action(feature)
            benefit = self._determine_benefit(feature, persona)

            story = {
                'id': f"US-{len(stories)+1:03d}",
                'title': f"{persona.title()} {action}",
                'description': self.story_templates['basic'].format(
                    persona=persona,
                    action=action,
                    benefit=benefit
                ),
                'persona': persona,
                'feature': feature,
                'priority': self._determine_story_priority(feature),
                'acceptance_criteria': self._generate_acceptance_criteria(action, persona),
                'story_points': self._estimate_story_points(feature),
                'tags': self._generate_tags(feature)
            }
            stories.append(story)

        return stories

    def _determine_persona(self, user_type: str) -> str:
        """페르소나 결정"""
        user_lower = user_type.lower()
        
        for persona, patterns in self.persona_patterns.items():
            if any(pattern in user_lower for pattern in patterns):
                return persona
        
        return 'user'

    def _extract_action(self, feature: str) -> str:
        """액션 추출"""
        # 동사 패턴 찾기
        action_patterns = [
            r'(create|add|make|build)\s+(.+)',
            r'(view|see|display|show)\s+(.+)',
            r'(edit|update|modify|change)\s+(.+)',
            r'(delete|remove|cancel)\s+(.+)',
            r'(login|register|authenticate)\s*(.+)?',
            r'(search|find|filter)\s+(.+)',
            r'(upload|download|import|export)\s+(.+)'
        ]

        feature_lower = feature.lower()
        
        for pattern in action_patterns:
            match = re.search(pattern, feature_lower)
            if match:
                action = match.group(1)
                object_part = match.group(2) if len(match.groups()) > 1 else ""
                return f"{action} {object_part}".strip()

        # 패턴이 없으면 기본 액션
        return f"use {feature}"

    def _determine_benefit(self, feature: str, persona: str) -> str:
        """혜택 결정"""
        benefit_map = {
            'login': 'I can access my personal account',
            'register': 'I can create a new account',
            'create': 'I can add new information to the system',
            'view': 'I can see the information I need',
            'edit': 'I can update information when needed',
            'delete': 'I can remove unwanted information',
            'search': 'I can quickly find what I\'m looking for',
            'upload': 'I can share my files with the system',
            'download': 'I can get files from the system'
        }

        feature_lower = feature.lower()
        
        for action, benefit in benefit_map.items():
            if action in feature_lower:
                return benefit

        # 기본 혜택
        if persona == 'admin':
            return 'I can manage the system effectively'
        else:
            return 'I can accomplish my goals efficiently'

    def _determine_story_priority(self, feature: str) -> str:
        """스토리 우선순위 결정"""
        high_priority_features = ['login', 'register', 'authentication', 'security']
        medium_priority_features = ['create', 'view', 'edit', 'search']
        
        feature_lower = feature.lower()
        
        if any(keyword in feature_lower for keyword in high_priority_features):
            return 'high'
        elif any(keyword in feature_lower for keyword in medium_priority_features):
            return 'medium'
        else:
            return 'low'

    def _generate_acceptance_criteria(self, action: str, persona: str) -> List[str]:
        """수용 기준 생성"""
        criteria_templates = {
            'login': [
                "Given I am on the login page",
                "When I enter valid credentials",
                "Then I should be logged in successfully",
                "And I should be redirected to the dashboard"
            ],
            'create': [
                "Given I have the necessary permissions",
                "When I fill out the creation form",
                "Then a new item should be created",
                "And I should see a success confirmation"
            ],
            'view': [
                "Given I am logged in",
                "When I navigate to the view page",
                "Then I should see the requested information",
                "And the information should be accurate and up-to-date"
            ]
        }

        action_key = action.split()[0].lower() if action else 'default'
        
        if action_key in criteria_templates:
            return criteria_templates[action_key]
        else:
            return [
                f"Given I am a {persona}",
                f"When I {action}",
                "Then the system should respond appropriately",
                "And I should receive feedback about the action"
            ]

    def _estimate_story_points(self, feature: str) -> int:
        """스토리 포인트 추정"""
        complexity_indicators = {
            'simple': ['view', 'display', 'show', 'list'],
            'medium': ['create', 'edit', 'update', 'search'],
            'complex': ['integrate', 'calculate', 'process', 'analyze'],
            'very_complex': ['optimize', 'machine learning', 'ai', 'algorithm']
        }

        feature_lower = feature.lower()
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in feature_lower for indicator in indicators):
                if complexity == 'simple':
                    return 1
                elif complexity == 'medium':
                    return 3
                elif complexity == 'complex':
                    return 5
                else:  # very_complex
                    return 8

        return 2  # 기본값

    def _generate_tags(self, feature: str) -> List[str]:
        """태그 생성"""
        tags = []
        feature_lower = feature.lower()

        tag_patterns = {
            'ui': ['interface', 'display', 'view', 'form'],
            'backend': ['process', 'calculate', 'store', 'database'],
            'security': ['login', 'auth', 'secure', 'permission'],
            'integration': ['api', 'external', 'connect', 'integrate'],
            'reporting': ['report', 'export', 'analytics', 'dashboard']
        }

        for tag, patterns in tag_patterns.items():
            if any(pattern in feature_lower for pattern in patterns):
                tags.append(tag)

        return tags if tags else ['general']