"""
Design Pattern Selector Module
Selects appropriate design patterns based on requirements
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class PatternCategory(Enum):
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    ARCHITECTURAL = "architectural"
    CONCURRENCY = "concurrency"
    MESSAGING = "messaging"


class DesignPatternSelector:
    """Selects appropriate design patterns"""

    def __init__(self):
        self.pattern_catalog = self._build_pattern_catalog()
        self.pattern_relationships = self._build_pattern_relationships()

    async def select(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select design patterns based on requirements"""

        patterns = []

        # Analyze requirements for pattern indicators
        indicators = self._analyze_pattern_indicators(requirements)

        # Select creational patterns
        creational = self._select_creational_patterns(indicators)
        patterns.extend(creational)

        # Select structural patterns
        structural = self._select_structural_patterns(indicators)
        patterns.extend(structural)

        # Select behavioral patterns
        behavioral = self._select_behavioral_patterns(indicators)
        patterns.extend(behavioral)

        # Select architectural patterns
        architectural = self._select_architectural_patterns(indicators)
        patterns.extend(architectural)

        # Select concurrency patterns
        if indicators.get("concurrent_processing"):
            concurrency = self._select_concurrency_patterns(indicators)
            patterns.extend(concurrency)

        # Select messaging patterns
        if indicators.get("async_communication"):
            messaging = self._select_messaging_patterns(indicators)
            patterns.extend(messaging)

        # Resolve pattern conflicts
        patterns = self._resolve_conflicts(patterns)

        # Add implementation details
        for pattern in patterns:
            pattern["implementation"] = self._generate_implementation_guide(pattern)
            pattern["examples"] = self._provide_examples(pattern)
            pattern["considerations"] = self._get_considerations(pattern)

        return patterns

    def _analyze_pattern_indicators(self, requirements: Dict) -> Dict:
        """Analyze requirements for pattern indicators"""

        text = str(requirements).lower()

        indicators = {
            "object_creation": "create" in text or "instantiate" in text,
            "single_instance": "singleton" in text or "single instance" in text,
            "object_families": "family" in text or "related objects" in text,
            "complex_construction": "complex" in text or "step-by-step" in text,
            "interface_adaptation": "adapt" in text or "wrapper" in text,
            "object_composition": "compose" in text or "tree structure" in text,
            "functionality_extension": "extend" in text or "decorate" in text,
            "subsystem_simplification": "simplify" in text or "facade" in text,
            "algorithm_family": "algorithm" in text or "strategy" in text,
            "state_dependent": "state" in text or "behavior change" in text,
            "one_to_many": "notify" in text or "observe" in text,
            "request_handling": "chain" in text or "responsibility" in text,
            "concurrent_processing": "concurrent" in text or "parallel" in text,
            "async_communication": "async" in text or "message" in text,
            "distributed_system": "distributed" in text or "microservice" in text,
            "event_driven": "event" in text or "reactive" in text,
            "caching_needed": "cache" in text or "performance" in text,
            "transaction_support": "transaction" in text or "atomic" in text,
        }

        return indicators

    def _select_creational_patterns(self, indicators: Dict) -> List[Dict]:
        """Select creational design patterns"""
        patterns = []

        if indicators.get("single_instance"):
            patterns.append(
                {
                    "type": "Singleton",
                    "category": PatternCategory.CREATIONAL.value,
                    "purpose": "Ensure single instance of a class",
                    "use_case": "Database connections, Configuration managers",
                    "priority": 8,
                }
            )

        if indicators.get("object_families"):
            patterns.append(
                {
                    "type": "Abstract Factory",
                    "category": PatternCategory.CREATIONAL.value,
                    "purpose": "Create families of related objects",
                    "use_case": "UI component factories, Database driver factories",
                    "priority": 7,
                }
            )

        if indicators.get("complex_construction"):
            patterns.append(
                {
                    "type": "Builder",
                    "category": PatternCategory.CREATIONAL.value,
                    "purpose": "Construct complex objects step by step",
                    "use_case": "Configuration builders, Query builders",
                    "priority": 7,
                }
            )

        if indicators.get("object_creation"):
            patterns.append(
                {
                    "type": "Factory Method",
                    "category": PatternCategory.CREATIONAL.value,
                    "purpose": "Define interface for creating objects",
                    "use_case": "Service factories, Parser factories",
                    "priority": 8,
                }
            )

        return patterns

    def _select_structural_patterns(self, indicators: Dict) -> List[Dict]:
        """Select structural design patterns"""
        patterns = []

        if indicators.get("interface_adaptation"):
            patterns.append(
                {
                    "type": "Adapter",
                    "category": PatternCategory.STRUCTURAL.value,
                    "purpose": "Convert interface to another interface",
                    "use_case": "Third-party library integration",
                    "priority": 8,
                }
            )

        if indicators.get("object_composition"):
            patterns.append(
                {
                    "type": "Composite",
                    "category": PatternCategory.STRUCTURAL.value,
                    "purpose": "Compose objects into tree structures",
                    "use_case": "Menu systems, Organization charts",
                    "priority": 6,
                }
            )

        if indicators.get("functionality_extension"):
            patterns.append(
                {
                    "type": "Decorator",
                    "category": PatternCategory.STRUCTURAL.value,
                    "purpose": "Add new functionality dynamically",
                    "use_case": "Middleware, Feature toggles",
                    "priority": 7,
                }
            )

        if indicators.get("subsystem_simplification"):
            patterns.append(
                {
                    "type": "Facade",
                    "category": PatternCategory.STRUCTURAL.value,
                    "purpose": "Provide simplified interface to subsystem",
                    "use_case": "API gateways, Service wrappers",
                    "priority": 8,
                }
            )

        if indicators.get("caching_needed"):
            patterns.append(
                {
                    "type": "Proxy",
                    "category": PatternCategory.STRUCTURAL.value,
                    "purpose": "Provide placeholder for another object",
                    "use_case": "Lazy loading, Caching proxy",
                    "priority": 7,
                }
            )

        return patterns

    def _select_behavioral_patterns(self, indicators: Dict) -> List[Dict]:
        """Select behavioral design patterns"""
        patterns = []

        if indicators.get("algorithm_family"):
            patterns.append(
                {
                    "type": "Strategy",
                    "category": PatternCategory.BEHAVIORAL.value,
                    "purpose": "Define family of algorithms",
                    "use_case": "Payment processing, Sorting algorithms",
                    "priority": 8,
                }
            )

        if indicators.get("state_dependent"):
            patterns.append(
                {
                    "type": "State",
                    "category": PatternCategory.BEHAVIORAL.value,
                    "purpose": "Change behavior based on state",
                    "use_case": "Order processing, User sessions",
                    "priority": 7,
                }
            )

        if indicators.get("one_to_many"):
            patterns.append(
                {
                    "type": "Observer",
                    "category": PatternCategory.BEHAVIORAL.value,
                    "purpose": "Define one-to-many dependency",
                    "use_case": "Event systems, Model-View patterns",
                    "priority": 9,
                }
            )

        if indicators.get("request_handling"):
            patterns.append(
                {
                    "type": "Chain of Responsibility",
                    "category": PatternCategory.BEHAVIORAL.value,
                    "purpose": "Pass requests along chain of handlers",
                    "use_case": "Middleware chains, Validation pipelines",
                    "priority": 7,
                }
            )

        patterns.append(
            {
                "type": "Command",
                "category": PatternCategory.BEHAVIORAL.value,
                "purpose": "Encapsulate request as object",
                "use_case": "Undo/Redo, Queued operations",
                "priority": 6,
            }
        )

        return patterns

    def _select_architectural_patterns(self, indicators: Dict) -> List[Dict]:
        """Select architectural patterns"""
        patterns = []

        if indicators.get("distributed_system"):
            patterns.append(
                {
                    "type": "Service-Oriented Architecture",
                    "category": PatternCategory.ARCHITECTURAL.value,
                    "purpose": "Organize system as services",
                    "use_case": "Microservices, API-first design",
                    "priority": 9,
                }
            )

        patterns.append(
            {
                "type": "Repository",
                "category": PatternCategory.ARCHITECTURAL.value,
                "purpose": "Encapsulate data access logic",
                "use_case": "Data access layer, ORM abstraction",
                "priority": 8,
            }
        )

        patterns.append(
            {
                "type": "Dependency Injection",
                "category": PatternCategory.ARCHITECTURAL.value,
                "purpose": "Inject dependencies at runtime",
                "use_case": "IoC containers, Testing",
                "priority": 9,
            }
        )

        if indicators.get("event_driven"):
            patterns.append(
                {
                    "type": "Event Sourcing",
                    "category": PatternCategory.ARCHITECTURAL.value,
                    "purpose": "Store events instead of state",
                    "use_case": "Audit logs, Time travel debugging",
                    "priority": 7,
                }
            )

            patterns.append(
                {
                    "type": "CQRS",
                    "category": PatternCategory.ARCHITECTURAL.value,
                    "purpose": "Separate read and write models",
                    "use_case": "Complex domains, Performance optimization",
                    "priority": 7,
                }
            )

        return patterns

    def _select_concurrency_patterns(self, indicators: Dict) -> List[Dict]:
        """Select concurrency patterns"""
        patterns = []

        patterns.append(
            {
                "type": "Thread Pool",
                "category": PatternCategory.CONCURRENCY.value,
                "purpose": "Manage pool of worker threads",
                "use_case": "Request handling, Batch processing",
                "priority": 8,
            }
        )

        patterns.append(
            {
                "type": "Producer-Consumer",
                "category": PatternCategory.CONCURRENCY.value,
                "purpose": "Decouple production from consumption",
                "use_case": "Queue processing, Data pipelines",
                "priority": 8,
            }
        )

        if indicators.get("transaction_support"):
            patterns.append(
                {
                    "type": "Two-Phase Commit",
                    "category": PatternCategory.CONCURRENCY.value,
                    "purpose": "Coordinate distributed transactions",
                    "use_case": "Distributed databases, Microservices",
                    "priority": 7,
                }
            )

        patterns.append(
            {
                "type": "Circuit Breaker",
                "category": PatternCategory.CONCURRENCY.value,
                "purpose": "Prevent cascading failures",
                "use_case": "Service calls, External APIs",
                "priority": 9,
            }
        )

        return patterns

    def _select_messaging_patterns(self, indicators: Dict) -> List[Dict]:
        """Select messaging patterns"""
        patterns = []

        patterns.append(
            {
                "type": "Publish-Subscribe",
                "category": PatternCategory.MESSAGING.value,
                "purpose": "Broadcast messages to subscribers",
                "use_case": "Event bus, Notifications",
                "priority": 8,
            }
        )

        patterns.append(
            {
                "type": "Message Queue",
                "category": PatternCategory.MESSAGING.value,
                "purpose": "Asynchronous message processing",
                "use_case": "Task queues, Email sending",
                "priority": 8,
            }
        )

        if indicators.get("distributed_system"):
            patterns.append(
                {
                    "type": "Saga",
                    "category": PatternCategory.MESSAGING.value,
                    "purpose": "Manage distributed transactions",
                    "use_case": "Order processing, Workflow orchestration",
                    "priority": 7,
                }
            )

        patterns.append(
            {
                "type": "Request-Reply",
                "category": PatternCategory.MESSAGING.value,
                "purpose": "Synchronous messaging pattern",
                "use_case": "RPC calls, Service communication",
                "priority": 6,
            }
        )

        return patterns

    def _resolve_conflicts(self, patterns: List[Dict]) -> List[Dict]:
        """Resolve conflicting patterns"""
        resolved = []
        seen_purposes = set()

        # Remove duplicate patterns with same purpose
        for pattern in sorted(patterns, key=lambda x: x.get("priority", 0), reverse=True):
            purpose_key = f"{pattern['category']}_{pattern['purpose']}"
            if purpose_key not in seen_purposes:
                resolved.append(pattern)
                seen_purposes.add(purpose_key)

        # Check for incompatible patterns
        incompatible_pairs = [
            ("Singleton", "Dependency Injection"),
            ("Two-Phase Commit", "Saga"),
        ]

        pattern_types = {p["type"] for p in resolved}
        for pair in incompatible_pairs:
            if pair[0] in pattern_types and pair[1] in pattern_types:
                # Keep the one with higher priority
                resolved = [
                    p
                    for p in resolved
                    if not (
                        p["type"] == pair[1]
                        and any(
                            p2["type"] == pair[0] and p2.get("priority", 0) > p.get("priority", 0)
                            for p2 in resolved
                        )
                    )
                ]

        return resolved

    def _generate_implementation_guide(self, pattern: Dict) -> Dict:
        """Generate implementation guide for pattern"""

        guides = {
            "Singleton": {
                "steps": [
                    "Make constructor private",
                    "Create static instance variable",
                    "Provide static getInstance method",
                    "Handle thread safety",
                ],
                "code_template": """
class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
""",
            },
            "Repository": {
                "steps": [
                    "Define repository interface",
                    "Implement concrete repository",
                    "Abstract data access logic",
                    "Use dependency injection",
                ],
                "code_template": """
class IRepository:
    def get(self, id): pass
    def save(self, entity): pass
    def delete(self, id): pass

class UserRepository(IRepository):
    def get(self, id):
        # Database access logic
        pass
""",
            },
            "Observer": {
                "steps": [
                    "Define observer interface",
                    "Implement concrete observers",
                    "Create subject with observer list",
                    "Implement notify mechanism",
                ],
                "code_template": """
class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)
""",
            },
        }

        return guides.get(
            pattern["type"],
            {
                "steps": [
                    "Analyze requirements",
                    "Design structure",
                    "Implement pattern",
                    "Test thoroughly",
                ],
                "code_template": "# Pattern implementation",
            },
        )

    def _provide_examples(self, pattern: Dict) -> List[str]:
        """Provide real-world examples"""

        examples_map = {
            "Singleton": [
                "Database connection pool",
                "Logger instance",
                "Configuration manager",
            ],
            "Factory Method": [
                "Document creator (PDF, Word, Excel)",
                "Database driver factory",
                "Payment processor factory",
            ],
            "Observer": [
                "Event listeners",
                "Model-View-Controller",
                "Stock price updates",
            ],
            "Strategy": [
                "Sorting algorithms",
                "Payment methods",
                "Compression algorithms",
            ],
            "Repository": ["User repository", "Product repository", "Order repository"],
        }

        return examples_map.get(pattern["type"], ["Generic implementation"])

    def _get_considerations(self, pattern: Dict) -> List[str]:
        """Get pattern considerations and trade-offs"""

        considerations_map = {
            "Singleton": [
                "Thread safety in multi-threaded environments",
                "Testing difficulty due to global state",
                "Violates dependency injection principles",
            ],
            "Microservices": [
                "Network latency between services",
                "Data consistency challenges",
                "Increased operational complexity",
            ],
            "Event Sourcing": [
                "Storage requirements for events",
                "Event replay performance",
                "Complexity of event versioning",
            ],
            "CQRS": [
                "Eventual consistency between read/write models",
                "Increased system complexity",
                "Synchronization challenges",
            ],
        }

        return considerations_map.get(
            pattern["type"],
            [
                "Consider performance implications",
                "Evaluate complexity vs benefits",
                "Ensure proper documentation",
            ],
        )

    def _build_pattern_catalog(self) -> Dict:
        """Build comprehensive pattern catalog"""
        return {
            "creational": [
                "Singleton",
                "Factory Method",
                "Abstract Factory",
                "Builder",
                "Prototype",
                "Object Pool",
            ],
            "structural": [
                "Adapter",
                "Bridge",
                "Composite",
                "Decorator",
                "Facade",
                "Flyweight",
                "Proxy",
            ],
            "behavioral": [
                "Chain of Responsibility",
                "Command",
                "Iterator",
                "Mediator",
                "Memento",
                "Observer",
                "State",
                "Strategy",
                "Template Method",
                "Visitor",
            ],
            "architectural": [
                "MVC",
                "MVP",
                "MVVM",
                "Repository",
                "Service Layer",
                "Domain Model",
                "Transaction Script",
                "Table Module",
            ],
            "enterprise": [
                "DAO",
                "DTO",
                "Service Locator",
                "Dependency Injection",
                "Lazy Load",
                "Unit of Work",
                "Identity Map",
            ],
        }

    def _build_pattern_relationships(self) -> Dict:
        """Build pattern relationship graph"""
        return {
            "Factory Method": ["Abstract Factory", "Builder"],
            "Observer": ["MVC", "Publish-Subscribe"],
            "Strategy": ["State", "Template Method"],
            "Composite": ["Decorator", "Iterator"],
            "Repository": ["Unit of Work", "DAO"],
        }
