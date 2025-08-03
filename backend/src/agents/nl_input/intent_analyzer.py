# backend/src/agents/nl_input/intent_analyzer.py
from typing import Dict, List, Any, Optional
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

class IntentAnalyzer:
    """완성된 의도 분석 및 목표 추출"""

    def __init__(self):
        self.intent_patterns = {
            IntentType.BUILD_NEW: [
                r'build|create|develop|make|new',
                r'from scratch|start from|begin with'
            ],
            IntentType.MIGRATE_EXISTING: [
                r'migrate|move|transfer|port',
                r'from .+ to|convert .+ to'
            ],
            IntentType.MODERNIZE: [
                r'modernize|update|upgrade|refactor',
                r'legacy|old|outdated'
            ],
            IntentType.INTEGRATE: [
                r'integrate|connect|link|combine',
                r'with existing|into current'
            ]
        }

    async def analyze_user_intent(self, description: str, context: Optional[Dict[str, Any]] = None) -> UserIntent:
        """사용자 의도 분석 - 완성된 구현"""
        
        # 1. 주요 의도 분류
        primary_intent, confidence = self._classify_primary_intent(description)
        
        # 2. 보조 의도 식별
        secondary_intents = self._identify_secondary_intents(description, primary_intent)
        
        # 3. 비즈니스 목표 추출
        business_goals = await self._extract_business_goals(description)
        
        # 4. 기술적 목표 추출
        technical_goals = await self._extract_technical_goals(description)
        
        # 5. 제약사항 식별
        constraints = self._identify_constraints(description)

        return UserIntent(
            primary=primary_intent,
            secondary=secondary_intents,
            confidence=confidence,
            business_goals=business_goals,
            technical_goals=technical_goals,
            constraints=constraints
        )

    def _classify_primary_intent(self, description: str) -> tuple[IntentType, float]:
        """주요 의도 분류"""
        text_lower = description.lower()
        scores = {}

        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            scores[intent_type] = score

        if not scores or max(scores.values()) == 0:
            return IntentType.BUILD_NEW, 0.5  # 기본값

        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / len(self.intent_patterns[best_intent]), 1.0)
        
        return best_intent, confidence

    def _identify_secondary_intents(self, description: str, primary: IntentType) -> List[IntentType]:
        """보조 의도 식별"""
        secondary = []
        text_lower = description.lower()

        for intent_type, patterns in self.intent_patterns.items():
            if intent_type == primary:
                continue
                
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    secondary.append(intent_type)
                    break

        return secondary

    async def _extract_business_goals(self, description: str) -> List[BusinessGoal]:
        """비즈니스 목표 추출 - 완성된 구현"""
        goals = []

        # 성장 목표 패턴
        growth_patterns = [
            (r'increase\s+(\w+)\s+by\s+(\d+%?)', 'growth'),
            (r'grow\s+(\w+)\s+to\s+(\d+)', 'growth'),
            (r'expand\s+(\w+)', 'expansion')
        ]

        for pattern, goal_type in growth_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                goals.append(BusinessGoal(
                    type=goal_type,
                    description=match.group(0),
                    measurable_outcome=match.group(2) if len(match.groups()) > 1 else None,
                    priority=1
                ))

        # 효율성 목표 패턴
        efficiency_patterns = [
            (r'reduce\s+(\w+)\s+by\s+(\d+%?)', 'efficiency'),
            (r'automate\s+(.+?)(?:\.|,|$)', 'automation'),
            (r'streamline\s+(.+?)(?:\.|,|$)', 'optimization')
        ]

        for pattern, goal_type in efficiency_patterns:
            matches = re.finditer(pattern, description, re.IGNORECASE)
            for match in matches:
                goals.append(BusinessGoal(
                    type=goal_type,
                    description=match.group(0),
                    measurable_outcome=match.group(2) if len(match.groups()) > 1 else None,
                    priority=2
                ))

        return goals

    async def _extract_technical_goals(self, description: str) -> List[TechnicalGoal]:
        """기술적 목표 추출 - 완성된 구현"""
        goals = []

        # 성능 목표
        performance_match = re.search(
            r'(?:handle|support|serve)\s+(\d+)\s*(k|m|million)?\s*(?:users?|requests?|transactions?)',
            description, re.IGNORECASE
        )

        if performance_match:
            count = int(performance_match.group(1))
            multiplier = {'k': 1000, 'm': 1000000, 'million': 1000000}.get(
                performance_match.group(2), 1
            )
            
            goals.append(TechnicalGoal(
                type='performance',
                specification=f'Support {count * multiplier} concurrent users/requests',
                target_state=f'{count * multiplier} RPS',
                acceptance_criteria=[
                    'Response time < 200ms at p95',
                    'Error rate < 0.1%',
                    'Availability > 99.9%'
                ]
            ))

        # 확장성 목표
        if re.search(r'scalab|elastic|auto.?scal', description, re.IGNORECASE):
            goals.append(TechnicalGoal(
                type='scalability',
                specification='Auto-scaling capability',
                target_state='Horizontal scaling with automatic adjustment',
                acceptance_criteria=[
                    'Scale from 1 to N instances based on load',
                    'Scale up time < 2 minutes',
                    'Zero downtime during scaling'
                ]
            ))

        # 보안 목표
        security_keywords = ['secure', 'encrypt', 'auth', 'compliance', 'gdpr', 'hipaa']
        if any(keyword in description.lower() for keyword in security_keywords):
            goals.append(TechnicalGoal(
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

        return goals

    def _identify_constraints(self, description: str) -> List[str]:
        """제약사항 식별"""
        constraints = []

        # 예산 제약
        if re.search(r'budget|cost|cheap|affordable|low.?cost', description, re.IGNORECASE):
            constraints.append('Budget constraints')

        # 시간 제약
        if re.search(r'urgent|asap|quickly|deadline|timeline', description, re.IGNORECASE):
            constraints.append('Time constraints')

        # 기술 제약
        if re.search(r'must use|required to use|only.*allowed', description, re.IGNORECASE):
            constraints.append('Technology constraints')

        # 규정 준수
        if re.search(r'compliant|regulation|standard|policy', description, re.IGNORECASE):
            constraints.append('Compliance requirements')

        return constraints