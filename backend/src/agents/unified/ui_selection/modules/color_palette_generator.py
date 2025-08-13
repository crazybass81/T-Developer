"""
Color Palette Generator Module
Generates harmonious color palettes for UI design
"""

from typing import Dict, List, Tuple, Optional
import math
import colorsys


class ColorPaletteGenerator:
    """Generates and optimizes color palettes for UI design"""

    def __init__(self):
        self.color_schemes = {
            "monochromatic": self._generate_monochromatic,
            "analogous": self._generate_analogous,
            "complementary": self._generate_complementary,
            "triadic": self._generate_triadic,
            "tetradic": self._generate_tetradic,
            "split_complementary": self._generate_split_complementary,
        }

        self.brand_colors = {
            "tech": {
                "primary": "#2563EB",  # Blue
                "secondary": "#10B981",  # Green
                "accent": "#F59E0B",  # Amber
            },
            "corporate": {
                "primary": "#1E40AF",  # Dark Blue
                "secondary": "#6B7280",  # Gray
                "accent": "#DC2626",  # Red
            },
            "creative": {
                "primary": "#8B5CF6",  # Purple
                "secondary": "#EC4899",  # Pink
                "accent": "#F59E0B",  # Amber
            },
            "health": {
                "primary": "#10B981",  # Green
                "secondary": "#06B6D4",  # Cyan
                "accent": "#3B82F6",  # Blue
            },
            "finance": {
                "primary": "#059669",  # Green
                "secondary": "#1E40AF",  # Blue
                "accent": "#DC2626",  # Red
            },
        }

        self.semantic_colors = {
            "success": "#10B981",
            "warning": "#F59E0B",
            "error": "#EF4444",
            "info": "#3B82F6",
        }

        self.accessibility_standards = {
            "WCAG_AA": 4.5,  # Contrast ratio for normal text
            "WCAG_AA_LARGE": 3.0,  # Contrast ratio for large text
            "WCAG_AAA": 7.0,  # Enhanced contrast ratio
            "WCAG_AAA_LARGE": 4.5,  # Enhanced for large text
        }

    def generate(
        self,
        base_color: Optional[str] = None,
        scheme_type: str = "analogous",
        brand_type: Optional[str] = None,
        preferences: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete color palette

        Args:
            base_color: Base color in hex format
            scheme_type: Type of color scheme
            brand_type: Type of brand/industry
            preferences: User preferences

        Returns:
            Complete color palette configuration
        """
        # Determine base color
        if not base_color:
            if brand_type and brand_type in self.brand_colors:
                base_color = self.brand_colors[brand_type]["primary"]
            else:
                base_color = "#3B82F6"  # Default blue

        # Generate color scheme
        scheme_generator = self.color_schemes.get(scheme_type, self._generate_analogous)
        colors = scheme_generator(base_color)

        # Generate shades and tints
        palette = self._generate_full_palette(colors)

        # Add semantic colors
        palette["semantic"] = self.semantic_colors

        # Generate dark mode variant
        dark_palette = self._generate_dark_variant(palette)

        # Check accessibility
        accessibility = self._check_accessibility(palette)

        # Generate CSS variables
        css_variables = self._generate_css_variables(palette)

        # Generate usage guidelines
        guidelines = self._generate_usage_guidelines(palette, scheme_type)

        return {
            "palette": palette,
            "dark_mode": dark_palette,
            "scheme_type": scheme_type,
            "accessibility": accessibility,
            "css_variables": css_variables,
            "guidelines": guidelines,
            "variations": self._generate_variations(base_color),
        }

    def _generate_monochromatic(self, base_color: str) -> List[str]:
        """Generate monochromatic color scheme"""
        h, s, v = self._hex_to_hsv(base_color)

        colors = []
        # Vary lightness
        for i in range(5):
            new_v = max(0.2, min(1.0, v + (i - 2) * 0.15))
            colors.append(self._hsv_to_hex(h, s, new_v))

        return colors

    def _generate_analogous(self, base_color: str) -> List[str]:
        """Generate analogous color scheme"""
        h, s, v = self._hex_to_hsv(base_color)

        colors = [base_color]
        # Add colors 30 degrees apart
        for offset in [-30, 30, -60, 60]:
            new_h = (h + offset / 360) % 1.0
            colors.append(self._hsv_to_hex(new_h, s, v))

        return colors

    def _generate_complementary(self, base_color: str) -> List[str]:
        """Generate complementary color scheme"""
        h, s, v = self._hex_to_hsv(base_color)

        colors = [base_color]
        # Add complementary color (180 degrees)
        comp_h = (h + 0.5) % 1.0
        colors.append(self._hsv_to_hex(comp_h, s, v))

        # Add variations
        for offset in [-0.05, 0.05]:
            colors.append(self._hsv_to_hex(h, s, max(0.2, min(1.0, v + offset))))
            colors.append(self._hsv_to_hex(comp_h, s, max(0.2, min(1.0, v + offset))))

        return colors[:5]

    def _generate_triadic(self, base_color: str) -> List[str]:
        """Generate triadic color scheme"""
        h, s, v = self._hex_to_hsv(base_color)

        colors = [base_color]
        # Add colors 120 degrees apart
        for offset in [120, 240]:
            new_h = (h + offset / 360) % 1.0
            colors.append(self._hsv_to_hex(new_h, s, v))

        # Add variations
        colors.append(self._hsv_to_hex(h, s * 0.7, v))
        colors.append(self._hsv_to_hex(h, s, v * 0.8))

        return colors

    def _generate_tetradic(self, base_color: str) -> List[str]:
        """Generate tetradic (square) color scheme"""
        h, s, v = self._hex_to_hsv(base_color)

        colors = [base_color]
        # Add colors 90 degrees apart
        for offset in [90, 180, 270]:
            new_h = (h + offset / 360) % 1.0
            colors.append(self._hsv_to_hex(new_h, s, v))

        # Add neutral
        colors.append(self._hsv_to_hex(h, s * 0.2, v))

        return colors

    def _generate_split_complementary(self, base_color: str) -> List[str]:
        """Generate split-complementary color scheme"""
        h, s, v = self._hex_to_hsv(base_color)

        colors = [base_color]
        # Add colors 150 and 210 degrees from base
        for offset in [150, 210]:
            new_h = (h + offset / 360) % 1.0
            colors.append(self._hsv_to_hex(new_h, s, v))

        # Add variations
        colors.append(self._hsv_to_hex(h, s * 0.6, v))
        colors.append(self._hsv_to_hex(h, s, v * 0.7))

        return colors

    def _generate_full_palette(self, colors: List[str]) -> Dict[str, Any]:
        """Generate full palette with shades and tints"""
        palette = {
            "primary": {},
            "secondary": {},
            "accent": {},
            "neutral": {},
            "background": {},
            "text": {},
        }

        # Assign colors to roles
        if len(colors) >= 1:
            palette["primary"] = self._generate_shades(colors[0])
        if len(colors) >= 2:
            palette["secondary"] = self._generate_shades(colors[1])
        if len(colors) >= 3:
            palette["accent"] = self._generate_shades(colors[2])

        # Generate neutrals
        palette["neutral"] = self._generate_neutrals(colors[0] if colors else "#000000")

        # Generate background colors
        palette["background"] = {
            "primary": "#FFFFFF",
            "secondary": "#F9FAFB",
            "tertiary": "#F3F4F6",
        }

        # Generate text colors
        palette["text"] = {
            "primary": "#111827",
            "secondary": "#4B5563",
            "tertiary": "#9CA3AF",
            "inverse": "#FFFFFF",
        }

        return palette

    def _generate_shades(self, base_color: str) -> Dict[str, str]:
        """Generate shades of a color"""
        h, s, v = self._hex_to_hsv(base_color)

        shades = {}
        shade_values = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]

        for i, shade in enumerate(shade_values):
            # Calculate value based on shade number
            factor = 1.0 - (i * 0.1)
            new_v = max(0.1, min(1.0, v * factor + (1 - factor) * 0.95))
            new_s = max(0.1, min(1.0, s * (0.5 + factor * 0.5)))

            shades[str(shade)] = self._hsv_to_hex(h, new_s, new_v)

        return shades

    def _generate_neutrals(self, base_color: str) -> Dict[str, str]:
        """Generate neutral colors based on base color"""
        h, _, _ = self._hex_to_hsv(base_color)

        neutrals = {}
        shade_values = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]

        for i, shade in enumerate(shade_values):
            # Very low saturation, varying value
            s = 0.05  # Very low saturation
            v = 1.0 - (i * 0.09)  # Decrease value

            neutrals[str(shade)] = self._hsv_to_hex(h, s, v)

        return neutrals

    def _generate_dark_variant(self, palette: Dict) -> Dict[str, Any]:
        """Generate dark mode variant of palette"""
        dark_palette = {}

        for key, value in palette.items():
            if isinstance(value, dict):
                dark_palette[key] = {}
                for sub_key, color in value.items():
                    if isinstance(color, str) and color.startswith("#"):
                        # Invert and adjust color for dark mode
                        dark_palette[key][sub_key] = self._adjust_for_dark_mode(color)
                    else:
                        dark_palette[key][sub_key] = color
            else:
                dark_palette[key] = value

        # Override specific colors for dark mode
        dark_palette["background"] = {
            "primary": "#111827",
            "secondary": "#1F2937",
            "tertiary": "#374151",
        }

        dark_palette["text"] = {
            "primary": "#F9FAFB",
            "secondary": "#D1D5DB",
            "tertiary": "#9CA3AF",
            "inverse": "#111827",
        }

        return dark_palette

    def _adjust_for_dark_mode(self, color: str) -> str:
        """Adjust color for dark mode"""
        h, s, v = self._hex_to_hsv(color)

        # Reduce value for dark mode, increase saturation slightly
        new_v = max(0.3, v * 0.8)
        new_s = min(1.0, s * 1.1)

        return self._hsv_to_hex(h, new_s, new_v)

    def _check_accessibility(self, palette: Dict) -> Dict[str, Any]:
        """Check accessibility of color combinations"""
        results = {
            "passes_AA": [],
            "passes_AAA": [],
            "fails": [],
            "recommendations": [],
        }

        # Check primary text on backgrounds
        text_primary = palette["text"]["primary"]

        for bg_key, bg_color in palette["background"].items():
            if isinstance(bg_color, str) and bg_color.startswith("#"):
                ratio = self._calculate_contrast_ratio(text_primary, bg_color)

                combo = f"text-primary on background-{bg_key}"
                if ratio >= self.accessibility_standards["WCAG_AAA"]:
                    results["passes_AAA"].append({"combination": combo, "ratio": ratio})
                elif ratio >= self.accessibility_standards["WCAG_AA"]:
                    results["passes_AA"].append({"combination": combo, "ratio": ratio})
                else:
                    results["fails"].append(
                        {
                            "combination": combo,
                            "ratio": ratio,
                            "required": self.accessibility_standards["WCAG_AA"],
                        }
                    )

        # Generate recommendations
        if results["fails"]:
            results["recommendations"].append(
                "Consider adjusting text or background colors for better contrast"
            )

        return results

    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors"""
        l1 = self._get_relative_luminance(color1)
        l2 = self._get_relative_luminance(color2)

        # Ensure l1 is the lighter color
        if l1 < l2:
            l1, l2 = l2, l1

        return (l1 + 0.05) / (l2 + 0.05)

    def _get_relative_luminance(self, color: str) -> float:
        """Calculate relative luminance of a color"""
        r, g, b = self._hex_to_rgb(color)

        # Convert to linear RGB
        def linearize(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4

        r_lin = linearize(r)
        g_lin = linearize(g)
        b_lin = linearize(b)

        # Calculate luminance
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    def _generate_css_variables(self, palette: Dict) -> str:
        """Generate CSS variables for palette"""
        css = ":root {\n"

        for category, colors in palette.items():
            if isinstance(colors, dict):
                for key, value in colors.items():
                    if isinstance(value, str) and value.startswith("#"):
                        var_name = f"--color-{category}-{key}".replace("_", "-")
                        css += f"  {var_name}: {value};\n"

        css += "}\n"
        return css

    def _generate_usage_guidelines(self, palette: Dict, scheme_type: str) -> List[str]:
        """Generate usage guidelines for palette"""
        guidelines = [
            f"Color scheme type: {scheme_type}",
            "Use primary color for main actions and brand elements",
            "Use secondary color for supporting elements",
            "Use accent color sparingly for emphasis",
            "Maintain consistent color usage across components",
            "Ensure text has sufficient contrast on backgrounds",
            "Test colors with color blindness simulators",
        ]

        if scheme_type == "monochromatic":
            guidelines.append("Use different shades to create hierarchy")
        elif scheme_type == "complementary":
            guidelines.append("Balance warm and cool colors")

        return guidelines

    def _generate_variations(self, base_color: str) -> List[Dict]:
        """Generate color variations"""
        variations = []

        for scheme_type in ["monochromatic", "analogous", "complementary"]:
            scheme_func = self.color_schemes[scheme_type]
            colors = scheme_func(base_color)

            variations.append(
                {
                    "type": scheme_type,
                    "colors": colors[:3],
                    "preview": self._generate_preview_style(colors[:3]),
                }
            )

        return variations

    def _generate_preview_style(self, colors: List[str]) -> str:
        """Generate CSS for color preview"""
        gradients = ", ".join(colors)
        return f"linear-gradient(90deg, {gradients})"

    # Utility methods
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex to RGB"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB to hex"""
        return f"#{r:02x}{g:02x}{b:02x}"

    def _hex_to_hsv(self, hex_color: str) -> Tuple[float, float, float]:
        """Convert hex to HSV"""
        r, g, b = self._hex_to_rgb(hex_color)
        return colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    def _hsv_to_hex(self, h: float, s: float, v: float) -> str:
        """Convert HSV to hex"""
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return self._rgb_to_hex(int(r * 255), int(g * 255), int(b * 255))
