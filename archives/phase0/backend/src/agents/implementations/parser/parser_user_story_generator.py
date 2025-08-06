# backend/src/agents/implementations/parser_user_story_generator.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from agno.agent import Agent
from agno.models.aws import AwsBedrock

@dataclass
class UserStory:
    id: str
    title: str
    description: str
    actor: str
    goal: str
    benefit: str
    acceptance_criteria: List[str]
    priority: str
    story_points: int
    epic: Optional[str] = None
    tags: List[str] = None

@dataclass
class Epic:
    id: str
    title: str
    description: str
    user_stories: List[str]
    business_value: str
    acceptance_criteria: List[str]

class UserStoryGenerator:
    """사용자 스토리 생성기"""

    def __init__(self):
        self.story_agent = Agent(
            name="User-Story-Generator",
            model=AwsBedrock(
                id="anthropic.claude-3-sonnet-v2:0",
                region="us-east-1"
            ),
            role="Expert user story writer and product analyst",
            instructions=[
                "Generate well-structured user stories from requirements",
                "Follow the 'As a... I want... So that...' format",
                "Create clear acceptance criteria",
                "Estimate story points accurately",
                "Group related stories into epics"
            ],
            temperature=0.3
        )

        self.story_templates = self._load_story_templates()
        self.persona_analyzer = PersonaAnalyzer()

    async def generate_user_stories(
        self,
        requirements: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """요구사항에서 사용자 스토리 생성"""

        # 1. 사용자 페르소나 식별
        personas = await self.persona_analyzer.identify_personas(requirements)

        # 2. 에픽 생성
        epics = await self._generate_epics(requirements, personas)

        # 3. 사용자 스토리 생성
        user_stories = []
        for req in requirements:
            stories = await self._generate_stories_from_requirement(req, personas, epics)
            user_stories.extend(stories)

        # 4. 스토리 검증 및 개선
        validated_stories = await self._validate_and_improve_stories(user_stories)

        # 5. 우선순위 및 스토리 포인트 할당
        prioritized_stories = await self._prioritize_and_estimate(validated_stories)

        return {
            'epics': epics,
            'user_stories': prioritized_stories,
            'personas': personas,
            'story_map': self._create_story_map(epics, prioritized_stories)
        }

    async def _generate_epics(
        self,
        requirements: List[Dict[str, Any]],
        personas: List[Dict[str, Any]]
    ) -> List[Epic]:
        """에픽 생성"""
        epics = []

        # 요구사항을 기능 영역별로 그룹화
        feature_groups = self._group_requirements_by_feature(requirements)

        for group_name, group_reqs in feature_groups.items():
            epic_prompt = f"""
            Create an epic for the following related requirements:
            
            Feature Area: {group_name}
            Requirements: {[req.get('description', '') for req in group_reqs]}
            
            Generate an epic with:
            1. Clear title
            2. Description of the business value
            3. High-level acceptance criteria
            """

            epic_response = await self.story_agent.arun(epic_prompt)
            epic_data = self._parse_epic_response(epic_response.content)

            epic = Epic(
                id=f"EPIC-{len(epics) + 1:03d}",
                title=epic_data.get('title', f"{group_name} Epic"),
                description=epic_data.get('description', ''),
                user_stories=[],  # Will be populated later
                business_value=epic_data.get('business_value', ''),
                acceptance_criteria=epic_data.get('acceptance_criteria', [])
            )
            epics.append(epic)

        return epics

    async def _generate_stories_from_requirement(
        self,
        requirement: Dict[str, Any],
        personas: List[Dict[str, Any]],
        epics: List[Epic]
    ) -> List[UserStory]:
        """단일 요구사항에서 사용자 스토리 생성"""
        stories = []

        # 관련 페르소나 찾기
        relevant_personas = self._find_relevant_personas(requirement, personas)

        for persona in relevant_personas:
            story_prompt = f"""
            Create a user story from this requirement:
            
            Requirement: {requirement.get('description', '')}
            User Persona: {persona.get('name', '')} - {persona.get('description', '')}
            
            Generate a user story following this format:
            - Title: Brief descriptive title
            - As a [persona], I want [goal] so that [benefit]
            - Acceptance Criteria: List of testable criteria
            
            Make it specific, testable, and valuable.
            """

            story_response = await self.story_agent.arun(story_prompt)
            story_data = self._parse_story_response(story_response.content)

            # 관련 에픽 찾기
            related_epic = self._find_related_epic(requirement, epics)

            story = UserStory(
                id=f"US-{len(stories) + 1:03d}",
                title=story_data.get('title', ''),
                description=story_data.get('description', ''),
                actor=persona.get('name', ''),
                goal=story_data.get('goal', ''),
                benefit=story_data.get('benefit', ''),
                acceptance_criteria=story_data.get('acceptance_criteria', []),
                priority=requirement.get('priority', 'medium'),
                story_points=0,  # Will be estimated later
                epic=related_epic.id if related_epic else None,
                tags=self._extract_tags(requirement)
            )
            stories.append(story)

        return stories

    async def _validate_and_improve_stories(
        self,
        stories: List[UserStory]
    ) -> List[UserStory]:
        """스토리 검증 및 개선"""
        improved_stories = []

        for story in stories:
            # INVEST 기준 검증
            validation_result = await self._validate_invest_criteria(story)

            if validation_result['valid']:
                improved_stories.append(story)
            else:
                # 개선 제안 적용
                improved_story = await self._improve_story(story, validation_result['issues'])
                improved_stories.append(improved_story)

        return improved_stories

    async def _validate_invest_criteria(self, story: UserStory) -> Dict[str, Any]:
        """INVEST 기준으로 스토리 검증"""
        issues = []
        
        # Independent
        if not self._is_independent(story):
            issues.append("Story has dependencies that should be resolved")
        
        # Negotiable
        if not self._is_negotiable(story):
            issues.append("Story is too detailed and not negotiable")
        
        # Valuable
        if not story.benefit or len(story.benefit) < 10:
            issues.append("Business value is not clear")
        
        # Estimable
        if not self._is_estimable(story):
            issues.append("Story is too vague to estimate")
        
        # Small
        if self._is_too_large(story):
            issues.append("Story is too large and should be split")
        
        # Testable
        if not story.acceptance_criteria or len(story.acceptance_criteria) == 0:
            issues.append("No testable acceptance criteria")

        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

    async def _prioritize_and_estimate(
        self,
        stories: List[UserStory]
    ) -> List[UserStory]:
        """우선순위 및 스토리 포인트 할당"""
        
        for story in stories:
            # 스토리 포인트 추정
            story.story_points = await self._estimate_story_points(story)
            
            # 우선순위 조정 (비즈니스 가치 기반)
            story.priority = await self._calculate_priority(story)

        # 우선순위 순으로 정렬
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        stories.sort(key=lambda s: (priority_order.get(s.priority, 4), -s.story_points))

        return stories

    async def _estimate_story_points(self, story: UserStory) -> int:
        """스토리 포인트 추정"""
        estimation_prompt = f"""
        Estimate story points (1, 2, 3, 5, 8, 13) for this user story:
        
        Title: {story.title}
        Description: {story.description}
        Acceptance Criteria: {story.acceptance_criteria}
        
        Consider:
        - Complexity of implementation
        - Amount of work required
        - Risk and uncertainty
        - Knowledge needed
        
        Return only the number.
        """

        response = await self.story_agent.arun(estimation_prompt)
        
        try:
            points = int(response.content.strip())
            # 피보나치 수열로 정규화
            fibonacci = [1, 2, 3, 5, 8, 13]
            return min(fibonacci, key=lambda x: abs(x - points))
        except:
            return 3  # 기본값

    def _group_requirements_by_feature(
        self,
        requirements: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """기능 영역별 요구사항 그룹화"""
        groups = {}
        
        # 키워드 기반 그룹화
        feature_keywords = {
            'Authentication': ['login', 'auth', 'user', 'account', 'register'],
            'Payment': ['payment', 'billing', 'checkout', 'transaction'],
            'Search': ['search', 'filter', 'find', 'query'],
            'Notification': ['notification', 'email', 'alert', 'message'],
            'Reporting': ['report', 'analytics', 'dashboard', 'chart'],
            'Admin': ['admin', 'management', 'configure', 'settings']
        }

        for req in requirements:
            description = req.get('description', '').lower()
            assigned = False

            for feature, keywords in feature_keywords.items():
                if any(keyword in description for keyword in keywords):
                    if feature not in groups:
                        groups[feature] = []
                    groups[feature].append(req)
                    assigned = True
                    break

            if not assigned:
                if 'General' not in groups:
                    groups['General'] = []
                groups['General'].append(req)

        return groups

    def _find_relevant_personas(
        self,
        requirement: Dict[str, Any],
        personas: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """요구사항과 관련된 페르소나 찾기"""
        relevant = []
        description = requirement.get('description', '').lower()

        for persona in personas:
            persona_keywords = persona.get('keywords', [])
            if any(keyword.lower() in description for keyword in persona_keywords):
                relevant.append(persona)

        # 관련 페르소나가 없으면 기본 사용자 페르소나 사용
        if not relevant and personas:
            relevant.append(personas[0])

        return relevant

    def _find_related_epic(
        self,
        requirement: Dict[str, Any],
        epics: List[Epic]
    ) -> Optional[Epic]:
        """관련 에픽 찾기"""
        description = requirement.get('description', '').lower()

        for epic in epics:
            epic_keywords = epic.title.lower().split()
            if any(keyword in description for keyword in epic_keywords):
                return epic

        return None

    def _extract_tags(self, requirement: Dict[str, Any]) -> List[str]:
        """요구사항에서 태그 추출"""
        tags = []
        description = requirement.get('description', '').lower()

        # 기술 태그
        tech_tags = {
            'api': ['api', 'endpoint', 'rest'],
            'ui': ['interface', 'screen', 'page', 'form'],
            'database': ['database', 'data', 'store', 'persist'],
            'security': ['secure', 'auth', 'permission', 'encrypt'],
            'performance': ['fast', 'performance', 'optimize', 'speed']
        }

        for tag, keywords in tech_tags.items():
            if any(keyword in description for keyword in keywords):
                tags.append(tag)

        return tags

    def _create_story_map(
        self,
        epics: List[Epic],
        stories: List[UserStory]
    ) -> Dict[str, Any]:
        """스토리 맵 생성"""
        story_map = {}

        for epic in epics:
            epic_stories = [s for s in stories if s.epic == epic.id]
            story_map[epic.title] = {
                'epic': epic,
                'stories': epic_stories,
                'total_points': sum(s.story_points for s in epic_stories)
            }

        return story_map

    def _parse_story_response(self, response: str) -> Dict[str, Any]:
        """스토리 응답 파싱"""
        data = {}
        
        # 제목 추출
        title_match = re.search(r'Title:\s*(.+)', response, re.IGNORECASE)
        if title_match:
            data['title'] = title_match.group(1).strip()

        # As a... I want... So that... 패턴 추출
        story_pattern = r'As a (.+?), I want (.+?) so that (.+?)(?:\.|$)'
        story_match = re.search(story_pattern, response, re.IGNORECASE | re.DOTALL)
        
        if story_match:
            data['actor'] = story_match.group(1).strip()
            data['goal'] = story_match.group(2).strip()
            data['benefit'] = story_match.group(3).strip()
            data['description'] = f"As a {data['actor']}, I want {data['goal']} so that {data['benefit']}"

        # 수용 기준 추출
        criteria_pattern = r'Acceptance Criteria:(.+?)(?:\n\n|\Z)'
        criteria_match = re.search(criteria_pattern, response, re.IGNORECASE | re.DOTALL)
        
        if criteria_match:
            criteria_text = criteria_match.group(1).strip()
            criteria_lines = [line.strip('- ').strip() for line in criteria_text.split('\n') if line.strip()]
            data['acceptance_criteria'] = [c for c in criteria_lines if c]

        return data

    def _parse_epic_response(self, response: str) -> Dict[str, Any]:
        """에픽 응답 파싱"""
        data = {}
        
        # 제목 추출
        title_match = re.search(r'Title:\s*(.+)', response, re.IGNORECASE)
        if title_match:
            data['title'] = title_match.group(1).strip()

        # 설명 추출
        desc_match = re.search(r'Description:\s*(.+?)(?:\n\n|\Z)', response, re.IGNORECASE | re.DOTALL)
        if desc_match:
            data['description'] = desc_match.group(1).strip()

        # 비즈니스 가치 추출
        value_match = re.search(r'Business Value:\s*(.+?)(?:\n\n|\Z)', response, re.IGNORECASE | re.DOTALL)
        if value_match:
            data['business_value'] = value_match.group(1).strip()

        return data

class PersonaAnalyzer:
    """사용자 페르소나 분석기"""

    def __init__(self):
        self.default_personas = [
            {
                'name': 'End User',
                'description': 'Primary application user',
                'keywords': ['user', 'customer', 'client'],
                'goals': ['accomplish tasks', 'get information', 'complete workflows']
            },
            {
                'name': 'Administrator',
                'description': 'System administrator',
                'keywords': ['admin', 'administrator', 'manager'],
                'goals': ['manage system', 'configure settings', 'monitor performance']
            },
            {
                'name': 'Developer',
                'description': 'System developer/integrator',
                'keywords': ['developer', 'api', 'integration'],
                'goals': ['integrate systems', 'access data', 'build applications']
            }
        ]

    async def identify_personas(
        self,
        requirements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """요구사항에서 페르소나 식별"""
        identified_personas = []
        
        # 요구사항에서 언급된 사용자 유형 추출
        user_types = set()
        for req in requirements:
            description = req.get('description', '').lower()
            
            # 사용자 유형 패턴 매칭
            user_patterns = [
                r'(admin|administrator|manager)',
                r'(user|customer|client|visitor)',
                r'(developer|programmer|integrator)',
                r'(analyst|reporter|viewer)',
                r'(guest|anonymous|public)'
            ]
            
            for pattern in user_patterns:
                matches = re.findall(pattern, description)
                user_types.update(matches)

        # 식별된 사용자 유형에 대한 페르소나 생성
        for user_type in user_types:
            persona = self._create_persona_for_user_type(user_type)
            if persona:
                identified_personas.append(persona)

        # 기본 페르소나 추가 (식별된 것이 없는 경우)
        if not identified_personas:
            identified_personas.extend(self.default_personas)

        return identified_personas

    def _create_persona_for_user_type(self, user_type: str) -> Optional[Dict[str, Any]]:
        """사용자 유형에 대한 페르소나 생성"""
        persona_templates = {
            'admin': {
                'name': 'System Administrator',
                'description': 'Manages and configures the system',
                'keywords': ['admin', 'configure', 'manage', 'settings'],
                'goals': ['system management', 'user administration', 'monitoring']
            },
            'user': {
                'name': 'End User',
                'description': 'Primary user of the application',
                'keywords': ['user', 'access', 'use', 'interact'],
                'goals': ['complete tasks', 'access information', 'achieve objectives']
            },
            'developer': {
                'name': 'Developer',
                'description': 'Integrates with the system via APIs',
                'keywords': ['api', 'integrate', 'develop', 'code'],
                'goals': ['system integration', 'data access', 'application development']
            }
        }

        return persona_templates.get(user_type.lower())