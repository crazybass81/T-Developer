"""
Component Decision Agent - Intelligent component selection and architecture decisions
Makes optimal decisions about component selection, architecture patterns, and technical choices
"""

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.memory import ConversationSummaryMemory
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import json
from enum import Enum

class DecisionType(Enum):
    COMPONENT_SELECTION = "component_selection"
    ARCHITECTURE_PATTERN = "architecture_pattern"
    TECHNOLOGY_STACK = "technology_stack"
    INTEGRATION_APPROACH = "integration_approach"

@dataclass
class ComponentOption:
    name: str
    version: str
    pros: List[str]
    cons: List[str]
    compatibility_score: float
    performance_score: float
    security_score: float
    maintenance_score: float
    cost_score: float

@dataclass
class DecisionCriteria:
    performance_weight: float = 0.25
    security_weight: float = 0.20
    compatibility_weight: float = 0.20
    maintenance_weight: float = 0.20
    cost_weight: float = 0.15
    custom_weights: Dict[str, float] = None

@dataclass
class ComponentDecision:
    selected_option: ComponentOption
    confidence_score: float
    reasoning: str
    alternatives: List[ComponentOption]
    risk_assessment: Dict[str, Any]
    implementation_plan: List[str]

class ArchitectureAnalyzer:
    """아키텍처 패턴 분석기"""
    
    def __init__(self):
        self.patterns = {
            'microservices': {
                'pros': ['Scalability', 'Technology diversity', 'Team independence'],
                'cons': ['Complexity', 'Network overhead', 'Data consistency'],
                'best_for': ['Large teams', 'High scalability needs', 'Complex domains']
            },
            'monolith': {
                'pros': ['Simplicity', 'Easy deployment', 'Strong consistency'],
                'cons': ['Limited scalability', 'Technology lock-in', 'Team bottlenecks'],
                'best_for': ['Small teams', 'Simple domains', 'Rapid prototyping']
            },
            'serverless': {
                'pros': ['Auto-scaling', 'Pay-per-use', 'No server management'],
                'cons': ['Cold starts', 'Vendor lock-in', 'Limited runtime'],
                'best_for': ['Event-driven', 'Variable load', 'Cost optimization']
            }
        }
    
    async def analyze_architecture_fit(
        self,
        requirements: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, float]:
        """아키텍처 패턴 적합도 분석"""
        
        scores = {}
        
        for pattern, details in self.patterns.items():
            score = await self._calculate_pattern_score(
                pattern, details, requirements, constraints
            )
            scores[pattern] = score
        
        return scores
    
    async def _calculate_pattern_score(
        self,
        pattern: str,
        details: Dict,
        requirements: Dict,
        constraints: Dict
    ) -> float:
        """패턴별 점수 계산"""
        
        score = 0.5  # 기본 점수
        
        # 팀 크기 고려
        team_size = requirements.get('team_size', 5)
        if pattern == 'microservices' and team_size > 10:
            score += 0.2
        elif pattern == 'monolith' and team_size <= 5:
            score += 0.2
        
        # 확장성 요구사항
        scalability = requirements.get('scalability_needs', 'medium')
        if pattern == 'microservices' and scalability == 'high':
            score += 0.3
        elif pattern == 'serverless' and scalability == 'variable':
            score += 0.3
        
        # 복잡도 고려
        complexity = requirements.get('domain_complexity', 'medium')
        if pattern == 'monolith' and complexity == 'low':
            score += 0.2
        elif pattern == 'microservices' and complexity == 'high':
            score += 0.2
        
        return min(score, 1.0)

class SecurityAnalyzer:
    """보안 분석기"""
    
    def __init__(self):
        self.vulnerability_db = {}
        self.security_patterns = {
            'authentication': ['OAuth2', 'JWT', 'SAML'],
            'authorization': ['RBAC', 'ABAC', 'ACL'],
            'encryption': ['AES-256', 'RSA', 'TLS 1.3'],
            'data_protection': ['GDPR', 'HIPAA', 'PCI-DSS']
        }
    
    async def analyze_security_requirements(
        self,
        component: ComponentOption,
        security_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """보안 요구사항 분석"""
        
        analysis = {
            'vulnerability_score': await self._check_vulnerabilities(component),
            'compliance_score': await self._check_compliance(component, security_requirements),
            'security_features': await self._analyze_security_features(component),
            'recommendations': []
        }
        
        # 보안 권장사항 생성
        if analysis['vulnerability_score'] < 0.7:
            analysis['recommendations'].append(
                "Consider using a more secure alternative or implement additional security measures"
            )
        
        return analysis
    
    async def _check_vulnerabilities(self, component: ComponentOption) -> float:
        """취약점 검사"""
        # 실제 구현에서는 CVE 데이터베이스 조회
        known_secure = ['react', 'vue', 'angular', 'express', 'fastapi']
        
        if component.name.lower() in known_secure:
            return 0.9
        
        return 0.7  # 기본 점수
    
    async def _check_compliance(
        self,
        component: ComponentOption,
        requirements: Dict[str, Any]
    ) -> float:
        """규정 준수 검사"""
        
        compliance_score = 0.8  # 기본 점수
        
        required_standards = requirements.get('compliance_standards', [])
        
        for standard in required_standards:
            if standard in ['GDPR', 'HIPAA', 'PCI-DSS']:
                # 엄격한 규정 준수 필요
                compliance_score = min(compliance_score, 0.9)
        
        return compliance_score
    
    async def _analyze_security_features(self, component: ComponentOption) -> List[str]:
        """보안 기능 분석"""
        
        features = []
        
        # 컴포넌트별 보안 기능 매핑
        security_features_map = {
            'express': ['CORS support', 'Helmet integration', 'Rate limiting'],
            'fastapi': ['Built-in validation', 'OAuth2 support', 'HTTPS enforcement'],
            'react': ['XSS protection', 'CSP support', 'Secure defaults'],
            'vue': ['Template sanitization', 'CSP support', 'Secure routing']
        }
        
        return security_features_map.get(component.name.lower(), [])

class PerformanceAnalyzer:
    """성능 분석기"""
    
    def __init__(self):
        self.benchmark_data = {}
        self.performance_patterns = {
            'caching': ['Redis', 'Memcached', 'CDN'],
            'database': ['Connection pooling', 'Query optimization', 'Indexing'],
            'frontend': ['Code splitting', 'Lazy loading', 'Bundle optimization']
        }
    
    async def analyze_performance_impact(
        self,
        component: ComponentOption,
        performance_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성능 영향 분석"""
        
        analysis = {
            'latency_impact': await self._estimate_latency(component),
            'throughput_impact': await self._estimate_throughput(component),
            'resource_usage': await self._estimate_resources(component),
            'scalability_score': await self._analyze_scalability(component),
            'optimization_suggestions': []
        }
        
        # 성능 최적화 제안
        if analysis['latency_impact'] > 100:  # 100ms 초과
            analysis['optimization_suggestions'].append(
                "Consider implementing caching to reduce latency"
            )
        
        return analysis
    
    async def _estimate_latency(self, component: ComponentOption) -> float:
        """지연 시간 추정 (ms)"""
        
        # 컴포넌트별 평균 지연 시간
        latency_map = {
            'react': 50,
            'vue': 45,
            'angular': 60,
            'express': 30,
            'fastapi': 25,
            'django': 40
        }
        
        return latency_map.get(component.name.lower(), 50)
    
    async def _estimate_throughput(self, component: ComponentOption) -> float:
        """처리량 추정 (requests/sec)"""
        
        throughput_map = {
            'express': 5000,
            'fastapi': 8000,
            'django': 3000,
            'flask': 2000
        }
        
        return throughput_map.get(component.name.lower(), 1000)
    
    async def _estimate_resources(self, component: ComponentOption) -> Dict[str, float]:
        """리소스 사용량 추정"""
        
        return {
            'memory_mb': 100,  # 기본값
            'cpu_percent': 10,
            'disk_mb': 50
        }
    
    async def _analyze_scalability(self, component: ComponentOption) -> float:
        """확장성 분석"""
        
        scalability_map = {
            'react': 0.9,
            'vue': 0.85,
            'angular': 0.8,
            'express': 0.85,
            'fastapi': 0.9
        }
        
        return scalability_map.get(component.name.lower(), 0.7)

class ComponentDecisionAgent:
    """컴포넌트 결정 에이전트"""
    
    def __init__(self):
        self.agent = Agent(
            name="Component-Decision-Maker",
            model=AwsBedrock(
                id="anthropic.claude-3-opus-v1:0",
                region="us-east-1"
            ),
            role="Expert software architect making component and architecture decisions",
            instructions=[
                "Analyze component options and make optimal decisions",
                "Consider performance, security, maintainability, and cost factors",
                "Provide detailed reasoning for all decisions",
                "Identify potential risks and mitigation strategies"
            ],
            memory=ConversationSummaryMemory(
                storage_type="dynamodb",
                table_name="t-dev-component-decisions"
            ),
            temperature=0.3
        )
        
        self.architecture_analyzer = ArchitectureAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        self.performance_analyzer = PerformanceAnalyzer()
    
    async def make_component_decision(
        self,
        options: List[ComponentOption],
        requirements: Dict[str, Any],
        criteria: DecisionCriteria = None
    ) -> ComponentDecision:
        """컴포넌트 선택 결정"""
        
        if criteria is None:
            criteria = DecisionCriteria()
        
        # 1. 각 옵션 분석
        analyzed_options = []
        for option in options:
            analysis = await self._analyze_option(option, requirements)
            analyzed_options.append((option, analysis))
        
        # 2. 점수 계산
        scored_options = []
        for option, analysis in analyzed_options:
            score = await self._calculate_total_score(option, analysis, criteria)
            scored_options.append((option, analysis, score))
        
        # 3. 최적 옵션 선택
        scored_options.sort(key=lambda x: x[2], reverse=True)
        best_option, best_analysis, best_score = scored_options[0]
        
        # 4. AI 기반 추가 분석
        ai_reasoning = await self._get_ai_reasoning(
            best_option, scored_options, requirements
        )
        
        # 5. 위험 평가
        risk_assessment = await self._assess_risks(best_option, best_analysis)
        
        # 6. 구현 계획 생성
        implementation_plan = await self._generate_implementation_plan(
            best_option, requirements
        )
        
        return ComponentDecision(
            selected_option=best_option,
            confidence_score=best_score,
            reasoning=ai_reasoning,
            alternatives=[opt for opt, _, _ in scored_options[1:4]],  # Top 3 alternatives
            risk_assessment=risk_assessment,
            implementation_plan=implementation_plan
        )
    
    async def _analyze_option(
        self,
        option: ComponentOption,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """옵션 종합 분석"""
        
        analysis = {}
        
        # 보안 분석
        if 'security_requirements' in requirements:
            analysis['security'] = await self.security_analyzer.analyze_security_requirements(
                option, requirements['security_requirements']
            )
        
        # 성능 분석
        if 'performance_requirements' in requirements:
            analysis['performance'] = await self.performance_analyzer.analyze_performance_impact(
                option, requirements['performance_requirements']
            )
        
        # 아키텍처 적합성
        if 'architecture_requirements' in requirements:
            analysis['architecture'] = await self.architecture_analyzer.analyze_architecture_fit(
                requirements['architecture_requirements'],
                requirements.get('constraints', {})
            )
        
        return analysis
    
    async def _calculate_total_score(
        self,
        option: ComponentOption,
        analysis: Dict[str, Any],
        criteria: DecisionCriteria
    ) -> float:
        """총 점수 계산"""
        
        total_score = 0.0
        
        # 기본 점수들
        total_score += option.performance_score * criteria.performance_weight
        total_score += option.security_score * criteria.security_weight
        total_score += option.compatibility_score * criteria.compatibility_weight
        total_score += option.maintenance_score * criteria.maintenance_weight
        total_score += option.cost_score * criteria.cost_weight
        
        # 분석 결과 반영
        if 'security' in analysis:
            security_bonus = analysis['security']['vulnerability_score'] * 0.1
            total_score += security_bonus
        
        if 'performance' in analysis:
            perf_bonus = analysis['performance']['scalability_score'] * 0.1
            total_score += perf_bonus
        
        return min(total_score, 1.0)
    
    async def _get_ai_reasoning(
        self,
        selected_option: ComponentOption,
        all_options: List[Tuple],
        requirements: Dict[str, Any]
    ) -> str:
        """AI 기반 결정 이유 생성"""
        
        reasoning_prompt = f"""
        다음 컴포넌트 선택 결정에 대한 상세한 이유를 제공해주세요:
        
        선택된 컴포넌트: {selected_option.name} v{selected_option.version}
        
        요구사항:
        {json.dumps(requirements, indent=2)}
        
        고려된 옵션들:
        {json.dumps([opt[0].name for opt in all_options[:5]], indent=2)}
        
        다음 관점에서 설명해주세요:
        1. 왜 이 컴포넌트가 최적인가?
        2. 주요 장점과 단점
        3. 대안 대비 우위점
        4. 잠재적 위험과 완화 방안
        """
        
        response = await self.agent.arun(reasoning_prompt)
        return response.content
    
    async def _assess_risks(
        self,
        option: ComponentOption,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """위험 평가"""
        
        risks = {
            'technical_risks': [],
            'business_risks': [],
            'mitigation_strategies': []
        }
        
        # 기술적 위험
        if option.compatibility_score < 0.7:
            risks['technical_risks'].append("Low compatibility with existing systems")
            risks['mitigation_strategies'].append("Implement adapter patterns")
        
        if 'security' in analysis and analysis['security']['vulnerability_score'] < 0.8:
            risks['technical_risks'].append("Potential security vulnerabilities")
            risks['mitigation_strategies'].append("Regular security audits and updates")
        
        # 비즈니스 위험
        if option.maintenance_score < 0.6:
            risks['business_risks'].append("High maintenance overhead")
            risks['mitigation_strategies'].append("Allocate dedicated maintenance resources")
        
        return risks
    
    async def _generate_implementation_plan(
        self,
        option: ComponentOption,
        requirements: Dict[str, Any]
    ) -> List[str]:
        """구현 계획 생성"""
        
        plan = [
            f"1. Install {option.name} v{option.version}",
            "2. Configure development environment",
            "3. Set up testing framework",
            "4. Implement core functionality",
            "5. Performance optimization",
            "6. Security hardening",
            "7. Documentation and training"
        ]
        
        # 요구사항별 추가 단계
        if 'security_requirements' in requirements:
            plan.insert(-1, "6.5. Security compliance verification")
        
        if 'performance_requirements' in requirements:
            plan.insert(-1, "5.5. Load testing and optimization")
        
        return plan
    
    async def compare_architectures(
        self,
        architectures: List[str],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """아키텍처 패턴 비교"""
        
        comparison = {}
        
        for arch in architectures:
            scores = await self.architecture_analyzer.analyze_architecture_fit(
                requirements, requirements.get('constraints', {})
            )
            comparison[arch] = scores.get(arch, 0.5)
        
        # 최적 아키텍처 선택
        best_arch = max(comparison.items(), key=lambda x: x[1])
        
        return {
            'recommended_architecture': best_arch[0],
            'confidence': best_arch[1],
            'comparison_scores': comparison,
            'reasoning': await self._get_architecture_reasoning(best_arch[0], comparison)
        }
    
    async def _get_architecture_reasoning(
        self,
        selected_arch: str,
        comparison: Dict[str, float]
    ) -> str:
        """아키텍처 선택 이유"""
        
        reasoning_prompt = f"""
        다음 아키텍처 선택에 대한 이유를 설명해주세요:
        
        선택된 아키텍처: {selected_arch}
        점수 비교: {json.dumps(comparison, indent=2)}
        
        왜 이 아키텍처가 최적인지 설명해주세요.
        """
        
        response = await self.agent.arun(reasoning_prompt)
        return response.content
    
    async def evaluate_integration_approach(
        self,
        components: List[ComponentOption],
        integration_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통합 접근 방식 평가"""
        
        approaches = ['direct_integration', 'api_gateway', 'message_queue', 'event_driven']
        
        evaluation = {}
        
        for approach in approaches:
            score = await self._evaluate_integration_score(
                approach, components, integration_requirements
            )
            evaluation[approach] = score
        
        best_approach = max(evaluation.items(), key=lambda x: x[1])
        
        return {
            'recommended_approach': best_approach[0],
            'confidence': best_approach[1],
            'evaluation_scores': evaluation,
            'integration_plan': await self._generate_integration_plan(
                best_approach[0], components
            )
        }
    
    async def _evaluate_integration_score(
        self,
        approach: str,
        components: List[ComponentOption],
        requirements: Dict[str, Any]
    ) -> float:
        """통합 접근 방식 점수 계산"""
        
        base_scores = {
            'direct_integration': 0.7,
            'api_gateway': 0.8,
            'message_queue': 0.75,
            'event_driven': 0.85
        }
        
        score = base_scores.get(approach, 0.5)
        
        # 요구사항별 조정
        if requirements.get('scalability') == 'high' and approach == 'event_driven':
            score += 0.1
        
        if requirements.get('complexity') == 'low' and approach == 'direct_integration':
            score += 0.1
        
        return min(score, 1.0)
    
    async def _generate_integration_plan(
        self,
        approach: str,
        components: List[ComponentOption]
    ) -> List[str]:
        """통합 계획 생성"""
        
        plans = {
            'direct_integration': [
                "1. Define component interfaces",
                "2. Implement direct API calls",
                "3. Handle error propagation",
                "4. Set up monitoring"
            ],
            'api_gateway': [
                "1. Set up API Gateway",
                "2. Configure routing rules",
                "3. Implement authentication",
                "4. Set up rate limiting",
                "5. Configure monitoring"
            ],
            'event_driven': [
                "1. Set up event bus",
                "2. Define event schemas",
                "3. Implement event handlers",
                "4. Configure dead letter queues",
                "5. Set up event monitoring"
            ]
        }
        
        return plans.get(approach, ["1. Custom integration approach needed"])