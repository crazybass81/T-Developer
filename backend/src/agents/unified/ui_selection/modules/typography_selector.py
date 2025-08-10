"""
Typography Selector Module
Selects and configures typography systems for UI design
"""

from typing import Dict, List, Any, Optional


class TypographySelector:
    """Selects and configures typography for projects"""
    
    def __init__(self):
        self.font_stacks = {
            'system': {
                'name': 'System Font Stack',
                'fonts': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                'fallback': 'sans-serif',
                'performance': 'excellent',
                'licensing': 'free',
                'characteristics': ['native', 'fast', 'familiar']
            },
            'inter': {
                'name': 'Inter',
                'fonts': '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
                'import': 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
                'fallback': 'sans-serif',
                'performance': 'good',
                'licensing': 'open-source',
                'characteristics': ['modern', 'readable', 'versatile']
            },
            'roboto': {
                'name': 'Roboto',
                'fonts': '"Roboto", "Helvetica Neue", Arial, sans-serif',
                'import': 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap',
                'fallback': 'sans-serif',
                'performance': 'good',
                'licensing': 'open-source',
                'characteristics': ['material', 'clean', 'geometric']
            },
            'poppins': {
                'name': 'Poppins',
                'fonts': '"Poppins", "Helvetica Neue", Arial, sans-serif',
                'import': 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap',
                'fallback': 'sans-serif',
                'performance': 'good',
                'licensing': 'open-source',
                'characteristics': ['geometric', 'modern', 'friendly']
            },
            'playfair': {
                'name': 'Playfair Display',
                'fonts': '"Playfair Display", Georgia, serif',
                'import': 'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap',
                'fallback': 'serif',
                'performance': 'good',
                'licensing': 'open-source',
                'characteristics': ['elegant', 'editorial', 'classic']
            },
            'montserrat': {
                'name': 'Montserrat',
                'fonts': '"Montserrat", "Helvetica Neue", Arial, sans-serif',
                'import': 'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap',
                'fallback': 'sans-serif',
                'performance': 'good',
                'licensing': 'open-source',
                'characteristics': ['geometric', 'urban', 'modern']
            },
            'jetbrains': {
                'name': 'JetBrains Mono',
                'fonts': '"JetBrains Mono", "Courier New", monospace',
                'import': 'https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap',
                'fallback': 'monospace',
                'performance': 'good',
                'licensing': 'open-source',
                'characteristics': ['monospace', 'developer', 'readable']
            }
        }
        
        self.type_scales = {
            'minor_second': {
                'name': 'Minor Second',
                'ratio': 1.067,
                'use_case': 'Subtle hierarchy',
                'sizes': self._generate_scale(1.067)
            },
            'major_second': {
                'name': 'Major Second',
                'ratio': 1.125,
                'use_case': 'Modest hierarchy',
                'sizes': self._generate_scale(1.125)
            },
            'minor_third': {
                'name': 'Minor Third',
                'ratio': 1.2,
                'use_case': 'Standard web',
                'sizes': self._generate_scale(1.2)
            },
            'major_third': {
                'name': 'Major Third',
                'ratio': 1.25,
                'use_case': 'Traditional',
                'sizes': self._generate_scale(1.25)
            },
            'perfect_fourth': {
                'name': 'Perfect Fourth',
                'ratio': 1.333,
                'use_case': 'Distinctive',
                'sizes': self._generate_scale(1.333)
            },
            'augmented_fourth': {
                'name': 'Augmented Fourth',
                'ratio': 1.414,
                'use_case': 'High contrast',
                'sizes': self._generate_scale(1.414)
            },
            'perfect_fifth': {
                'name': 'Perfect Fifth',
                'ratio': 1.5,
                'use_case': 'Bold hierarchy',
                'sizes': self._generate_scale(1.5)
            },
            'golden_ratio': {
                'name': 'Golden Ratio',
                'ratio': 1.618,
                'use_case': 'Dramatic',
                'sizes': self._generate_scale(1.618)
            }
        }
        
        self.font_weights = {
            'thin': 100,
            'extra_light': 200,
            'light': 300,
            'regular': 400,
            'medium': 500,
            'semi_bold': 600,
            'bold': 700,
            'extra_bold': 800,
            'black': 900
        }
        
        self.line_heights = {
            'tight': 1.2,
            'snug': 1.375,
            'normal': 1.5,
            'relaxed': 1.625,
            'loose': 2
        }
        
        self.letter_spacings = {
            'tighter': '-0.05em',
            'tight': '-0.025em',
            'normal': '0',
            'wide': '0.025em',
            'wider': '0.05em',
            'widest': '0.1em'
        }
    
    def select(
        self,
        project_type: str,
        brand_personality: Optional[str] = None,
        preferences: Dict[str, Any] = None,
        constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Select typography system
        
        Args:
            project_type: Type of project
            brand_personality: Brand personality traits
            preferences: User preferences
            constraints: Technical constraints
            
        Returns:
            Typography configuration
        """
        # Select font stack
        font_stack = self._select_font_stack(
            project_type,
            brand_personality,
            preferences,
            constraints
        )
        
        # Select type scale
        type_scale = self._select_type_scale(project_type, brand_personality)
        
        # Configure font weights
        weights = self._configure_weights(project_type)
        
        # Configure line heights
        line_heights = self._configure_line_heights(project_type)
        
        # Configure letter spacing
        letter_spacing = self._configure_letter_spacing(project_type)
        
        # Generate font pairs
        font_pairs = self._generate_font_pairs(font_stack)
        
        # Create responsive typography
        responsive = self._create_responsive_typography(type_scale)
        
        # Generate CSS
        css = self._generate_typography_css(
            font_stack,
            type_scale,
            weights,
            line_heights,
            letter_spacing
        )
        
        # Performance optimization
        performance = self._optimize_performance(font_stack)
        
        return {
            'font_stack': font_stack,
            'type_scale': type_scale,
            'weights': weights,
            'line_heights': line_heights,
            'letter_spacing': letter_spacing,
            'font_pairs': font_pairs,
            'responsive': responsive,
            'css': css,
            'performance': performance,
            'guidelines': self._generate_guidelines(font_stack, type_scale)
        }
    
    def _select_font_stack(
        self,
        project_type: str,
        brand_personality: Optional[str],
        preferences: Optional[Dict],
        constraints: Optional[Dict]
    ) -> Dict[str, Any]:
        """Select appropriate font stack"""
        
        # Check constraints first
        if constraints and constraints.get('performance_critical'):
            return self.font_stacks['system']
        
        # Map project types to fonts
        type_map = {
            'dashboard': 'inter',
            'blog': 'playfair',
            'ecommerce': 'poppins',
            'corporate': 'roboto',
            'creative': 'montserrat',
            'developer': 'jetbrains',
            'saas': 'inter'
        }
        
        # Check brand personality
        if brand_personality:
            personality_map = {
                'modern': 'inter',
                'playful': 'poppins',
                'elegant': 'playfair',
                'technical': 'roboto',
                'bold': 'montserrat'
            }
            
            if brand_personality in personality_map:
                return self.font_stacks[personality_map[brand_personality]]
        
        # Use project type mapping
        font_key = type_map.get(project_type, 'inter')
        return self.font_stacks[font_key]
    
    def _select_type_scale(self, project_type: str, brand_personality: Optional[str]) -> Dict:
        """Select type scale based on project"""
        
        # Map project types to scales
        scale_map = {
            'dashboard': 'minor_third',
            'blog': 'perfect_fourth',
            'ecommerce': 'major_third',
            'landing': 'perfect_fifth',
            'portfolio': 'golden_ratio'
        }
        
        # Check brand personality
        if brand_personality == 'bold':
            return self.type_scales['perfect_fifth']
        elif brand_personality == 'subtle':
            return self.type_scales['minor_second']
        
        scale_key = scale_map.get(project_type, 'major_third')
        return self.type_scales[scale_key]
    
    def _configure_weights(self, project_type: str) -> Dict[str, int]:
        """Configure font weights for project"""
        
        if project_type in ['dashboard', 'admin']:
            # More weight variations for data-heavy interfaces
            return {
                'body': self.font_weights['regular'],
                'medium': self.font_weights['medium'],
                'heading': self.font_weights['semi_bold'],
                'bold': self.font_weights['bold']
            }
        elif project_type in ['blog', 'article']:
            # Lighter weights for readability
            return {
                'body': self.font_weights['regular'],
                'heading': self.font_weights['medium'],
                'bold': self.font_weights['semi_bold']
            }
        else:
            # Standard weights
            return {
                'body': self.font_weights['regular'],
                'medium': self.font_weights['medium'],
                'heading': self.font_weights['bold'],
                'bold': self.font_weights['extra_bold']
            }
    
    def _configure_line_heights(self, project_type: str) -> Dict[str, float]:
        """Configure line heights"""
        
        if project_type in ['blog', 'article', 'documentation']:
            # More spacing for readability
            return {
                'body': self.line_heights['relaxed'],
                'heading': self.line_heights['snug'],
                'display': self.line_heights['tight']
            }
        else:
            # Standard spacing
            return {
                'body': self.line_heights['normal'],
                'heading': self.line_heights['tight'],
                'display': self.line_heights['tight']
            }
    
    def _configure_letter_spacing(self, project_type: str) -> Dict[str, str]:
        """Configure letter spacing"""
        
        return {
            'body': self.letter_spacings['normal'],
            'heading': self.letter_spacings['tight'],
            'display': self.letter_spacings['tighter'],
            'caps': self.letter_spacings['wider']
        }
    
    def _generate_font_pairs(self, primary_font: Dict) -> List[Dict]:
        """Generate font pairing suggestions"""
        pairs = []
        
        # Determine good pairings
        if primary_font['fallback'] == 'sans-serif':
            # Pair sans-serif with serif for contrast
            pairs.append({
                'primary': primary_font['name'],
                'secondary': 'Playfair Display',
                'use_case': 'Heading/body contrast'
            })
            # Pair with monospace for code
            pairs.append({
                'primary': primary_font['name'],
                'secondary': 'JetBrains Mono',
                'use_case': 'Code blocks'
            })
        elif primary_font['fallback'] == 'serif':
            # Pair serif with sans-serif
            pairs.append({
                'primary': primary_font['name'],
                'secondary': 'Inter',
                'use_case': 'Modern contrast'
            })
        
        return pairs
    
    def _create_responsive_typography(self, type_scale: Dict) -> Dict:
        """Create responsive typography system"""
        
        return {
            'mobile': {
                'base_size': '14px',
                'scale_factor': 0.9,
                'line_height_factor': 1.1
            },
            'tablet': {
                'base_size': '15px',
                'scale_factor': 0.95,
                'line_height_factor': 1.05
            },
            'desktop': {
                'base_size': '16px',
                'scale_factor': 1.0,
                'line_height_factor': 1.0
            },
            'wide': {
                'base_size': '18px',
                'scale_factor': 1.1,
                'line_height_factor': 1.0
            }
        }
    
    def _generate_typography_css(
        self,
        font_stack: Dict,
        type_scale: Dict,
        weights: Dict,
        line_heights: Dict,
        letter_spacing: Dict
    ) -> str:
        """Generate CSS for typography"""
        
        css = ""
        
        # Font import if needed
        if 'import' in font_stack:
            css += f"@import url('{font_stack['import']}');\n\n"
        
        # Root variables
        css += ":root {\n"
        css += f"  --font-family: {font_stack['fonts']};\n"
        
        # Type scale
        for key, size in type_scale['sizes'].items():
            css += f"  --font-size-{key}: {size}rem;\n"
        
        # Weights
        for key, weight in weights.items():
            css += f"  --font-weight-{key}: {weight};\n"
        
        # Line heights
        for key, height in line_heights.items():
            css += f"  --line-height-{key}: {height};\n"
        
        # Letter spacing
        for key, spacing in letter_spacing.items():
            css += f"  --letter-spacing-{key}: {spacing};\n"
        
        css += "}\n\n"
        
        # Typography classes
        css += self._generate_typography_classes(type_scale, weights, line_heights)
        
        return css
    
    def _generate_typography_classes(
        self,
        type_scale: Dict,
        weights: Dict,
        line_heights: Dict
    ) -> str:
        """Generate utility classes for typography"""
        
        css = "/* Typography Classes */\n"
        
        # Heading classes
        headings = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        sizes = list(type_scale['sizes'].values())
        
        for i, heading in enumerate(headings):
            if i < len(sizes):
                css += f".{heading} {{\n"
                css += f"  font-size: {sizes[-(i+1)]}rem;\n"
                css += f"  font-weight: var(--font-weight-heading);\n"
                css += f"  line-height: var(--line-height-heading);\n"
                css += "}\n\n"
        
        # Body classes
        css += ".body-text {\n"
        css += "  font-size: var(--font-size-base);\n"
        css += "  font-weight: var(--font-weight-body);\n"
        css += "  line-height: var(--line-height-body);\n"
        css += "}\n\n"
        
        return css
    
    def _optimize_performance(self, font_stack: Dict) -> Dict[str, Any]:
        """Optimize font loading performance"""
        
        optimizations = {
            'preload': [],
            'font_display': 'swap',
            'subset': 'latin',
            'variable_fonts': False
        }
        
        if font_stack['performance'] != 'excellent':
            optimizations['preload'] = [
                'woff2 format for modern browsers',
                'Critical font weights only'
            ]
            
            optimizations['recommendations'] = [
                'Use font-display: swap',
                'Subset fonts to required characters',
                'Consider variable fonts for multiple weights',
                'Implement fallback fonts'
            ]
        
        return optimizations
    
    def _generate_guidelines(self, font_stack: Dict, type_scale: Dict) -> List[str]:
        """Generate typography usage guidelines"""
        
        guidelines = [
            f"Primary font: {font_stack['name']}",
            f"Type scale: {type_scale['name']} ({type_scale['ratio']})",
            "Use consistent font weights across similar elements",
            "Maintain hierarchy through size and weight",
            "Ensure minimum 16px for body text on mobile",
            "Test readability across devices",
            "Consider loading performance"
        ]
        
        if font_stack['licensing'] != 'free':
            guidelines.append(f"Check licensing requirements for {font_stack['name']}")
        
        return guidelines
    
    def _generate_scale(self, ratio: float) -> Dict[str, float]:
        """Generate type scale sizes"""
        base = 1.0  # 1rem
        
        return {
            'xs': round(base / (ratio ** 2), 3),
            'sm': round(base / ratio, 3),
            'base': base,
            'lg': round(base * ratio, 3),
            'xl': round(base * (ratio ** 2), 3),
            '2xl': round(base * (ratio ** 3), 3),
            '3xl': round(base * (ratio ** 4), 3),
            '4xl': round(base * (ratio ** 5), 3),
            '5xl': round(base * (ratio ** 6), 3)
        }