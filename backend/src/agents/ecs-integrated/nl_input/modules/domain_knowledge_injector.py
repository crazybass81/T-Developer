"""
Domain Knowledge Injector Module
Injects domain-specific knowledge and maps industry terminology
"""

from typing import Dict, Any, List, Optional
import re

class DomainKnowledgeInjector:
    """Injects domain-specific knowledge into project requirements"""
    
    def __init__(self):
        self.domain_patterns = {
            "healthcare": {
                "keywords": ["patient", "medical", "health", "clinical", "hospital", "doctor", "diagnosis", "treatment", "ehr", "emr"],
                "requirements": [
                    "HIPAA compliance for patient data protection",
                    "HL7/FHIR standards for data exchange",
                    "Audit logging for all data access",
                    "Role-based access control (RBAC)",
                    "Data encryption at rest and in transit"
                ],
                "tech_suggestions": {
                    "database": ["PostgreSQL with encryption", "MongoDB with field-level encryption"],
                    "auth": ["OAuth2 with MFA", "SAML integration"],
                    "monitoring": ["Audit trail system", "Access logging"]
                },
                "compliance": ["HIPAA", "GDPR", "FDA 21 CFR Part 11"],
                "terminology_map": {
                    "patient record": "Electronic Health Record (EHR)",
                    "medical history": "Patient Medical Record (PMR)",
                    "appointment system": "Patient Scheduling System",
                    "billing": "Revenue Cycle Management (RCM)"
                }
            },
            "finance": {
                "keywords": ["banking", "payment", "transaction", "finance", "trading", "investment", "portfolio", "account"],
                "requirements": [
                    "PCI DSS compliance for payment processing",
                    "SOC 2 Type II certification requirements",
                    "Real-time fraud detection",
                    "Transaction atomicity and consistency",
                    "Regulatory reporting capabilities"
                ],
                "tech_suggestions": {
                    "database": ["PostgreSQL with ACID compliance", "Oracle for enterprise"],
                    "messaging": ["Apache Kafka for event streaming", "RabbitMQ for transactions"],
                    "security": ["Hardware Security Modules (HSM)", "Tokenization services"]
                },
                "compliance": ["PCI DSS", "SOX", "GDPR", "MiFID II", "Basel III"],
                "terminology_map": {
                    "money transfer": "Electronic Funds Transfer (EFT)",
                    "user verification": "Know Your Customer (KYC)",
                    "fraud check": "Anti-Money Laundering (AML)",
                    "payment gateway": "Payment Service Provider (PSP)"
                }
            },
            "education": {
                "keywords": ["student", "course", "learning", "school", "education", "teacher", "curriculum", "assessment"],
                "requirements": [
                    "FERPA compliance for student data",
                    "SCORM/xAPI for learning content",
                    "Accessibility compliance (WCAG 2.1 AA)",
                    "Multi-tenant architecture for institutions",
                    "Progress tracking and analytics"
                ],
                "tech_suggestions": {
                    "lms": ["Moodle integration", "Canvas API", "Blackboard"],
                    "content": ["SCORM packages", "H5P interactive content"],
                    "video": ["Video streaming with DRM", "Live classroom features"]
                },
                "compliance": ["FERPA", "COPPA", "GDPR", "Section 508"],
                "terminology_map": {
                    "online course": "Learning Management System (LMS)",
                    "student tracking": "Student Information System (SIS)",
                    "grades": "Gradebook Management",
                    "online test": "Computer-Based Assessment (CBA)"
                }
            },
            "ecommerce": {
                "keywords": ["shop", "store", "product", "cart", "checkout", "order", "inventory", "catalog"],
                "requirements": [
                    "PCI compliance for payment processing",
                    "Inventory management system",
                    "Multi-currency support",
                    "Tax calculation engine",
                    "Shipping integration"
                ],
                "tech_suggestions": {
                    "payment": ["Stripe", "PayPal", "Square"],
                    "shipping": ["ShipStation", "FedEx API", "UPS API"],
                    "tax": ["TaxJar", "Avalara"],
                    "search": ["Elasticsearch", "Algolia"]
                },
                "compliance": ["PCI DSS", "GDPR", "CCPA"],
                "terminology_map": {
                    "product list": "Product Catalog",
                    "shopping cart": "Cart Management System",
                    "payment": "Payment Gateway Integration",
                    "stock": "Inventory Management System"
                }
            },
            "iot": {
                "keywords": ["sensor", "device", "iot", "telemetry", "mqtt", "embedded", "arduino", "raspberry"],
                "requirements": [
                    "MQTT protocol support",
                    "Time-series data storage",
                    "Edge computing capabilities",
                    "Device provisioning and management",
                    "Real-time data streaming"
                ],
                "tech_suggestions": {
                    "protocols": ["MQTT", "CoAP", "AMQP"],
                    "database": ["InfluxDB", "TimescaleDB", "Cassandra"],
                    "platforms": ["AWS IoT Core", "Azure IoT Hub", "Google Cloud IoT"]
                },
                "compliance": ["IEC 62443", "ISO 27001"],
                "terminology_map": {
                    "device data": "Telemetry Data",
                    "device control": "Command and Control (C2)",
                    "data collection": "Data Ingestion Pipeline",
                    "device update": "Over-The-Air (OTA) Updates"
                }
            }
        }
        
        self.cross_domain_requirements = {
            "security": [
                "Implement proper authentication and authorization",
                "Use HTTPS/TLS for all communications",
                "Regular security audits and penetration testing",
                "Input validation and sanitization"
            ],
            "performance": [
                "Implement caching strategy",
                "Database query optimization",
                "CDN for static assets",
                "Load balancing for high availability"
            ],
            "scalability": [
                "Microservices architecture consideration",
                "Horizontal scaling capability",
                "Message queue for async processing",
                "Database sharding strategy"
            ]
        }
    
    async def inject(
        self,
        description: str,
        requirements: Dict[str, Any],
        detected_domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Inject domain-specific knowledge into requirements
        
        Args:
            description: Project description
            requirements: Existing requirements
            detected_domain: Pre-detected domain
            
        Returns:
            Enhanced requirements with domain knowledge
        """
        
        # Detect domain if not provided
        if not detected_domain:
            detected_domain = self._detect_domain(description)
        
        if not detected_domain:
            return requirements
        
        # Get domain configuration
        domain_config = self.domain_patterns.get(detected_domain, {})
        
        # Enhance requirements
        enhanced = requirements.copy()
        
        # Add domain-specific requirements
        if "functional_requirements" not in enhanced:
            enhanced["functional_requirements"] = []
        
        enhanced["functional_requirements"].extend(
            domain_config.get("requirements", [])
        )
        
        # Add compliance requirements
        if "compliance_requirements" not in enhanced:
            enhanced["compliance_requirements"] = []
        
        enhanced["compliance_requirements"].extend(
            domain_config.get("compliance", [])
        )
        
        # Add technology suggestions
        if "technology_suggestions" not in enhanced:
            enhanced["technology_suggestions"] = {}
        
        enhanced["technology_suggestions"].update(
            domain_config.get("tech_suggestions", {})
        )
        
        # Apply terminology mapping
        enhanced["mapped_terminology"] = self._map_terminology(
            description,
            domain_config.get("terminology_map", {})
        )
        
        # Add cross-domain requirements based on project scale
        enhanced = self._add_cross_domain_requirements(enhanced, description)
        
        # Add domain metadata
        enhanced["domain_metadata"] = {
            "detected_domain": detected_domain,
            "confidence": self._calculate_confidence(description, detected_domain),
            "domain_specific_features": self._extract_domain_features(description, detected_domain)
        }
        
        return enhanced
    
    def _detect_domain(self, description: str) -> Optional[str]:
        """Detect domain from description"""
        
        description_lower = description.lower()
        scores = {}
        
        for domain, config in self.domain_patterns.items():
            keywords = config.get("keywords", [])
            score = sum(1 for keyword in keywords if keyword in description_lower)
            
            if score > 0:
                scores[domain] = score
        
        if scores:
            # Return domain with highest score
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _map_terminology(self, description: str, terminology_map: Dict[str, str]) -> Dict[str, str]:
        """Map common terms to domain-specific terminology"""
        
        mapped = {}
        description_lower = description.lower()
        
        for common_term, domain_term in terminology_map.items():
            if common_term in description_lower:
                mapped[common_term] = domain_term
        
        return mapped
    
    def _add_cross_domain_requirements(
        self,
        requirements: Dict[str, Any],
        description: str
    ) -> Dict[str, Any]:
        """Add cross-domain requirements based on project characteristics"""
        
        description_lower = description.lower()
        
        # Check for security needs
        if any(word in description_lower for word in ["secure", "privacy", "sensitive", "confidential"]):
            if "non_functional_requirements" not in requirements:
                requirements["non_functional_requirements"] = []
            requirements["non_functional_requirements"].extend(
                self.cross_domain_requirements["security"]
            )
        
        # Check for performance needs
        if any(word in description_lower for word in ["fast", "real-time", "performance", "speed"]):
            requirements["non_functional_requirements"].extend(
                self.cross_domain_requirements["performance"]
            )
        
        # Check for scalability needs
        if any(word in description_lower for word in ["scale", "growth", "enterprise", "millions"]):
            requirements["non_functional_requirements"].extend(
                self.cross_domain_requirements["scalability"]
            )
        
        # Remove duplicates
        if "non_functional_requirements" in requirements:
            requirements["non_functional_requirements"] = list(set(
                requirements["non_functional_requirements"]
            ))
        
        return requirements
    
    def _calculate_confidence(self, description: str, domain: str) -> float:
        """Calculate confidence score for domain detection"""
        
        if not domain or domain not in self.domain_patterns:
            return 0.0
        
        keywords = self.domain_patterns[domain]["keywords"]
        description_lower = description.lower()
        
        matches = sum(1 for keyword in keywords if keyword in description_lower)
        
        # Calculate confidence based on keyword matches
        confidence = min(matches / 3.0, 1.0)  # 3 keywords = 100% confidence
        
        return round(confidence, 2)
    
    def _extract_domain_features(self, description: str, domain: str) -> List[str]:
        """Extract domain-specific features from description"""
        
        features = []
        
        if domain == "healthcare":
            feature_patterns = [
                ("telemedicine", "Telemedicine capabilities"),
                ("appointment", "Appointment scheduling"),
                ("prescription", "E-prescription management"),
                ("lab results", "Laboratory results integration")
            ]
        elif domain == "finance":
            feature_patterns = [
                ("portfolio", "Portfolio management"),
                ("trading", "Trading platform"),
                ("budget", "Budget tracking"),
                ("invoice", "Invoice management")
            ]
        elif domain == "education":
            feature_patterns = [
                ("quiz", "Assessment tools"),
                ("video", "Video lectures"),
                ("discussion", "Discussion forums"),
                ("certificate", "Certificate generation")
            ]
        else:
            return features
        
        description_lower = description.lower()
        
        for pattern, feature in feature_patterns:
            if pattern in description_lower:
                features.append(feature)
        
        return features