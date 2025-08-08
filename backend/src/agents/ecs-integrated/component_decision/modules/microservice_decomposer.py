"""
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
