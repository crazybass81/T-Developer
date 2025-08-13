"""🧬 Legacy Analyzer <6.5KB"""
import ast
import re
from pathlib import Path
from typing import Dict, List


class LegacyAnalyzer:
    """Analyzes legacy agents - ultra compact"""
    
    def __init__(self):
        self.patterns = {
            r'class\s+\w+\(object\)': 'old_class',
            r'print\s+["\']': 'print_stmt',
            r'\.has_key\(': 'has_key',
            r'xrange\(': 'xrange',
            r'unicode\(': 'unicode'
        }
    
    def analyze(self, path: str) -> Dict:
        """Analyze agent file"""
        p = Path(path)
        if not p.exists():
            return {"name": p.stem, "error": "not found"}
        
        try:
            code = p.read_text()
            tree = ast.parse(code)
            
            # Metrics
            lines = len(code.splitlines())
            classes = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
            funcs = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef))
            
            # Dependencies
            deps = set()
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    deps.update(a.name.split('.')[0] for a in n.names)
                elif isinstance(n, ast.ImportFrom) and n.module:
                    deps.add(n.module.split('.')[0])
            
            # Patterns
            found = [name for pat, name in self.patterns.items() if re.search(pat, code)]
            
            # Complexity
            score = (lines > 200) + (lines > 500) + len(found) // 2 + len(deps) // 5
            complexity = "low" if score <= 2 else "medium" if score <= 4 else "high"
            
            return {
                "name": p.stem,
                "lines": lines,
                "classes": classes,
                "funcs": funcs,
                "deps": list(deps),
                "patterns": found,
                "complexity": complexity
            }
        except Exception as e:
            return {"name": p.stem, "error": str(e)}
    
    def batch(self, dir_path: str) -> List[Dict]:
        """Analyze directory"""
        results = []
        for f in Path(dir_path).glob("**/*.py"):
            if not f.name.startswith('__'):
                results.append(self.analyze(str(f)))
        return results
    
    def report(self, results: List[Dict]) -> Dict:
        """Generate report"""
        if not results:
            return {}
        
        total = len(results)
        errors = sum(1 for r in results if "error" in r)
        
        complexity = {"low": 0, "medium": 0, "high": 0}
        for r in results:
            if c := r.get("complexity"):
                complexity[c] += 1
        
        # Effort estimate
        points = complexity["low"] + complexity["medium"] * 3 + complexity["high"] * 8
        effort = "1-2 days" if points < 10 else "3-5 days" if points < 30 else "1+ week"
        
        return {
            "total": total,
            "errors": errors,
            "complexity": complexity,
            "effort": effort
        }