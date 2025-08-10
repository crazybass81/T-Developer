"""
API Parser Module  
Parses and generates API specifications from requirements
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from enum import Enum
from collections import defaultdict


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIAuthType(Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"
    OAUTH2 = "oauth2"
    JWT = "jwt"


class APIParser:
    """Parses API requirements and generates specifications"""
    
    def __init__(self):
        # API patterns
        self.api_patterns = {
            'endpoint': r'(?:GET|POST|PUT|PATCH|DELETE)\s+(/[\w/\{\}-]+)',
            'rest_resource': r'(?:resource|endpoint|api):\s*(/?\w+(?:/\w+)*)',
            'request_body': r'(?:body|payload|data):\s*\{([^}]+)\}',
            'response': r'(?:returns?|response):\s*\{([^}]+)\}',
            'parameter': r'(?:param|parameter)\s+(\w+):\s*(\w+)',
            'query': r'(?:query|filter|search):\s*([^\n]+)',
            'header': r'(?:header)\s+([^:]+):\s*([^\n]+)',
            'status': r'(?:status|code):\s*(\d{3})'
        }
        
        # REST conventions
        self.rest_conventions = {
            'list': {'method': HTTPMethod.GET, 'path': '/{resource}'},
            'get': {'method': HTTPMethod.GET, 'path': '/{resource}/{id}'},
            'create': {'method': HTTPMethod.POST, 'path': '/{resource}'},
            'update': {'method': HTTPMethod.PUT, 'path': '/{resource}/{id}'},
            'patch': {'method': HTTPMethod.PATCH, 'path': '/{resource}/{id}'},
            'delete': {'method': HTTPMethod.DELETE, 'path': '/{resource}/{id}'},
            'search': {'method': HTTPMethod.GET, 'path': '/{resource}/search'},
            'bulk': {'method': HTTPMethod.POST, 'path': '/{resource}/bulk'}
        }
        
        # Common response codes
        self.status_codes = {
            200: 'OK',
            201: 'Created',
            204: 'No Content',
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            422: 'Unprocessable Entity',
            500: 'Internal Server Error'
        }
        
        # Data type mappings
        self.openapi_types = {
            'string': 'string',
            'integer': 'integer',
            'float': 'number',
            'boolean': 'boolean',
            'date': 'string',
            'datetime': 'string',
            'uuid': 'string',
            'email': 'string',
            'url': 'string',
            'array': 'array',
            'object': 'object'
        }
    
    async def parse(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parse API specifications from text
        
        Args:
            text: Text containing API requirements
            entities: Extracted entities
            
        Returns:
            API specifications
        """
        # Extract explicit API definitions
        explicit_apis = self._extract_explicit_apis(text)
        
        # Generate CRUD APIs for entities
        entity_apis = self._generate_entity_apis(entities)
        
        # Extract business operation APIs
        operation_apis = self._extract_operation_apis(text, entities)
        
        # Merge and deduplicate APIs
        all_apis = self._merge_apis(explicit_apis, entity_apis, operation_apis)
        
        # Enhance APIs with details
        enhanced_apis = []
        for api in all_apis:
            enhanced = await self._enhance_api(api, text, entities)
            enhanced_apis.append(enhanced)
        
        # Generate OpenAPI specification
        openapi_spec = self._generate_openapi_spec(enhanced_apis)
        
        # Generate API documentation
        documentation = self._generate_documentation(enhanced_apis)
        
        # Generate client SDKs
        sdk_specs = self._generate_sdk_specs(enhanced_apis)
        
        # Validate APIs
        validation = self._validate_apis(enhanced_apis)
        
        # Generate test cases
        test_cases = self._generate_test_cases(enhanced_apis)
        
        # Create API gateway configuration
        gateway_config = self._generate_gateway_config(enhanced_apis)
        
        return {
            'endpoints': enhanced_apis,
            'openapi': openapi_spec,
            'documentation': documentation,
            'sdk_specs': sdk_specs,
            'validation': validation,
            'test_cases': test_cases,
            'gateway_config': gateway_config,
            'statistics': self._calculate_statistics(enhanced_apis)
        }
    
    def _extract_explicit_apis(self, text: str) -> List[Dict]:
        """Extract explicitly defined APIs from text"""
        apis = []
        
        # Find HTTP method + path patterns
        pattern = r'(GET|POST|PUT|PATCH|DELETE)\s+(/[\w/\{\}-]+)'
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            method = match.group(1).upper()
            path = match.group(2)
            
            # Extract context around the match
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 200)
            context = text[start:end]
            
            api = {
                'method': method,
                'path': path,
                'description': self._extract_description(context),
                'parameters': self._extract_parameters(path, context),
                'request_body': self._extract_request_body(context),
                'responses': self._extract_responses(context),
                'authentication': self._extract_auth(context),
                'source': 'explicit'
            }
            
            apis.append(api)
        
        return apis
    
    def _generate_entity_apis(self, entities: Dict[str, Any]) -> List[Dict]:
        """Generate CRUD APIs for entities"""
        apis = []
        
        # Get entity models
        entity_list = entities.get('entities', {}).get('objects', [])
        
        for entity in entity_list:
            resource_name = entity['text'].lower()
            
            # Skip if too generic
            if resource_name in ['data', 'object', 'item', 'entity']:
                continue
            
            # Generate standard CRUD endpoints
            for operation, convention in self.rest_conventions.items():
                if operation in ['search', 'bulk']:
                    continue  # Skip advanced operations for now
                
                path = convention['path'].replace('{resource}', resource_name + 's')
                
                api = {
                    'method': convention['method'].value,
                    'path': path,
                    'description': f"{operation.capitalize()} {resource_name}",
                    'parameters': self._get_path_parameters(path),
                    'request_body': self._get_request_body_for_method(convention['method'], resource_name),
                    'responses': self._get_standard_responses(convention['method']),
                    'authentication': {'type': APIAuthType.BEARER.value},
                    'source': 'generated',
                    'resource': resource_name
                }
                
                apis.append(api)
        
        return apis
    
    def _extract_operation_apis(
        self,
        text: str,
        entities: Dict[str, Any]
    ) -> List[Dict]:
        """Extract business operation APIs"""
        apis = []
        operations = []
        
        # Look for operation keywords
        operation_patterns = [
            r'(?:user|system)\s+(?:can|should|must)\s+(\w+)\s+(?:the\s+)?(\w+)',
            r'(\w+)\s+(?:the\s+)?(\w+)\s+(?:functionality|feature|operation)',
            r'(?:implement|create|add)\s+(\w+)\s+(?:for|to)\s+(\w+)'
        ]
        
        for pattern in operation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                action = match.group(1).lower()
                resource = match.group(2).lower()
                
                # Skip common words
                if action in ['the', 'a', 'an', 'this', 'that']:
                    continue
                
                operations.append({
                    'action': action,
                    'resource': resource
                })
        
        # Convert operations to APIs
        for op in operations:
            method, path = self._operation_to_api(op['action'], op['resource'])
            
            api = {
                'method': method,
                'path': path,
                'description': f"{op['action'].capitalize()} {op['resource']}",
                'parameters': self._get_path_parameters(path),
                'request_body': self._get_request_body_for_action(op['action']),
                'responses': self._get_standard_responses(HTTPMethod[method]),
                'authentication': {'type': APIAuthType.BEARER.value},
                'source': 'inferred',
                'operation': op['action']
            }
            
            apis.append(api)
        
        return apis
    
    def _operation_to_api(self, action: str, resource: str) -> Tuple[str, str]:
        """Convert operation to HTTP method and path"""
        # Action to method mapping
        action_methods = {
            'create': 'POST',
            'add': 'POST',
            'get': 'GET',
            'retrieve': 'GET',
            'fetch': 'GET',
            'list': 'GET',
            'update': 'PUT',
            'modify': 'PUT',
            'edit': 'PUT',
            'patch': 'PATCH',
            'delete': 'DELETE',
            'remove': 'DELETE',
            'search': 'GET',
            'filter': 'GET',
            'export': 'GET',
            'import': 'POST',
            'upload': 'POST',
            'download': 'GET',
            'send': 'POST',
            'approve': 'POST',
            'reject': 'POST',
            'process': 'POST',
            'calculate': 'POST',
            'validate': 'POST'
        }
        
        method = action_methods.get(action, 'POST')
        
        # Generate path
        if action in ['list', 'create']:
            path = f"/{resource}s"
        elif action in ['search', 'filter']:
            path = f"/{resource}s/search"
        elif action in ['export', 'import']:
            path = f"/{resource}s/{action}"
        elif action in ['approve', 'reject']:
            path = f"/{resource}s/{{id}}/{action}"
        else:
            path = f"/{resource}s/{{id}}"
        
        return method, path
    
    def _merge_apis(self, *api_lists) -> List[Dict]:
        """Merge and deduplicate API lists"""
        merged = []
        seen = set()
        
        for api_list in api_lists:
            for api in api_list:
                # Create unique key
                key = (api['method'], api['path'])
                
                if key not in seen:
                    seen.add(key)
                    merged.append(api)
        
        return merged
    
    async def _enhance_api(
        self,
        api: Dict,
        text: str,
        entities: Dict[str, Any]
    ) -> Dict:
        """Enhance API with additional details"""
        # Add OpenAPI operation ID
        api['operationId'] = self._generate_operation_id(api)
        
        # Add tags
        api['tags'] = self._extract_tags(api, entities)
        
        # Enhance parameters
        api['parameters'] = self._enhance_parameters(api['parameters'])
        
        # Add security requirements
        api['security'] = self._determine_security(api, text)
        
        # Add rate limiting
        api['rateLimit'] = self._determine_rate_limit(api)
        
        # Add caching
        api['cache'] = self._determine_caching(api)
        
        # Add examples
        api['examples'] = self._generate_examples(api)
        
        # Add validation rules
        api['validation'] = self._generate_validation_rules(api)
        
        return api
    
    def _extract_description(self, context: str) -> str:
        """Extract API description from context"""
        # Look for description patterns
        patterns = [
            r'(?:description|purpose):\s*([^\n]+)',
            r'(?:to|for)\s+([^\n]+)',
            r'#\s*([^\n]+)'  # Comment
        ]
        
        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Use first sentence as description
        sentences = context.split('.')
        if sentences:
            return sentences[0].strip()
        
        return "API endpoint"
    
    def _extract_parameters(self, path: str, context: str) -> List[Dict]:
        """Extract parameters from path and context"""
        parameters = []
        
        # Extract path parameters
        path_params = re.findall(r'\{(\w+)\}', path)
        for param in path_params:
            parameters.append({
                'name': param,
                'in': 'path',
                'required': True,
                'type': 'string',
                'description': f"{param} identifier"
            })
        
        # Extract query parameters from context
        query_pattern = r'(?:query|param|parameter)\s+(\w+)(?:\s*:\s*(\w+))?'
        matches = re.finditer(query_pattern, context, re.IGNORECASE)
        
        for match in matches:
            param_name = match.group(1)
            param_type = match.group(2) if match.group(2) else 'string'
            
            parameters.append({
                'name': param_name,
                'in': 'query',
                'required': False,
                'type': param_type,
                'description': f"Query parameter {param_name}"
            })
        
        return parameters
    
    def _extract_request_body(self, context: str) -> Optional[Dict]:
        """Extract request body from context"""
        # Look for body definition
        body_pattern = r'(?:body|payload|data):\s*\{([^}]+)\}'
        match = re.search(body_pattern, context, re.IGNORECASE)
        
        if match:
            body_text = match.group(1)
            fields = self._parse_fields(body_text)
            
            return {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': fields,
                            'required': [k for k, v in fields.items() if v.get('required')]
                        }
                    }
                }
            }
        
        return None
    
    def _parse_fields(self, text: str) -> Dict:
        """Parse field definitions from text"""
        fields = {}
        
        # Parse field: type pattern
        field_pattern = r'(\w+)\s*:\s*(\w+)'
        matches = re.finditer(field_pattern, text)
        
        for match in matches:
            field_name = match.group(1)
            field_type = match.group(2)
            
            fields[field_name] = {
                'type': self.openapi_types.get(field_type.lower(), 'string'),
                'required': 'required' in text.lower()
            }
        
        return fields
    
    def _extract_responses(self, context: str) -> Dict[int, Dict]:
        """Extract response definitions from context"""
        responses = {}
        
        # Default responses based on method
        responses[200] = {
            'description': 'Successful response',
            'content': {
                'application/json': {
                    'schema': {'type': 'object'}
                }
            }
        }
        
        # Look for specific status codes
        status_pattern = r'(?:returns?|response)\s+(\d{3})'
        matches = re.finditer(status_pattern, context, re.IGNORECASE)
        
        for match in matches:
            status = int(match.group(1))
            responses[status] = {
                'description': self.status_codes.get(status, 'Response'),
                'content': {
                    'application/json': {
                        'schema': {'type': 'object'}
                    }
                }
            }
        
        # Add error responses
        responses[400] = {'description': 'Bad Request'}
        responses[401] = {'description': 'Unauthorized'}
        responses[404] = {'description': 'Not Found'}
        responses[500] = {'description': 'Internal Server Error'}
        
        return responses
    
    def _extract_auth(self, context: str) -> Dict:
        """Extract authentication requirements"""
        auth = {'type': APIAuthType.NONE.value}
        
        auth_keywords = {
            'api key': APIAuthType.API_KEY,
            'bearer': APIAuthType.BEARER,
            'jwt': APIAuthType.JWT,
            'oauth': APIAuthType.OAUTH2,
            'basic auth': APIAuthType.BASIC
        }
        
        context_lower = context.lower()
        for keyword, auth_type in auth_keywords.items():
            if keyword in context_lower:
                auth['type'] = auth_type.value
                break
        
        # Default to bearer for protected resources
        if any(word in context_lower for word in ['authenticated', 'authorized', 'protected']):
            auth['type'] = APIAuthType.BEARER.value
        
        return auth
    
    def _get_path_parameters(self, path: str) -> List[Dict]:
        """Get parameters from path"""
        parameters = []
        
        # Extract path parameters
        params = re.findall(r'\{(\w+)\}', path)
        for param in params:
            param_type = 'string'
            if param == 'id' or param.endswith('_id'):
                param_type = 'uuid'
            
            parameters.append({
                'name': param,
                'in': 'path',
                'required': True,
                'type': param_type,
                'description': f"{param} parameter"
            })
        
        return parameters
    
    def _get_request_body_for_method(
        self,
        method: HTTPMethod,
        resource: str
    ) -> Optional[Dict]:
        """Get request body based on HTTP method"""
        if method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.PATCH]:
            return {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'description': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        
        return None
    
    def _get_request_body_for_action(self, action: str) -> Optional[Dict]:
        """Get request body based on action"""
        if action in ['create', 'add', 'update', 'modify', 'import', 'upload', 'send']:
            return {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {'type': 'object'}
                    }
                }
            }
        
        return None
    
    def _get_standard_responses(self, method: HTTPMethod) -> Dict[int, Dict]:
        """Get standard responses for HTTP method"""
        responses = {}
        
        if method == HTTPMethod.GET:
            responses[200] = {'description': 'Success'}
            responses[404] = {'description': 'Not Found'}
        elif method == HTTPMethod.POST:
            responses[201] = {'description': 'Created'}
            responses[400] = {'description': 'Bad Request'}
        elif method in [HTTPMethod.PUT, HTTPMethod.PATCH]:
            responses[200] = {'description': 'Updated'}
            responses[404] = {'description': 'Not Found'}
        elif method == HTTPMethod.DELETE:
            responses[204] = {'description': 'Deleted'}
            responses[404] = {'description': 'Not Found'}
        
        # Common error responses
        responses[401] = {'description': 'Unauthorized'}
        responses[500] = {'description': 'Internal Server Error'}
        
        return responses
    
    def _generate_operation_id(self, api: Dict) -> str:
        """Generate OpenAPI operation ID"""
        method = api['method'].lower()
        path_parts = api['path'].strip('/').split('/')
        
        # Remove parameter placeholders
        path_parts = [p for p in path_parts if not p.startswith('{')]
        
        # Generate ID
        if path_parts:
            return f"{method}_{}_'.join(path_parts)}"
        
        return f"{method}_root"
    
    def _extract_tags(self, api: Dict, entities: Dict) -> List[str]:
        """Extract tags for API"""
        tags = []
        
        # Add resource tag
        if 'resource' in api:
            tags.append(api['resource'].capitalize())
        
        # Add operation tag
        if 'operation' in api:
            tags.append(api['operation'].capitalize())
        
        # Extract from path
        path_parts = api['path'].strip('/').split('/')
        if path_parts:
            tags.append(path_parts[0].capitalize())
        
        return list(set(tags))
    
    def _enhance_parameters(self, parameters: List[Dict]) -> List[Dict]:
        """Enhance parameter definitions"""
        enhanced = []
        
        for param in parameters:
            enhanced_param = param.copy()
            
            # Add schema
            enhanced_param['schema'] = {
                'type': param.get('type', 'string')
            }
            
            # Add validation
            if param['name'] == 'id' or param['name'].endswith('_id'):
                enhanced_param['schema']['format'] = 'uuid'
            elif param['name'] == 'email':
                enhanced_param['schema']['format'] = 'email'
            elif param['name'] in ['page', 'limit', 'offset']:
                enhanced_param['schema']['type'] = 'integer'
                enhanced_param['schema']['minimum'] = 0
            
            enhanced.append(enhanced_param)
        
        return enhanced
    
    def _determine_security(self, api: Dict, text: str) -> List[Dict]:
        """Determine security requirements"""
        security = []
        
        auth_type = api.get('authentication', {}).get('type', 'none')
        
        if auth_type == APIAuthType.BEARER.value:
            security.append({'bearerAuth': []})
        elif auth_type == APIAuthType.API_KEY.value:
            security.append({'apiKey': []})
        elif auth_type == APIAuthType.OAUTH2.value:
            security.append({'oauth2': ['read', 'write']})
        
        return security
    
    def _determine_rate_limit(self, api: Dict) -> Dict:
        """Determine rate limiting for API"""
        # Default rate limits based on method
        if api['method'] == 'GET':
            return {'requests': 100, 'window': '1m'}
        elif api['method'] in ['POST', 'PUT', 'PATCH']:
            return {'requests': 50, 'window': '1m'}
        elif api['method'] == 'DELETE':
            return {'requests': 20, 'window': '1m'}
        
        return {'requests': 60, 'window': '1m'}
    
    def _determine_caching(self, api: Dict) -> Dict:
        """Determine caching strategy"""
        cache = {'enabled': False}
        
        if api['method'] == 'GET':
            # Cache GET requests
            cache = {
                'enabled': True,
                'ttl': 300,  # 5 minutes
                'vary': ['Authorization']
            }
            
            # Don't cache search/filter
            if 'search' in api['path'] or any(p['name'] in ['q', 'query', 'filter'] for p in api.get('parameters', [])):
                cache['enabled'] = False
        
        return cache
    
    def _generate_examples(self, api: Dict) -> Dict:
        """Generate request/response examples"""
        examples = {}
        
        # Request example
        if api.get('request_body'):
            examples['request'] = {
                'name': 'Example',
                'description': 'Sample data'
            }
        
        # Response example
        examples['response'] = {
            'id': '123e4567-e89b-12d3-a456-426614174000',
            'name': 'Example',
            'created_at': '2024-01-01T00:00:00Z'
        }
        
        return examples
    
    def _generate_validation_rules(self, api: Dict) -> List[Dict]:
        """Generate validation rules for API"""
        rules = []
        
        # Parameter validation
        for param in api.get('parameters', []):
            if param.get('required'):
                rules.append({
                    'field': param['name'],
                    'rule': 'required',
                    'message': f"{param['name']} is required"
                })
        
        # Body validation
        if api.get('request_body'):
            schema = api['request_body'].get('content', {}).get('application/json', {}).get('schema', {})
            for field in schema.get('required', []):
                rules.append({
                    'field': field,
                    'rule': 'required',
                    'message': f"{field} is required"
                })
        
        return rules
    
    def _generate_openapi_spec(self, apis: List[Dict]) -> Dict:
        """Generate OpenAPI specification"""
        paths = {}
        
        for api in apis:
            path = api['path']
            method = api['method'].lower()
            
            if path not in paths:
                paths[path] = {}
            
            paths[path][method] = {
                'summary': api.get('description', ''),
                'operationId': api.get('operationId', ''),
                'tags': api.get('tags', []),
                'parameters': api.get('parameters', []),
                'requestBody': api.get('request_body'),
                'responses': api.get('responses', {}),
                'security': api.get('security', [])
            }
        
        return {
            'openapi': '3.0.0',
            'info': {
                'title': 'Generated API',
                'version': '1.0.0'
            },
            'paths': paths,
            'components': {
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer',
                        'bearerFormat': 'JWT'
                    },
                    'apiKey': {
                        'type': 'apiKey',
                        'in': 'header',
                        'name': 'X-API-Key'
                    }
                }
            }
        }
    
    def _generate_documentation(self, apis: List[Dict]) -> str:
        """Generate API documentation"""
        doc = "# API Documentation\n\n"
        
        # Group by tags
        by_tag = defaultdict(list)
        for api in apis:
            for tag in api.get('tags', ['General']):
                by_tag[tag].append(api)
        
        for tag, tag_apis in by_tag.items():
            doc += f"## {tag}\n\n"
            
            for api in tag_apis:
                doc += f"### {api['method']} {api['path']}\n\n"
                doc += f"{api.get('description', '')}\n\n"
                
                if api.get('parameters'):
                    doc += "**Parameters:**\n"
                    for param in api['parameters']:
                        doc += f"- `{param['name']}` ({param['in']}): {param.get('description', '')}\n"
                    doc += "\n"
                
                if api.get('request_body'):
                    doc += "**Request Body:**\n"
                    doc += "```json\n"
                    doc += "{\n  // Request body schema\n}\n"
                    doc += "```\n\n"
                
                doc += "**Responses:**\n"
                for status, response in api.get('responses', {}).items():
                    doc += f"- {status}: {response.get('description', '')}\n"
                doc += "\n---\n\n"
        
        return doc
    
    def _generate_sdk_specs(self, apis: List[Dict]) -> Dict:
        """Generate SDK specifications"""
        return {
            'javascript': self._generate_js_sdk(apis),
            'python': self._generate_python_sdk(apis),
            'java': self._generate_java_sdk(apis)
        }
    
    def _generate_js_sdk(self, apis: List[Dict]) -> str:
        """Generate JavaScript SDK spec"""
        sdk = "// JavaScript SDK\n\n"
        sdk += "class APIClient {\n"
        
        for api in apis:
            operation_id = api.get('operationId', 'operation')
            sdk += f"  async {operation_id}(params) {{\n"
            sdk += f"    // {api.get('description', '')}\n"
            sdk += f"    return this.request('{api['method']}', '{api['path']}', params);\n"
            sdk += "  }\n\n"
        
        sdk += "}\n"
        
        return sdk
    
    def _generate_python_sdk(self, apis: List[Dict]) -> str:
        """Generate Python SDK spec"""
        sdk = "# Python SDK\n\n"
        sdk += "class APIClient:\n"
        
        for api in apis:
            operation_id = api.get('operationId', 'operation')
            sdk += f"    def {operation_id}(self, **params):\n"
            sdk += f"        \"\"\" {api.get('description', '')} \"\"\"\n"
            sdk += f"        return self.request('{api['method']}', '{api['path']}', params)\n\n"
        
        return sdk
    
    def _generate_java_sdk(self, apis: List[Dict]) -> str:
        """Generate Java SDK spec"""
        sdk = "// Java SDK\n\n"
        sdk += "public class APIClient {\n"
        
        for api in apis:
            operation_id = api.get('operationId', 'operation')
            sdk += f"    public Response {operation_id}(Map<String, Object> params) {{\n"
            sdk += f"        // {api.get('description', '')}\n"
            sdk += f"        return request(\"{api['method']}\", \"{api['path']}\", params);\n"
            sdk += "    }\n\n"
        
        sdk += "}\n"
        
        return sdk
    
    def _validate_apis(self, apis: List[Dict]) -> Dict:
        """Validate API specifications"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        paths = set()
        
        for api in apis:
            # Check for duplicate paths
            key = (api['method'], api['path'])
            if key in paths:
                validation['errors'].append(f"Duplicate API: {api['method']} {api['path']}")
            paths.add(key)
            
            # Check for missing descriptions
            if not api.get('description'):
                validation['warnings'].append(f"Missing description: {api['method']} {api['path']}")
            
            # Check for missing responses
            if not api.get('responses'):
                validation['warnings'].append(f"Missing responses: {api['method']} {api['path']}")
        
        validation['valid'] = len(validation['errors']) == 0
        
        return validation
    
    def _generate_test_cases(self, apis: List[Dict]) -> List[Dict]:
        """Generate test cases for APIs"""
        test_cases = []
        
        for api in apis:
            test_case = {
                'name': f"Test {api.get('operationId', api['path'])}",
                'method': api['method'],
                'path': api['path'],
                'tests': []
            }
            
            # Success test
            test_case['tests'].append({
                'name': 'Success case',
                'input': api.get('examples', {}).get('request', {}),
                'expected_status': 200 if api['method'] == 'GET' else 201,
                'expected_response': api.get('examples', {}).get('response', {})
            })
            
            # Error tests
            if api.get('parameters'):
                test_case['tests'].append({
                    'name': 'Missing required parameter',
                    'input': {},
                    'expected_status': 400
                })
            
            test_cases.append(test_case)
        
        return test_cases
    
    def _generate_gateway_config(self, apis: List[Dict]) -> Dict:
        """Generate API gateway configuration"""
        return {
            'routes': [
                {
                    'path': api['path'],
                    'method': api['method'],
                    'backend': 'http://backend-service',
                    'timeout': 30,
                    'rateLimit': api.get('rateLimit', {}),
                    'cache': api.get('cache', {}),
                    'authentication': api.get('authentication', {})
                }
                for api in apis
            ],
            'globalRateLimit': {
                'requests': 1000,
                'window': '1m'
            },
            'cors': {
                'enabled': True,
                'origins': ['*'],
                'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
            }
        }
    
    def _calculate_statistics(self, apis: List[Dict]) -> Dict:
        """Calculate API statistics"""
        method_counts = defaultdict(int)
        auth_types = defaultdict(int)
        
        for api in apis:
            method_counts[api['method']] += 1
            auth_type = api.get('authentication', {}).get('type', 'none')
            auth_types[auth_type] += 1
        
        return {
            'total_endpoints': len(apis),
            'by_method': dict(method_counts),
            'by_auth_type': dict(auth_types),
            'public_endpoints': auth_types.get('none', 0),
            'protected_endpoints': len(apis) - auth_types.get('none', 0)
        }