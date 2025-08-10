"""
Theme Generator Module
Generates comprehensive UI themes with all design tokens
"""

from typing import Dict, List, Any, Optional
import json


class ThemeGenerator:
    """Generates complete theme configurations"""
    
    def __init__(self):
        self.theme_presets = {
            'light': {
                'name': 'Light Theme',
                'mode': 'light',
                'primary_bg': '#FFFFFF',
                'secondary_bg': '#F5F5F5',
                'text': '#212121',
                'border': '#E0E0E0'
            },
            'dark': {
                'name': 'Dark Theme',
                'mode': 'dark',
                'primary_bg': '#121212',
                'secondary_bg': '#1E1E1E',
                'text': '#E0E0E0',
                'border': '#333333'
            },
            'high_contrast': {
                'name': 'High Contrast',
                'mode': 'contrast',
                'primary_bg': '#000000',
                'secondary_bg': '#FFFFFF',
                'text': '#FFFFFF',
                'border': '#FFFFFF'
            },
            'sepia': {
                'name': 'Sepia Theme',
                'mode': 'sepia',
                'primary_bg': '#F4EADC',
                'secondary_bg': '#EBE0D0',
                'text': '#5C4B37',
                'border': '#D4C4B0'
            }
        }
        
        self.spacing_systems = {
            'compact': {
                'base': 4,
                'scale': [0, 4, 8, 12, 16, 20, 24, 32, 40, 48]
            },
            'comfortable': {
                'base': 8,
                'scale': [0, 8, 16, 24, 32, 40, 48, 64, 80, 96]
            },
            'spacious': {
                'base': 12,
                'scale': [0, 12, 24, 36, 48, 60, 72, 96, 120, 144]
            }
        }
        
        self.radius_systems = {
            'sharp': {
                'none': '0',
                'sm': '2px',
                'md': '4px',
                'lg': '6px',
                'xl': '8px',
                'full': '9999px'
            },
            'rounded': {
                'none': '0',
                'sm': '4px',
                'md': '8px',
                'lg': '12px',
                'xl': '16px',
                'full': '9999px'
            },
            'smooth': {
                'none': '0',
                'sm': '8px',
                'md': '12px',
                'lg': '16px',
                'xl': '24px',
                'full': '9999px'
            }
        }
        
        self.shadow_systems = {
            'subtle': {
                'none': 'none',
                'sm': '0 1px 2px rgba(0,0,0,0.05)',
                'md': '0 2px 4px rgba(0,0,0,0.06)',
                'lg': '0 4px 6px rgba(0,0,0,0.07)',
                'xl': '0 8px 10px rgba(0,0,0,0.08)'
            },
            'material': {
                'none': 'none',
                'sm': '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)',
                'md': '0 3px 6px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12)',
                'lg': '0 10px 20px rgba(0,0,0,0.15), 0 3px 6px rgba(0,0,0,0.10)',
                'xl': '0 15px 25px rgba(0,0,0,0.15), 0 5px 10px rgba(0,0,0,0.05)'
            },
            'neumorphic': {
                'none': 'none',
                'sm': '2px 2px 4px #d1d1d1, -2px -2px 4px #ffffff',
                'md': '5px 5px 10px #d1d1d1, -5px -5px 10px #ffffff',
                'lg': '10px 10px 20px #d1d1d1, -10px -10px 20px #ffffff',
                'xl': '20px 20px 40px #d1d1d1, -20px -20px 40px #ffffff'
            }
        }
        
        self.transition_systems = {
            'instant': {
                'fast': '50ms',
                'normal': '100ms',
                'slow': '150ms'
            },
            'smooth': {
                'fast': '150ms',
                'normal': '250ms',
                'slow': '350ms'
            },
            'relaxed': {
                'fast': '250ms',
                'normal': '400ms',
                'slow': '600ms'
            }
        }
        
        self.z_index_system = {
            'dropdown': 1000,
            'sticky': 1020,
            'fixed': 1030,
            'modal_backdrop': 1040,
            'modal': 1050,
            'popover': 1060,
            'tooltip': 1070,
            'toast': 1080
        }
    
    def generate(
        self,
        project_type: str,
        brand_colors: Dict[str, str],
        design_system: str,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate complete theme
        
        Args:
            project_type: Type of project
            brand_colors: Brand color palette
            design_system: Selected design system
            preferences: User preferences
            
        Returns:
            Complete theme configuration
        """
        # Select base theme
        base_theme = self._select_base_theme(project_type, preferences)
        
        # Generate color tokens
        color_tokens = self._generate_color_tokens(brand_colors, base_theme)
        
        # Generate spacing tokens
        spacing_tokens = self._generate_spacing_tokens(project_type)
        
        # Generate typography tokens
        typography_tokens = self._generate_typography_tokens(design_system)
        
        # Generate component tokens
        component_tokens = self._generate_component_tokens(
            design_system,
            color_tokens,
            spacing_tokens
        )
        
        # Generate motion tokens
        motion_tokens = self._generate_motion_tokens(preferences)
        
        # Generate elevation tokens
        elevation_tokens = self._generate_elevation_tokens(design_system)
        
        # Create theme variants
        variants = self._create_theme_variants(color_tokens)
        
        # Generate CSS variables
        css_variables = self._generate_css_variables(
            color_tokens,
            spacing_tokens,
            typography_tokens,
            component_tokens,
            motion_tokens,
            elevation_tokens
        )
        
        # Generate theme configuration
        config = self._generate_theme_config(
            base_theme,
            color_tokens,
            spacing_tokens,
            typography_tokens,
            component_tokens
        )
        
        return {
            'base': base_theme,
            'tokens': {
                'colors': color_tokens,
                'spacing': spacing_tokens,
                'typography': typography_tokens,
                'components': component_tokens,
                'motion': motion_tokens,
                'elevation': elevation_tokens
            },
            'variants': variants,
            'css_variables': css_variables,
            'config': config,
            'export': self._generate_exports(config),
            'guidelines': self._generate_guidelines()
        }
    
    def _select_base_theme(
        self,
        project_type: str,
        preferences: Optional[Dict]
    ) -> Dict[str, Any]:
        """Select base theme preset"""
        if preferences and 'theme_mode' in preferences:
            return self.theme_presets.get(
                preferences['theme_mode'],
                self.theme_presets['light']
            )
        
        # Default selections based on project type
        if project_type in ['dashboard', 'admin']:
            return self.theme_presets['light']
        elif project_type in ['creative', 'portfolio']:
            return self.theme_presets['dark']
        else:
            return self.theme_presets['light']
    
    def _generate_color_tokens(
        self,
        brand_colors: Dict[str, str],
        base_theme: Dict
    ) -> Dict[str, Any]:
        """Generate color design tokens"""
        tokens = {
            'primary': brand_colors.get('primary', '#6200EA'),
            'secondary': brand_colors.get('secondary', '#00BCD4'),
            'tertiary': brand_colors.get('tertiary', '#FFC107'),
            'success': brand_colors.get('success', '#4CAF50'),
            'warning': brand_colors.get('warning', '#FF9800'),
            'error': brand_colors.get('error', '#F44336'),
            'info': brand_colors.get('info', '#2196F3'),
            
            'background': {
                'primary': base_theme['primary_bg'],
                'secondary': base_theme['secondary_bg'],
                'tertiary': self._lighten(base_theme['secondary_bg'], 0.05)
            },
            
            'text': {
                'primary': base_theme['text'],
                'secondary': self._lighten(base_theme['text'], 0.3),
                'tertiary': self._lighten(base_theme['text'], 0.5),
                'disabled': self._lighten(base_theme['text'], 0.6),
                'inverse': base_theme['primary_bg']
            },
            
            'border': {
                'default': base_theme['border'],
                'light': self._lighten(base_theme['border'], 0.2),
                'dark': self._darken(base_theme['border'], 0.2)
            },
            
            'surface': {
                'default': base_theme['primary_bg'],
                'raised': self._lighten(base_theme['primary_bg'], 0.02),
                'overlay': self._darken(base_theme['primary_bg'], 0.02),
                'scrim': 'rgba(0,0,0,0.5)'
            }
        }
        
        # Generate shades for primary colors
        for color_name in ['primary', 'secondary', 'success', 'warning', 'error']:
            if color_name in tokens:
                tokens[f'{color_name}_shades'] = self._generate_color_shades(
                    tokens[color_name]
                )
        
        return tokens
    
    def _generate_spacing_tokens(self, project_type: str) -> Dict[str, Any]:
        """Generate spacing design tokens"""
        # Select spacing system
        if project_type in ['dashboard', 'admin']:
            system = self.spacing_systems['compact']
        elif project_type in ['blog', 'article']:
            system = self.spacing_systems['spacious']
        else:
            system = self.spacing_systems['comfortable']
        
        tokens = {
            'base': system['base'],
            'scale': {}
        }
        
        # Generate named scale
        names = ['none', 'xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl']
        for i, name in enumerate(names):
            if i < len(system['scale']):
                tokens['scale'][name] = f"{system['scale'][i]}px"
        
        # Add component-specific spacing
        tokens['components'] = {
            'button_padding': f"{system['base'] * 2}px {system['base'] * 3}px",
            'card_padding': f"{system['base'] * 3}px",
            'input_padding': f"{system['base'] * 1.5}px {system['base'] * 2}px",
            'modal_padding': f"{system['base'] * 4}px",
            'section_margin': f"{system['base'] * 8}px"
        }
        
        return tokens
    
    def _generate_typography_tokens(self, design_system: str) -> Dict[str, Any]:
        """Generate typography design tokens"""
        # Font families based on design system
        font_map = {
            'material': 'Roboto, sans-serif',
            'ant': '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
            'carbon': 'IBM Plex Sans, sans-serif',
            'fluent': 'Segoe UI, sans-serif',
            'spectrum': 'Adobe Clean, sans-serif'
        }
        
        return {
            'font_family': {
                'sans': font_map.get(design_system, 'Inter, sans-serif'),
                'serif': 'Georgia, serif',
                'mono': 'JetBrains Mono, monospace'
            },
            'font_size': {
                'xs': '0.75rem',
                'sm': '0.875rem',
                'base': '1rem',
                'lg': '1.125rem',
                'xl': '1.25rem',
                '2xl': '1.5rem',
                '3xl': '1.875rem',
                '4xl': '2.25rem',
                '5xl': '3rem'
            },
            'font_weight': {
                'light': 300,
                'normal': 400,
                'medium': 500,
                'semibold': 600,
                'bold': 700
            },
            'line_height': {
                'tight': 1.25,
                'normal': 1.5,
                'relaxed': 1.75
            },
            'letter_spacing': {
                'tight': '-0.05em',
                'normal': '0',
                'wide': '0.05em'
            }
        }
    
    def _generate_component_tokens(
        self,
        design_system: str,
        colors: Dict,
        spacing: Dict
    ) -> Dict[str, Any]:
        """Generate component-specific tokens"""
        # Select radius system
        if design_system == 'material':
            radius = self.radius_systems['rounded']
        elif design_system == 'carbon':
            radius = self.radius_systems['sharp']
        else:
            radius = self.radius_systems['rounded']
        
        return {
            'button': {
                'radius': radius['md'],
                'padding': spacing['components']['button_padding'],
                'font_weight': 500,
                'text_transform': 'none',
                'min_height': '36px'
            },
            'card': {
                'radius': radius['lg'],
                'padding': spacing['components']['card_padding'],
                'shadow': self.shadow_systems['subtle']['md'],
                'background': colors['surface']['default']
            },
            'input': {
                'radius': radius['md'],
                'padding': spacing['components']['input_padding'],
                'border_width': '1px',
                'min_height': '40px',
                'background': colors['surface']['default']
            },
            'modal': {
                'radius': radius['xl'],
                'padding': spacing['components']['modal_padding'],
                'shadow': self.shadow_systems['material']['xl'],
                'max_width': '600px',
                'backdrop': colors['surface']['scrim']
            },
            'badge': {
                'radius': radius['full'],
                'padding': '2px 8px',
                'font_size': '0.75rem',
                'font_weight': 600
            },
            'chip': {
                'radius': radius['full'],
                'padding': '4px 12px',
                'font_size': '0.875rem'
            },
            'tooltip': {
                'radius': radius['sm'],
                'padding': '4px 8px',
                'font_size': '0.875rem',
                'background': 'rgba(0,0,0,0.9)'
            }
        }
    
    def _generate_motion_tokens(self, preferences: Optional[Dict]) -> Dict[str, Any]:
        """Generate motion design tokens"""
        # Select transition system
        if preferences and preferences.get('reduced_motion'):
            system = self.transition_systems['instant']
        elif preferences and preferences.get('smooth_animations'):
            system = self.transition_systems['relaxed']
        else:
            system = self.transition_systems['smooth']
        
        return {
            'duration': {
                'instant': '0ms',
                'fast': system['fast'],
                'normal': system['normal'],
                'slow': system['slow']
            },
            'easing': {
                'linear': 'linear',
                'ease_in': 'cubic-bezier(0.4, 0, 1, 1)',
                'ease_out': 'cubic-bezier(0, 0, 0.2, 1)',
                'ease_in_out': 'cubic-bezier(0.4, 0, 0.2, 1)',
                'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
            },
            'property': {
                'color': 'color',
                'background': 'background-color',
                'border': 'border-color',
                'shadow': 'box-shadow',
                'transform': 'transform',
                'opacity': 'opacity',
                'all': 'all'
            }
        }
    
    def _generate_elevation_tokens(self, design_system: str) -> Dict[str, Any]:
        """Generate elevation design tokens"""
        # Select shadow system
        if design_system == 'material':
            shadows = self.shadow_systems['material']
        elif design_system == 'neumorphic':
            shadows = self.shadow_systems['neumorphic']
        else:
            shadows = self.shadow_systems['subtle']
        
        return {
            'z_index': self.z_index_system,
            'shadows': shadows,
            'blur': {
                'none': '0',
                'sm': '4px',
                'md': '8px',
                'lg': '16px',
                'xl': '24px'
            }
        }
    
    def _create_theme_variants(self, colors: Dict) -> Dict[str, Dict]:
        """Create theme variants (light/dark)"""
        return {
            'light': {
                'colors': colors,
                'mode': 'light'
            },
            'dark': {
                'colors': self._create_dark_variant(colors),
                'mode': 'dark'
            },
            'auto': {
                'colors': colors,
                'mode': 'auto',
                'media_query': '@media (prefers-color-scheme: dark)'
            }
        }
    
    def _create_dark_variant(self, light_colors: Dict) -> Dict:
        """Create dark variant of colors"""
        # This would normally do proper color transformation
        # For now, returning a modified version
        dark = light_colors.copy()
        
        # Invert backgrounds and text
        dark['background'] = {
            'primary': '#121212',
            'secondary': '#1E1E1E',
            'tertiary': '#2A2A2A'
        }
        
        dark['text'] = {
            'primary': '#E0E0E0',
            'secondary': '#A0A0A0',
            'tertiary': '#707070',
            'disabled': '#505050',
            'inverse': '#121212'
        }
        
        return dark
    
    def _generate_css_variables(self, *token_groups) -> str:
        """Generate CSS custom properties"""
        css = ":root {\n"
        
        for tokens in token_groups:
            css += self._tokens_to_css_vars(tokens)
        
        css += "}\n"
        
        return css
    
    def _tokens_to_css_vars(self, tokens: Dict, prefix: str = "") -> str:
        """Convert tokens to CSS variables"""
        css = ""
        
        for key, value in tokens.items():
            var_name = f"--{prefix}{key}".replace('_', '-')
            
            if isinstance(value, dict):
                css += self._tokens_to_css_vars(value, f"{key}-")
            else:
                css += f"  {var_name}: {value};\n"
        
        return css
    
    def _generate_theme_config(
        self,
        base: Dict,
        colors: Dict,
        spacing: Dict,
        typography: Dict,
        components: Dict
    ) -> Dict:
        """Generate theme configuration object"""
        return {
            'name': base['name'],
            'mode': base['mode'],
            'colors': colors,
            'spacing': spacing,
            'typography': typography,
            'components': components,
            'breakpoints': {
                'sm': '640px',
                'md': '768px',
                'lg': '1024px',
                'xl': '1280px',
                '2xl': '1536px'
            }
        }
    
    def _generate_exports(self, config: Dict) -> Dict[str, str]:
        """Generate export formats"""
        return {
            'json': json.dumps(config, indent=2),
            'javascript': f"export const theme = {json.dumps(config, indent=2)};",
            'typescript': f"export const theme: Theme = {json.dumps(config, indent=2)};",
            'scss': self._config_to_scss(config),
            'css': self._config_to_css(config)
        }
    
    def _config_to_scss(self, config: Dict) -> str:
        """Convert config to SCSS variables"""
        scss = "// Theme Variables\n"
        
        def dict_to_scss(d: Dict, prefix: str = "$"):
            result = ""
            for key, value in d.items():
                if isinstance(value, dict):
                    result += dict_to_scss(value, f"{prefix}{key}-")
                else:
                    result += f"{prefix}{key}: {value};\n"
            return result
        
        scss += dict_to_scss(config)
        return scss
    
    def _config_to_css(self, config: Dict) -> str:
        """Convert config to CSS"""
        return self._generate_css_variables(
            config.get('colors', {}),
            config.get('spacing', {}),
            config.get('typography', {}),
            config.get('components', {})
        )
    
    def _lighten(self, color: str, amount: float) -> str:
        """Lighten a color (simplified)"""
        # This would normally use proper color manipulation
        return f"lighten({color}, {amount * 100}%)"
    
    def _darken(self, color: str, amount: float) -> str:
        """Darken a color (simplified)"""
        return f"darken({color}, {amount * 100}%)"
    
    def _generate_color_shades(self, base_color: str) -> Dict[str, str]:
        """Generate color shade variations"""
        return {
            '50': self._lighten(base_color, 0.9),
            '100': self._lighten(base_color, 0.7),
            '200': self._lighten(base_color, 0.5),
            '300': self._lighten(base_color, 0.3),
            '400': self._lighten(base_color, 0.1),
            '500': base_color,
            '600': self._darken(base_color, 0.1),
            '700': self._darken(base_color, 0.3),
            '800': self._darken(base_color, 0.5),
            '900': self._darken(base_color, 0.7)
        }
    
    def _generate_guidelines(self) -> List[str]:
        """Generate theme usage guidelines"""
        return [
            "Use semantic color tokens instead of hardcoded values",
            "Maintain consistent spacing using the spacing scale",
            "Apply elevation tokens for depth hierarchy",
            "Use motion tokens for all animations",
            "Support both light and dark themes",
            "Test theme with different color blind modes",
            "Ensure sufficient color contrast for accessibility",
            "Use CSS variables for runtime theme switching",
            "Document any custom tokens added to the theme",
            "Keep theme tokens in sync across platforms"
        ]