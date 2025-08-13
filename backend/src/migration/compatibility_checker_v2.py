"""🧬 Compatibility Checker <6.5KB
Day 16: Migration Framework
Validates agent compatibility with target environment
"""
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple


@dataclass
class CompatibilityResult:
    """Compatibility check result"""
    agent_name: str
    is_compatible: bool
    python_version: str
    memory_usage: float  # KB
    dependencies_ok: bool
    api_compatible: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


class CompatibilityChecker:
    """Checks agent compatibility with AgentCore requirements"""
    
    def __init__(self, target_version: str = "3.9"):
        self.target_version = target_version
        self.max_memory_kb = 6.5
        self.max_instantiation_us = 3.0
        
        # Required APIs for AgentCore
        self.required_methods = {
            '__init__',
            'process',
            'validate_input',
            'get_metadata'
        }
        
        # Allowed dependencies
        self.allowed_deps = {
            'ast', 'asyncio', 'dataclasses', 'datetime', 'enum',
            'functools', 'hashlib', 'json', 'logging', 'os',
            'pathlib', 're', 'sys', 'time', 'typing', 'uuid'
        }
        
        # Python version features
        self.version_features = {
            '3.6': ['f-strings', 'async/await'],
            '3.7': ['dataclasses', '__future__.annotations'],
            '3.8': ['walrus', 'positional-only'],
            '3.9': ['dict-merge', 'type-hints-generics'],
            '3.10': ['match-case', 'union-types'],
            '3.11': ['exception-groups', 'task-groups']
        }

    def check_agent(self, file_path: str) -> CompatibilityResult:
        """Check single agent compatibility"""
        path = Path(file_path)
        agent_name = path.stem
        
        result = CompatibilityResult(
            agent_name=agent_name,
            is_compatible=True,
            python_version=self.target_version,
            memory_usage=0,
            dependencies_ok=True,
            api_compatible=True
        )
        
        if not path.exists():
            result.is_compatible = False
            result.issues.append(f"File not found: {file_path}")
            return result
        
        try:
            code = path.read_text()
            
            # Check file size (memory constraint)
            size_kb = len(code.encode()) / 1024
            result.memory_usage = size_kb
            result.metrics['size_kb'] = size_kb
            
            if size_kb > self.max_memory_kb:
                result.is_compatible = False
                result.issues.append(f"Size {size_kb:.1f}KB exceeds {self.max_memory_kb}KB limit")
            
            # Parse AST
            tree = ast.parse(code)
            
            # Check Python version compatibility
            if not self._check_python_version(tree, code):
                result.is_compatible = False
                result.issues.append(f"Not compatible with Python {self.target_version}")
            
            # Check dependencies
            deps = self._extract_dependencies(tree)
            invalid_deps = deps - self.allowed_deps
            if invalid_deps:
                result.dependencies_ok = False
                result.warnings.append(f"Non-standard dependencies: {invalid_deps}")
            
            # Check API compatibility
            class_found, methods = self._check_api_methods(tree)
            if not class_found:
                result.api_compatible = False
                result.issues.append("No Agent class found")
            else:
                missing_methods = self.required_methods - methods
                if missing_methods:
                    result.api_compatible = False
                    result.issues.append(f"Missing required methods: {missing_methods}")
            
            # Check performance hints
            self._check_performance(tree, result)
            
            # Final compatibility decision
            result.is_compatible = (
                result.is_compatible and
                result.dependencies_ok and
                result.api_compatible and
                len(result.issues) == 0
            )
            
        except SyntaxError as e:
            result.is_compatible = False
            result.issues.append(f"Syntax error: {e}")
        except Exception as e:
            result.is_compatible = False
            result.issues.append(f"Check error: {e}")
        
        return result
    
    def _check_python_version(self, tree: ast.AST, code: str) -> bool:
        """Check Python version compatibility"""
        # Check for version-specific features
        min_version = '3.6'
        
        # F-strings (3.6+)
        if 'f"' in code or "f'" in code:
            min_version = max(min_version, '3.6')
        
        # Dataclasses (3.7+)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == 'dataclass':
                min_version = max(min_version, '3.7')
        
        # Walrus operator (3.8+)
        if ':=' in code:
            min_version = max(min_version, '3.8')
        
        # Match case (3.10+)
        if 'match ' in code and ':' in code:
            min_version = max(min_version, '3.10')
        
        # Compare versions
        return min_version <= self.target_version
    
    def _extract_dependencies(self, tree: ast.AST) -> Set[str]:
        """Extract import dependencies"""
        deps = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    deps.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    deps.add(node.module.split('.')[0])
        
        return deps
    
    def _check_api_methods(self, tree: ast.AST) -> Tuple[bool, Set[str]]:
        """Check for required API methods"""
        class_found = False
        methods = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if 'Agent' in node.name:
                    class_found = True
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.add(item.name)
        
        return class_found, methods
    
    def _check_performance(self, tree: ast.AST, result: CompatibilityResult):
        """Check performance characteristics"""
        # Count complexity indicators
        loops = sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.For, ast.While)))
        recursions = 0
        imports = sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.Import, ast.ImportFrom)))
        
        # Check for recursive functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call):
                        if hasattr(subnode.func, 'id') and subnode.func.id == node.name:
                            recursions += 1
        
        # Add metrics
        result.metrics['loops'] = loops
        result.metrics['recursions'] = recursions
        result.metrics['imports'] = imports
        
        # Performance warnings
        if loops > 5:
            result.warnings.append(f"High loop count ({loops}) may impact performance")
        
        if recursions > 0:
            result.warnings.append(f"Recursion detected ({recursions} calls)")
        
        if imports > 20:
            result.warnings.append(f"Many imports ({imports}) may slow instantiation")
        
        # Estimate instantiation time (rough)
        estimated_time = 0.5 + (imports * 0.1) + (loops * 0.05)
        result.metrics['estimated_instantiation_us'] = estimated_time
        
        if estimated_time > self.max_instantiation_us:
            result.warnings.append(f"Estimated instantiation {estimated_time:.1f}μs exceeds {self.max_instantiation_us}μs")
    
    def check_batch(self, file_paths: List[str]) -> Dict[str, CompatibilityResult]:
        """Check multiple agents"""
        results = {}
        for path in file_paths:
            results[path] = self.check_agent(path)
        return results
    
    def generate_report(self, results: Dict[str, CompatibilityResult]) -> Dict:
        """Generate compatibility report"""
        total = len(results)
        if not total:
            return {"error": "No agents checked"}
        
        compatible = sum(1 for r in results.values() if r.is_compatible)
        
        return {
            "total_agents": total,
            "compatible": compatible,
            "incompatible": total - compatible,
            "compatibility_rate": f"{(compatible/total*100):.1f}%",
            "common_issues": self._get_common_issues(results),
            "memory_stats": self._get_memory_stats(results),
            "recommendations": self._get_recommendations(results)
        }
    
    def _get_common_issues(self, results: Dict[str, CompatibilityResult]) -> List[str]:
        """Get most common issues"""
        issue_counts = {}
        
        for result in results.values():
            for issue in result.issues:
                # Generalize issue messages
                if "Size" in issue and "exceeds" in issue:
                    issue = "Size exceeds limit"
                elif "Missing required methods" in issue:
                    issue = "Missing required methods"
                
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [f"{issue} ({count} agents)" for issue, count in sorted_issues[:5]]
    
    def _get_memory_stats(self, results: Dict[str, CompatibilityResult]) -> Dict:
        """Get memory usage statistics"""
        sizes = [r.memory_usage for r in results.values() if r.memory_usage > 0]
        
        if not sizes:
            return {}
        
        return {
            "avg_size_kb": sum(sizes) / len(sizes),
            "max_size_kb": max(sizes),
            "min_size_kb": min(sizes),
            "over_limit": sum(1 for s in sizes if s > self.max_memory_kb)
        }
    
    def _get_recommendations(self, results: Dict[str, CompatibilityResult]) -> List[str]:
        """Get recommendations"""
        recs = []
        
        # Check size issues
        oversized = [name for name, r in results.items() if r.memory_usage > self.max_memory_kb]
        if oversized:
            recs.append(f"Optimize {len(oversized)} oversized agents")
        
        # Check API issues
        api_issues = [name for name, r in results.items() if not r.api_compatible]
        if api_issues:
            recs.append(f"Update {len(api_issues)} agents to match API requirements")
        
        # Check dependency issues
        dep_issues = [name for name, r in results.items() if not r.dependencies_ok]
        if dep_issues:
            recs.append(f"Review dependencies for {len(dep_issues)} agents")
        
        if not recs:
            recs.append("All agents are compatible!")
        
        return recs


# Example usage
if __name__ == "__main__":
    checker = CompatibilityChecker(target_version="3.9")
    
    # Check single agent
    result = checker.check_agent("backend/src/agents/migrated/test_agent.py")
    print(f"Agent: {result.agent_name}")
    print(f"Compatible: {result.is_compatible}")
    print(f"Issues: {result.issues}")
    
    # Check batch
    agents = [
        "backend/src/agents/migrated/agent1.py",
        "backend/src/agents/migrated/agent2.py"
    ]
    results = checker.check_batch(agents)
    report = checker.generate_report(results)
    print(f"Report: {json.dumps(report, indent=2)}")