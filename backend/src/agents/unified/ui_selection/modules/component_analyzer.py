"""
Component Analyzer Module
Analyzes project requirements to determine needed UI components
"""

from typing import Dict, List, Any, Set
import re


class ComponentAnalyzer:
    """Analyzes and identifies required UI components"""
    
    def __init__(self):
        # Component categories and their indicators
        self.component_patterns = {
            'forms': {
                'indicators': ['login', 'register', 'signup', 'form', 'input', 'submit'],
                'components': ['TextField', 'Button', 'Checkbox', 'Radio', 'Select', 'DatePicker', 'FileUpload'],
                'advanced': ['FormValidator', 'MultiStepForm', 'DynamicForm', 'ConditionalFields']
            },
            'navigation': {
                'indicators': ['menu', 'nav', 'sidebar', 'breadcrumb', 'tabs'],
                'components': ['Navbar', 'Sidebar', 'Breadcrumbs', 'Tabs', 'Stepper'],
                'advanced': ['MegaMenu', 'ContextMenu', 'CommandPalette', 'NavigationRail']
            },
            'data_display': {
                'indicators': ['table', 'list', 'grid', 'card', 'chart', 'graph'],
                'components': ['Table', 'DataGrid', 'Card', 'List', 'Chart', 'Timeline'],
                'advanced': ['VirtualList', 'InfiniteScroll', 'DataTable', 'TreeView', 'Kanban']
            },
            'feedback': {
                'indicators': ['alert', 'notification', 'toast', 'message', 'error', 'success'],
                'components': ['Alert', 'Toast', 'Snackbar', 'Modal', 'Dialog', 'Notification'],
                'advanced': ['ProgressIndicator', 'Skeleton', 'LoadingOverlay', 'ConfirmDialog']
            },
            'media': {
                'indicators': ['image', 'video', 'audio', 'gallery', 'carousel', 'media'],
                'components': ['Image', 'Video', 'Audio', 'Carousel', 'Gallery', 'Avatar'],
                'advanced': ['ImageEditor', 'VideoPlayer', 'AudioVisualizer', 'Lightbox', '3DViewer']
            },
            'interaction': {
                'indicators': ['drag', 'drop', 'resize', 'sort', 'filter', 'search'],
                'components': ['DragDrop', 'Resizable', 'Sortable', 'SearchBar', 'FilterPanel'],
                'advanced': ['GestureHandler', 'TouchControls', 'VoiceInput', 'DrawingCanvas']
            },
            'layout': {
                'indicators': ['container', 'grid', 'flex', 'stack', 'divider', 'spacer'],
                'components': ['Container', 'Grid', 'Flex', 'Stack', 'Divider', 'Spacer'],
                'advanced': ['MasonryGrid', 'SplitPane', 'ResponsiveGrid', 'FloatingPanel']
            },
            'commerce': {
                'indicators': ['product', 'cart', 'checkout', 'payment', 'price', 'shop'],
                'components': ['ProductCard', 'ShoppingCart', 'PriceTag', 'PaymentForm', 'OrderSummary'],
                'advanced': ['ProductComparison', 'WishList', 'ReviewSystem', 'InventoryTracker']
            },
            'social': {
                'indicators': ['comment', 'like', 'share', 'follow', 'chat', 'message'],
                'components': ['CommentBox', 'LikeButton', 'ShareButton', 'ChatWindow', 'UserCard'],
                'advanced': ['RealTimeChat', 'ActivityFeed', 'UserPresence', 'ReactionPicker']
            },
            'content': {
                'indicators': ['editor', 'markdown', 'rich text', 'wysiwyg', 'blog', 'article'],
                'components': ['RichTextEditor', 'MarkdownEditor', 'CodeEditor', 'ContentViewer'],
                'advanced': ['CollaborativeEditor', 'VersionHistory', 'ContentManagement', 'DiffViewer']
            }
        }
        
        # Component complexity scoring
        self.complexity_scores = {
            'basic': 1,
            'intermediate': 2,
            'advanced': 3,
            'expert': 4
        }
        
        # Component dependencies
        self.dependencies = {
            'DataTable': ['Pagination', 'SortableHeaders', 'FilterRow'],
            'Form': ['Validation', 'ErrorDisplay', 'SubmitHandler'],
            'Chart': ['Legend', 'Tooltip', 'Axis', 'DataProcessor'],
            'Gallery': ['Thumbnail', 'Lightbox', 'NavigationControls'],
            'RichTextEditor': ['Toolbar', 'FormatButtons', 'MediaUpload']
        }
    
    def analyze(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze requirements to determine needed components
        
        Args:
            requirements: Project requirements
            
        Returns:
            Component analysis results
        """
        project_type = requirements.get('project_type', '')
        features = requirements.get('features', [])
        description = requirements.get('description', '')
        complexity = requirements.get('complexity', 'medium')
        
        # Combine all text for analysis
        text_content = f"{project_type} {' '.join(features)} {description}".lower()
        
        # Identify component categories
        needed_categories = self._identify_categories(text_content, features)
        
        # Select components for each category
        selected_components = self._select_components(
            needed_categories,
            complexity,
            features
        )
        
        # Add dependencies
        all_components = self._add_dependencies(selected_components)
        
        # Calculate metrics
        metrics = self._calculate_metrics(all_components)
        
        # Generate component hierarchy
        hierarchy = self._generate_hierarchy(all_components, project_type)
        
        # Optimize component selection
        optimized = self._optimize_selection(all_components, requirements)
        
        return {
            'categories': needed_categories,
            'components': optimized,
            'hierarchy': hierarchy,
            'metrics': metrics,
            'dependencies': self._get_dependencies_map(optimized),
            'recommendations': self._generate_recommendations(optimized, requirements)
        }
    
    def _identify_categories(self, text: str, features: List[str]) -> Set[str]:
        """Identify needed component categories"""
        categories = set()
        
        for category, patterns in self.component_patterns.items():
            # Check indicators
            for indicator in patterns['indicators']:
                if indicator in text:
                    categories.add(category)
                    break
            
            # Check features
            for feature in features:
                if feature.lower() in patterns['indicators']:
                    categories.add(category)
        
        # Add default categories
        categories.update(['layout', 'navigation', 'feedback'])
        
        return categories
    
    def _select_components(
        self,
        categories: Set[str],
        complexity: str,
        features: List[str]
    ) -> List[str]:
        """Select components based on categories and complexity"""
        components = []
        
        for category in categories:
            if category in self.component_patterns:
                pattern = self.component_patterns[category]
                
                # Add basic components
                components.extend(pattern['components'])
                
                # Add advanced components based on complexity
                if complexity in ['medium', 'complex']:
                    # Add some advanced components
                    advanced = pattern.get('advanced', [])
                    if complexity == 'medium':
                        components.extend(advanced[:2])  # Add first 2 advanced
                    else:
                        components.extend(advanced)  # Add all advanced
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(components))
    
    def _add_dependencies(self, components: List[str]) -> List[str]:
        """Add component dependencies"""
        all_components = components.copy()
        
        for component in components:
            if component in self.dependencies:
                deps = self.dependencies[component]
                for dep in deps:
                    if dep not in all_components:
                        all_components.append(dep)
        
        return all_components
    
    def _calculate_metrics(self, components: List[str]) -> Dict[str, Any]:
        """Calculate component metrics"""
        total = len(components)
        
        # Categorize by complexity
        basic = sum(1 for c in components if not any(
            c in self.component_patterns[cat].get('advanced', [])
            for cat in self.component_patterns
        ))
        
        advanced = total - basic
        
        return {
            'total_components': total,
            'basic_components': basic,
            'advanced_components': advanced,
            'complexity_ratio': advanced / max(total, 1),
            'estimated_development_hours': self._estimate_hours(components),
            'bundle_size_estimate': self._estimate_bundle_size(components)
        }
    
    def _generate_hierarchy(self, components: List[str], project_type: str) -> Dict[str, Any]:
        """Generate component hierarchy"""
        hierarchy = {
            'root': 'App',
            'providers': [],
            'layouts': [],
            'pages': [],
            'components': {}
        }
        
        # Categorize components
        for component in components:
            if 'Provider' in component or 'Context' in component:
                hierarchy['providers'].append(component)
            elif 'Layout' in component or 'Container' in component:
                hierarchy['layouts'].append(component)
            elif 'Page' in component or 'View' in component:
                hierarchy['pages'].append(component)
            else:
                # Group by category
                category = self._get_component_category(component)
                if category not in hierarchy['components']:
                    hierarchy['components'][category] = []
                hierarchy['components'][category].append(component)
        
        return hierarchy
    
    def _optimize_selection(
        self,
        components: List[str],
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Optimize component selection"""
        optimized = components.copy()
        
        # Remove redundant components
        redundant_pairs = [
            ('Modal', 'Dialog'),  # Choose one
            ('Toast', 'Snackbar'),  # Choose one
            ('DataGrid', 'Table'),  # Choose one based on complexity
        ]
        
        for comp1, comp2 in redundant_pairs:
            if comp1 in optimized and comp2 in optimized:
                # Keep the more appropriate one
                if requirements.get('complexity') == 'simple':
                    optimized.remove(comp1 if comp1 in ['DataGrid', 'Modal'] else comp2)
                else:
                    optimized.remove(comp2 if comp1 in ['DataGrid', 'Modal'] else comp1)
        
        return optimized
    
    def _get_dependencies_map(self, components: List[str]) -> Dict[str, List[str]]:
        """Get dependencies for selected components"""
        deps_map = {}
        
        for component in components:
            if component in self.dependencies:
                deps_map[component] = self.dependencies[component]
        
        return deps_map
    
    def _generate_recommendations(
        self,
        components: List[str],
        requirements: Dict[str, Any]
    ) -> List[str]:
        """Generate component recommendations"""
        recommendations = []
        
        # Check for missing essential components
        if 'Form' in str(components) and 'Validation' not in str(components):
            recommendations.append("Add form validation components")
        
        if 'Table' in str(components) and 'Pagination' not in str(components):
            recommendations.append("Consider adding pagination for tables")
        
        if len(components) > 30:
            recommendations.append("Consider using lazy loading for better performance")
        
        if 'Chart' in str(components):
            recommendations.append("Use a specialized charting library like Recharts or D3")
        
        return recommendations
    
    def _get_component_category(self, component: str) -> str:
        """Determine component category"""
        for category, pattern in self.component_patterns.items():
            if component in pattern.get('components', []) or \
               component in pattern.get('advanced', []):
                return category
        return 'misc'
    
    def _estimate_hours(self, components: List[str]) -> int:
        """Estimate development hours for components"""
        base_hours = len(components) * 2  # 2 hours per component average
        
        # Add complexity multiplier
        advanced_count = sum(1 for c in components if self._is_advanced(c))
        base_hours += advanced_count * 3  # Additional 3 hours for advanced
        
        return base_hours
    
    def _estimate_bundle_size(self, components: List[str]) -> str:
        """Estimate bundle size impact"""
        # Rough estimates in KB
        size_map = {
            'basic': 5,
            'intermediate': 15,
            'advanced': 30
        }
        
        total_kb = sum(
            size_map.get(self._get_complexity_level(c), 10)
            for c in components
        )
        
        if total_kb < 100:
            return "Small (<100KB)"
        elif total_kb < 300:
            return "Medium (100-300KB)"
        else:
            return "Large (>300KB)"
    
    def _is_advanced(self, component: str) -> bool:
        """Check if component is advanced"""
        for pattern in self.component_patterns.values():
            if component in pattern.get('advanced', []):
                return True
        return False
    
    def _get_complexity_level(self, component: str) -> str:
        """Get complexity level of component"""
        if self._is_advanced(component):
            return 'advanced'
        elif any(dep in component for dep in ['Data', 'Rich', 'Multi']):
            return 'intermediate'
        return 'basic'