"""
Component Decision Agent - Production Implementation
Decides which components and architecture to use based on parsed requirements
"""

from typing import Dict, List, Any, Optional
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Import base classes
import sys
sys.path.append('/home/ec2-user/T-DeveloperMVP/backend/src')

from src.agents.unified.base import UnifiedBaseAgent, AgentConfig, AgentContext, AgentResult
# from agents.phase2_enhancements import Phase2ComponentDecisionResult  # Commented out - module not available

# Import all specialized modules
from .modules.architecture_selector import ArchitectureSelector
from .modules.component_analyzer import ComponentAnalyzer
from .modules.design_pattern_selector import DesignPatternSelector
from .modules.technology_stack_builder import TechnologyStackBuilder
from .modules.dependency_resolver import DependencyResolver
from .modules.integration_mapper import IntegrationMapper
from .modules.scalability_analyzer import ScalabilityAnalyzer
from .modules.security_architect import SecurityArchitect
from .modules.database_designer import DatabaseDesigner
from .modules.api_architect import APIArchitect
from .modules.infrastructure_planner import InfrastructurePlanner
from .modules.cost_optimizer import CostOptimizer


class EnhancedComponentDecisionResult:
    """Enhanced result with ECS and production features"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.success = data.get("success", False)
        self.architecture_decisions = {}
        self.component_map = {}
        self.technology_stack = {}
        self.design_patterns = []
        self.dependencies = []
        self.integrations = []
        self.infrastructure_plan = {}
        self.cost_analysis = {}
        self.security_architecture = {}
        self.api_design = {}
        self.database_design = {}
        self.scalability_plan = {}
        self.deployment_strategy = {}
        self.monitoring_strategy = {}
        self.optimization_recommendations = []


class ComponentDecisionAgent(UnifiedBaseAgent):
    """
    Production-ready Component Decision Agent
    Analyzes requirements and decides on architecture, components, and technology stack
    """
    
    def __init__(self):
        super().__init__()
        self.agent_name = "ComponentDecision"
        self.version = "3.0.0"
        
        # Initialize all specialized modules (12+ modules)
        self.architecture_selector = ArchitectureSelector()
        self.component_analyzer = ComponentAnalyzer()
        self.design_pattern_selector = DesignPatternSelector()
        self.tech_stack_builder = TechnologyStackBuilder()
        self.dependency_resolver = DependencyResolver()
        self.integration_mapper = IntegrationMapper()
        self.scalability_analyzer = ScalabilityAnalyzer()
        self.security_architect = SecurityArchitect()
        self.database_designer = DatabaseDesigner()
        self.api_architect = APIArchitect()
        self.infrastructure_planner = InfrastructurePlanner()
        self.cost_optimizer = CostOptimizer()
        
        # Configuration
        self.config = {
            'max_components': 50,
            'optimization_level': 'high',
            'cost_threshold': 10000,
            'performance_priority': 0.8,
            'security_level': 'enterprise',
            'scalability_target': '10000_users',
            'compliance_requirements': ['GDPR', 'SOC2'],
            'deployment_environments': ['dev', 'staging', 'production']
        }
        
        # Component templates library
        self.component_templates = self._load_component_templates()
        
        # Architecture patterns
        self.architecture_patterns = {
            'microservices': {
                'components': ['api_gateway', 'service_registry', 'message_queue'],
                'suitable_for': ['large_scale', 'distributed', 'multi_team']
            },
            'serverless': {
                'components': ['lambda', 'api_gateway', 'event_bridge'],
                'suitable_for': ['event_driven', 'cost_optimized', 'auto_scaling']
            },
            'monolithic': {
                'components': ['web_server', 'application_server', 'database'],
                'suitable_for': ['simple', 'small_team', 'rapid_development']
            },
            'event_driven': {
                'components': ['event_bus', 'event_store', 'processors'],
                'suitable_for': ['real_time', 'async_processing', 'decoupled']
            },
            'layered': {
                'components': ['presentation', 'business', 'data', 'infrastructure'],
                'suitable_for': ['traditional', 'clear_separation', 'maintainable']
            }
        }
    
    async def process(self, input_data: Dict[str, Any]) -> EnhancedComponentDecisionResult:
        """
        Main processing method for component decision
        
        Args:
            input_data: Parsed requirements from Parser Agent
            
        Returns:
            EnhancedComponentDecisionResult with architecture decisions
        """
        start_time = datetime.now()
        
        try:
            # Validate input
            if not self._validate_input(input_data):
                return self._create_error_result("Invalid input data")
            
            # Extract requirements
            requirements = input_data.get('requirements', {})
            specifications = input_data.get('specifications', {})
            constraints = input_data.get('constraints', {})
            
            # Run all analysis modules in parallel
            analysis_tasks = [
                self.architecture_selector.select(requirements, constraints),
                self.component_analyzer.analyze(requirements, specifications),
                self.design_pattern_selector.select(requirements),
                self.tech_stack_builder.build(requirements, constraints),
                self.dependency_resolver.resolve(specifications),
                self.integration_mapper.map(requirements),
                self.scalability_analyzer.analyze(requirements, constraints),
                self.security_architect.design(requirements, constraints),
                self.database_designer.design(specifications.get('data', {})),
                self.api_architect.design(specifications.get('api', {})),
                self.infrastructure_planner.plan(requirements, constraints),
                self.cost_optimizer.optimize(requirements, constraints)
            ]
            
            results = await asyncio.gather(*analysis_tasks)
            
            # Unpack results
            (
                architecture,
                components,
                design_patterns,
                tech_stack,
                dependencies,
                integrations,
                scalability,
                security,
                database,
                api_design,
                infrastructure,
                cost_analysis
            ) = results
            
            # Make component decisions
            component_decisions = self._make_component_decisions(
                architecture,
                components,
                design_patterns,
                tech_stack,
                requirements
            )
            
            # Generate deployment strategy
            deployment_strategy = self._generate_deployment_strategy(
                architecture,
                infrastructure,
                scalability
            )
            
            # Generate monitoring strategy
            monitoring_strategy = self._generate_monitoring_strategy(
                components,
                infrastructure
            )
            
            # Generate optimization recommendations
            optimizations = self._generate_optimizations(
                cost_analysis,
                scalability,
                security
            )
            
            # Create comprehensive result
            result = EnhancedComponentDecisionResult(
                success=True,
                data=component_decisions,
                metadata={
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'total_components': len(component_decisions['components']),
                    'architecture_type': architecture.get('type'),
                    'estimated_cost': cost_analysis.get('monthly_cost'),
                    'complexity_score': self._calculate_complexity(component_decisions)
                }
            )
            
            # Populate all result fields
            result.architecture_decisions = architecture
            result.component_map = component_decisions
            result.technology_stack = tech_stack
            result.design_patterns = design_patterns
            result.dependencies = dependencies
            result.integrations = integrations
            result.infrastructure_plan = infrastructure
            result.cost_analysis = cost_analysis
            result.security_architecture = security
            result.api_design = api_design
            result.database_design = database
            result.scalability_plan = scalability
            result.deployment_strategy = deployment_strategy
            result.monitoring_strategy = monitoring_strategy
            result.optimization_recommendations = optimizations
            
            # Log success
            await self.log_event("component_decision_complete", {
                'components': len(component_decisions['components']),
                'architecture': architecture.get('type'),
                'processing_time': result.metadata['processing_time']
            })
            
            return result
            
        except Exception as e:
            await self.log_event("component_decision_error", {"error": str(e)})
            return self._create_error_result(f"Component decision failed: {str(e)}")
    
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data structure"""
        required_fields = ['requirements', 'specifications']
        return all(field in input_data for field in required_fields)
    
    def _make_component_decisions(
        self,
        architecture: Dict,
        components: List[Dict],
        design_patterns: List[Dict],
        tech_stack: Dict,
        requirements: Dict
    ) -> Dict[str, Any]:
        """Make final component decisions based on all analysis"""
        
        decisions = {
            'components': [],
            'architecture': architecture,
            'patterns': design_patterns,
            'technology': tech_stack
        }
        
        # Select core components based on architecture
        arch_type = architecture.get('type', 'layered')
        core_components = self.architecture_patterns[arch_type]['components']
        
        # Add architecture-specific components
        for comp_type in core_components:
            component = self._create_component(comp_type, tech_stack, requirements)
            decisions['components'].append(component)
        
        # Add requirement-specific components
        for comp in components:
            if not self._is_duplicate(comp, decisions['components']):
                decisions['components'].append(comp)
        
        # Apply design patterns to components
        for pattern in design_patterns:
            self._apply_pattern_to_components(pattern, decisions['components'])
        
        # Sort components by priority
        decisions['components'].sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return decisions
    
    def _create_component(
        self,
        component_type: str,
        tech_stack: Dict,
        requirements: Dict
    ) -> Dict[str, Any]:
        """Create a component specification"""
        
        # Get template if available
        template = self.component_templates.get(component_type, {})
        
        component = {
            'id': f"comp_{component_type}_{datetime.now().timestamp()}",
            'type': component_type,
            'name': template.get('name', component_type.replace('_', ' ').title()),
            'description': template.get('description', f"Component for {component_type}"),
            'technology': self._select_technology_for_component(component_type, tech_stack),
            'interfaces': template.get('interfaces', []),
            'dependencies': template.get('dependencies', []),
            'configuration': template.get('configuration', {}),
            'priority': template.get('priority', 1),
            'resources': self._estimate_resources(component_type, requirements),
            'monitoring': {
                'metrics': template.get('metrics', ['health', 'performance']),
                'alerts': template.get('alerts', [])
            }
        }
        
        return component
    
    def _select_technology_for_component(
        self,
        component_type: str,
        tech_stack: Dict
    ) -> Dict[str, Any]:
        """Select appropriate technology for component"""
        
        technology_map = {
            'api_gateway': {
                'primary': tech_stack.get('api_gateway', 'Kong'),
                'alternatives': ['AWS API Gateway', 'Nginx', 'Traefik']
            },
            'service_registry': {
                'primary': 'Consul',
                'alternatives': ['Eureka', 'etcd', 'ZooKeeper']
            },
            'message_queue': {
                'primary': tech_stack.get('messaging', 'RabbitMQ'),
                'alternatives': ['Kafka', 'AWS SQS', 'Redis Pub/Sub']
            },
            'database': {
                'primary': tech_stack.get('database', 'PostgreSQL'),
                'alternatives': ['MySQL', 'MongoDB', 'DynamoDB']
            },
            'cache': {
                'primary': 'Redis',
                'alternatives': ['Memcached', 'Hazelcast']
            },
            'web_server': {
                'primary': tech_stack.get('frontend', 'React'),
                'alternatives': ['Vue', 'Angular', 'Svelte']
            }
        }
        
        return technology_map.get(component_type, {'primary': 'Generic', 'alternatives': []})
    
    def _estimate_resources(
        self,
        component_type: str,
        requirements: Dict
    ) -> Dict[str, Any]:
        """Estimate resource requirements for component"""
        
        # Base resource requirements
        base_resources = {
            'api_gateway': {'cpu': '2', 'memory': '4GB', 'storage': '10GB'},
            'service_registry': {'cpu': '1', 'memory': '2GB', 'storage': '5GB'},
            'message_queue': {'cpu': '2', 'memory': '8GB', 'storage': '50GB'},
            'database': {'cpu': '4', 'memory': '16GB', 'storage': '100GB'},
            'cache': {'cpu': '2', 'memory': '8GB', 'storage': '20GB'},
            'web_server': {'cpu': '2', 'memory': '4GB', 'storage': '10GB'},
            'lambda': {'memory': '1GB', 'timeout': '300s', 'concurrent': '1000'}
        }
        
        resources = base_resources.get(component_type, {
            'cpu': '1',
            'memory': '2GB',
            'storage': '10GB'
        })
        
        # Scale based on requirements
        scale_factor = self._calculate_scale_factor(requirements)
        if scale_factor > 1:
            resources = self._scale_resources(resources, scale_factor)
        
        return resources
    
    def _calculate_scale_factor(self, requirements: Dict) -> float:
        """Calculate scaling factor based on requirements"""
        
        # Analyze requirements for scaling indicators
        scale_indicators = {
            'users': requirements.get('expected_users', 100),
            'transactions': requirements.get('transactions_per_second', 10),
            'data_volume': requirements.get('data_volume_gb', 10)
        }
        
        # Calculate scale factor
        scale_factor = 1.0
        
        if scale_indicators['users'] > 1000:
            scale_factor *= (scale_indicators['users'] / 1000)
        
        if scale_indicators['transactions'] > 100:
            scale_factor *= (scale_indicators['transactions'] / 100)
        
        if scale_indicators['data_volume'] > 100:
            scale_factor *= (scale_indicators['data_volume'] / 100) ** 0.5
        
        return min(scale_factor, 10.0)  # Cap at 10x
    
    def _scale_resources(self, resources: Dict, factor: float) -> Dict:
        """Scale resource requirements by factor"""
        scaled = {}
        
        for key, value in resources.items():
            if key == 'cpu':
                scaled[key] = str(int(float(value) * factor))
            elif 'GB' in str(value):
                num = float(value.replace('GB', ''))
                scaled[key] = f"{int(num * factor)}GB"
            elif 'MB' in str(value):
                num = float(value.replace('MB', ''))
                scaled[key] = f"{int(num * factor)}MB"
            else:
                scaled[key] = value
        
        return scaled
    
    def _is_duplicate(self, component: Dict, existing: List[Dict]) -> bool:
        """Check if component is duplicate"""
        for existing_comp in existing:
            if component.get('type') == existing_comp.get('type'):
                return True
        return False
    
    def _apply_pattern_to_components(
        self,
        pattern: Dict,
        components: List[Dict]
    ) -> None:
        """Apply design pattern to components"""
        pattern_type = pattern.get('type')
        
        if pattern_type == 'singleton':
            for comp in components:
                if comp['type'] in ['service_registry', 'configuration']:
                    comp['instances'] = 1
                    comp['pattern'] = 'singleton'
        
        elif pattern_type == 'factory':
            for comp in components:
                if 'service' in comp['type']:
                    comp['creation_pattern'] = 'factory'
        
        elif pattern_type == 'observer':
            for comp in components:
                if comp['type'] in ['event_bus', 'message_queue']:
                    comp['pattern'] = 'observer'
                    comp['subscribers'] = []
    
    def _generate_deployment_strategy(
        self,
        architecture: Dict,
        infrastructure: Dict,
        scalability: Dict
    ) -> Dict[str, Any]:
        """Generate deployment strategy"""
        
        strategy = {
            'method': 'blue_green',  # Default to blue-green deployment
            'environments': ['development', 'staging', 'production'],
            'rollback_strategy': 'automatic',
            'health_checks': {
                'enabled': True,
                'interval': '30s',
                'timeout': '5s',
                'threshold': 3
            }
        }
        
        # Adjust based on architecture
        if architecture.get('type') == 'serverless':
            strategy['method'] = 'canary'
            strategy['canary_percentage'] = 10
        elif architecture.get('type') == 'microservices':
            strategy['method'] = 'rolling'
            strategy['max_surge'] = '25%'
            strategy['max_unavailable'] = '25%'
        
        # Add infrastructure-specific settings
        if 'kubernetes' in str(infrastructure).lower():
            strategy['orchestrator'] = 'kubernetes'
            strategy['namespace_strategy'] = 'environment_based'
        elif 'ecs' in str(infrastructure).lower():
            strategy['orchestrator'] = 'ecs'
            strategy['task_definition_family'] = 'app'
        
        # Add scalability settings
        if scalability.get('auto_scaling'):
            strategy['auto_scaling'] = {
                'enabled': True,
                'min_instances': scalability.get('min_instances', 2),
                'max_instances': scalability.get('max_instances', 10),
                'target_cpu': 70,
                'target_memory': 80
            }
        
        return strategy
    
    def _generate_monitoring_strategy(
        self,
        components: List[Dict],
        infrastructure: Dict
    ) -> Dict[str, Any]:
        """Generate monitoring strategy"""
        
        strategy = {
            'tools': ['CloudWatch', 'Prometheus', 'Grafana'],
            'metrics': {
                'application': [
                    'response_time',
                    'error_rate',
                    'throughput',
                    'availability'
                ],
                'infrastructure': [
                    'cpu_usage',
                    'memory_usage',
                    'disk_io',
                    'network_io'
                ],
                'business': [
                    'user_activity',
                    'transaction_volume',
                    'conversion_rate'
                ]
            },
            'logging': {
                'centralized': True,
                'retention_days': 30,
                'log_levels': ['ERROR', 'WARN', 'INFO'],
                'structured_logging': True
            },
            'alerting': {
                'channels': ['email', 'slack', 'pagerduty'],
                'severity_levels': ['critical', 'warning', 'info'],
                'escalation_policy': True
            },
            'tracing': {
                'enabled': True,
                'sampling_rate': 0.1,
                'tool': 'AWS X-Ray'
            }
        }
        
        # Add component-specific monitoring
        for component in components:
            comp_type = component.get('type')
            if comp_type == 'database':
                strategy['metrics']['database'] = [
                    'query_performance',
                    'connection_pool',
                    'replication_lag'
                ]
            elif comp_type == 'message_queue':
                strategy['metrics']['messaging'] = [
                    'queue_depth',
                    'message_rate',
                    'consumer_lag'
                ]
        
        return strategy
    
    def _generate_optimizations(
        self,
        cost_analysis: Dict,
        scalability: Dict,
        security: Dict
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        
        optimizations = []
        
        # Cost optimizations
        if cost_analysis.get('monthly_cost', 0) > self.config['cost_threshold']:
            optimizations.append({
                'type': 'cost',
                'priority': 'high',
                'recommendation': 'Consider using reserved instances or savings plans',
                'potential_savings': '30-50%'
            })
            optimizations.append({
                'type': 'cost',
                'priority': 'medium',
                'recommendation': 'Implement auto-scaling to reduce idle resources',
                'potential_savings': '20-30%'
            })
        
        # Performance optimizations
        if scalability.get('bottlenecks'):
            for bottleneck in scalability['bottlenecks']:
                optimizations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'recommendation': f"Optimize {bottleneck['component']}: {bottleneck['solution']}",
                    'impact': 'High'
                })
        
        # Security optimizations
        if security.get('vulnerabilities'):
            for vuln in security['vulnerabilities']:
                optimizations.append({
                    'type': 'security',
                    'priority': 'critical',
                    'recommendation': f"Address {vuln['type']}: {vuln['mitigation']}",
                    'compliance_impact': vuln.get('compliance_impact', [])
                })
        
        # General optimizations
        optimizations.extend([
            {
                'type': 'maintainability',
                'priority': 'medium',
                'recommendation': 'Implement comprehensive logging and monitoring',
                'impact': 'Improved debugging and troubleshooting'
            },
            {
                'type': 'reliability',
                'priority': 'high',
                'recommendation': 'Add circuit breakers and retry logic',
                'impact': 'Increased system resilience'
            },
            {
                'type': 'scalability',
                'priority': 'medium',
                'recommendation': 'Implement caching at multiple levels',
                'impact': '50-70% reduction in database load'
            }
        ])
        
        return optimizations
    
    def _calculate_complexity(self, decisions: Dict) -> float:
        """Calculate overall system complexity score"""
        
        complexity = 0.0
        
        # Component complexity
        component_count = len(decisions.get('components', []))
        complexity += component_count * 0.1
        
        # Architecture complexity
        arch_type = decisions.get('architecture', {}).get('type')
        arch_complexity = {
            'monolithic': 0.2,
            'layered': 0.3,
            'event_driven': 0.5,
            'microservices': 0.7,
            'serverless': 0.6
        }
        complexity += arch_complexity.get(arch_type, 0.5)
        
        # Technology diversity
        tech_stack = decisions.get('technology', {})
        tech_count = sum(len(v) if isinstance(v, list) else 1 for v in tech_stack.values())
        complexity += tech_count * 0.05
        
        # Pattern complexity
        pattern_count = len(decisions.get('patterns', []))
        complexity += pattern_count * 0.08
        
        return min(complexity, 10.0)  # Cap at 10
    
    def _load_component_templates(self) -> Dict[str, Dict]:
        """Load component templates from configuration"""
        
        templates = {
            'api_gateway': {
                'name': 'API Gateway',
                'description': 'Central entry point for all API requests',
                'interfaces': ['REST', 'GraphQL', 'WebSocket'],
                'dependencies': [],
                'configuration': {
                    'rate_limiting': True,
                    'authentication': True,
                    'caching': True
                },
                'metrics': ['request_rate', 'latency', 'error_rate'],
                'alerts': ['high_error_rate', 'high_latency'],
                'priority': 10
            },
            'service_registry': {
                'name': 'Service Registry',
                'description': 'Service discovery and registration',
                'interfaces': ['HTTP', 'DNS'],
                'dependencies': [],
                'configuration': {
                    'health_checks': True,
                    'auto_deregister': True
                },
                'metrics': ['registered_services', 'health_check_failures'],
                'alerts': ['service_down', 'registry_unavailable'],
                'priority': 9
            },
            'message_queue': {
                'name': 'Message Queue',
                'description': 'Asynchronous message processing',
                'interfaces': ['AMQP', 'MQTT', 'STOMP'],
                'dependencies': [],
                'configuration': {
                    'persistence': True,
                    'dead_letter_queue': True,
                    'message_ttl': 86400
                },
                'metrics': ['queue_depth', 'message_rate', 'consumer_lag'],
                'alerts': ['queue_overflow', 'consumer_lag_high'],
                'priority': 8
            },
            'database': {
                'name': 'Database',
                'description': 'Primary data storage',
                'interfaces': ['SQL', 'NoSQL'],
                'dependencies': [],
                'configuration': {
                    'replication': True,
                    'backup': True,
                    'encryption': True
                },
                'metrics': ['query_time', 'connections', 'disk_usage'],
                'alerts': ['slow_queries', 'connection_pool_exhausted'],
                'priority': 10
            },
            'cache': {
                'name': 'Cache Layer',
                'description': 'In-memory data caching',
                'interfaces': ['Redis Protocol', 'Memcached Protocol'],
                'dependencies': ['database'],
                'configuration': {
                    'eviction_policy': 'LRU',
                    'max_memory': '4GB',
                    'persistence': False
                },
                'metrics': ['hit_rate', 'evictions', 'memory_usage'],
                'alerts': ['low_hit_rate', 'memory_full'],
                'priority': 7
            }
        }
        
        return templates
    
    def _create_error_result(self, error_message: str) -> EnhancedComponentDecisionResult:
        """Create error result"""
        result = EnhancedComponentDecisionResult(
            success=False,
            data={},
            error=error_message
        )
        return result
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health"""
        health = await super().health_check()
        
        # Add module-specific health checks
        health['modules'] = {
            'architecture_selector': 'healthy',
            'component_analyzer': 'healthy',
            'design_pattern_selector': 'healthy',
            'tech_stack_builder': 'healthy',
            'dependency_resolver': 'healthy',
            'integration_mapper': 'healthy',
            'scalability_analyzer': 'healthy',
            'security_architect': 'healthy',
            'database_designer': 'healthy',
            'api_architect': 'healthy',
            'infrastructure_planner': 'healthy',
            'cost_optimizer': 'healthy'
        }
        
        health['templates_loaded'] = len(self.component_templates)
        health['architecture_patterns'] = len(self.architecture_patterns)
        
        return health