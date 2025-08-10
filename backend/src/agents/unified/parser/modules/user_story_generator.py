"""
User Story Generator Module
Generates user stories and acceptance criteria from requirements
"""

from typing import Dict, List, Any, Optional
import re
from enum import Enum


class StorySize(Enum):
    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"


class UserStoryGenerator:
    """Generates user stories from requirements"""
    
    def __init__(self):
        self.story_template = "As a {actor}, I want to {action} so that {benefit}"
        self.acceptance_template = "Given {context}, When {action}, Then {outcome}"
        
        self.story_points = {
            StorySize.XS: 1,
            StorySize.S: 2,
            StorySize.M: 3,
            StorySize.L: 5,
            StorySize.XL: 8
        }
        
        self.personas = {
            'user': 'end user who uses the system',
            'admin': 'system administrator who manages the system',
            'customer': 'customer who purchases products/services',
            'developer': 'developer who maintains the system',
            'manager': 'manager who oversees operations',
            'guest': 'visitor who browses without account'
        }
    
    async def generate(
        self,
        requirements: List[Dict[str, Any]],
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate user stories from requirements"""
        
        # Extract actors from entities
        actors = self._extract_actors(entities)
        
        # Generate stories for each requirement
        stories = []
        for req in requirements:
            story = self._generate_story(req, actors)
            if story:
                stories.append(story)
        
        # Generate epics
        epics = self._group_into_epics(stories)
        
        # Generate acceptance criteria
        for story in stories:
            story['acceptance_criteria'] = self._generate_acceptance_criteria(story)
        
        # Estimate story points
        for story in stories:
            story['story_points'] = self._estimate_story_points(story)
        
        # Generate test scenarios
        for story in stories:
            story['test_scenarios'] = self._generate_test_scenarios(story)
        
        # Create story map
        story_map = self._create_story_map(stories, epics)
        
        return {
            'stories': stories,
            'epics': epics,
            'story_map': story_map,
            'personas': self._generate_personas(actors),
            'statistics': self._calculate_statistics(stories)
        }
    
    def _extract_actors(self, entities: Dict) -> List[str]:
        """Extract actors from entities"""
        actors = []
        
        # Get actors from entity categories
        for entity in entities.get('entities', {}).get('actors', []):
            actors.append(entity.get('text', 'user'))
        
        # Add default actors if none found
        if not actors:
            actors = ['user', 'admin']
        
        return actors
    
    def _generate_story(self, requirement: Dict, actors: List[str]) -> Optional[Dict]:
        """Generate user story from requirement"""
        req_text = requirement.get('text', '')
        req_type = requirement.get('type', '')
        
        # Skip non-functional requirements
        if req_type == 'non_functional':
            return None
        
        # Extract action from requirement
        action = requirement.get('action', self._extract_action(req_text))
        
        # Select appropriate actor
        actor = self._select_actor(req_text, actors)
        
        # Generate benefit
        benefit = self._generate_benefit(req_text, action)
        
        story = {
            'id': f"US-{requirement.get('id', 'XXX')}",
            'title': self._generate_title(action),
            'description': self.story_template.format(
                actor=actor,
                action=action,
                benefit=benefit
            ),
            'requirement_id': requirement.get('id'),
            'priority': requirement.get('priority', 'medium'),
            'category': requirement.get('category', 'general'),
            'original_requirement': req_text
        }
        
        return story
    
    def _extract_action(self, text: str) -> str:
        """Extract action from requirement text"""
        # Look for action verbs
        action_patterns = [
            r'(?:can|should|must|will)\s+(\w+(?:\s+\w+)*)',
            r'(?:to)\s+(\w+(?:\s+\w+)*)',
            r'(\w+)\s+(?:the|a|an)\s+(\w+)'
        ]
        
        for pattern in action_patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip()
        
        return "perform action"
    
    def _select_actor(self, text: str, actors: List[str]) -> str:
        """Select appropriate actor for requirement"""
        text_lower = text.lower()
        
        # Check for actor mentions
        for actor in actors:
            if actor.lower() in text_lower:
                return actor
        
        # Default based on keywords
        if any(word in text_lower for word in ['admin', 'manage', 'configure']):
            return 'admin'
        elif any(word in text_lower for word in ['customer', 'purchase', 'buy']):
            return 'customer'
        
        return 'user'
    
    def _generate_benefit(self, text: str, action: str) -> str:
        """Generate benefit statement"""
        text_lower = text.lower()
        
        # Look for explicit benefits
        benefit_patterns = [
            r'so that\s+(.+)',
            r'in order to\s+(.+)',
            r'to\s+(?:be able to|can)\s+(.+)'
        ]
        
        for pattern in benefit_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1).strip()
        
        # Generate based on action
        if 'create' in action:
            return "I can add new items to the system"
        elif 'view' in action or 'see' in action:
            return "I can access the information I need"
        elif 'update' in action or 'edit' in action:
            return "I can keep information current"
        elif 'delete' in action or 'remove' in action:
            return "I can maintain data cleanliness"
        
        return "I can achieve my goals efficiently"
    
    def _generate_title(self, action: str) -> str:
        """Generate story title"""
        words = action.split()
        return ' '.join(word.capitalize() for word in words[:5])
    
    def _group_into_epics(self, stories: List[Dict]) -> List[Dict]:
        """Group stories into epics"""
        epics = {}
        
        for story in stories:
            category = story.get('category', 'general')
            
            if category not in epics:
                epics[category] = {
                    'id': f"EPIC-{len(epics) + 1}",
                    'name': f"{category.replace('_', ' ').title()} Epic",
                    'stories': []
                }
            
            epics[category]['stories'].append(story['id'])
        
        return list(epics.values())
    
    def _generate_acceptance_criteria(self, story: Dict) -> List[str]:
        """Generate acceptance criteria for story"""
        criteria = []
        action = self._extract_action(story.get('original_requirement', ''))
        
        # Generate Given-When-Then scenarios
        criteria.append(
            self.acceptance_template.format(
                context="the user is logged in",
                action=f"they {action}",
                outcome="the action is completed successfully"
            )
        )
        
        # Add validation criteria
        criteria.append(
            self.acceptance_template.format(
                context="invalid data is provided",
                action=f"they attempt to {action}",
                outcome="an appropriate error message is displayed"
            )
        )
        
        # Add permission criteria
        if 'admin' in story.get('description', '').lower():
            criteria.append(
                self.acceptance_template.format(
                    context="a non-admin user",
                    action=f"attempts to {action}",
                    outcome="access is denied"
                )
            )
        
        return criteria
    
    def _estimate_story_points(self, story: Dict) -> int:
        """Estimate story points based on complexity"""
        text = story.get('original_requirement', '').lower()
        
        # Estimate based on keywords
        complexity_indicators = {
            'simple': StorySize.S,
            'basic': StorySize.S,
            'complex': StorySize.L,
            'advanced': StorySize.L,
            'integration': StorySize.XL,
            'multiple': StorySize.L
        }
        
        for indicator, size in complexity_indicators.items():
            if indicator in text:
                return self.story_points[size]
        
        # Default based on acceptance criteria count
        criteria_count = len(story.get('acceptance_criteria', []))
        if criteria_count <= 2:
            return self.story_points[StorySize.S]
        elif criteria_count <= 4:
            return self.story_points[StorySize.M]
        else:
            return self.story_points[StorySize.L]
    
    def _generate_test_scenarios(self, story: Dict) -> List[Dict]:
        """Generate test scenarios for story"""
        scenarios = []
        
        # Happy path
        scenarios.append({
            'name': 'Happy Path',
            'type': 'positive',
            'steps': [
                'Navigate to feature',
                'Perform action',
                'Verify success'
            ],
            'expected': 'Action completes successfully'
        })
        
        # Error handling
        scenarios.append({
            'name': 'Error Handling',
            'type': 'negative',
            'steps': [
                'Navigate to feature',
                'Provide invalid input',
                'Attempt action'
            ],
            'expected': 'Error message displayed'
        })
        
        return scenarios
    
    def _create_story_map(self, stories: List[Dict], epics: List[Dict]) -> Dict:
        """Create story map structure"""
        return {
            'backbone': [epic['name'] for epic in epics],
            'walking_skeleton': [s['id'] for s in stories if s.get('priority') == 'critical'],
            'releases': self._plan_releases(stories),
            'dependencies': self._identify_story_dependencies(stories)
        }
    
    def _plan_releases(self, stories: List[Dict]) -> List[Dict]:
        """Plan story releases"""
        releases = {
            'mvp': [],
            'v1': [],
            'v2': [],
            'backlog': []
        }
        
        for story in stories:
            priority = story.get('priority', 'medium')
            
            if priority == 'critical':
                releases['mvp'].append(story['id'])
            elif priority == 'high':
                releases['v1'].append(story['id'])
            elif priority == 'medium':
                releases['v2'].append(story['id'])
            else:
                releases['backlog'].append(story['id'])
        
        return [
            {'name': name, 'stories': stories}
            for name, stories in releases.items()
            if stories
        ]
    
    def _identify_story_dependencies(self, stories: List[Dict]) -> List[Dict]:
        """Identify dependencies between stories"""
        dependencies = []
        
        for i, story1 in enumerate(stories):
            for story2 in stories[i+1:]:
                # Check if stories are related
                if story1.get('category') == story2.get('category'):
                    # Simple heuristic: CRUD operations have dependencies
                    action1 = self._extract_action(story1.get('original_requirement', ''))
                    action2 = self._extract_action(story2.get('original_requirement', ''))
                    
                    if 'create' in action1 and any(word in action2 for word in ['update', 'delete', 'view']):
                        dependencies.append({
                            'from': story1['id'],
                            'to': story2['id'],
                            'type': 'blocks'
                        })
        
        return dependencies
    
    def _generate_personas(self, actors: List[str]) -> List[Dict]:
        """Generate user personas"""
        personas = []
        
        for actor in actors:
            persona = {
                'name': actor.capitalize(),
                'description': self.personas.get(actor, f"{actor} of the system"),
                'goals': self._generate_persona_goals(actor),
                'pain_points': self._generate_pain_points(actor)
            }
            personas.append(persona)
        
        return personas
    
    def _generate_persona_goals(self, actor: str) -> List[str]:
        """Generate goals for persona"""
        goals_map = {
            'user': [
                'Complete tasks efficiently',
                'Access information quickly',
                'Have a smooth user experience'
            ],
            'admin': [
                'Manage system effectively',
                'Monitor system health',
                'Control user access'
            ],
            'customer': [
                'Find products easily',
                'Complete purchases quickly',
                'Track orders'
            ]
        }
        
        return goals_map.get(actor, ['Use the system effectively'])
    
    def _generate_pain_points(self, actor: str) -> List[str]:
        """Generate pain points for persona"""
        pain_points_map = {
            'user': [
                'Complex navigation',
                'Slow response times',
                'Unclear error messages'
            ],
            'admin': [
                'Lack of monitoring tools',
                'Complex configuration',
                'Limited automation'
            ],
            'customer': [
                'Difficult checkout process',
                'Limited payment options',
                'Poor search functionality'
            ]
        }
        
        return pain_points_map.get(actor, ['System complexity'])
    
    def _calculate_statistics(self, stories: List[Dict]) -> Dict[str, Any]:
        """Calculate user story statistics"""
        total_points = sum(story.get('story_points', 0) for story in stories)
        
        priority_counts = {}
        for story in stories:
            priority = story.get('priority', 'medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            'total_stories': len(stories),
            'total_story_points': total_points,
            'average_story_points': total_points / len(stories) if stories else 0,
            'by_priority': priority_counts,
            'total_acceptance_criteria': sum(len(s.get('acceptance_criteria', [])) for s in stories)
        }