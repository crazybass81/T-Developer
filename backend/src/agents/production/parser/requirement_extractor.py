"""
Requirement Extractor Component
Task 4.21: 요구사항 추출 및 분류
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import boto3
from aws_lambda_powertools import Logger

from .core import ParsedRequirement, RequirementType, RequirementPriority

logger = Logger()
comprehend = boto3.client('comprehend')


class RequirementExtractor:
    """요구사항 추출 및 분류 컴포넌트"""
    
    def __init__(self):
        self._init_patterns()
        self._init_keywords()
    
    def _init_patterns(self):
        """패턴 초기화"""
        self.patterns = {
            'functional': {
                'user_action': r'(?:user|customer|admin) (?:can|should|must|will) (\w+)',
                'system_behavior': r'(?:system|app|application) (?:shall|must|should) (\w+)',
                'feature': r'(?:feature|functionality|capability) (?:to|for) (\w+)',
            },
            'non_functional': {
                'performance': r'(?:response time|latency|throughput) (?:must|should) (?:be|less than|greater than)',
                'security': r'(?:secure|encrypt|authenticate|authorize|protect)',
                'scalability': r'(?:scale|handle|support) (?:\d+|multiple|concurrent) (?:users|requests)',
                'availability': r'(?:uptime|availability|reliability) (?:of|must be|should be) (?:\d+%?)',
            },
            'technical': {
                'technology': r'(?:use|implement|integrate) (?:with)? (\w+) (?:framework|library|service|api)',
                'architecture': r'(?:microservice|monolithic|serverless|cloud-native) (?:architecture|design)',
                'database': r'(?:database|data store|cache) (?:using|with) (\w+)',
            },
            'business': {
                'goal': r'(?:business|revenue|market) (?:goal|objective|target)',
                'compliance': r'(?:comply|compliance|regulation|standard) (?:with|to) (\w+)',
                'roi': r'(?:roi|return on investment|cost|budget) (?:of|must be|should be)',
            }
        }
    
    def _init_keywords(self):
        """키워드 초기화"""
        self.priority_keywords = {
            RequirementPriority.CRITICAL: ['critical', 'must', 'mandatory', 'essential', 'required'],
            RequirementPriority.HIGH: ['should', 'important', 'significant', 'key'],
            RequirementPriority.MEDIUM: ['could', 'would', 'normal', 'standard'],
            RequirementPriority.LOW: ['nice to have', 'optional', 'future', 'enhancement'],
            RequirementPriority.NICE_TO_HAVE: ['wish', 'maybe', 'consider', 'possibly']
        }
        
        self.acceptance_keywords = [
            'given', 'when', 'then',
            'verify', 'validate', 'ensure',
            'test', 'check', 'confirm'
        ]
    
    async def extract_requirements(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ParsedRequirement]:
        """요구사항 추출"""
        requirements = []
        
        # 문장 분리
        sentences = self._split_into_sentences(text)
        
        # 각 문장 분석
        for idx, sentence in enumerate(sentences):
            req_type = self._identify_requirement_type(sentence)
            if req_type:
                requirement = await self._create_requirement(
                    sentence, req_type, idx, context
                )
                requirements.append(requirement)
        
        # 중복 제거 및 병합
        requirements = self._merge_duplicates(requirements)
        
        # 우선순위 재조정
        requirements = self._adjust_priorities(requirements)
        
        return requirements
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """문장 분리"""
        # 개선된 문장 분리 (약어, 숫자 등 고려)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _identify_requirement_type(self, sentence: str) -> Optional[RequirementType]:
        """요구사항 타입 식별"""
        sentence_lower = sentence.lower()
        
        # 패턴 매칭으로 타입 결정
        scores = {}
        
        for req_type, patterns in self.patterns.items():
            score = 0
            for pattern_name, pattern in patterns.items():
                if re.search(pattern, sentence_lower):
                    score += 1
            scores[req_type] = score
        
        # 가장 높은 점수의 타입 반환
        if max(scores.values()) > 0:
            req_type = max(scores, key=scores.get)
            return RequirementType(req_type)
        
        # 기본값: functional
        if any(word in sentence_lower for word in ['user', 'feature', 'function']):
            return RequirementType.FUNCTIONAL
        
        return None
    
    async def _create_requirement(
        self,
        sentence: str,
        req_type: RequirementType,
        index: int,
        context: Optional[Dict[str, Any]]
    ) -> ParsedRequirement:
        """요구사항 객체 생성"""
        # 제목 생성
        title = self._generate_title(sentence)
        
        # 우선순위 결정
        priority = self._determine_priority(sentence)
        
        # 수용 기준 추출
        acceptance_criteria = self._extract_acceptance_criteria(sentence)
        
        # 의존성 추출
        dependencies = self._extract_dependencies(sentence, context)
        
        # 제약사항 추출
        constraints = self._extract_constraints(sentence)
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(sentence, req_type)
        
        return ParsedRequirement(
            id=f"{req_type.value}_{index+1}",
            type=req_type,
            title=title,
            description=sentence,
            priority=priority,
            acceptance_criteria=acceptance_criteria,
            dependencies=dependencies,
            constraints=constraints,
            metadata={
                'source': 'requirement_extractor',
                'context': context or {},
                'keywords': self._extract_keywords(sentence)
            },
            confidence_score=confidence
        )
    
    def _generate_title(self, text: str) -> str:
        """제목 생성"""
        # 첫 50자 또는 첫 구문
        if len(text) <= 50:
            return text
        
        # 동사 찾기
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in ['shall', 'must', 'should', 'can', 'will']:
                # 동사 이후 3-5 단어로 제목 생성
                title_words = words[i:i+5]
                return ' '.join(title_words)
        
        # 기본: 첫 5단어
        return ' '.join(words[:5]) + '...'
    
    def _determine_priority(self, text: str) -> RequirementPriority:
        """우선순위 결정"""
        text_lower = text.lower()
        
        for priority, keywords in self.priority_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return priority
        
        return RequirementPriority.MEDIUM
    
    def _extract_acceptance_criteria(self, text: str) -> List[str]:
        """수용 기준 추출"""
        criteria = []
        text_lower = text.lower()
        
        # Given-When-Then 패턴
        gwt_pattern = r'given (.+?) when (.+?) then (.+?)(?:\.|$)'
        matches = re.finditer(gwt_pattern, text_lower, re.IGNORECASE)
        for match in matches:
            criteria.append(f"Given {match.group(1)}, When {match.group(2)}, Then {match.group(3)}")
        
        # 검증 키워드 기반
        for keyword in self.acceptance_keywords:
            if keyword in text_lower:
                # 키워드 이후 텍스트 추출
                idx = text_lower.index(keyword)
                criterion = text[idx:].split('.')[0]
                if len(criterion) > 10:  # 의미있는 길이
                    criteria.append(criterion)
        
        return criteria[:5]  # 최대 5개
    
    def _extract_dependencies(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """의존성 추출"""
        dependencies = []
        
        # 참조 패턴
        ref_pattern = r'(?:depends on|requires|after|following) (.+?)(?:\.|,|$)'
        matches = re.finditer(ref_pattern, text, re.IGNORECASE)
        for match in matches:
            dependencies.append(match.group(1).strip())
        
        # 컨텍스트에서 의존성 확인
        if context and 'related_requirements' in context:
            for req_id in context['related_requirements']:
                if req_id in text:
                    dependencies.append(req_id)
        
        return dependencies
    
    def _extract_constraints(self, text: str) -> List[str]:
        """제약사항 추출"""
        constraints = []
        
        # 제약 패턴
        constraint_patterns = [
            r'(?:must not|cannot|should not|limit|maximum|minimum) (.+?)(?:\.|,|$)',
            r'(?:within|less than|greater than|between) (.+?)(?:\.|,|$)',
            r'(?:constraint|restriction|limitation): (.+?)(?:\.|,|$)'
        ]
        
        for pattern in constraint_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                constraints.append(match.group(1).strip())
        
        return constraints
    
    def _calculate_confidence(self, text: str, req_type: RequirementType) -> float:
        """신뢰도 계산"""
        confidence = 0.5  # 기본값
        
        # 명확한 키워드가 있으면 신뢰도 증가
        clarity_keywords = ['must', 'shall', 'will', 'should']
        if any(keyword in text.lower() for keyword in clarity_keywords):
            confidence += 0.2
        
        # 패턴 매칭 성공시 신뢰도 증가
        for patterns in self.patterns[req_type.value].values():
            if re.search(patterns, text.lower()):
                confidence += 0.1
        
        # 길이가 적절하면 신뢰도 증가
        if 20 <= len(text.split()) <= 50:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        keywords = []
        
        # 중요 단어 패턴
        important_words = re.findall(r'\b[A-Z][a-z]+\b', text)  # 대문자로 시작하는 단어
        keywords.extend(important_words)
        
        # 기술 용어
        tech_terms = re.findall(r'\b(?:API|UI|UX|DB|SQL|REST|HTTP|JSON|XML)\b', text, re.IGNORECASE)
        keywords.extend(tech_terms)
        
        return list(set(keywords))[:10]  # 중복 제거, 최대 10개
    
    def _merge_duplicates(self, requirements: List[ParsedRequirement]) -> List[ParsedRequirement]:
        """중복 요구사항 병합"""
        merged = {}
        
        for req in requirements:
            # 유사도 기반 키 생성
            key = self._generate_similarity_key(req.description)
            
            if key in merged:
                # 병합: 더 높은 우선순위 유지
                existing = merged[key]
                if req.priority.value < existing.priority.value:  # enum 값이 낮을수록 높은 우선순위
                    existing.priority = req.priority
                
                # 수용 기준 병합
                existing.acceptance_criteria.extend(req.acceptance_criteria)
                existing.acceptance_criteria = list(set(existing.acceptance_criteria))
                
                # 의존성 병합
                existing.dependencies.extend(req.dependencies)
                existing.dependencies = list(set(existing.dependencies))
            else:
                merged[key] = req
        
        return list(merged.values())
    
    def _generate_similarity_key(self, text: str) -> str:
        """유사도 키 생성"""
        # 주요 단어 추출
        words = re.findall(r'\b\w+\b', text.lower())
        # 불용어 제거
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if w not in stopwords and len(w) > 2]
        # 정렬하여 키 생성
        return '_'.join(sorted(keywords[:5]))
    
    def _adjust_priorities(self, requirements: List[ParsedRequirement]) -> List[ParsedRequirement]:
        """우선순위 재조정"""
        # 의존성 기반 우선순위 조정
        req_dict = {req.id: req for req in requirements}
        
        for req in requirements:
            for dep_id in req.dependencies:
                if dep_id in req_dict:
                    dep_req = req_dict[dep_id]
                    # 의존성이 있는 요구사항의 우선순위가 더 낮으면 조정
                    if dep_req.priority.value > req.priority.value:
                        dep_req.priority = req.priority
        
        return requirements