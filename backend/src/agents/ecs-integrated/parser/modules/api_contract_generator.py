"""
API Contract Generator Module
Generates OpenAPI/Swagger specifications and GraphQL schemas
"""

from typing import Dict, Any, List, Optional
import json
import yaml

class APIContractGenerator:
    """Generates API contracts and specifications"""
    
    def __init__(self):
        self.openapi_version = "3.0.3"
        self.graphql_version = "June 2018"
    
    async def generate_openapi(
        self,
        requirements: Dict[str, Any],
        endpoints: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate OpenAPI specification"""
        
        spec = {
            "openapi": self.openapi_version,
            "info": {
                "title": requirements.get("project_name", "API"),
                "version": "1.0.0",
                "description": requirements.get("description", "")
            },
            "servers": [
                {"url": "https://api.example.com/v1"}
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {}
            }
        }
        
        for endpoint in endpoints:
            path = endpoint.get("path", "/")
            method = endpoint.get("method", "get").lower()
            
            if path not in spec["paths"]:
                spec["paths"][path] = {}
            
            spec["paths"][path][method] = {
                "summary": endpoint.get("summary", ""),
                "operationId": endpoint.get("operationId", f"{method}_{path.replace('/', '_')}"),
                "parameters": self._generate_parameters(endpoint),
                "requestBody": self._generate_request_body(endpoint),
                "responses": self._generate_responses(endpoint)
            }
        
        return spec
    
    async def generate_graphql_schema(
        self,
        requirements: Dict[str, Any],
        entities: List[Dict[str, Any]]
    ) -> str:
        """Generate GraphQL schema"""
        
        schema = []
        
        # Add types
        for entity in entities:
            schema.append(self._generate_graphql_type(entity))
        
        # Add queries
        schema.append(self._generate_graphql_queries(entities))
        
        # Add mutations
        schema.append(self._generate_graphql_mutations(entities))
        
        return "\n\n".join(schema)
    
    def _generate_parameters(self, endpoint: Dict) -> List[Dict]:
        """Generate OpenAPI parameters"""
        params = []
        
        for param in endpoint.get("parameters", []):
            params.append({
                "name": param["name"],
                "in": param.get("in", "query"),
                "required": param.get("required", False),
                "schema": {"type": param.get("type", "string")}
            })
        
        return params
    
    def _generate_request_body(self, endpoint: Dict) -> Optional[Dict]:
        """Generate request body specification"""
        
        if "requestBody" not in endpoint:
            return None
        
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": endpoint["requestBody"]
                }
            }
        }
    
    def _generate_responses(self, endpoint: Dict) -> Dict:
        """Generate response specifications"""
        
        return {
            "200": {
                "description": "Success",
                "content": {
                    "application/json": {
                        "schema": endpoint.get("responseSchema", {"type": "object"})
                    }
                }
            },
            "400": {"description": "Bad Request"},
            "401": {"description": "Unauthorized"},
            "500": {"description": "Internal Server Error"}
        }
    
    def _generate_graphql_type(self, entity: Dict) -> str:
        """Generate GraphQL type definition"""
        
        fields = []
        for field in entity.get("fields", []):
            field_def = f"  {field['name']}: {field['type']}"
            if field.get("required"):
                field_def += "!"
            fields.append(field_def)
        
        return f"""type {entity['name']} {{
{chr(10).join(fields)}
}}"""
    
    def _generate_graphql_queries(self, entities: List[Dict]) -> str:
        """Generate GraphQL queries"""
        
        queries = []
        for entity in entities:
            name = entity['name']
            queries.append(f"  get{name}(id: ID!): {name}")
            queries.append(f"  list{name}s(limit: Int, offset: Int): [{name}]")
        
        return f"""type Query {{
{chr(10).join(queries)}
}}"""
    
    def _generate_graphql_mutations(self, entities: List[Dict]) -> str:
        """Generate GraphQL mutations"""
        
        mutations = []
        for entity in entities:
            name = entity['name']
            mutations.append(f"  create{name}(input: {name}Input!): {name}")
            mutations.append(f"  update{name}(id: ID!, input: {name}Input!): {name}")
            mutations.append(f"  delete{name}(id: ID!): Boolean")
        
        return f"""type Mutation {{
{chr(10).join(mutations)}
}}"""
