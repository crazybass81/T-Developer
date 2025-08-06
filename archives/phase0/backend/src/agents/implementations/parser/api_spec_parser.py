from typing import Dict, List, Any
import re

class APISpecificationParser:
    """API 명세 파서"""

    def __init__(self):
        self.endpoint_patterns = self._load_endpoint_patterns()
        self.method_patterns = self._load_method_patterns()
        self.parameter_patterns = self._load_parameter_patterns()

    def _load_endpoint_patterns(self) -> List[str]:
        """엔드포인트 패턴 로드"""
        return [
            r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w/\-{}]+)',
            r'endpoint\s+(/[\w/\-{}]+)',
            r'route\s+(/[\w/\-{}]+)',
            r'api\s+(/[\w/\-{}]+)',
            r'(/api/[\w/\-{}]+)'
        ]

    def _load_method_patterns(self) -> Dict[str, List[str]]:
        """HTTP 메서드 패턴 로드"""
        return {
            'GET': ['get', 'retrieve', 'fetch', 'list', 'show', 'view'],
            'POST': ['post', 'create', 'add', 'insert', 'new'],
            'PUT': ['put', 'update', 'modify', 'edit', 'replace'],
            'DELETE': ['delete', 'remove', 'destroy'],
            'PATCH': ['patch', 'partial update', 'modify']
        }

    def _load_parameter_patterns(self) -> List[str]:
        """파라미터 패턴 로드"""
        return [
            r'parameter\s+(\w+)\s+\((\w+)\)',
            r'(\w+)\s+parameter\s+of\s+type\s+(\w+)',
            r'\{(\w+)\}',  # path parameters
            r'query\s+(\w+)',
            r'body\s+(\w+)'
        ]

    async def parse(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """API 명세 파싱"""
        api_specs = []
        text = str(base_structure)

        # 엔드포인트 추출
        endpoints = self._extract_endpoints(text)
        
        for endpoint in endpoints:
            spec = {
                'path': endpoint['path'],
                'method': endpoint['method'],
                'summary': self._generate_summary(endpoint),
                'description': self._generate_description(endpoint),
                'parameters': self._extract_parameters(text, endpoint['path']),
                'request_body': self._extract_request_body(text, endpoint),
                'responses': self._generate_responses(endpoint),
                'tags': self._generate_tags(endpoint['path']),
                'security': self._determine_security(endpoint),
                'metadata': {
                    'generated': True,
                    'confidence': 0.8
                }
            }
            api_specs.append(spec)

        # 기본 API가 없으면 추론
        if not api_specs:
            api_specs = self._infer_basic_apis(base_structure)

        return api_specs

    def _extract_endpoints(self, text: str) -> List[Dict[str, Any]]:
        """엔드포인트 추출"""
        endpoints = []
        
        for pattern in self.endpoint_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                endpoint = self._parse_endpoint_match(match)
                if endpoint and endpoint not in endpoints:
                    endpoints.append(endpoint)

        return endpoints

    def _parse_endpoint_match(self, match) -> Dict[str, Any]:
        """엔드포인트 매치 파싱"""
        groups = match.groups()
        
        if len(groups) >= 2 and groups[0] in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
            return {
                'method': groups[0].upper(),
                'path': groups[1],
                'raw_match': match.group()
            }
        elif len(groups) >= 1 and groups[0].startswith('/'):
            # 메서드가 명시되지 않은 경우 경로에서 추론
            path = groups[0]
            method = self._infer_method_from_path(path)
            return {
                'method': method,
                'path': path,
                'raw_match': match.group()
            }
        
        return {}

    def _infer_method_from_path(self, path: str) -> str:
        """경로에서 HTTP 메서드 추론"""
        path_lower = path.lower()
        
        if 'create' in path_lower or 'add' in path_lower:
            return 'POST'
        elif 'update' in path_lower or 'edit' in path_lower:
            return 'PUT'
        elif 'delete' in path_lower or 'remove' in path_lower:
            return 'DELETE'
        elif 'list' in path_lower or 'search' in path_lower:
            return 'GET'
        else:
            return 'GET'  # 기본값

    def _generate_summary(self, endpoint: Dict[str, Any]) -> str:
        """요약 생성"""
        method = endpoint['method']
        path = endpoint['path']
        
        # 경로에서 리소스 추출
        resource = self._extract_resource_from_path(path)
        
        summary_templates = {
            'GET': f"Get {resource}",
            'POST': f"Create {resource}",
            'PUT': f"Update {resource}",
            'DELETE': f"Delete {resource}",
            'PATCH': f"Partially update {resource}"
        }
        
        return summary_templates.get(method, f"{method} {resource}")

    def _generate_description(self, endpoint: Dict[str, Any]) -> str:
        """설명 생성"""
        method = endpoint['method']
        path = endpoint['path']
        resource = self._extract_resource_from_path(path)
        
        description_templates = {
            'GET': f"Retrieves {resource} information from the system",
            'POST': f"Creates a new {resource} in the system",
            'PUT': f"Updates an existing {resource} in the system",
            'DELETE': f"Removes a {resource} from the system",
            'PATCH': f"Partially updates a {resource} in the system"
        }
        
        return description_templates.get(method, f"Performs {method} operation on {resource}")

    def _extract_resource_from_path(self, path: str) -> str:
        """경로에서 리소스 추출"""
        # /api/users/{id} -> users
        # /products -> products
        parts = path.strip('/').split('/')
        
        for part in parts:
            if part and not part.startswith('{') and part != 'api':
                return part.rstrip('s') if part.endswith('s') else part
        
        return 'resource'

    def _extract_parameters(self, text: str, path: str) -> List[Dict[str, Any]]:
        """파라미터 추출"""
        parameters = []
        
        # 경로 파라미터 추출
        path_params = re.findall(r'\{(\w+)\}', path)
        for param in path_params:
            parameters.append({
                'name': param,
                'in': 'path',
                'required': True,
                'type': 'string',
                'description': f"The {param} identifier"
            })
        
        # 쿼리 파라미터 패턴 찾기
        query_patterns = [
            r'query\s+parameter\s+(\w+)',
            r'filter\s+by\s+(\w+)',
            r'search\s+(\w+)',
            r'page\s+(\w+)',
            r'limit\s+(\w+)'
        ]
        
        for pattern in query_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                param_name = match.group(1)
                parameters.append({
                    'name': param_name,
                    'in': 'query',
                    'required': False,
                    'type': self._infer_parameter_type(param_name),
                    'description': f"Filter by {param_name}"
                })

        return parameters

    def _infer_parameter_type(self, param_name: str) -> str:
        """파라미터 타입 추론"""
        type_hints = {
            'id': 'integer',
            'page': 'integer',
            'limit': 'integer',
            'count': 'integer',
            'size': 'integer',
            'offset': 'integer',
            'email': 'string',
            'name': 'string',
            'title': 'string',
            'description': 'string',
            'date': 'string',
            'created_at': 'string',
            'updated_at': 'string',
            'active': 'boolean',
            'enabled': 'boolean'
        }
        
        return type_hints.get(param_name.lower(), 'string')

    def _extract_request_body(self, text: str, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """요청 본문 추출"""
        if endpoint['method'] in ['POST', 'PUT', 'PATCH']:
            resource = self._extract_resource_from_path(endpoint['path'])
            
            return {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': self._generate_schema_properties(resource),
                            'required': self._get_required_fields(resource)
                        }
                    }
                }
            }
        
        return {}

    def _generate_schema_properties(self, resource: str) -> Dict[str, Any]:
        """스키마 속성 생성"""
        common_properties = {
            'user': {
                'email': {'type': 'string', 'format': 'email'},
                'name': {'type': 'string'},
                'password': {'type': 'string', 'minLength': 8}
            },
            'product': {
                'name': {'type': 'string'},
                'description': {'type': 'string'},
                'price': {'type': 'number', 'minimum': 0},
                'category': {'type': 'string'}
            },
            'order': {
                'user_id': {'type': 'integer'},
                'items': {'type': 'array'},
                'total_amount': {'type': 'number', 'minimum': 0}
            }
        }
        
        return common_properties.get(resource, {
            'name': {'type': 'string'},
            'description': {'type': 'string'}
        })

    def _get_required_fields(self, resource: str) -> List[str]:
        """필수 필드 반환"""
        required_fields = {
            'user': ['email', 'name'],
            'product': ['name', 'price'],
            'order': ['user_id', 'items']
        }
        
        return required_fields.get(resource, ['name'])

    def _generate_responses(self, endpoint: Dict[str, Any]) -> Dict[str, Any]:
        """응답 생성"""
        method = endpoint['method']
        
        responses = {
            '400': {
                'description': 'Bad Request',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'error': {'type': 'string'},
                                'message': {'type': 'string'}
                            }
                        }
                    }
                }
            },
            '500': {
                'description': 'Internal Server Error'
            }
        }
        
        if method == 'GET':
            responses['200'] = {
                'description': 'Success',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'data': {'type': 'object'},
                                'message': {'type': 'string'}
                            }
                        }
                    }
                }
            }
            responses['404'] = {'description': 'Not Found'}
        elif method == 'POST':
            responses['201'] = {
                'description': 'Created',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'message': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        elif method in ['PUT', 'PATCH']:
            responses['200'] = {'description': 'Updated'}
            responses['404'] = {'description': 'Not Found'}
        elif method == 'DELETE':
            responses['204'] = {'description': 'No Content'}
            responses['404'] = {'description': 'Not Found'}

        return responses

    def _generate_tags(self, path: str) -> List[str]:
        """태그 생성"""
        resource = self._extract_resource_from_path(path)
        return [resource.capitalize()]

    def _determine_security(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """보안 요구사항 결정"""
        # 대부분의 API는 인증이 필요하다고 가정
        return [{'bearerAuth': []}]

    def _infer_basic_apis(self, base_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """기본 API 추론"""
        project_type = base_structure.get('project_info', {}).get('type', 'web')
        
        if 'ecommerce' in str(base_structure).lower():
            return self._create_ecommerce_apis()
        elif 'blog' in str(base_structure).lower():
            return self._create_blog_apis()
        else:
            return self._create_generic_apis()

    def _create_ecommerce_apis(self) -> List[Dict[str, Any]]:
        """이커머스 API 생성"""
        return [
            {
                'path': '/api/users',
                'method': 'GET',
                'summary': 'Get users',
                'description': 'Retrieves list of users',
                'parameters': [],
                'responses': {'200': {'description': 'Success'}},
                'tags': ['Users']
            },
            {
                'path': '/api/products',
                'method': 'GET',
                'summary': 'Get products',
                'description': 'Retrieves list of products',
                'parameters': [],
                'responses': {'200': {'description': 'Success'}},
                'tags': ['Products']
            }
        ]

    def _create_blog_apis(self) -> List[Dict[str, Any]]:
        """블로그 API 생성"""
        return [
            {
                'path': '/api/posts',
                'method': 'GET',
                'summary': 'Get posts',
                'description': 'Retrieves list of blog posts',
                'parameters': [],
                'responses': {'200': {'description': 'Success'}},
                'tags': ['Posts']
            }
        ]

    def _create_generic_apis(self) -> List[Dict[str, Any]]:
        """일반 API 생성"""
        return [
            {
                'path': '/api/health',
                'method': 'GET',
                'summary': 'Health check',
                'description': 'Check API health status',
                'parameters': [],
                'responses': {'200': {'description': 'API is healthy'}},
                'tags': ['System']
            }
        ]