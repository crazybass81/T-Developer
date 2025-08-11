"""
Technical Compatibility Module
Assesses technical compatibility between components and requirements
"""

from typing import Dict, List, Any, Optional
import re


class TechnicalCompatibility:
    """Assesses technical compatibility"""
    
    def __init__(self):
        self.compatibility_matrix = self._build_compatibility_matrix()
        self.version_requirements = self._build_version_requirements()
        
    async def assess(
        self,
        components: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Assess technical compatibility"""
        
        compatibility_results = {}
        
        # Extract technical requirements
        tech_requirements = self._extract_technical_requirements(requirements)
        
        for component in components:
            component_id = component.get('id', component.get('name'))
            
            # Extract technical specifications
            tech_specs = self._extract_technical_specs(component)
            
            # Assess different compatibility aspects
            assessments = {
                'platform_compatibility': self._assess_platform_compatibility(tech_specs, tech_requirements),
                'language_compatibility': self._assess_language_compatibility(tech_specs, tech_requirements),
                'framework_compatibility': self._assess_framework_compatibility(tech_specs, tech_requirements),
                'database_compatibility': self._assess_database_compatibility(tech_specs, tech_requirements),
                'deployment_compatibility': self._assess_deployment_compatibility(tech_specs, tech_requirements),
                'dependency_compatibility': self._assess_dependency_compatibility(tech_specs, tech_requirements)
            }
            
            # Calculate overall compatibility score
            compatibility_score = self._calculate_compatibility_score(assessments)
            
            compatibility_results[component_id] = {
                'compatibility_score': compatibility_score,
                'detailed_assessments': assessments,
                'compatibility_issues': self._identify_compatibility_issues(assessments),
                'migration_complexity': self._assess_migration_complexity(tech_specs, tech_requirements),
                'recommendations': self._generate_compatibility_recommendations(assessments)
            }
        
        return compatibility_results
    
    def _extract_technical_requirements(self, requirements: Dict) -> Dict[str, Any]:
        """Extract technical requirements"""
        
        tech_req = {
            'platforms': [],
            'languages': [],
            'frameworks': [],
            'databases': [],
            'deployment': [],
            'performance': {},
            'security': {},
            'compliance': []
        }
        
        # Extract from text
        text = str(requirements).lower()
        
        # Platform requirements
        platforms = ['web', 'mobile', 'desktop', 'cloud', 'on-premise']
        tech_req['platforms'] = [p for p in platforms if p in text]
        
        # Language requirements
        languages = ['python', 'javascript', 'java', 'csharp', 'go', 'rust', 'php', 'ruby']
        tech_req['languages'] = [l for l in languages if l in text]
        
        # Framework requirements
        frameworks = ['react', 'vue', 'angular', 'django', 'flask', 'spring', 'express']
        tech_req['frameworks'] = [f for f in frameworks if f in text]
        
        # Database requirements
        databases = ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch']
        tech_req['databases'] = [d for d in databases if d in text]
        
        return tech_req
    
    def _extract_technical_specs(self, component: Dict) -> Dict[str, Any]:
        """Extract technical specifications from component"""
        
        specs = {
            'platforms': [],
            'languages': [],
            'frameworks': [],
            'databases': [],
            'deployment_options': [],
            'dependencies': [],
            'system_requirements': {},
            'performance_characteristics': {}
        }
        
        # Extract from component data
        text = str(component).lower()
        
        # Extract platform support
        platforms = ['web', 'mobile', 'desktop', 'cloud', 'on-premise']
        specs['platforms'] = [p for p in platforms if p in text]
        
        # Extract languages
        languages = ['python', 'javascript', 'java', 'csharp', 'go', 'rust', 'php', 'ruby']
        specs['languages'] = [l for l in languages if l in text]
        
        # Extract specific technical details if available
        if 'technical_specs' in component:
            specs.update(component['technical_specs'])
        
        return specs
    
    def _assess_platform_compatibility(self, specs: Dict, requirements: Dict) -> Dict[str, Any]:
        """Assess platform compatibility"""
        
        required_platforms = set(requirements.get('platforms', []))
        supported_platforms = set(specs.get('platforms', []))
        
        if not required_platforms:
            return {'score': 1.0, 'status': 'no_requirements', 'details': 'No specific platform requirements'}
        
        # Calculate compatibility
        compatible_platforms = required_platforms.intersection(supported_platforms)
        incompatible_platforms = required_platforms - supported_platforms
        
        compatibility_score = len(compatible_platforms) / len(required_platforms)
        
        return {
            'score': compatibility_score,
            'compatible_platforms': list(compatible_platforms),
            'incompatible_platforms': list(incompatible_platforms),
            'status': 'compatible' if compatibility_score >= 0.8 else 'partially_compatible' if compatibility_score > 0 else 'incompatible'
        }
    
    def _assess_language_compatibility(self, specs: Dict, requirements: Dict) -> Dict[str, Any]:
        """Assess programming language compatibility"""
        
        required_languages = set(requirements.get('languages', []))
        supported_languages = set(specs.get('languages', []))
        
        if not required_languages:
            return {'score': 1.0, 'status': 'no_requirements'}
        
        # Check direct compatibility
        compatible_languages = required_languages.intersection(supported_languages)
        
        # Check interoperability
        interoperable_score = self._calculate_language_interoperability(
            required_languages, supported_languages
        )
        
        direct_score = len(compatible_languages) / len(required_languages)
        combined_score = max(direct_score, interoperable_score * 0.7)  # Interop gets 70% weight
        
        return {
            'score': combined_score,
            'directly_compatible': list(compatible_languages),
            'interoperability_score': interoperable_score,
            'status': self._determine_language_status(combined_score)
        }
    
    def _calculate_language_interoperability(self, required: set, supported: set) -> float:
        """Calculate language interoperability score"""
        
        # Language interoperability matrix
        interop_matrix = {
            'javascript': ['typescript', 'nodejs'],
            'python': ['cython', 'jython'],
            'java': ['scala', 'kotlin', 'groovy'],
            'csharp': ['fsharp', 'vb.net']
        }
        
        interop_score = 0
        for req_lang in required:
            for supp_lang in supported:
                if supp_lang in interop_matrix.get(req_lang, []) or req_lang in interop_matrix.get(supp_lang, []):
                    interop_score += 1
                    break
        
        return interop_score / len(required) if required else 0
    
    def _determine_language_status(self, score: float) -> str:
        """Determine language compatibility status"""
        
        if score >= 0.9:
            return 'fully_compatible'
        elif score >= 0.7:
            return 'mostly_compatible'
        elif score >= 0.4:
            return 'partially_compatible'
        else:
            return 'incompatible'
    
    def _assess_framework_compatibility(self, specs: Dict, requirements: Dict) -> Dict[str, Any]:
        """Assess framework compatibility"""
        
        required_frameworks = set(requirements.get('frameworks', []))
        supported_frameworks = set(specs.get('frameworks', []))
        
        if not required_frameworks:
            return {'score': 1.0, 'status': 'no_requirements'}
        
        # Direct compatibility
        compatible = required_frameworks.intersection(supported_frameworks)
        compatibility_score = len(compatible) / len(required_frameworks)
        
        # Check framework family compatibility
        family_score = self._assess_framework_family_compatibility(
            required_frameworks, supported_frameworks
        )
        
        final_score = max(compatibility_score, family_score * 0.8)
        
        return {
            'score': final_score,
            'directly_compatible': list(compatible),
            'family_compatibility': family_score,
            'status': 'compatible' if final_score >= 0.7 else 'partially_compatible' if final_score > 0 else 'incompatible'
        }
    
    def _assess_framework_family_compatibility(self, required: set, supported: set) -> float:
        """Assess compatibility within framework families"""
        
        framework_families = {
            'frontend_js': ['react', 'vue', 'angular', 'svelte'],
            'backend_python': ['django', 'flask', 'fastapi', 'tornado'],
            'backend_js': ['express', 'koa', 'fastify', 'nestjs'],
            'backend_java': ['spring', 'struts', 'play']
        }
        
        compatibility_count = 0
        for req_fw in required:
            for family, frameworks in framework_families.items():
                if req_fw in frameworks:
                    if any(fw in frameworks for fw in supported):
                        compatibility_count += 1
                        break
        
        return compatibility_count / len(required) if required else 0
    
    def _assess_database_compatibility(self, specs: Dict, requirements: Dict) -> Dict[str, Any]:
        """Assess database compatibility"""
        
        required_dbs = set(requirements.get('databases', []))
        supported_dbs = set(specs.get('databases', []))
        
        if not required_dbs:
            return {'score': 1.0, 'status': 'no_requirements'}
        
        # Direct compatibility
        compatible = required_dbs.intersection(supported_dbs)
        
        # Type compatibility (SQL vs NoSQL)
        type_compatibility = self._assess_database_type_compatibility(required_dbs, supported_dbs)
        
        direct_score = len(compatible) / len(required_dbs)
        final_score = max(direct_score, type_compatibility * 0.6)
        
        return {
            'score': final_score,
            'directly_compatible': list(compatible),
            'type_compatibility': type_compatibility,
            'migration_required': direct_score < 1.0,
            'status': self._determine_db_status(final_score)
        }
    
    def _assess_database_type_compatibility(self, required: set, supported: set) -> float:
        """Assess database type compatibility"""
        
        db_types = {
            'sql': ['postgresql', 'mysql', 'sqlite', 'mssql', 'oracle'],
            'nosql_document': ['mongodb', 'couchdb', 'dynamodb'],
            'nosql_key_value': ['redis', 'memcached', 'riak'],
            'search': ['elasticsearch', 'solr']
        }
        
        required_types = set()
        supported_types = set()
        
        for req_db in required:
            for db_type, dbs in db_types.items():
                if req_db in dbs:
                    required_types.add(db_type)
        
        for supp_db in supported:
            for db_type, dbs in db_types.items():
                if supp_db in dbs:
                    supported_types.add(db_type)
        
        if not required_types:
            return 0.0
        
        return len(required_types.intersection(supported_types)) / len(required_types)
    
    def _determine_db_status(self, score: float) -> str:
        """Determine database compatibility status"""
        
        if score >= 0.8:
            return 'compatible'
        elif score >= 0.5:
            return 'migration_required'
        else:
            return 'incompatible'
    
    def _assess_deployment_compatibility(self, specs: Dict, requirements: Dict) -> Dict[str, Any]:
        """Assess deployment compatibility"""
        
        required_deployment = requirements.get('deployment', [])
        supported_deployment = specs.get('deployment_options', [])
        
        if not required_deployment:
            return {'score': 1.0, 'status': 'flexible'}
        
        deployment_types = {
            'cloud': ['aws', 'azure', 'gcp', 'heroku'],
            'container': ['docker', 'kubernetes', 'openshift'],
            'traditional': ['vm', 'bare_metal', 'dedicated']
        }
        
        compatibility_score = self._calculate_deployment_compatibility(
            required_deployment, supported_deployment, deployment_types
        )
        
        return {
            'score': compatibility_score,
            'status': 'compatible' if compatibility_score >= 0.7 else 'requires_setup'
        }
    
    def _calculate_deployment_compatibility(self, required: List, supported: List, types: Dict) -> float:
        """Calculate deployment compatibility score"""
        
        if not required:
            return 1.0
        
        # Simple overlap calculation for now
        required_set = set(str(r).lower() for r in required)
        supported_set = set(str(s).lower() for s in supported)
        
        overlap = len(required_set.intersection(supported_set))
        return overlap / len(required_set) if required_set else 1.0
    
    def _assess_dependency_compatibility(self, specs: Dict, requirements: Dict) -> Dict[str, Any]:
        """Assess dependency compatibility"""
        
        component_deps = specs.get('dependencies', [])
        
        # Analyze dependency conflicts
        conflicts = self._identify_dependency_conflicts(component_deps)
        
        # Calculate dependency health score
        health_score = self._calculate_dependency_health(component_deps)
        
        return {
            'score': health_score,
            'conflicts': conflicts,
            'dependency_count': len(component_deps),
            'status': 'healthy' if health_score > 0.8 and not conflicts else 'issues'
        }
    
    def _identify_dependency_conflicts(self, dependencies: List) -> List[str]:
        """Identify potential dependency conflicts"""
        
        # Simplified conflict detection
        conflicts = []
        
        # Check for version conflicts (simplified)
        dep_names = {}
        for dep in dependencies:
            name = str(dep).split('@')[0] if '@' in str(dep) else str(dep)
            if name in dep_names:
                conflicts.append(f"Potential version conflict for {name}")
            else:
                dep_names[name] = dep
        
        return conflicts
    
    def _calculate_dependency_health(self, dependencies: List) -> float:
        """Calculate dependency health score"""
        
        if not dependencies:
            return 1.0  # No dependencies is good
        
        # Penalize too many dependencies
        dep_count_penalty = max(0, (len(dependencies) - 10) * 0.05)
        base_score = 1.0 - dep_count_penalty
        
        return max(0.1, base_score)
    
    def _calculate_compatibility_score(self, assessments: Dict[str, Dict]) -> float:
        """Calculate overall compatibility score"""
        
        weights = {
            'platform_compatibility': 0.2,
            'language_compatibility': 0.25,
            'framework_compatibility': 0.2,
            'database_compatibility': 0.15,
            'deployment_compatibility': 0.1,
            'dependency_compatibility': 0.1
        }
        
        total_score = sum(
            assessments[category]['score'] * weights[category]
            for category in weights.keys()
            if category in assessments
        )
        
        return min(1.0, max(0.0, total_score))
    
    def _identify_compatibility_issues(self, assessments: Dict) -> List[str]:
        """Identify compatibility issues"""
        
        issues = []
        
        for category, assessment in assessments.items():
            score = assessment.get('score', 1.0)
            status = assessment.get('status', 'unknown')
            
            if score < 0.5:
                issues.append(f"Low {category.replace('_', ' ')}: {status}")
            elif 'incompatible' in status:
                issues.append(f"Incompatible {category.replace('_', ' ')}")
        
        return issues
    
    def _assess_migration_complexity(self, specs: Dict, requirements: Dict) -> str:
        """Assess migration complexity"""
        
        # Simple heuristic based on technology differences
        spec_techs = set(str(v).lower() for v in specs.values() if isinstance(v, str))
        req_techs = set(str(v).lower() for v in requirements.values() if isinstance(v, str))
        
        overlap = len(spec_techs.intersection(req_techs))
        total = len(spec_techs.union(req_techs))
        
        similarity = overlap / total if total > 0 else 1.0
        
        if similarity > 0.8:
            return 'low'
        elif similarity > 0.5:
            return 'medium'
        else:
            return 'high'
    
    def _generate_compatibility_recommendations(self, assessments: Dict) -> List[str]:
        """Generate compatibility recommendations"""
        
        recommendations = []
        
        for category, assessment in assessments.items():
            score = assessment.get('score', 1.0)
            
            if score < 0.6:
                recommendations.append(f"Address {category.replace('_', ' ')} issues before proceeding")
            elif score < 0.8:
                recommendations.append(f"Review {category.replace('_', ' ')} requirements")
        
        if not recommendations:
            recommendations.append("Good technical compatibility - proceed with implementation")
        
        return recommendations
    
    def _build_compatibility_matrix(self) -> Dict[str, Dict]:
        """Build technology compatibility matrix"""
        
        return {
            'languages': {
                'javascript': ['nodejs', 'typescript', 'react', 'vue'],
                'python': ['django', 'flask', 'fastapi'],
                'java': ['spring', 'hibernate']
            },
            'databases': {
                'postgresql': ['mysql', 'sqlite'],
                'mongodb': ['couchdb'],
                'redis': ['memcached']
            }
        }
    
    def _build_version_requirements(self) -> Dict[str, str]:
        """Build version requirement mappings"""
        
        return {
            'nodejs': '>=14.0.0',
            'python': '>=3.8',
            'java': '>=11',
            'react': '>=17.0',
            'postgresql': '>=12.0'
        }
