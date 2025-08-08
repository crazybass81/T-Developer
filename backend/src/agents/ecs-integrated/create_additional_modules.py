#!/usr/bin/env python3
"""
Script to create additional recommended modules for all agents
"""

import os
from pathlib import Path

# Module definitions for each agent
MODULES = {
    "parser": {
        "api_contract_generator": '''"""
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
        
        return "\\n\\n".join(schema)
    
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
''',
        "database_schema_designer": '''"""
Database Schema Designer Module
Automatically designs database schemas with normalization
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

class NormalizationLevel(Enum):
    FIRST_NF = "1NF"
    SECOND_NF = "2NF"
    THIRD_NF = "3NF"
    BCNF = "BCNF"

class DatabaseSchemaDesigner:
    """Designs optimized database schemas"""
    
    def __init__(self):
        self.supported_databases = ["PostgreSQL", "MySQL", "MongoDB", "DynamoDB"]
        self.data_types = {
            "PostgreSQL": {
                "string": "VARCHAR",
                "text": "TEXT",
                "integer": "INTEGER",
                "decimal": "DECIMAL",
                "boolean": "BOOLEAN",
                "date": "DATE",
                "datetime": "TIMESTAMP",
                "json": "JSONB",
                "uuid": "UUID"
            },
            "MySQL": {
                "string": "VARCHAR",
                "text": "TEXT",
                "integer": "INT",
                "decimal": "DECIMAL",
                "boolean": "BOOLEAN",
                "date": "DATE",
                "datetime": "DATETIME",
                "json": "JSON",
                "uuid": "CHAR(36)"
            }
        }
    
    async def design_schema(
        self,
        entities: List[Dict[str, Any]],
        database_type: str,
        normalization_level: str = "3NF"
    ) -> Dict[str, Any]:
        """Design database schema"""
        
        # Analyze relationships
        relationships = self._analyze_relationships(entities)
        
        # Apply normalization
        normalized_entities = self._normalize_entities(
            entities,
            NormalizationLevel(normalization_level)
        )
        
        # Generate schema
        if database_type in ["PostgreSQL", "MySQL"]:
            schema = self._generate_sql_schema(normalized_entities, database_type)
        elif database_type == "MongoDB":
            schema = self._generate_nosql_schema(normalized_entities)
        else:
            schema = self._generate_dynamodb_schema(normalized_entities)
        
        # Add indexes
        indexes = self._recommend_indexes(normalized_entities, relationships)
        
        # Add constraints
        constraints = self._generate_constraints(normalized_entities, relationships)
        
        return {
            "database_type": database_type,
            "tables": schema,
            "relationships": relationships,
            "indexes": indexes,
            "constraints": constraints,
            "migrations": self._generate_migrations(schema)
        }
    
    def _analyze_relationships(self, entities: List[Dict]) -> List[Dict]:
        """Analyze entity relationships"""
        
        relationships = []
        
        for entity in entities:
            for field in entity.get("fields", []):
                if field.get("type") == "reference":
                    relationships.append({
                        "from": entity["name"],
                        "to": field["references"],
                        "type": field.get("relationship", "many-to-one"),
                        "field": field["name"]
                    })
        
        return relationships
    
    def _normalize_entities(
        self,
        entities: List[Dict],
        level: NormalizationLevel
    ) -> List[Dict]:
        """Apply database normalization"""
        
        normalized = entities.copy()
        
        if level.value >= "1NF":
            # Remove repeating groups
            normalized = self._apply_1nf(normalized)
        
        if level.value >= "2NF":
            # Remove partial dependencies
            normalized = self._apply_2nf(normalized)
        
        if level.value >= "3NF":
            # Remove transitive dependencies
            normalized = self._apply_3nf(normalized)
        
        return normalized
    
    def _apply_1nf(self, entities: List[Dict]) -> List[Dict]:
        """Apply First Normal Form"""
        
        result = []
        
        for entity in entities:
            # Check for multi-valued attributes
            new_entities = []
            modified_entity = entity.copy()
            
            for field in entity.get("fields", []):
                if field.get("multi_valued"):
                    # Create separate table for multi-valued attribute
                    new_entity = {
                        "name": f"{entity['name']}_{field['name']}",
                        "fields": [
                            {"name": f"{entity['name'].lower()}_id", "type": "reference"},
                            {"name": field['name'], "type": field['type']}
                        ]
                    }
                    new_entities.append(new_entity)
                    # Remove from original
                    modified_entity["fields"] = [
                        f for f in modified_entity["fields"]
                        if f["name"] != field["name"]
                    ]
            
            result.append(modified_entity)
            result.extend(new_entities)
        
        return result
    
    def _apply_2nf(self, entities: List[Dict]) -> List[Dict]:
        """Apply Second Normal Form"""
        # Implementation for 2NF
        return entities
    
    def _apply_3nf(self, entities: List[Dict]) -> List[Dict]:
        """Apply Third Normal Form"""
        # Implementation for 3NF
        return entities
    
    def _generate_sql_schema(
        self,
        entities: List[Dict],
        database_type: str
    ) -> List[Dict]:
        """Generate SQL schema"""
        
        tables = []
        data_types = self.data_types[database_type]
        
        for entity in entities:
            table = {
                "name": entity["name"].lower(),
                "columns": [],
                "primary_key": None
            }
            
            # Add ID column
            table["columns"].append({
                "name": "id",
                "type": data_types["uuid"],
                "nullable": False,
                "primary": True
            })
            table["primary_key"] = "id"
            
            # Add other columns
            for field in entity.get("fields", []):
                column = {
                    "name": field["name"].lower(),
                    "type": data_types.get(field["type"], "VARCHAR(255)"),
                    "nullable": not field.get("required", False)
                }
                
                if field.get("unique"):
                    column["unique"] = True
                
                table["columns"].append(column)
            
            # Add timestamps
            table["columns"].extend([
                {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                {"name": "updated_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
            ])
            
            tables.append(table)
        
        return tables
    
    def _generate_nosql_schema(self, entities: List[Dict]) -> List[Dict]:
        """Generate NoSQL schema"""
        
        collections = []
        
        for entity in entities:
            collection = {
                "name": entity["name"].lower(),
                "schema": {
                    "_id": "ObjectId",
                    "fields": {}
                },
                "indexes": []
            }
            
            for field in entity.get("fields", []):
                collection["schema"]["fields"][field["name"]] = {
                    "type": field["type"],
                    "required": field.get("required", False)
                }
            
            collections.append(collection)
        
        return collections
    
    def _generate_dynamodb_schema(self, entities: List[Dict]) -> List[Dict]:
        """Generate DynamoDB schema"""
        
        tables = []
        
        for entity in entities:
            table = {
                "name": entity["name"],
                "partition_key": "id",
                "sort_key": None,
                "attributes": [],
                "global_indexes": []
            }
            
            tables.append(table)
        
        return tables
    
    def _recommend_indexes(
        self,
        entities: List[Dict],
        relationships: List[Dict]
    ) -> List[Dict]:
        """Recommend database indexes"""
        
        indexes = []
        
        # Foreign key indexes
        for rel in relationships:
            indexes.append({
                "table": rel["from"].lower(),
                "column": rel["field"],
                "type": "btree",
                "reason": "Foreign key optimization"
            })
        
        # Unique constraint indexes
        for entity in entities:
            for field in entity.get("fields", []):
                if field.get("unique"):
                    indexes.append({
                        "table": entity["name"].lower(),
                        "column": field["name"],
                        "type": "unique",
                        "reason": "Unique constraint"
                    })
        
        return indexes
    
    def _generate_constraints(
        self,
        entities: List[Dict],
        relationships: List[Dict]
    ) -> List[Dict]:
        """Generate database constraints"""
        
        constraints = []
        
        # Foreign key constraints
        for rel in relationships:
            constraints.append({
                "type": "foreign_key",
                "table": rel["from"].lower(),
                "column": rel["field"],
                "references_table": rel["to"].lower(),
                "references_column": "id",
                "on_delete": "CASCADE",
                "on_update": "CASCADE"
            })
        
        # Check constraints
        for entity in entities:
            for field in entity.get("fields", []):
                if field.get("validation"):
                    constraints.append({
                        "type": "check",
                        "table": entity["name"].lower(),
                        "column": field["name"],
                        "condition": field["validation"]
                    })
        
        return constraints
    
    def _generate_migrations(self, schema: List[Dict]) -> List[str]:
        """Generate migration scripts"""
        
        migrations = []
        
        for table in schema:
            # Create table migration
            columns_sql = []
            for col in table["columns"]:
                col_sql = f"{col['name']} {col['type']}"
                if not col.get("nullable", True):
                    col_sql += " NOT NULL"
                if col.get("primary"):
                    col_sql += " PRIMARY KEY"
                columns_sql.append(col_sql)
            
            create_sql = f"""CREATE TABLE {table['name']} (
    {', '.join(columns_sql)}
);"""
            migrations.append(create_sql)
        
        return migrations
'''
    },
    "component_decision": {
        "design_pattern_selector": '''"""
Design Pattern Selector Module
Recommends design patterns based on project requirements
"""

from typing import Dict, Any, List, Optional
from enum import Enum

class ArchitecturePattern(Enum):
    MVC = "Model-View-Controller"
    MVP = "Model-View-Presenter"
    MVVM = "Model-View-ViewModel"
    CLEAN = "Clean Architecture"
    HEXAGONAL = "Hexagonal Architecture"
    MICROSERVICES = "Microservices"
    SERVERLESS = "Serverless"
    EVENT_DRIVEN = "Event-Driven"

class DesignPatternSelector:
    """Selects appropriate design patterns"""
    
    def __init__(self):
        self.patterns = {
            ArchitecturePattern.MVC: {
                "use_cases": ["web_apps", "traditional_apps"],
                "pros": ["Simple", "Well-known", "Good separation"],
                "cons": ["Can become complex", "Tight coupling possible"],
                "complexity": "low",
                "scalability": "medium"
            },
            ArchitecturePattern.CLEAN: {
                "use_cases": ["enterprise", "complex_domains"],
                "pros": ["Testable", "Independent of frameworks", "Flexible"],
                "cons": ["Complex", "More code", "Learning curve"],
                "complexity": "high",
                "scalability": "high"
            },
            ArchitecturePattern.MICROSERVICES: {
                "use_cases": ["large_scale", "multiple_teams"],
                "pros": ["Independent deployment", "Technology diversity", "Scalable"],
                "cons": ["Complex", "Network overhead", "Data consistency"],
                "complexity": "very_high",
                "scalability": "very_high"
            }
        }
        
        self.design_patterns = {
            "creational": ["Singleton", "Factory", "Builder", "Prototype"],
            "structural": ["Adapter", "Decorator", "Facade", "Proxy"],
            "behavioral": ["Observer", "Strategy", "Command", "Iterator"]
        }
    
    async def select_architecture(
        self,
        requirements: Dict[str, Any],
        constraints: List[str]
    ) -> Dict[str, Any]:
        """Select architecture pattern"""
        
        # Analyze requirements
        scores = {}
        
        for pattern, config in self.patterns.items():
            score = self._calculate_pattern_score(pattern, requirements, constraints)
            scores[pattern] = score
        
        # Select best pattern
        best_pattern = max(scores.items(), key=lambda x: x[1])
        
        # Get implementation details
        implementation = self._get_implementation_guide(best_pattern[0], requirements)
        
        # Recommend specific design patterns
        recommended_patterns = self._recommend_design_patterns(
            best_pattern[0],
            requirements
        )
        
        return {
            "architecture": best_pattern[0].value,
            "confidence": best_pattern[1],
            "implementation": implementation,
            "design_patterns": recommended_patterns,
            "folder_structure": self._generate_folder_structure(best_pattern[0]),
            "boilerplate": self._generate_boilerplate(best_pattern[0])
        }
    
    def _calculate_pattern_score(
        self,
        pattern: ArchitecturePattern,
        requirements: Dict,
        constraints: List[str]
    ) -> float:
        """Calculate pattern suitability score"""
        
        score = 0.5  # Base score
        config = self.patterns[pattern]
        
        # Check use cases
        project_type = requirements.get("project_type", "")
        if project_type in config["use_cases"]:
            score += 0.2
        
        # Check scalability requirements
        if requirements.get("scalability") == "high":
            if config["scalability"] in ["high", "very_high"]:
                score += 0.15
        
        # Check complexity tolerance
        team_size = requirements.get("team_size", 1)
        if team_size > 5 and config["complexity"] in ["high", "very_high"]:
            score += 0.1
        elif team_size <= 2 and config["complexity"] == "low":
            score += 0.15
        
        # Check constraints
        for constraint in constraints:
            if "simple" in constraint.lower() and config["complexity"] == "low":
                score += 0.1
            elif "enterprise" in constraint.lower() and pattern == ArchitecturePattern.CLEAN:
                score += 0.2
        
        return min(score, 1.0)
    
    def _get_implementation_guide(
        self,
        pattern: ArchitecturePattern,
        requirements: Dict
    ) -> Dict[str, Any]:
        """Get implementation guide for pattern"""
        
        guides = {
            ArchitecturePattern.CLEAN: {
                "layers": [
                    {"name": "Domain", "responsibility": "Business logic and entities"},
                    {"name": "Application", "responsibility": "Use cases and application logic"},
                    {"name": "Infrastructure", "responsibility": "External services and frameworks"},
                    {"name": "Presentation", "responsibility": "UI and API endpoints"}
                ],
                "dependencies": "Inner layers don't depend on outer layers",
                "testing": "Test each layer independently"
            },
            ArchitecturePattern.MICROSERVICES: {
                "services": self._identify_service_boundaries(requirements),
                "communication": "REST or gRPC for sync, Message Queue for async",
                "data": "Database per service pattern",
                "deployment": "Container orchestration with Kubernetes"
            }
        }
        
        return guides.get(pattern, {})
    
    def _recommend_design_patterns(
        self,
        architecture: ArchitecturePattern,
        requirements: Dict
    ) -> Dict[str, List[str]]:
        """Recommend specific design patterns"""
        
        patterns = {
            "creational": [],
            "structural": [],
            "behavioral": []
        }
        
        # Recommend based on requirements
        if requirements.get("multi_tenant"):
            patterns["creational"].append("Factory")
            patterns["structural"].append("Proxy")
        
        if requirements.get("real_time"):
            patterns["behavioral"].append("Observer")
            patterns["behavioral"].append("Pub-Sub")
        
        if requirements.get("complex_workflows"):
            patterns["behavioral"].append("State Machine")
            patterns["behavioral"].append("Chain of Responsibility")
        
        if requirements.get("caching"):
            patterns["structural"].append("Proxy")
            patterns["creational"].append("Singleton")
        
        return patterns
    
    def _generate_folder_structure(self, pattern: ArchitecturePattern) -> Dict[str, str]:
        """Generate folder structure for pattern"""
        
        if pattern == ArchitecturePattern.CLEAN:
            return {
                "src/domain/": "Entities and business rules",
                "src/application/": "Use cases and DTOs",
                "src/infrastructure/": "Database, external services",
                "src/presentation/": "Controllers, views",
                "tests/unit/": "Unit tests for each layer",
                "tests/integration/": "Integration tests"
            }
        elif pattern == ArchitecturePattern.MVC:
            return {
                "src/models/": "Data models and business logic",
                "src/views/": "UI templates and components",
                "src/controllers/": "Request handlers",
                "src/routes/": "Route definitions",
                "src/services/": "Business services",
                "src/utils/": "Utility functions"
            }
        else:
            return {}
    
    def _generate_boilerplate(self, pattern: ArchitecturePattern) -> Dict[str, str]:
        """Generate boilerplate code for pattern"""
        
        # Return code templates for the pattern
        return {}
    
    def _identify_service_boundaries(self, requirements: Dict) -> List[Dict]:
        """Identify microservice boundaries"""
        
        services = []
        
        # Analyze domain entities
        entities = requirements.get("entities", [])
        
        # Group related entities into services
        # This is a simplified example
        if "user" in str(entities).lower():
            services.append({
                "name": "user-service",
                "responsibilities": ["User management", "Authentication"]
            })
        
        if "product" in str(entities).lower():
            services.append({
                "name": "product-service",
                "responsibilities": ["Product catalog", "Inventory"]
            })
        
        if "order" in str(entities).lower():
            services.append({
                "name": "order-service",
                "responsibilities": ["Order processing", "Payment"]
            })
        
        return services
''',
        "microservice_decomposer": '''"""
Microservice Decomposer Module
Identifies service boundaries and communication strategies
"""

from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

class DecompositionStrategy(Enum):
    DOMAIN_DRIVEN = "domain_driven"
    BUSINESS_CAPABILITY = "business_capability"
    SUBDOMAIN = "subdomain"
    DATA_DRIVEN = "data_driven"

class CommunicationPattern(Enum):
    SYNC_REST = "sync_rest"
    SYNC_GRPC = "sync_grpc"
    ASYNC_MESSAGING = "async_messaging"
    EVENT_STREAMING = "event_streaming"

class MicroserviceDecomposer:
    """Decomposes monolith into microservices"""
    
    def __init__(self):
        self.min_service_size = 3  # Minimum entities per service
        self.max_service_size = 10  # Maximum entities per service
    
    async def decompose(
        self,
        entities: List[Dict[str, Any]],
        requirements: Dict[str, Any],
        strategy: DecompositionStrategy = DecompositionStrategy.DOMAIN_DRIVEN
    ) -> Dict[str, Any]:
        """Decompose into microservices"""
        
        # Analyze relationships
        relationships = self._analyze_entity_relationships(entities)
        
        # Identify boundaries
        if strategy == DecompositionStrategy.DOMAIN_DRIVEN:
            services = self._domain_driven_decomposition(entities, relationships)
        elif strategy == DecompositionStrategy.BUSINESS_CAPABILITY:
            services = self._capability_driven_decomposition(entities, requirements)
        else:
            services = self._data_driven_decomposition(entities, relationships)
        
        # Define communication
        communication = self._define_communication_patterns(services, relationships)
        
        # Create service contracts
        contracts = self._create_service_contracts(services, communication)
        
        # Generate deployment config
        deployment = self._generate_deployment_config(services, requirements)
        
        return {
            "services": services,
            "communication": communication,
            "contracts": contracts,
            "deployment": deployment,
            "data_management": self._define_data_management(services),
            "saga_patterns": self._identify_saga_patterns(services, relationships)
        }
    
    def _analyze_entity_relationships(
        self,
        entities: List[Dict]
    ) -> Dict[str, List[str]]:
        """Analyze relationships between entities"""
        
        relationships = {}
        
        for entity in entities:
            entity_name = entity["name"]
            relationships[entity_name] = []
            
            for field in entity.get("fields", []):
                if field.get("type") == "reference":
                    relationships[entity_name].append(field["references"])
        
        return relationships
    
    def _domain_driven_decomposition(
        self,
        entities: List[Dict],
        relationships: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Decompose using Domain-Driven Design"""
        
        services = []
        assigned_entities = set()
        
        # Identify aggregates
        aggregates = self._identify_aggregates(entities, relationships)
        
        for aggregate_root, aggregate_entities in aggregates.items():
            if aggregate_root not in assigned_entities:
                service = {
                    "name": f"{aggregate_root.lower()}-service",
                    "entities": aggregate_entities,
                    "aggregate_root": aggregate_root,
                    "bounded_context": self._identify_bounded_context(aggregate_root),
                    "capabilities": self._identify_capabilities(aggregate_entities),
                    "api_endpoints": [],
                    "events": []
                }
                
                # Mark entities as assigned
                assigned_entities.update(aggregate_entities)
                
                services.append(service)
        
        return services
    
    def _capability_driven_decomposition(
        self,
        entities: List[Dict],
        requirements: Dict
    ) -> List[Dict[str, Any]]:
        """Decompose by business capabilities"""
        
        capabilities = {
            "user_management": ["User", "Profile", "Role", "Permission"],
            "product_catalog": ["Product", "Category", "Brand", "Review"],
            "order_management": ["Order", "OrderItem", "Cart", "Checkout"],
            "payment_processing": ["Payment", "Transaction", "Invoice", "Refund"],
            "inventory": ["Stock", "Warehouse", "Supplier", "PurchaseOrder"],
            "shipping": ["Shipment", "Tracking", "Carrier", "Address"],
            "notification": ["Notification", "Template", "Channel", "Preference"],
            "reporting": ["Report", "Analytics", "Dashboard", "Metric"]
        }
        
        services = []
        
        for capability, related_entities in capabilities.items():
            service_entities = [
                e for e in entities
                if any(re in e["name"] for re in related_entities)
            ]
            
            if service_entities:
                services.append({
                    "name": capability.replace("_", "-"),
                    "entities": [e["name"] for e in service_entities],
                    "capability": capability,
                    "responsibilities": self._define_responsibilities(capability)
                })
        
        return services
    
    def _data_driven_decomposition(
        self,
        entities: List[Dict],
        relationships: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """Decompose based on data relationships"""
        
        # Group entities with strong relationships
        clusters = self._cluster_entities(entities, relationships)
        
        services = []
        for i, cluster in enumerate(clusters):
            services.append({
                "name": f"service-{i+1}",
                "entities": cluster,
                "data_ownership": "exclusive",
                "consistency": "eventual" if len(cluster) > 5 else "strong"
            })
        
        return services
    
    def _identify_aggregates(
        self,
        entities: List[Dict],
        relationships: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Identify DDD aggregates"""
        
        aggregates = {}
        
        for entity in entities:
            entity_name = entity["name"]
            
            # Check if entity is an aggregate root
            if self._is_aggregate_root(entity, relationships):
                # Find entities within the aggregate boundary
                aggregate_entities = [entity_name]
                aggregate_entities.extend(
                    self._find_aggregate_members(entity_name, relationships)
                )
                aggregates[entity_name] = aggregate_entities
        
        return aggregates
    
    def _is_aggregate_root(
        self,
        entity: Dict,
        relationships: Dict[str, List[str]]
    ) -> bool:
        """Check if entity is an aggregate root"""
        
        # Heuristics for aggregate root
        # 1. Has identity
        # 2. Referenced by other entities
        # 3. Contains business logic
        
        entity_name = entity["name"]
        
        # Check if referenced by others
        referenced_by = sum(
            1 for refs in relationships.values()
            if entity_name in refs
        )
        
        return referenced_by > 0 or "id" in str(entity.get("fields", []))
    
    def _find_aggregate_members(
        self,
        root: str,
        relationships: Dict[str, List[str]]
    ) -> List[str]:
        """Find entities that belong to an aggregate"""
        
        members = []
        
        # Find directly owned entities
        if root in relationships:
            for related in relationships[root]:
                # Check for composition relationship
                if self._is_composition(root, related):
                    members.append(related)
        
        return members
    
    def _is_composition(self, parent: str, child: str) -> bool:
        """Check if relationship is composition"""
        
        # Simplified check - in real implementation would analyze cardinality
        return child.startswith(parent) or child.endswith("Item")
    
    def _identify_bounded_context(self, aggregate_root: str) -> str:
        """Identify bounded context for aggregate"""
        
        contexts = {
            "User": "identity",
            "Product": "catalog",
            "Order": "sales",
            "Payment": "billing",
            "Inventory": "warehouse",
            "Customer": "crm"
        }
        
        return contexts.get(aggregate_root, "core")
    
    def _identify_capabilities(self, entities: List[str]) -> List[str]:
        """Identify business capabilities"""
        
        capabilities = []
        
        for entity in entities:
            if "User" in entity:
                capabilities.extend(["authentication", "authorization"])
            if "Product" in entity:
                capabilities.extend(["catalog_management", "search"])
            if "Order" in entity:
                capabilities.extend(["order_processing", "fulfillment"])
        
        return list(set(capabilities))
    
    def _define_communication_patterns(
        self,
        services: List[Dict],
        relationships: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Define communication patterns between services"""
        
        patterns = {
            "synchronous": [],
            "asynchronous": [],
            "event_driven": []
        }
        
        for i, service1 in enumerate(services):
            for j, service2 in enumerate(services):
                if i != j:
                    # Check if services need to communicate
                    if self._services_communicate(service1, service2, relationships):
                        comm_type = self._determine_communication_type(
                            service1,
                            service2
                        )
                        
                        pattern = {
                            "from": service1["name"],
                            "to": service2["name"],
                            "type": comm_type,
                            "protocol": self._select_protocol(comm_type)
                        }
                        
                        if comm_type == "sync":
                            patterns["synchronous"].append(pattern)
                        elif comm_type == "async":
                            patterns["asynchronous"].append(pattern)
                        else:
                            patterns["event_driven"].append(pattern)
        
        return patterns
    
    def _services_communicate(
        self,
        service1: Dict,
        service2: Dict,
        relationships: Dict
    ) -> bool:
        """Check if two services need to communicate"""
        
        # Check if entities in service1 reference entities in service2
        for entity1 in service1.get("entities", []):
            if entity1 in relationships:
                for entity2 in service2.get("entities", []):
                    if entity2 in relationships[entity1]:
                        return True
        
        return False
    
    def _determine_communication_type(
        self,
        service1: Dict,
        service2: Dict
    ) -> str:
        """Determine communication type between services"""
        
        # Use heuristics to determine communication pattern
        if "payment" in service1["name"] or "payment" in service2["name"]:
            return "sync"  # Payment requires synchronous
        elif "notification" in service1["name"] or "notification" in service2["name"]:
            return "async"  # Notifications are async
        elif "analytics" in service1["name"] or "analytics" in service2["name"]:
            return "event"  # Analytics use events
        else:
            return "sync"  # Default to synchronous
    
    def _select_protocol(self, comm_type: str) -> str:
        """Select communication protocol"""
        
        if comm_type == "sync":
            return "REST"
        elif comm_type == "async":
            return "AMQP"
        else:
            return "Kafka"
    
    def _create_service_contracts(
        self,
        services: List[Dict],
        communication: Dict
    ) -> List[Dict]:
        """Create service contracts"""
        
        contracts = []
        
        for pattern in communication.get("synchronous", []):
            contract = {
                "consumer": pattern["from"],
                "provider": pattern["to"],
                "protocol": pattern["protocol"],
                "endpoints": self._generate_endpoints(pattern["to"]),
                "sla": {
                    "availability": "99.9%",
                    "response_time": "< 500ms",
                    "rate_limit": "1000 req/min"
                }
            }
            contracts.append(contract)
        
        return contracts
    
    def _generate_endpoints(self, service_name: str) -> List[Dict]:
        """Generate API endpoints for service"""
        
        base_path = f"/api/{service_name.replace('-service', '')}"
        
        return [
            {"method": "GET", "path": f"{base_path}", "description": "List all"},
            {"method": "GET", "path": f"{base_path}/{{id}}", "description": "Get by ID"},
            {"method": "POST", "path": f"{base_path}", "description": "Create new"},
            {"method": "PUT", "path": f"{base_path}/{{id}}", "description": "Update"},
            {"method": "DELETE", "path": f"{base_path}/{{id}}", "description": "Delete"}
        ]
    
    def _generate_deployment_config(
        self,
        services: List[Dict],
        requirements: Dict
    ) -> Dict[str, Any]:
        """Generate deployment configuration"""
        
        return {
            "orchestrator": "Kubernetes",
            "services": [
                {
                    "name": service["name"],
                    "replicas": self._calculate_replicas(service, requirements),
                    "resources": self._calculate_resources(service),
                    "health_check": f"/health",
                    "environment": "production"
                }
                for service in services
            ],
            "infrastructure": {
                "service_mesh": "Istio",
                "api_gateway": "Kong",
                "message_broker": "RabbitMQ",
                "event_streaming": "Kafka"
            }
        }
    
    def _calculate_replicas(self, service: Dict, requirements: Dict) -> int:
        """Calculate number of replicas for service"""
        
        base_replicas = 2
        
        if requirements.get("high_availability"):
            base_replicas = 3
        
        if "payment" in service["name"] or "order" in service["name"]:
            base_replicas += 1
        
        return base_replicas
    
    def _calculate_resources(self, service: Dict) -> Dict[str, str]:
        """Calculate resource requirements"""
        
        entity_count = len(service.get("entities", []))
        
        if entity_count > 5:
            return {"cpu": "1000m", "memory": "1Gi"}
        elif entity_count > 2:
            return {"cpu": "500m", "memory": "512Mi"}
        else:
            return {"cpu": "250m", "memory": "256Mi"}
    
    def _define_data_management(self, services: List[Dict]) -> Dict[str, Any]:
        """Define data management strategy"""
        
        return {
            "pattern": "Database per Service",
            "consistency": "Eventual Consistency",
            "transactions": "Saga Pattern",
            "caching": "Redis per Service",
            "backup": "Daily snapshots"
        }
    
    def _identify_saga_patterns(
        self,
        services: List[Dict],
        relationships: Dict
    ) -> List[Dict]:
        """Identify saga patterns for distributed transactions"""
        
        sagas = []
        
        # Order processing saga
        if any("order" in s["name"] for s in services):
            sagas.append({
                "name": "OrderProcessingSaga",
                "steps": [
                    {"service": "order-service", "action": "CreateOrder"},
                    {"service": "inventory-service", "action": "ReserveItems"},
                    {"service": "payment-service", "action": "ProcessPayment"},
                    {"service": "shipping-service", "action": "CreateShipment"}
                ],
                "compensation": [
                    {"service": "shipping-service", "action": "CancelShipment"},
                    {"service": "payment-service", "action": "RefundPayment"},
                    {"service": "inventory-service", "action": "ReleaseItems"},
                    {"service": "order-service", "action": "CancelOrder"}
                ]
            })
        
        return sagas
    
    def _cluster_entities(
        self,
        entities: List[Dict],
        relationships: Dict[str, List[str]]
    ) -> List[List[str]]:
        """Cluster entities based on relationships"""
        
        # Simple clustering algorithm
        clusters = []
        assigned = set()
        
        for entity in entities:
            if entity["name"] not in assigned:
                cluster = [entity["name"]]
                assigned.add(entity["name"])
                
                # Add related entities
                if entity["name"] in relationships:
                    for related in relationships[entity["name"]]:
                        if related not in assigned and len(cluster) < self.max_service_size:
                            cluster.append(related)
                            assigned.add(related)
                
                clusters.append(cluster)
        
        return clusters
    
    def _define_responsibilities(self, capability: str) -> List[str]:
        """Define service responsibilities"""
        
        responsibilities = {
            "user_management": [
                "User registration and authentication",
                "Profile management",
                "Role and permission management"
            ],
            "product_catalog": [
                "Product information management",
                "Category and brand management",
                "Search and filtering"
            ],
            "order_management": [
                "Order creation and processing",
                "Cart management",
                "Order status tracking"
            ]
        }
        
        return responsibilities.get(capability, [])
'''
    }
}

def create_modules():
    """Create all additional modules"""
    
    base_path = Path("/home/ec2-user/T-DeveloperMVP/backend/src/agents/ecs-integrated")
    
    created_count = 0
    
    for agent_name, modules in MODULES.items():
        agent_dir = base_path / agent_name / "modules"
        
        for module_name, module_content in modules.items():
            module_file = agent_dir / f"{module_name}.py"
            
            if not module_file.exists():
                module_file.write_text(module_content)
                print(f"✅ Created {agent_name}/{module_name}.py")
                created_count += 1
            else:
                print(f"⏭️  Skipped {agent_name}/{module_name}.py (already exists)")
    
    print(f"\n🎉 Created {created_count} new modules!")

if __name__ == "__main__":
    create_modules()