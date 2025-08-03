# backend/src/agents/implementations/parser_api_spec_parser.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
import json

@dataclass
class APIEndpoint:
    path: str
    method: str
    description: str
    parameters: List[Dict[str, Any]]
    request_body: Optional[Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    authentication: Optional[str]

@dataclass
class APISpecification:
    base_url: str
    version: str
    endpoints: List[APIEndpoint]
    authentication_schemes: List[str]
    data_models: List[str]

class APISpecificationParser:
    """API 명세 파서"""

    def __init__(self):
        self.endpoint_patterns = [
            r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/\-{}]+)',
            r'(endpoint|route|api):\s*(/[\w/\-{}]+)',
            r'(GET|POST|PUT|DELETE|PATCH)\s+.*?(/api/[\w/\-{}]+)'
        ]
        
        self.parameter_patterns = [
            r'parameter[s]?:\s*([^.]+)',
            r'query:\s*([^.]+)',
            r'path:\s*([^.]+)',
            r'\{(\w+)\}'  # Path parameters
        ]

    async def parse_api_specifications(
        self,
        requirements: List[Dict[str, Any]]
    ) -> List[APISpecification]:
        """API 명세 파싱"""
        
        api_specs = []
        endpoints = []
        
        for req in requirements:
            description = req.get('description', '')
            
            # API 엔드포인트 추출
            req_endpoints = self._extract_endpoints(description)
            endpoints.extend(req_endpoints)
            
        if endpoints:
            # 기본 API 명세 생성
            api_spec = APISpecification(
                base_url="/api/v1",
                version="1.0.0",
                endpoints=endpoints,
                authentication_schemes=self._detect_auth_schemes(requirements),
                data_models=self._extract_data_models(requirements)
            )
            api_specs.append(api_spec)
            
        return api_specs

    def _extract_endpoints(self, text: str) -> List[APIEndpoint]:
        """엔드포인트 추출"""
        endpoints = []
        
        for pattern in self.endpoint_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    method = match.group(1).upper()
                    path = match.group(2)
                    
                    endpoint = APIEndpoint(
                        path=path,
                        method=method,
                        description=f"{method} {path}",
                        parameters=self._extract_parameters(text, path),
                        request_body=self._extract_request_body(text, method),
                        responses=self._extract_responses(text),
                        authentication=self._detect_endpoint_auth(text)
                    )
                    endpoints.append(endpoint)
                    
        return endpoints

    def _extract_parameters(self, text: str, path: str) -> List[Dict[str, Any]]:
        """파라미터 추출"""
        parameters = []
        
        # Path parameters
        path_params = re.findall(r'\{(\w+)\}', path)
        for param in path_params:
            parameters.append({
                'name': param,
                'in': 'path',
                'required': True,
                'type': 'string'
            })
            
        # Query parameters
        for pattern in self.parameter_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, str):
                    param_names = [p.strip() for p in match.split(',')]
                    for param_name in param_names:
                        if param_name and param_name not in [p['name'] for p in parameters]:
                            parameters.append({
                                'name': param_name,
                                'in': 'query',
                                'required': False,
                                'type': 'string'
                            })
                            
        return parameters

    def _extract_request_body(self, text: str, method: str) -> Optional[Dict[str, Any]]:
        """요청 본문 추출"""
        if method in ['POST', 'PUT', 'PATCH']:
            # 요청 본문 패턴 찾기
            body_patterns = [
                r'request\s+body:\s*([^.]+)',
                r'payload:\s*([^.]+)',
                r'data:\s*([^.]+)'
            ]
            
            for pattern in body_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return {
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'description': match.group(1).strip()
                                }
                            }
                        }
                    }
        return None

    def _extract_responses(self, text: str) -> Dict[str, Dict[str, Any]]:
        """응답 추출"""
        responses = {
            '200': {
                'description': 'Success',
                'content': {
                    'application/json': {
                        'schema': {'type': 'object'}
                    }
                }
            }
        }
        
        # 에러 응답 패턴
        if re.search(r'error|fail|invalid', text, re.IGNORECASE):
            responses['400'] = {
                'description': 'Bad Request'
            }
            responses['500'] = {
                'description': 'Internal Server Error'
            }
            
        return responses

    def _detect_auth_schemes(self, requirements: List[Dict[str, Any]]) -> List[str]:
        """인증 스키마 감지"""
        auth_schemes = []
        
        for req in requirements:
            description = req.get('description', '').lower()
            
            if 'jwt' in description or 'token' in description:
                auth_schemes.append('Bearer')
            elif 'oauth' in description:
                auth_schemes.append('OAuth2')
            elif 'api key' in description:
                auth_schemes.append('ApiKey')
            elif 'basic auth' in description:
                auth_schemes.append('Basic')
                
        return list(set(auth_schemes))

    def _detect_endpoint_auth(self, text: str) -> Optional[str]:
        """엔드포인트별 인증 감지"""
        text_lower = text.lower()
        
        if 'authenticated' in text_lower or 'login required' in text_lower:
            return 'required'
        elif 'public' in text_lower or 'no auth' in text_lower:
            return 'none'
        else:
            return 'optional'

    def _extract_data_models(self, requirements: List[Dict[str, Any]]) -> List[str]:
        """데이터 모델 추출"""
        models = set()
        
        for req in requirements:
            description = req.get('description', '').lower()
            
            # 일반적인 데이터 모델 키워드
            model_keywords = [
                'user', 'customer', 'account', 'profile',
                'product', 'item', 'inventory',
                'order', 'transaction', 'payment',
                'category', 'tag', 'comment', 'review'
            ]
            
            for keyword in model_keywords:
                if keyword in description:
                    models.add(keyword.capitalize())
                    
        return list(models)