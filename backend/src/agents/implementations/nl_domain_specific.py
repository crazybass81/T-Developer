from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class DomainRequirements:
    domain: str
    general_requirements: List[str]
    domain_specific_requirements: List[str]
    entities: Dict[str, Any]
    compliance_requirements: List[str]
    recommended_architecture: Dict[str, Any]
    security_requirements: List[str]

class DomainClassifier:
    def __init__(self, model_name: str):
        self.model_name = model_name
        
    async def classify_requirements(self, description: str, entities: Dict) -> Dict[str, List[str]]:
        return {
            'general': ['user management', 'data storage'],
            'specific': [f'{self.model_name} specific requirement']
        }
        
    async def get_confidence(self, description: str) -> float:
        return 0.8

class DomainSpecificExtractor:
    def __init__(self, domain: str):
        self.domain = domain
        
    async def extract_entities(self, description: str) -> Dict[str, Any]:
        domain_entities = {
            'fintech': ['payment', 'transaction', 'compliance'],
            'healthcare': ['patient', 'medical_record', 'hipaa'],
            'ecommerce': ['product', 'cart', 'payment']
        }
        
        entities = []
        desc_lower = description.lower()
        for entity in domain_entities.get(self.domain, []):
            if entity in desc_lower:
                entities.append(entity)
                
        return {'domain_entities': entities}

class DomainSpecificNLProcessor:
    """도메인별 특화 언어 처리"""

    DOMAIN_MODELS = {
        'fintech': 'finbert-base',
        'healthcare': 'biobert-base',
        'legal': 'legal-bert-base',
        'ecommerce': 'ecommerce-bert-base'
    }

    def __init__(self):
        self.domain_classifiers = {}
        self.domain_extractors = {}
        self._load_domain_models()

    def _load_domain_models(self):
        """도메인별 모델 로드"""
        for domain, model_name in self.DOMAIN_MODELS.items():
            self.domain_classifiers[domain] = DomainClassifier(model_name)
            self.domain_extractors[domain] = DomainSpecificExtractor(domain)

    async def process_domain_specific_requirements(
        self,
        description: str,
        detected_domain: Optional[str] = None
    ) -> DomainRequirements:
        """도메인 특화 요구사항 처리"""

        # 1. 도메인 자동 감지
        if not detected_domain:
            detected_domain = await self._detect_domain(description)

        if detected_domain not in self.domain_classifiers:
            return await self._process_general_domain(description)

        # 2. 도메인 특화 처리
        domain_classifier = self.domain_classifiers[detected_domain]
        domain_extractor = self.domain_extractors[detected_domain]

        # 3. 도메인별 엔티티 추출
        entities = await domain_extractor.extract_entities(description)

        # 4. 도메인별 요구사항 분류
        requirements = await domain_classifier.classify_requirements(description, entities)

        # 5. 도메인별 제약사항 및 규정 확인
        compliance_requirements = await self._check_domain_compliance(detected_domain, requirements)

        return DomainRequirements(
            domain=detected_domain,
            general_requirements=requirements['general'],
            domain_specific_requirements=requirements['specific'],
            entities=entities,
            compliance_requirements=compliance_requirements,
            recommended_architecture=self._get_domain_architecture(detected_domain),
            security_requirements=self._get_domain_security(detected_domain)
        )

    async def _detect_domain(self, description: str) -> str:
        """텍스트에서 도메인 자동 감지"""
        domain_keywords = {
            'fintech': ['payment', 'banking', 'transaction', 'finance', '금융', '결제'],
            'healthcare': ['patient', 'medical', 'health', 'diagnosis', '의료', '환자'],
            'ecommerce': ['shop', 'product', 'cart', 'order', '쇼핑', '상품'],
            'legal': ['contract', 'legal', 'law', 'compliance', '법률', '계약']
        }

        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in description.lower())
            scores[domain] = score

        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return 'general'

    async def _process_general_domain(self, description: str) -> DomainRequirements:
        """일반 도메인 처리"""
        return DomainRequirements(
            domain='general',
            general_requirements=['basic functionality'],
            domain_specific_requirements=[],
            entities={},
            compliance_requirements=[],
            recommended_architecture={'pattern': 'modular-monolith'},
            security_requirements=['basic authentication']
        )

    async def _check_domain_compliance(self, domain: str, requirements: Dict) -> List[str]:
        """도메인별 규정 준수 요구사항"""
        compliance_map = {
            'fintech': ['PCI DSS', 'SOX', 'Anti-money laundering'],
            'healthcare': ['HIPAA', 'FDA regulations'],
            'legal': ['Data protection', 'Client confidentiality']
        }
        return compliance_map.get(domain, [])

    def _get_domain_architecture(self, domain: str) -> Dict[str, Any]:
        """도메인별 추천 아키텍처"""
        architectures = {
            'fintech': {
                'pattern': 'microservices',
                'key_components': ['payment-gateway', 'fraud-detection', 'audit-log'],
                'data_storage': 'event-sourcing',
                'messaging': 'kafka',
                'security': 'zero-trust'
            },
            'healthcare': {
                'pattern': 'layered',
                'key_components': ['hl7-adapter', 'fhir-server', 'imaging-storage'],
                'data_storage': 'hybrid',
                'messaging': 'hl7-mllp',
                'security': 'hipaa-compliant'
            },
            'ecommerce': {
                'pattern': 'microservices',
                'key_components': ['product-catalog', 'inventory', 'checkout', 'recommendation'],
                'data_storage': 'polyglot',
                'messaging': 'event-driven',
                'security': 'pci-dss'
            }
        }
        return architectures.get(domain, {'pattern': 'modular-monolith'})

    def _get_domain_security(self, domain: str) -> List[str]:
        """도메인별 보안 요구사항"""
        security_map = {
            'fintech': ['Multi-factor authentication', 'Encryption at rest', 'Fraud detection'],
            'healthcare': ['Patient data encryption', 'Access logging', 'Audit trails'],
            'ecommerce': ['Payment security', 'User data protection', 'SSL/TLS']
        }
        return security_map.get(domain, ['Basic authentication', 'HTTPS'])