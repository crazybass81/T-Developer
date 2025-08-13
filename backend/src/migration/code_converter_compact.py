"""🧬 Code Converter <6.5KB"""
import ast
import re
from pathlib import Path
from typing import Tuple


class CodeConverter:
    """Converts legacy code - ultra compact"""
    
    def __init__(self):
        self.rules = [
            ('print ', 'print('),
            ('xrange(', 'range('),
            ('unicode(', 'str('),
            ('.has_key(', ' in '),
            ('<>', '!='),
            ('.iteritems()', '.items()'),
            ('.iterkeys()', '.keys()'),
            ('.itervalues()', '.values()'),
            ('import urllib2', 'import urllib.request'),
            ('import urlparse', 'import urllib.parse'),
            ('import ConfigParser', 'import configparser'),
            ('import Queue', 'import queue'),
        ]
        
        self.regex_rules = [
            (r'class (\w+)\(object\):', r'class \1:'),
            (r'except (\w+), (\w+):', r'except \1 as \2:'),
        ]
    
    def convert(self, input_path: str, output_path: str = None) -> Tuple[bool, str]:
        """Convert file"""
        try:
            p = Path(input_path)
            if not p.exists():
                return False, "Not found"
            
            code = p.read_text()
            
            # Apply simple replacements
            for old, new in self.rules:
                code = code.replace(old, new)
            
            # Apply regex replacements
            for pattern, repl in self.regex_rules:
                code = re.sub(pattern, repl, code)
            
            # Fix print statements
            code = self._fix_print(code)
            
            # Add type hints (basic)
            code = self._add_hints(code)
            
            # Validate
            try:
                ast.parse(code)
            except SyntaxError:
                return False, "Syntax error"
            
            # Save
            if output_path:
                Path(output_path).write_text(code)
                return True, "Converted"
            
            return True, code
            
        except Exception as e:
            return False, str(e)
    
    def _fix_print(self, code: str) -> str:
        """Fix print statements"""
        lines = []
        for line in code.split('\n'):
            if 'print(' not in line and 'print ' in line:
                m = re.match(r'^(\s*)print\s+(.+)$', line)
                if m:
                    indent, content = m.groups()
                    if content.endswith(','):
                        lines.append(f'{indent}print({content[:-1]}, end="")')
                    else:
                        lines.append(f'{indent}print({content})')
                else:
                    lines.append(line)
            else:
                lines.append(line)
        return '\n'.join(lines)
    
    def _add_hints(self, code: str) -> str:
        """Add basic type hints"""
        lines = []
        has_hints = False
        
        for line in code.split('\n'):
            m = re.match(r'^(\s*)def\s+(\w+)\s*\((.*?)\)\s*:$', line)
            if m and '->' not in line:
                indent, name, params = m.groups()
                # Add return type based on name
                if name.startswith(('is_', 'has_')):
                    line = f'{indent}def {name}({params}) -> bool:'
                    has_hints = True
                elif name.startswith('get_'):
                    line = f'{indent}def {name}({params}) -> Any:'
                    has_hints = True
            lines.append(line)
        
        # Add typing import if needed
        if has_hints and 'from typing import' not in code:
            lines.insert(0, 'from typing import Any')
        
        return '\n'.join(lines)
    
    def to_agentcore(self, code: str) -> str:
        """Convert to AgentCore format"""
        # Add base class
        code = re.sub(r'class\s+(\w+Agent)\s*(\([^)]*\))?\s*:', r'class \1(AgentCore):', code)
        
        # Add imports
        if 'from agentcore import' not in code:
            code = 'from agentcore import AgentCore\n' + code
        
        # Add decorator
        code = re.sub(r'(class\s+\w+Agent)', r'@memory_limit(6.5)\n\1', code)
        
        return code