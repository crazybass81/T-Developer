"""🧬 Compatibility Checker <6.5KB"""
import ast
from pathlib import Path
from typing import Dict, Set, Tuple


class CompatibilityChecker:
    """Checks compatibility - ultra compact"""
    
    def __init__(self):
        self.max_kb = 6.5
        self.required = {'__init__', 'process', 'validate_input', 'get_metadata'}
        self.allowed = {
            'ast', 'asyncio', 'dataclasses', 'datetime', 'enum',
            'functools', 'hashlib', 'json', 'logging', 'os',
            'pathlib', 're', 'sys', 'time', 'typing', 'uuid'
        }
    
    def check(self, path: str) -> Dict:
        """Check agent compatibility"""
        p = Path(path)
        result = {
            "name": p.stem,
            "compatible": True,
            "size_kb": 0,
            "issues": [],
            "warnings": []
        }
        
        if not p.exists():
            result["compatible"] = False
            result["issues"].append("Not found")
            return result
        
        try:
            code = p.read_text()
            
            # Size check
            size_kb = len(code.encode()) / 1024
            result["size_kb"] = round(size_kb, 2)
            if size_kb > self.max_kb:
                result["compatible"] = False
                result["issues"].append(f"Size {size_kb:.1f}KB > {self.max_kb}KB")
            
            # Parse
            tree = ast.parse(code)
            
            # Check dependencies
            deps = self._get_deps(tree)
            invalid = deps - self.allowed
            if invalid:
                result["warnings"].append(f"External deps: {invalid}")
            
            # Check API
            has_class, methods = self._check_api(tree)
            if not has_class:
                result["compatible"] = False
                result["issues"].append("No Agent class")
            else:
                missing = self.required - methods
                if missing:
                    result["compatible"] = False
                    result["issues"].append(f"Missing: {missing}")
            
            # Performance check
            self._check_perf(tree, code, result)
            
            result["compatible"] = result["compatible"] and len(result["issues"]) == 0
            
        except SyntaxError:
            result["compatible"] = False
            result["issues"].append("Syntax error")
        except Exception as e:
            result["compatible"] = False
            result["issues"].append(str(e))
        
        return result
    
    def _get_deps(self, tree: ast.AST) -> Set[str]:
        """Get dependencies"""
        deps = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                deps.update(a.name.split('.')[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom) and n.module:
                deps.add(n.module.split('.')[0])
        return deps
    
    def _check_api(self, tree: ast.AST) -> Tuple[bool, Set[str]]:
        """Check API methods"""
        found = False
        methods = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef) and 'Agent' in n.name:
                found = True
                methods.update(
                    item.name for item in n.body 
                    if isinstance(item, ast.FunctionDef)
                )
        return found, methods
    
    def _check_perf(self, tree: ast.AST, code: str, result: Dict):
        """Check performance"""
        loops = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
        imports = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)))
        
        if loops > 5:
            result["warnings"].append(f"High loops: {loops}")
        if imports > 20:
            result["warnings"].append(f"Many imports: {imports}")
        
        # Estimate instantiation
        est_us = 0.5 + imports * 0.1 + loops * 0.05
        if est_us > 3.0:
            result["warnings"].append(f"Slow init: {est_us:.1f}μs")
    
    def batch(self, paths: list) -> Dict[str, Dict]:
        """Check multiple agents"""
        return {p: self.check(p) for p in paths}
    
    def report(self, results: Dict[str, Dict]) -> Dict:
        """Generate report"""
        if not results:
            return {}
        
        total = len(results)
        compat = sum(1 for r in results.values() if r["compatible"])
        
        # Common issues
        issues = {}
        for r in results.values():
            for issue in r["issues"]:
                key = "Size limit" if "Size" in issue else issue[:20]
                issues[key] = issues.get(key, 0) + 1
        
        return {
            "total": total,
            "compatible": compat,
            "rate": f"{compat/total*100:.1f}%",
            "issues": dict(sorted(issues.items(), key=lambda x: x[1], reverse=True)[:3])
        }