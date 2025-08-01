from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re

class IntentType(Enum):
    BUILD_NEW = 'build_new'
    MIGRATE_EXISTING = 'migrate_existing'
    MODERNIZE = 'modernize'
    INTEGRATE = 'integrate'
    OPTIMIZE = 'optimize'
    FIX_ISSUES = 'fix_issues'

@dataclass
class BusinessGoal:
    type: str
    description: str
    measurable_outcome: Optional[str] = None
    timeline: Optional[str] = None
    priority: int = 1

@dataclass
class TechnicalGoal:
    type: str
    specification: str
    current_state: Optional[str] = None
    target_state: str = ""
    acceptance_criteria: List[str] = None

@dataclass
class UserIntent:
    primary: IntentType
    secondary: List[IntentType]
    confidence: float
    business_goals: List[BusinessGoal]
    technical_goals: List[TechnicalGoal]
    constraints: List[str]

class IntentClassifier:
    def __init__(self):
        self.intent_patterns = {
            IntentType.BUILD_NEW: [r'create|build|develop|make|new'],
            IntentType.MIGRATE_EXISTING: [r'migrate|move|transfer|port'],
            IntentType.MODERNIZE: [r'modernize|update|upgrade|refactor'],
            IntentType.INTEGRATE: [r'integrate|connect|combine|merge'],
            IntentType.OPTIMIZE: [r'optimize|improve|enhance|speed'],
            IntentType.FIX_ISSUES: [r'fix|repair|debug|solve|issue']
        }
    
    async def classify(self, description: str) -> Dict[str, Any]:
        scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(len(re.findall(pattern, description.lower())) for pattern in patterns)
            scores[intent] = score
        
        primary = max(scores, key=scores.get) if scores else IntentType.BUILD_NEW
        secondary = [intent for intent, score in scores.items() if score > 0 and intent != primary]
        
        return {
            'primary': primary,
            'secondary': secondary[:2],  # Top 2 secondary intents
            'confidence': min(scores[primary] / 10.0, 1.0)
        }

class GoalExtractor:
    async def extract_goals(self, description: str) -> List[BusinessGoal]:
        goals = []
        
        # Performance goals
        perf_match = re.search(r'(\d+)\s*(users?|requests?|transactions?)', description.lower())
        if perf_match:
            goals.append(BusinessGoal(
                type='performance',
                description=f'Support {perf_match.group(1)} {perf_match.group(2)}',
                measurable_outcome=f'{perf_match.group(1)} {perf_match.group(2)}',
                priority=1
            ))
        
        # Cost reduction goals
        if re.search(r'reduce.*cost|save.*money|cheaper', description.lower()):
            goals.append(BusinessGoal(
                type='cost_reduction',
                description='Reduce operational costs',
                priority=2
            ))
        
        return goals

class IntentAnalyzer:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.goal_extractor = GoalExtractor()

    async def analyze_user_intent(self, description: str, context: Optional[Dict] = None) -> UserIntent:
        # 1. 주요 의도 분류
        intents = await self.intent_classifier.classify(description)

        # 2. 비즈니스 목표 추출
        business_goals = await self.extract_business_goals(description)

        # 3. 기술적 목표 추출
        technical_goals = await self.extract_technical_goals(description)

        # 4. 제약사항 식별
        constraints = await self.identify_constraints(description)

        return UserIntent(
            primary=intents['primary'],
            secondary=intents['secondary'],
            confidence=intents['confidence'],
            business_goals=business_goals,
            technical_goals=technical_goals,
            constraints=constraints
        )

    async def extract_business_goals(self, description: str) -> List[BusinessGoal]:
        goals = []

        # Growth goals
        growth_match = re.search(r'increase\s+(\w+)\s+by\s+(\d+%?)', description.lower())
        if growth_match:
            goals.append(BusinessGoal(
                type='growth',
                description=f'Increase {growth_match.group(1)} by {growth_match.group(2)}',
                measurable_outcome=growth_match.group(2),
                priority=1
            ))

        # Efficiency goals
        reduce_match = re.search(r'reduce\s+(\w+)(?:\s+by\s+(\d+%?))?', description.lower())
        if reduce_match:
            goals.append(BusinessGoal(
                type='efficiency',
                description=f'Reduce {reduce_match.group(1)}',
                measurable_outcome=reduce_match.group(2) or 'significant reduction',
                priority=1
            ))

        # Automation goals
        if re.search(r'automate', description.lower()):
            goals.append(BusinessGoal(
                type='automation',
                description='Process automation',
                priority=2
            ))

        return goals

    async def extract_technical_goals(self, description: str) -> List[TechnicalGoal]:
        technical_goals = []

        # Performance goals
        perf_match = re.search(r'(?:handle|support|serve)\s+(\d+)\s*(k|m|million)?\s*(?:users?|requests?|transactions?)', description.lower())
        if perf_match:
            count = int(perf_match.group(1))
            multiplier = {'k': 1000, 'm': 1000000, 'million': 1000000}.get(perf_match.group(2), 1)
            
            technical_goals.append(TechnicalGoal(
                type='performance',
                specification=f'Support {count * multiplier} concurrent users/requests',
                target_state=f'{count * multiplier} RPS',
                acceptance_criteria=[
                    'Response time < 200ms at p95',
                    'Error rate < 0.1%',
                    'Availability > 99.9%'
                ]
            ))

        # Scalability goals
        if re.search(r'scalab|elastic|auto.?scal', description.lower()):
            technical_goals.append(TechnicalGoal(
                type='scalability',
                specification='Auto-scaling capability',
                target_state='Horizontal scaling with automatic adjustment',
                acceptance_criteria=[
                    'Scale from 1 to N instances based on load',
                    'Scale up time < 2 minutes',
                    'Zero downtime during scaling'
                ]
            ))

        # Security goals
        security_keywords = ['secure', 'encrypt', 'auth', 'compliance', 'gdpr', 'hipaa']
        if any(keyword in description.lower() for keyword in security_keywords):
            technical_goals.append(TechnicalGoal(
                type='security',
                specification='Enterprise-grade security',
                target_state='Fully secured application',
                acceptance_criteria=[
                    'End-to-end encryption',
                    'Multi-factor authentication',
                    'Role-based access control',
                    'Security audit compliance'
                ]
            ))

        return technical_goals

    async def identify_constraints(self, description: str) -> List[str]:
        constraints = []
        
        # Budget constraints
        if re.search(r'budget|cost|cheap|free', description.lower()):
            constraints.append('Budget limitations')
        
        # Time constraints
        if re.search(r'urgent|asap|quickly|deadline', description.lower()):
            constraints.append('Time constraints')
        
        # Technology constraints
        if re.search(r'must use|required|existing', description.lower()):
            constraints.append('Technology stack constraints')
        
        return constraints