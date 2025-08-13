"""🧬 Code Converter Engine <6.5KB
Day 16: Migration Framework
Converts legacy code to modern patterns
"""
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CodeConverter:
    """Converts legacy agent code to modern patterns"""
    
    def __init__(self):
        # Conversion rules
        self.simple_replacements = {
            # Python 2 to 3
            'print ': 'print(',
            'xrange(': 'range(',
            'unicode(': 'str(',
            '.has_key(': ' in ',
            '<>': '!=',
            '.iteritems()': '.items()',
            '.iterkeys()': '.keys()',
            '.itervalues()': '.values()',
            'execfile(': 'exec(open(',
            # Old patterns
            'class (\\w+)\\(object\\):': 'class \\1:',
            'except (\\w+), (\\w+):': 'except \\1 as \\2:',
            # Imports
            'from __future__ import': '# from __future__ import',
            'import urllib2': 'import urllib.request',
            'import urlparse': 'import urllib.parse',
        }
        
        self.import_mappings = {
            'urllib2': 'urllib.request',
            'urlparse': 'urllib.parse',
            'ConfigParser': 'configparser',
            'Queue': 'queue',
            'cPickle': 'pickle',
            '__builtin__': 'builtins',
            'StringIO': 'io',
            'httplib': 'http.client',
        }

    def convert_file(self, input_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """Convert single file"""
        try:
            path = Path(input_path)
            if not path.exists():
                return False, f"File not found: {input_path}"
            
            code = path.read_text()
            
            # Apply conversions
            converted = self._apply_conversions(code)
            
            # Save or return
            if output_path:
                Path(output_path).write_text(converted)
                return True, f"Converted to {output_path}"
            else:
                return True, converted
                
        except Exception as e:
            return False, f"Conversion error: {e}"
    
    def _apply_conversions(self, code: str) -> str:
        """Apply all conversion rules"""
        # Simple text replacements
        for old, new in self.simple_replacements.items():
            if old.startswith('class ') or old.startswith('except '):
                # Use regex for complex patterns
                code = re.sub(old, new, code)
            else:
                code = code.replace(old, new)
        
        # Fix print statements
        code = self._fix_print_statements(code)
        
        # Update imports
        code = self._update_imports(code)
        
        # Add type hints (basic)
        code = self._add_basic_type_hints(code)
        
        # Convert to f-strings
        code = self._convert_to_fstrings(code)
        
        # Add async support where applicable
        code = self._add_async_support(code)
        
        return code
    
    def _fix_print_statements(self, code: str) -> str:
        """Fix print statements"""
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if 'print(' not in line and 'print ' in line:
                # Basic print statement conversion
                match = re.match(r'^(\s*)print\s+(.+)$', line)
                if match:
                    indent, content = match.groups()
                    # Handle trailing comma (no newline)
                    if content.endswith(','):
                        content = content[:-1]
                        fixed_lines.append(f'{indent}print({content}, end="")')
                    else:
                        fixed_lines.append(f'{indent}print({content})')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _update_imports(self, code: str) -> str:
        """Update import statements"""
        lines = code.split('\n')
        updated_lines = []
        
        for line in lines:
            # Check for import statements
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                for old_module, new_module in self.import_mappings.items():
                    if old_module in line:
                        line = line.replace(old_module, new_module)
            updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def _add_basic_type_hints(self, code: str) -> str:
        """Add basic type hints to functions"""
        # Simple pattern for def statements
        lines = code.split('\n')
        updated_lines = []
        
        for line in lines:
            # Basic function definition
            match = re.match(r'^(\s*)def\s+(\w+)\s*\((.*?)\)\s*:$', line)
            if match:
                indent, func_name, params = match.groups()
                
                # Skip if already has type hints
                if '->' in line or ':' in params:
                    updated_lines.append(line)
                    continue
                
                # Add basic return type hint
                if func_name.startswith('is_') or func_name.startswith('has_'):
                    line = f'{indent}def {func_name}({params}) -> bool:'
                elif func_name.startswith('get_'):
                    line = f'{indent}def {func_name}({params}) -> Any:'
                
            updated_lines.append(line)
        
        # Add typing import if type hints were added
        if ' -> ' in '\n'.join(updated_lines):
            if 'from typing import' not in code:
                updated_lines.insert(0, 'from typing import Any, Dict, List, Optional')
        
        return '\n'.join(updated_lines)
    
    def _convert_to_fstrings(self, code: str) -> str:
        """Convert string formatting to f-strings"""
        # Pattern for .format()
        pattern = r'"([^"]*?)"\s*\.format\((.*?)\)'
        
        def replace_format(match):
            template, args = match.groups()
            # Simple case: positional arguments
            if '{0}' in template or '{1}' in template:
                # Count placeholders
                placeholders = re.findall(r'\{(\d+)\}', template)
                if placeholders:
                    args_list = [a.strip() for a in args.split(',')]
                    for i, arg in enumerate(args_list[:len(placeholders)]):
                        template = template.replace(f'{{{i}}}', f'{{{arg}}}')
                    return f'f"{template}"'
            # Named arguments - skip for simplicity
            return match.group(0)
        
        code = re.sub(pattern, replace_format, code)
        
        # Pattern for % formatting
        pattern = r'"([^"]*?)"\s*%\s*\((.*?)\)'
        code = re.sub(pattern, lambda m: f'f"{m.group(1)}"', code)
        
        return code
    
    def _add_async_support(self, code: str) -> str:
        """Add async/await where applicable"""
        # Look for I/O operations that could be async
        io_patterns = [
            (r'def\s+(\w*fetch\w*)\s*\(', 'async def \\1('),
            (r'def\s+(\w*download\w*)\s*\(', 'async def \\1('),
            (r'def\s+(\w*upload\w*)\s*\(', 'async def \\1('),
            (r'def\s+(\w*process\w*)\s*\(', 'async def \\1('),
        ]
        
        for pattern, replacement in io_patterns:
            code = re.sub(pattern, replacement, code)
        
        # Add await for async calls
        if 'async def' in code:
            # Add asyncio import
            if 'import asyncio' not in code:
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        lines.insert(i, 'import asyncio')
                        break
                code = '\n'.join(lines)
        
        return code
    
    def convert_to_agentcore(self, code: str) -> str:
        """Convert to AgentCore compatible format"""
        # Add AgentCore base class
        code = re.sub(
            r'class\s+(\w+Agent)\s*(\([^)]*\))?\s*:',
            r'class \1(AgentCore):',
            code
        )
        
        # Add required imports
        if 'from agentcore import AgentCore' not in code:
            lines = code.split('\n')
            lines.insert(0, 'from agentcore import AgentCore')
            code = '\n'.join(lines)
        
        # Add memory constraint decorator
        code = re.sub(
            r'(class\s+\w+Agent\([^)]*\):)',
            r'@memory_limit(6.5)\n\1',
            code
        )
        
        return code
    
    def validate_conversion(self, code: str) -> Tuple[bool, List[str]]:
        """Validate converted code"""
        issues = []
        
        try:
            # Check syntax
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
            return False, issues
        
        # Check for remaining legacy patterns
        legacy_patterns = [
            ('print ', 'print statement'),
            ('xrange', 'xrange usage'),
            ('.has_key', 'dict.has_key'),
            ('execfile', 'execfile usage'),
        ]
        
        for pattern, desc in legacy_patterns:
            if pattern in code:
                issues.append(f"Legacy pattern found: {desc}")
        
        # Check size constraint
        size_kb = len(code.encode()) / 1024
        if size_kb > 6.5:
            issues.append(f"Size exceeds 6.5KB: {size_kb:.1f}KB")
        
        return len(issues) == 0, issues


# Example usage
if __name__ == "__main__":
    converter = CodeConverter()
    
    # Convert file
    success, result = converter.convert_file(
        "backend/src/agents/legacy/old_agent.py",
        "backend/src/agents/modern/new_agent.py"
    )
    
    if success:
        print(f"Conversion successful: {result}")
    else:
        print(f"Conversion failed: {result}")