"""
Specification Builder Module
Builds complete specifications from parsed requirements
"""

from typing import Dict, List, Any, Optional


class SpecificationBuilder:
    """Builds comprehensive specifications"""
    
    def __init__(self):
        self.spec_sections = [
            'functional',
            'non_functional',
            'technical',
            'data',
            'api',
            'ui',
            'security',
            'deployment'
        ]
    
    async def build(
        self,
        entities: Dict,
        requirements: List[Dict],
        data_model: Dict,
        apis: List[Dict],
        constraints: Dict
    ) -> Dict[str, Any]:
        """Build complete specifications"""
        
        specs = {
            'functional': self._build_functional_spec(requirements, entities),
            'non_functional': self._build_non_functional_spec(constraints),
            'technical': self._build_technical_spec(requirements, constraints),
            'data': self._build_data_spec(data_model),
            'api': self._build_api_spec(apis),
            'ui': self._build_ui_spec(requirements, entities),
            'security': self._build_security_spec(constraints),
            'deployment': self._build_deployment_spec(constraints)
        }
        
        return specs
    
    def _build_functional_spec(self, requirements: List[Dict], entities: Dict) -> Dict:
        """Build functional specification"""
        return {
            'features': [
                {
                    'id': req.get('id'),
                    'name': req.get('action', 'Feature'),
                    'description': req.get('text'),
                    'priority': req.get('priority')
                }
                for req in requirements
                if req.get('type') == 'functional'
            ],
            'use_cases': self._generate_use_cases(requirements, entities),
            'workflows': self._generate_workflows(requirements)
        }
    
    def _build_non_functional_spec(self, constraints: Dict) -> Dict:
        """Build non-functional specification"""
        return {
            'performance': constraints.get('performance', []),
            'security': constraints.get('security', []),
            'scalability': [
                {'type': 'horizontal', 'target': '1000 concurrent users'}
            ],
            'usability': [
                {'type': 'responsive', 'target': 'All modern browsers'}
            ]
        }
    
    def _build_technical_spec(self, requirements: List[Dict], constraints: Dict) -> Dict:
        """Build technical specification"""
        return {
            'architecture': 'microservices',
            'technology_stack': {
                'frontend': ['React', 'TypeScript'],
                'backend': ['Python', 'FastAPI'],
                'database': ['PostgreSQL', 'Redis'],
                'infrastructure': ['AWS', 'Docker', 'Kubernetes']
            },
            'integrations': self._identify_integrations(requirements),
            'constraints': constraints.get('technical', [])
        }
    
    def _build_data_spec(self, data_model: Dict) -> Dict:
        """Build data specification"""
        return {
            'models': data_model.get('models', {}),
            'schemas': data_model.get('schemas', {}),
            'migrations': data_model.get('migrations', [])
        }
    
    def _build_api_spec(self, apis: List[Dict]) -> Dict:
        """Build API specification"""
        return {
            'endpoints': apis,
            'authentication': {'type': 'JWT'},
            'documentation': {'format': 'OpenAPI 3.0'}
        }
    
    def _build_ui_spec(self, requirements: List[Dict], entities: Dict) -> Dict:
        """Build UI specification"""
        return {
            'screens': self._identify_screens(requirements),
            'components': self._identify_ui_components(entities),
            'design_system': 'Material Design',
            'responsive': True
        }
    
    def _build_security_spec(self, constraints: Dict) -> Dict:
        """Build security specification"""
        return {
            'authentication': 'Multi-factor',
            'authorization': 'Role-based',
            'encryption': 'AES-256',
            'compliance': constraints.get('compliance', {}).get('standards', [])
        }
    
    def _build_deployment_spec(self, constraints: Dict) -> Dict:
        """Build deployment specification"""
        return {
            'environment': ['development', 'staging', 'production'],
            'deployment_method': 'CI/CD',
            'monitoring': ['CloudWatch', 'Datadog'],
            'backup': {'frequency': 'daily', 'retention': '30 days'}
        }
    
    def _generate_use_cases(self, requirements: List[Dict], entities: Dict) -> List[Dict]:
        """Generate use cases"""
        use_cases = []
        for req in requirements[:5]:  # Limit to first 5
            use_cases.append({
                'name': f"UC-{req.get('id', 'X')}",
                'description': req.get('text'),
                'actors': entities.get('entities', {}).get('actors', [])
            })
        return use_cases
    
    def _generate_workflows(self, requirements: List[Dict]) -> List[Dict]:
        """Generate workflows"""
        return [
            {
                'name': 'Main Workflow',
                'steps': ['Initialize', 'Process', 'Complete'],
                'requirements': [r.get('id') for r in requirements[:3]]
            }
        ]
    
    def _identify_integrations(self, requirements: List[Dict]) -> List[str]:
        """Identify required integrations"""
        integrations = []
        
        for req in requirements:
            text = req.get('text', '').lower()
            if 'payment' in text:
                integrations.append('Payment Gateway')
            if 'email' in text:
                integrations.append('Email Service')
            if 'sms' in text:
                integrations.append('SMS Service')
        
        return list(set(integrations))
    
    def _identify_screens(self, requirements: List[Dict]) -> List[str]:
        """Identify UI screens"""
        screens = ['Dashboard', 'Login', 'Profile']
        
        for req in requirements:
            text = req.get('text', '').lower()
            if 'list' in text:
                screens.append('List View')
            if 'detail' in text:
                screens.append('Detail View')
            if 'form' in text:
                screens.append('Form View')
        
        return list(set(screens))
    
    def _identify_ui_components(self, entities: Dict) -> List[str]:
        """Identify UI components"""
        components = ['Button', 'Form', 'Table', 'Card']
        
        if 'objects' in entities.get('entities', {}):
            components.extend(['List', 'Grid', 'Modal'])
        
        return components