"""
Faceted Search Module
Provides faceted search capabilities for refined component discovery
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import math


class FacetedSearch:
    """Advanced faceted search implementation"""
    
    def __init__(self):
        self.facet_types = {
            'category': self._build_category_facets,
            'technology': self._build_technology_facets,
            'tags': self._build_tag_facets,
            'license': self._build_license_facets,
            'popularity': self._build_popularity_facets,
            'quality': self._build_quality_facets,
            'features': self._build_feature_facets,
            'size': self._build_size_facets,
            'maintenance': self._build_maintenance_facets,
            'security': self._build_security_facets,
            'date': self._build_date_facets,
            'performance': self._build_performance_facets
        }
        
        # Facet display configurations
        self.facet_configs = {
            'category': {'max_items': 15, 'sort_by': 'count', 'show_count': True},
            'technology': {'max_items': 20, 'sort_by': 'count', 'show_count': True},
            'tags': {'max_items': 25, 'sort_by': 'count', 'show_count': True},
            'license': {'max_items': 10, 'sort_by': 'count', 'show_count': True},
            'popularity': {'max_items': 5, 'sort_by': 'value', 'show_count': True},
            'quality': {'max_items': 5, 'sort_by': 'value', 'show_count': True},
            'features': {'max_items': 30, 'sort_by': 'count', 'show_count': True},
            'size': {'max_items': 6, 'sort_by': 'value', 'show_count': True},
            'maintenance': {'max_items': 8, 'sort_by': 'count', 'show_count': True},
            'security': {'max_items': 5, 'sort_by': 'value', 'show_count': True},
            'date': {'max_items': 8, 'sort_by': 'value', 'show_count': True},
            'performance': {'max_items': 5, 'sort_by': 'value', 'show_count': True}
        }
        
    async def search(
        self,
        query: Dict[str, Any],
        components: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Perform faceted search"""
        
        if not components:
            return {}
        
        # Get selected facets from query
        selected_facets = query.get('facets', {})
        
        # Apply facet filters if any are selected
        filtered_components = self._apply_facet_filters(components, selected_facets)
        
        # Build facet results for each facet type
        facet_results = {}
        
        for facet_type in self.facet_types.keys():
            if facet_type in self.facet_configs:
                facets = await self.facet_types[facet_type](
                    filtered_components, 
                    selected_facets.get(facet_type)
                )
                
                if facets:
                    facet_results[facet_type] = self._format_facets(
                        facets, 
                        facet_type,
                        self.facet_configs[facet_type]
                    )
        
        return facet_results
    
    def _apply_facet_filters(
        self,
        components: List[Dict[str, Any]],
        selected_facets: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply currently selected facet filters"""
        
        filtered = components
        
        for facet_type, facet_values in selected_facets.items():
            if facet_type == 'category' and facet_values:
                filtered = [
                    c for c in filtered
                    if c.get('category') in facet_values
                ]
            
            elif facet_type == 'technology' and facet_values:
                filtered = [
                    c for c in filtered
                    if c.get('technology') in facet_values
                ]
            
            elif facet_type == 'tags' and facet_values:
                filtered = [
                    c for c in filtered
                    if any(tag in c.get('tags', []) for tag in facet_values)
                ]
            
            elif facet_type == 'license' and facet_values:
                filtered = [
                    c for c in filtered
                    if c.get('license') in facet_values
                ]
            
            elif facet_type == 'popularity' and facet_values:
                popularity_range = facet_values
                if 'min' in popularity_range and 'max' in popularity_range:
                    filtered = [
                        c for c in filtered
                        if popularity_range['min'] <= c.get('popularity', 0) <= popularity_range['max']
                    ]
            
            elif facet_type == 'quality' and facet_values:
                quality_range = facet_values
                if 'min' in quality_range and 'max' in quality_range:
                    filtered = [
                        c for c in filtered
                        if quality_range['min'] <= c.get('quality', 0) <= quality_range['max']
                    ]
            
            elif facet_type == 'features' and facet_values:
                filtered = [
                    c for c in filtered
                    if any(feature in c.get('features', []) for feature in facet_values)
                ]
        
        return filtered
    
    async def _build_category_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Build category facets"""
        
        category_counts = Counter()
        
        for component in components:
            category = component.get('category')
            if category:
                category_counts[category] += 1
        
        facets = []
        for category, count in category_counts.items():
            facets.append({
                'value': category,
                'label': category,
                'count': count,
                'selected': selected and category in selected,
                'percentage': (count / len(components)) * 100 if components else 0
            })
        
        return facets
    
    async def _build_technology_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Build technology facets"""
        
        tech_counts = Counter()
        
        for component in components:
            technology = component.get('technology')
            if technology:
                tech_counts[technology] += 1
        
        facets = []
        for tech, count in tech_counts.items():
            # Add technology ecosystem information
            ecosystem = self._get_technology_ecosystem(tech)
            
            facets.append({
                'value': tech,
                'label': tech,
                'count': count,
                'selected': selected and tech in selected,
                'percentage': (count / len(components)) * 100 if components else 0,
                'ecosystem': ecosystem,
                'popularity_score': self._calculate_tech_popularity(tech, components)
            })
        
        return facets
    
    async def _build_tag_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Build tag facets"""
        
        tag_counts = Counter()
        
        for component in components:
            tags = component.get('tags', [])
            for tag in tags:
                tag_counts[tag] += 1
        
        facets = []
        for tag, count in tag_counts.items():
            # Categorize tags
            tag_category = self._categorize_tag(tag)
            
            facets.append({
                'value': tag,
                'label': tag,
                'count': count,
                'selected': selected and tag in selected,
                'percentage': (count / len(components)) * 100 if components else 0,
                'category': tag_category,
                'relevance_score': self._calculate_tag_relevance(tag, components)
            })
        
        return facets
    
    async def _build_license_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Build license facets"""
        
        license_counts = Counter()
        
        for component in components:
            license_name = component.get('license')
            if license_name:
                license_counts[license_name] += 1
        
        facets = []
        for license_name, count in license_counts.items():
            # Add license information
            license_info = self._get_license_info(license_name)
            
            facets.append({
                'value': license_name,
                'label': license_name,
                'count': count,
                'selected': selected and license_name in selected,
                'percentage': (count / len(components)) * 100 if components else 0,
                'commercial_use': license_info.get('commercial_use', False),
                'copyleft': license_info.get('copyleft', False),
                'permissive': license_info.get('permissive', False)
            })
        
        return facets
    
    async def _build_popularity_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Build popularity range facets"""
        
        if not components:
            return []
        
        # Define popularity ranges
        ranges = [
            {'min': 9, 'max': 10, 'label': 'Extremely Popular (9-10)'},
            {'min': 7, 'max': 8.99, 'label': 'Very Popular (7-8.9)'},
            {'min': 5, 'max': 6.99, 'label': 'Popular (5-6.9)'},
            {'min': 3, 'max': 4.99, 'label': 'Moderately Popular (3-4.9)'},
            {'min': 0, 'max': 2.99, 'label': 'Less Popular (0-2.9)'}
        ]
        
        facets = []
        for range_config in ranges:
            count = sum(
                1 for c in components
                if range_config['min'] <= c.get('popularity', 0) <= range_config['max']
            )
            
            if count > 0:  # Only include ranges with components
                facets.append({
                    'value': {'min': range_config['min'], 'max': range_config['max']},
                    'label': range_config['label'],
                    'count': count,
                    'selected': (
                        selected and 
                        selected.get('min') == range_config['min'] and 
                        selected.get('max') == range_config['max']
                    ),
                    'percentage': (count / len(components)) * 100
                })
        
        return facets
    
    async def _build_quality_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Build quality range facets"""
        
        if not components:
            return []
        
        ranges = [
            {'min': 9, 'max': 10, 'label': 'Excellent Quality (9-10)'},
            {'min': 7, 'max': 8.99, 'label': 'High Quality (7-8.9)'},
            {'min': 5, 'max': 6.99, 'label': 'Good Quality (5-6.9)'},
            {'min': 3, 'max': 4.99, 'label': 'Fair Quality (3-4.9)'},
            {'min': 0, 'max': 2.99, 'label': 'Low Quality (0-2.9)'}
        ]
        
        facets = []
        for range_config in ranges:
            count = sum(
                1 for c in components
                if range_config['min'] <= c.get('quality', 0) <= range_config['max']
            )
            
            if count > 0:
                facets.append({
                    'value': {'min': range_config['min'], 'max': range_config['max']},
                    'label': range_config['label'],
                    'count': count,
                    'selected': (
                        selected and 
                        selected.get('min') == range_config['min'] and 
                        selected.get('max') == range_config['max']
                    ),
                    'percentage': (count / len(components)) * 100
                })
        
        return facets
    
    async def _build_feature_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Build feature facets"""
        
        feature_counts = Counter()
        
        for component in components:
            features = component.get('features', [])
            for feature in features:
                feature_counts[feature] += 1
        
        facets = []
        for feature, count in feature_counts.items():
            feature_info = self._analyze_feature(feature, components)
            
            facets.append({
                'value': feature,
                'label': feature.replace('_', ' ').title(),
                'count': count,
                'selected': selected and feature in selected,
                'percentage': (count / len(components)) * 100 if components else 0,
                'importance_score': feature_info.get('importance', 0.5),
                'category': feature_info.get('category', 'general')
            })
        
        return facets
    
    async def _build_size_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[Dict[str, int]] = None
    ) -> List[Dict[str, Any]]:
        """Build size range facets"""
        
        if not components:
            return []
        
        # Define size ranges (in KB)
        ranges = [
            {'min': 0, 'max': 50, 'label': 'Tiny (< 50KB)'},
            {'min': 50, 'max': 200, 'label': 'Small (50-200KB)'},
            {'min': 200, 'max': 500, 'label': 'Medium (200-500KB)'},
            {'min': 500, 'max': 1000, 'label': 'Large (500KB-1MB)'},
            {'min': 1000, 'max': 5000, 'label': 'Very Large (1-5MB)'},
            {'min': 5000, 'max': float('inf'), 'label': 'Huge (>5MB)'}
        ]
        
        facets = []
        for range_config in ranges:
            count = 0
            for component in components:
                size_kb = component.get('bundle_size', component.get('package_size', 0)) / 1024
                if range_config['min'] <= size_kb < range_config['max']:
                    count += 1
            
            if count > 0:
                facets.append({
                    'value': {'min': range_config['min'], 'max': range_config['max']},
                    'label': range_config['label'],
                    'count': count,
                    'selected': (
                        selected and 
                        selected.get('min') == range_config['min'] and 
                        selected.get('max') == range_config['max']
                    ),
                    'percentage': (count / len(components)) * 100
                })
        
        return facets
    
    async def _build_maintenance_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Build maintenance status facets"""
        
        maintenance_counts = Counter()
        
        for component in components:
            # Determine maintenance status
            status = self._determine_maintenance_status(component)
            maintenance_counts[status] += 1
        
        facets = []
        status_labels = {
            'active': 'Actively Maintained',
            'stable': 'Stable/Mature',
            'maintenance': 'Maintenance Mode',
            'deprecated': 'Deprecated',
            'experimental': 'Experimental',
            'unknown': 'Unknown Status'
        }
        
        for status, count in maintenance_counts.items():
            facets.append({
                'value': status,
                'label': status_labels.get(status, status),
                'count': count,
                'selected': selected and status in selected,
                'percentage': (count / len(components)) * 100 if components else 0,
                'risk_level': self._get_maintenance_risk_level(status)
            })
        
        return facets
    
    async def _build_security_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Build security score facets"""
        
        if not components:
            return []
        
        ranges = [
            {'min': 9, 'max': 10, 'label': 'Excellent Security (9-10)'},
            {'min': 7, 'max': 8.99, 'label': 'Good Security (7-8.9)'},
            {'min': 5, 'max': 6.99, 'label': 'Fair Security (5-6.9)'},
            {'min': 0, 'max': 4.99, 'label': 'Poor Security (0-4.9)'}
        ]
        
        facets = []
        for range_config in ranges:
            count = sum(
                1 for c in components
                if range_config['min'] <= c.get('security_score', 5) <= range_config['max']
            )
            
            if count > 0:
                facets.append({
                    'value': {'min': range_config['min'], 'max': range_config['max']},
                    'label': range_config['label'],
                    'count': count,
                    'selected': (
                        selected and 
                        selected.get('min') == range_config['min'] and 
                        selected.get('max') == range_config['max']
                    ),
                    'percentage': (count / len(components)) * 100
                })
        
        return facets
    
    async def _build_date_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Build date range facets"""
        
        from datetime import datetime, timedelta
        
        now = datetime.now()
        ranges = [
            {'days': 30, 'label': 'Last Month'},
            {'days': 90, 'label': 'Last 3 Months'},
            {'days': 180, 'label': 'Last 6 Months'},
            {'days': 365, 'label': 'Last Year'},
            {'days': 730, 'label': 'Last 2 Years'},
            {'days': float('inf'), 'label': 'Older than 2 Years'}
        ]
        
        facets = []
        for range_config in ranges:
            if range_config['days'] == float('inf'):
                cutoff_date = now - timedelta(days=730)
                count = sum(
                    1 for c in components
                    if self._get_component_date(c) < cutoff_date
                )
            else:
                cutoff_date = now - timedelta(days=range_config['days'])
                count = sum(
                    1 for c in components
                    if self._get_component_date(c) >= cutoff_date
                )
            
            if count > 0:
                facets.append({
                    'value': range_config['days'],
                    'label': range_config['label'],
                    'count': count,
                    'selected': selected == range_config['days'],
                    'percentage': (count / len(components)) * 100 if components else 0
                })
        
        return facets
    
    async def _build_performance_facets(
        self,
        components: List[Dict[str, Any]],
        selected: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Build performance score facets"""
        
        if not components:
            return []
        
        ranges = [
            {'min': 9, 'max': 10, 'label': 'Excellent Performance (9-10)'},
            {'min': 7, 'max': 8.99, 'label': 'High Performance (7-8.9)'},
            {'min': 5, 'max': 6.99, 'label': 'Good Performance (5-6.9)'},
            {'min': 0, 'max': 4.99, 'label': 'Poor Performance (0-4.9)'}
        ]
        
        facets = []
        for range_config in ranges:
            count = sum(
                1 for c in components
                if range_config['min'] <= c.get('performance_score', 5) <= range_config['max']
            )
            
            if count > 0:
                facets.append({
                    'value': {'min': range_config['min'], 'max': range_config['max']},
                    'label': range_config['label'],
                    'count': count,
                    'selected': (
                        selected and 
                        selected.get('min') == range_config['min'] and 
                        selected.get('max') == range_config['max']
                    ),
                    'percentage': (count / len(components)) * 100
                })
        
        return facets
    
    def _format_facets(
        self,
        facets: List[Dict[str, Any]],
        facet_type: str,
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Format facets according to configuration"""
        
        # Sort facets
        sort_by = config.get('sort_by', 'count')
        
        if sort_by == 'count':
            facets.sort(key=lambda x: x['count'], reverse=True)
        elif sort_by == 'value':
            facets.sort(key=lambda x: x['value'])
        elif sort_by == 'label':
            facets.sort(key=lambda x: x['label'])
        
        # Limit number of items
        max_items = config.get('max_items', 10)
        if len(facets) > max_items:
            facets = facets[:max_items]
        
        # Add formatting metadata
        for facet in facets:
            facet['type'] = facet_type
            facet['show_count'] = config.get('show_count', True)
        
        return facets
    
    def _get_technology_ecosystem(self, technology: str) -> str:
        """Get technology ecosystem"""
        
        tech_lower = technology.lower()
        
        if tech_lower in ['react', 'vue', 'angular', 'svelte']:
            return 'frontend'
        elif tech_lower in ['node', 'express', 'fastapi', 'django', 'flask']:
            return 'backend'
        elif tech_lower in ['python', 'javascript', 'typescript', 'java', 'go']:
            return 'language'
        elif tech_lower in ['mongodb', 'postgresql', 'mysql', 'redis']:
            return 'database'
        else:
            return 'other'
    
    def _calculate_tech_popularity(
        self, 
        technology: str, 
        components: List[Dict[str, Any]]
    ) -> float:
        """Calculate technology popularity score"""
        
        tech_components = [c for c in components if c.get('technology') == technology]
        if not tech_components:
            return 0.0
        
        avg_popularity = sum(c.get('popularity', 0) for c in tech_components) / len(tech_components)
        total_downloads = sum(
            max(c.get('npm_downloads', 0), c.get('pypi_downloads', 0)) 
            for c in tech_components
        )
        
        # Normalize to 0-10 scale
        popularity_score = (avg_popularity + math.log10(total_downloads + 1)) / 2
        return min(popularity_score, 10.0)
    
    def _categorize_tag(self, tag: str) -> str:
        """Categorize a tag"""
        
        tag_lower = tag.lower()
        
        if tag_lower in ['ui', 'ux', 'design', 'css', 'styling']:
            return 'ui_design'
        elif tag_lower in ['performance', 'fast', 'optimized', 'efficient']:
            return 'performance'
        elif tag_lower in ['security', 'auth', 'encryption', 'secure']:
            return 'security'
        elif tag_lower in ['testing', 'test', 'qa', 'unit-test']:
            return 'testing'
        elif tag_lower in ['api', 'rest', 'graphql', 'endpoint']:
            return 'api'
        elif tag_lower in ['database', 'db', 'storage', 'persistence']:
            return 'database'
        else:
            return 'general'
    
    def _calculate_tag_relevance(
        self, 
        tag: str, 
        components: List[Dict[str, Any]]
    ) -> float:
        """Calculate tag relevance score"""
        
        tag_components = [
            c for c in components 
            if tag in c.get('tags', [])
        ]
        
        if not tag_components:
            return 0.0
        
        # Calculate based on component quality and popularity
        avg_quality = sum(c.get('quality', 0) for c in tag_components) / len(tag_components)
        avg_popularity = sum(c.get('popularity', 0) for c in tag_components) / len(tag_components)
        
        return (avg_quality + avg_popularity) / 20.0  # Normalize to 0-1
    
    def _get_license_info(self, license_name: str) -> Dict[str, bool]:
        """Get license information"""
        
        license_lower = license_name.lower()
        
        commercial_friendly = license_lower in [
            'mit', 'apache-2.0', 'bsd-2-clause', 'bsd-3-clause', 'isc'
        ]
        
        copyleft = license_lower in [
            'gpl-2.0', 'gpl-3.0', 'lgpl-2.1', 'lgpl-3.0', 'agpl-3.0'
        ]
        
        permissive = license_lower in [
            'mit', 'apache-2.0', 'bsd-2-clause', 'bsd-3-clause', 'isc', 'unlicense'
        ]
        
        return {
            'commercial_use': commercial_friendly,
            'copyleft': copyleft,
            'permissive': permissive
        }
    
    def _analyze_feature(
        self, 
        feature: str, 
        components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze a feature"""
        
        feature_lower = feature.lower()
        
        # Determine feature category
        if feature_lower in ['responsive', 'mobile', 'adaptive']:
            category = 'responsive'
            importance = 0.8
        elif feature_lower in ['accessible', 'a11y', 'accessibility']:
            category = 'accessibility'
            importance = 0.9
        elif feature_lower in ['fast', 'performance', 'optimized']:
            category = 'performance'
            importance = 0.8
        elif feature_lower in ['secure', 'security', 'encrypted']:
            category = 'security'
            importance = 0.9
        else:
            category = 'general'
            importance = 0.5
        
        return {
            'category': category,
            'importance': importance
        }
    
    def _determine_maintenance_status(self, component: Dict[str, Any]) -> str:
        """Determine component maintenance status"""
        
        # Check maintenance indicators
        recent_commits = component.get('recent_commits', 0)
        last_updated = component.get('last_updated')
        maintenance_status = component.get('maintenance_status', '').lower()
        
        if maintenance_status:
            return maintenance_status
        
        # Infer from activity
        if recent_commits >= 10:
            return 'active'
        elif recent_commits >= 3:
            return 'stable'
        elif recent_commits >= 1:
            return 'maintenance'
        elif 'experimental' in component.get('tags', []):
            return 'experimental'
        elif 'deprecated' in component.get('tags', []):
            return 'deprecated'
        else:
            return 'unknown'
    
    def _get_maintenance_risk_level(self, status: str) -> str:
        """Get risk level for maintenance status"""
        
        risk_levels = {
            'active': 'low',
            'stable': 'low',
            'maintenance': 'medium',
            'experimental': 'high',
            'deprecated': 'very_high',
            'unknown': 'medium'
        }
        
        return risk_levels.get(status, 'medium')
    
    def _get_component_date(self, component: Dict[str, Any]) -> 'datetime':
        """Get component date for comparison"""
        
        from datetime import datetime
        from dateutil.parser import parse as parse_date
        
        date_str = component.get('last_updated')
        if not date_str:
            return datetime.min
        
        try:
            return parse_date(date_str)
        except:
            return datetime.min
    
    async def get_available_facets(
        self, 
        query: str, 
        components: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Get available facet values"""
        
        facets = {}
        
        # Get all available values for each facet type
        facets['categories'] = list(set(
            c.get('category') for c in components 
            if c.get('category')
        ))
        
        facets['technologies'] = list(set(
            c.get('technology') for c in components 
            if c.get('technology')
        ))
        
        facets['licenses'] = list(set(
            c.get('license') for c in components 
            if c.get('license')
        ))
        
        facets['tags'] = list(set(
            tag for c in components 
            for tag in c.get('tags', [])
        ))
        
        facets['features'] = list(set(
            feature for c in components 
            for feature in c.get('features', [])
        ))
        
        return facets