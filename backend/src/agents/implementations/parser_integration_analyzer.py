# backend/src/agents/implementations/parser_integration_analyzer.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class IntegrationPoint:
    name: str
    type: str  # 'api', 'database', 'service', 'webhook', 'file'
    direction: str  # 'inbound', 'outbound', 'bidirectional'
    protocol: str
    endpoint: Optional[str]
    authentication: Optional[str]
    data_format: str
    description: str

@dataclass
class ExternalService:
    name: str
    provider: str
    service_type: str
    integration_points: List[IntegrationPoint]
    configuration: Dict[str, Any]
    dependencies: List[str]

@dataclass
class IntegrationArchitecture:
    external_services: List[ExternalService]
    integration_points: List[IntegrationPoint]
    data_flows: List[Dict[str, Any]]
    security_requirements: List[str]
    monitoring_requirements: List[str]

class IntegrationAnalyzer:
    """통합 포인트 분석기"""

    def __init__(self):
        self.service_patterns = {
            'payment': [
                r'\b(stripe|paypal|square|braintree|adyen)\b',
                r'\b(payment|billing|checkout|transaction)\s+(gateway|processor|service)\b',
                r'\b(credit card|debit card|payment method)\b'
            ],
            'authentication': [
                r'\b(auth0|okta|firebase auth|cognito)\b',
                r'\b(oauth|saml|ldap|active directory)\b',
                r'\b(single sign.?on|sso|identity provider)\b'
            ],
            'email': [
                r'\b(sendgrid|mailgun|ses|mailchimp|postmark)\b',
                r'\b(email|mail|smtp|notification)\s+(service|provider)\b',
                r'\b(transactional email|email marketing)\b'
            ],
            'storage': [
                r'\b(aws s3|google cloud storage|azure blob)\b',
                r'\b(file storage|object storage|cdn)\b',
                r'\b(upload|download|file management)\b'
            ],
            'database': [
                r'\b(mongodb|postgresql|mysql|redis|elasticsearch)\b',
                r'\b(database|db|data store|cache)\b',
                r'\b(rds|dynamodb|cosmos db)\b'
            ],
            'messaging': [
                r'\b(kafka|rabbitmq|sqs|pubsub|eventbridge)\b',
                r'\b(message queue|event bus|pub.?sub)\b',
                r'\b(webhook|callback|notification)\b'
            ],
            'analytics': [
                r'\b(google analytics|mixpanel|amplitude|segment)\b',
                r'\b(tracking|analytics|metrics|monitoring)\b',
                r'\b(event tracking|user behavior)\b'
            ],
            'social': [
                r'\b(facebook|twitter|google|linkedin|github)\s+(api|login|integration)\b',
                r'\b(social login|social sharing|social media)\b',
                r'\b(oauth.*?(facebook|twitter|google|linkedin))\b'
            ]
        }
        
        self.protocol_patterns = {
            'rest': r'\b(rest|restful|http|https|api)\b',
            'graphql': r'\b(graphql|gql)\b',
            'websocket': r'\b(websocket|ws|real.?time|live)\b',
            'grpc': r'\b(grpc|protobuf)\b',
            'soap': r'\b(soap|wsdl|xml.?rpc)\b',
            'webhook': r'\b(webhook|callback|notification)\b'
        }

    async def analyze_integrations(
        self,
        requirements: List[Dict[str, Any]]
    ) -> IntegrationArchitecture:
        """통합 포인트 분석"""
        
        external_services = []
        integration_points = []
        data_flows = []
        
        for req in requirements:
            description = req.get('description', '')
            
            # 외부 서비스 식별
            services = self._identify_external_services(description)
            external_services.extend(services)
            
            # 통합 포인트 추출
            points = self._extract_integration_points(description)
            integration_points.extend(points)
            
            # 데이터 플로우 분석
            flows = self._analyze_data_flows(description)
            data_flows.extend(flows)
            
        # 중복 제거
        unique_services = self._deduplicate_services(external_services)
        unique_points = self._deduplicate_integration_points(integration_points)
        
        # 보안 요구사항 추출
        security_requirements = self._extract_security_requirements(requirements)
        
        # 모니터링 요구사항 추출
        monitoring_requirements = self._extract_monitoring_requirements(requirements)
        
        return IntegrationArchitecture(
            external_services=unique_services,
            integration_points=unique_points,
            data_flows=data_flows,
            security_requirements=security_requirements,
            monitoring_requirements=monitoring_requirements
        )

    def _identify_external_services(self, text: str) -> List[ExternalService]:
        """외부 서비스 식별"""
        services = []
        
        for service_type, patterns in self.service_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    service_name = match.group(1) if match.groups() else match.group(0)
                    
                    # 서비스 제공자 추론
                    provider = self._infer_provider(service_name, service_type)
                    
                    # 통합 포인트 생성
                    integration_points = self._create_service_integration_points(
                        service_name,
                        service_type,
                        text
                    )
                    
                    # 설정 추출
                    configuration = self._extract_service_configuration(
                        service_name,
                        service_type,
                        text
                    )
                    
                    # 의존성 분석
                    dependencies = self._analyze_service_dependencies(
                        service_name,
                        service_type,
                        text
                    )
                    
                    service = ExternalService(
                        name=service_name,
                        provider=provider,
                        service_type=service_type,
                        integration_points=integration_points,
                        configuration=configuration,
                        dependencies=dependencies
                    )
                    services.append(service)
                    
        return services

    def _extract_integration_points(self, text: str) -> List[IntegrationPoint]:
        """통합 포인트 추출"""
        points = []
        
        # API 엔드포인트 패턴
        api_patterns = [
            r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/\-{}]+)',
            r'(api|endpoint|service)\s*:\s*([^\s]+)',
            r'(webhook|callback)\s*:\s*([^\s]+)'
        ]
        
        for pattern in api_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 2:
                    method_or_type = groups[0].upper()
                    endpoint = groups[1]
                    
                    # 프로토콜 감지
                    protocol = self._detect_protocol(text, endpoint)
                    
                    # 방향 결정
                    direction = self._determine_direction(text, method_or_type)
                    
                    # 인증 방식 감지
                    authentication = self._detect_authentication(text)
                    
                    # 데이터 형식 감지
                    data_format = self._detect_data_format(text)
                    
                    point = IntegrationPoint(
                        name=f"{method_or_type}_{endpoint.replace('/', '_')}",
                        type='api',
                        direction=direction,
                        protocol=protocol,
                        endpoint=endpoint,
                        authentication=authentication,
                        data_format=data_format,
                        description=match.group(0)
                    )
                    points.append(point)
                    
        # 데이터베이스 연결 포인트
        db_points = self._extract_database_integration_points(text)
        points.extend(db_points)
        
        # 파일 시스템 통합 포인트
        file_points = self._extract_file_integration_points(text)
        points.extend(file_points)
        
        return points

    def _analyze_data_flows(self, text: str) -> List[Dict[str, Any]]:
        """데이터 플로우 분석"""
        flows = []
        
        # 데이터 플로우 패턴
        flow_patterns = [
            r'(data|information)\s+(flows?|moves?|transfers?)\s+from\s+(\w+)\s+to\s+(\w+)',
            r'(\w+)\s+(sends?|receives?|processes?)\s+(data|information|requests?)\s+(?:to|from)\s+(\w+)',
            r'(\w+)\s+→\s+(\w+)',
            r'(\w+)\s+(triggers?|notifies?|updates?)\s+(\w+)'
        ]
        
        for pattern in flow_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 2:
                    source = groups[-2] if len(groups) > 2 else groups[0]
                    target = groups[-1]
                    
                    # 데이터 타입 추론
                    data_type = self._infer_data_type(match.group(0))
                    
                    # 플로우 타입 결정
                    flow_type = self._determine_flow_type(match.group(0))
                    
                    flow = {
                        'source': source,
                        'target': target,
                        'data_type': data_type,
                        'flow_type': flow_type,
                        'description': match.group(0),
                        'synchronous': 'real-time' in match.group(0).lower() or 'sync' in match.group(0).lower()
                    }
                    flows.append(flow)
                    
        return flows

    def _infer_provider(self, service_name: str, service_type: str) -> str:
        """서비스 제공자 추론"""
        provider_mapping = {
            'stripe': 'Stripe',
            'paypal': 'PayPal',
            'square': 'Square',
            'auth0': 'Auth0',
            'okta': 'Okta',
            'cognito': 'AWS',
            'sendgrid': 'SendGrid',
            'mailgun': 'Mailgun',
            'ses': 'AWS',
            's3': 'AWS',
            'mongodb': 'MongoDB',
            'postgresql': 'PostgreSQL',
            'mysql': 'MySQL',
            'redis': 'Redis',
            'kafka': 'Apache Kafka',
            'rabbitmq': 'RabbitMQ',
            'sqs': 'AWS'
        }
        
        service_lower = service_name.lower()
        return provider_mapping.get(service_lower, 'Unknown')

    def _create_service_integration_points(
        self,
        service_name: str,
        service_type: str,
        context: str
    ) -> List[IntegrationPoint]:
        """서비스별 통합 포인트 생성"""
        points = []
        
        # 서비스 타입별 기본 통합 포인트
        default_points = {
            'payment': [
                {'name': 'create_payment', 'direction': 'outbound', 'protocol': 'rest'},
                {'name': 'webhook_payment_status', 'direction': 'inbound', 'protocol': 'webhook'}
            ],
            'authentication': [
                {'name': 'login', 'direction': 'outbound', 'protocol': 'oauth'},
                {'name': 'user_info', 'direction': 'inbound', 'protocol': 'rest'}
            ],
            'email': [
                {'name': 'send_email', 'direction': 'outbound', 'protocol': 'rest'},
                {'name': 'delivery_status', 'direction': 'inbound', 'protocol': 'webhook'}
            ],
            'storage': [
                {'name': 'upload_file', 'direction': 'outbound', 'protocol': 'rest'},
                {'name': 'download_file', 'direction': 'inbound', 'protocol': 'rest'}
            ]
        }
        
        if service_type in default_points:
            for point_config in default_points[service_type]:
                point = IntegrationPoint(
                    name=f"{service_name}_{point_config['name']}",
                    type='api',
                    direction=point_config['direction'],
                    protocol=point_config['protocol'],
                    endpoint=f"/{service_name}/{point_config['name']}",
                    authentication=self._detect_authentication(context),
                    data_format='json',
                    description=f"{service_name} {point_config['name']} integration"
                )
                points.append(point)
                
        return points

    def _extract_service_configuration(
        self,
        service_name: str,
        service_type: str,
        context: str
    ) -> Dict[str, Any]:
        """서비스 설정 추출"""
        config = {}
        
        # API 키 패턴
        if re.search(r'api\s+key|secret|token', context, re.IGNORECASE):
            config['requires_api_key'] = True
            
        # 환경 설정
        if re.search(r'sandbox|test|development', context, re.IGNORECASE):
            config['environment'] = 'development'
        elif re.search(r'production|live', context, re.IGNORECASE):
            config['environment'] = 'production'
        else:
            config['environment'] = 'development'
            
        # 지역 설정
        region_match = re.search(r'region[:\s]+(\w+)', context, re.IGNORECASE)
        if region_match:
            config['region'] = region_match.group(1)
            
        # 버전 설정
        version_match = re.search(r'version[:\s]+([v\d.]+)', context, re.IGNORECASE)
        if version_match:
            config['version'] = version_match.group(1)
            
        return config

    def _analyze_service_dependencies(
        self,
        service_name: str,
        service_type: str,
        context: str
    ) -> List[str]:
        """서비스 의존성 분석"""
        dependencies = []
        
        # 일반적인 의존성 패턴
        dependency_patterns = [
            r'requires?\s+(\w+)',
            r'depends?\s+on\s+(\w+)',
            r'needs?\s+(\w+)',
            r'after\s+(\w+)'
        ]
        
        for pattern in dependency_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            dependencies.extend(matches)
            
        # 서비스 타입별 일반적인 의존성
        common_dependencies = {
            'payment': ['user_authentication', 'order_management'],
            'email': ['user_management', 'template_engine'],
            'storage': ['authentication', 'file_validation'],
            'analytics': ['user_tracking', 'event_system']
        }
        
        if service_type in common_dependencies:
            dependencies.extend(common_dependencies[service_type])
            
        return list(set(dependencies))

    def _detect_protocol(self, text: str, endpoint: str) -> str:
        """프로토콜 감지"""
        text_lower = text.lower()
        
        for protocol, pattern in self.protocol_patterns.items():
            if re.search(pattern, text_lower):
                return protocol
                
        # 엔드포인트 기반 추론
        if endpoint.startswith('/api'):
            return 'rest'
        elif 'ws://' in endpoint or 'wss://' in endpoint:
            return 'websocket'
        else:
            return 'rest'

    def _determine_direction(self, text: str, method_or_type: str) -> str:
        """통합 방향 결정"""
        text_lower = text.lower()
        
        if method_or_type in ['GET', 'FETCH', 'RETRIEVE']:
            return 'inbound'
        elif method_or_type in ['POST', 'PUT', 'PATCH', 'DELETE', 'SEND']:
            return 'outbound'
        elif 'webhook' in text_lower or 'callback' in text_lower:
            return 'inbound'
        elif 'send' in text_lower or 'push' in text_lower:
            return 'outbound'
        elif 'receive' in text_lower or 'get' in text_lower:
            return 'inbound'
        else:
            return 'bidirectional'

    def _detect_authentication(self, text: str) -> Optional[str]:
        """인증 방식 감지"""
        text_lower = text.lower()
        
        if 'oauth' in text_lower:
            return 'oauth'
        elif 'jwt' in text_lower or 'bearer token' in text_lower:
            return 'bearer'
        elif 'api key' in text_lower:
            return 'api_key'
        elif 'basic auth' in text_lower:
            return 'basic'
        elif 'no auth' in text_lower or 'public' in text_lower:
            return 'none'
        else:
            return 'api_key'  # 기본값

    def _detect_data_format(self, text: str) -> str:
        """데이터 형식 감지"""
        text_lower = text.lower()
        
        if 'json' in text_lower:
            return 'json'
        elif 'xml' in text_lower:
            return 'xml'
        elif 'form' in text_lower or 'urlencoded' in text_lower:
            return 'form'
        elif 'multipart' in text_lower:
            return 'multipart'
        elif 'binary' in text_lower:
            return 'binary'
        else:
            return 'json'  # 기본값

    def _extract_database_integration_points(self, text: str) -> List[IntegrationPoint]:
        """데이터베이스 통합 포인트 추출"""
        points = []
        
        db_patterns = [
            r'\b(connect|connection)\s+to\s+(\w+)\s+(database|db)\b',
            r'\b(query|read|write|update)\s+(\w+)\s+(database|db|table)\b',
            r'\b(mongodb|postgresql|mysql|redis)\s+(connection|integration)\b'
        ]
        
        for pattern in db_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if len(groups) >= 2:
                    operation = groups[0]
                    db_name = groups[1]
                    
                    point = IntegrationPoint(
                        name=f"db_{db_name}_{operation}",
                        type='database',
                        direction='bidirectional',
                        protocol='tcp',
                        endpoint=f"{db_name}:5432",  # 기본 포트
                        authentication='credentials',
                        data_format='sql',
                        description=f"Database {operation} to {db_name}"
                    )
                    points.append(point)
                    
        return points

    def _extract_file_integration_points(self, text: str) -> List[IntegrationPoint]:
        """파일 시스템 통합 포인트 추출"""
        points = []
        
        file_patterns = [
            r'\b(upload|download|store|retrieve)\s+(file|document|image|video)\b',
            r'\b(file\s+storage|object\s+storage|cdn)\b',
            r'\b(s3|blob\s+storage|file\s+system)\b'
        ]
        
        for pattern in file_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                operation = match.group(1) if match.groups() else 'file_operation'
                
                direction = 'outbound' if operation.lower() in ['upload', 'store'] else 'inbound'
                
                point = IntegrationPoint(
                    name=f"file_{operation}",
                    type='file',
                    direction=direction,
                    protocol='rest',
                    endpoint='/files',
                    authentication='api_key',
                    data_format='multipart',
                    description=f"File {operation} integration"
                )
                points.append(point)
                
        return points

    def _infer_data_type(self, flow_text: str) -> str:
        """데이터 타입 추론"""
        text_lower = flow_text.lower()
        
        if any(keyword in text_lower for keyword in ['user', 'profile', 'account']):
            return 'user_data'
        elif any(keyword in text_lower for keyword in ['order', 'transaction', 'payment']):
            return 'transaction_data'
        elif any(keyword in text_lower for keyword in ['product', 'inventory', 'catalog']):
            return 'product_data'
        elif any(keyword in text_lower for keyword in ['event', 'log', 'activity']):
            return 'event_data'
        elif any(keyword in text_lower for keyword in ['file', 'document', 'media']):
            return 'file_data'
        else:
            return 'generic_data'

    def _determine_flow_type(self, flow_text: str) -> str:
        """플로우 타입 결정"""
        text_lower = flow_text.lower()
        
        if any(keyword in text_lower for keyword in ['trigger', 'event', 'notify']):
            return 'event_driven'
        elif any(keyword in text_lower for keyword in ['request', 'response', 'call']):
            return 'request_response'
        elif any(keyword in text_lower for keyword in ['stream', 'continuous', 'real-time']):
            return 'streaming'
        elif any(keyword in text_lower for keyword in ['batch', 'bulk', 'scheduled']):
            return 'batch'
        else:
            return 'synchronous'

    def _extract_security_requirements(self, requirements: List[Dict[str, Any]]) -> List[str]:
        """보안 요구사항 추출"""
        security_reqs = []
        
        security_keywords = [
            'encryption', 'ssl', 'tls', 'https',
            'authentication', 'authorization', 'oauth',
            'api key', 'token', 'jwt',
            'firewall', 'vpn', 'whitelist',
            'rate limiting', 'throttling',
            'data privacy', 'gdpr', 'compliance'
        ]
        
        for req in requirements:
            description = req.get('description', '').lower()
            
            for keyword in security_keywords:
                if keyword in description:
                    security_reqs.append(keyword)
                    
        return list(set(security_reqs))

    def _extract_monitoring_requirements(self, requirements: List[Dict[str, Any]]) -> List[str]:
        """모니터링 요구사항 추출"""
        monitoring_reqs = []
        
        monitoring_keywords = [
            'logging', 'monitoring', 'alerting',
            'metrics', 'analytics', 'tracking',
            'health check', 'uptime', 'availability',
            'performance monitoring', 'error tracking',
            'audit trail', 'compliance logging'
        ]
        
        for req in requirements:
            description = req.get('description', '').lower()
            
            for keyword in monitoring_keywords:
                if keyword in description:
                    monitoring_reqs.append(keyword)
                    
        return list(set(monitoring_reqs))

    def _deduplicate_services(self, services: List[ExternalService]) -> List[ExternalService]:
        """중복 서비스 제거"""
        unique_services = {}
        
        for service in services:
            key = f"{service.name}_{service.service_type}"
            if key not in unique_services:
                unique_services[key] = service
            else:
                # 통합 포인트 병합
                existing = unique_services[key]
                existing.integration_points.extend(service.integration_points)
                existing.configuration.update(service.configuration)
                existing.dependencies.extend(service.dependencies)
                
        return list(unique_services.values())

    def _deduplicate_integration_points(self, points: List[IntegrationPoint]) -> List[IntegrationPoint]:
        """중복 통합 포인트 제거"""
        unique_points = {}
        
        for point in points:
            key = f"{point.name}_{point.type}_{point.endpoint}"
            if key not in unique_points:
                unique_points[key] = point
                
        return list(unique_points.values())