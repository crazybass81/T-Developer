"""🧬 Legacy Agent Analyzer <6.5KB
Day 16: Migration Framework
Analyzes legacy agents for migration planning
"""
import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Set


class Complexity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class AnalysisResult:
    agent_name: str
    complexity: Complexity
    dependencies: List[str] = field(default_factory=list)
    patterns: Set[str] = field(default_factory=set)
    issues: List[str] = field(default_factory=list)
    metrics: Dict[str, int] = field(default_factory=dict)


class LegacyAnalyzer:
    """Analyzes legacy agents for migration <6.5KB optimized"""
    
    def __init__(self):
        # Patterns to detect
        self.legacy_patterns = {
            r'class\s+\w+\(object\)': 'old_style_class',
            r'print\s+["\']': 'print_statement',
            r'\.has_key\(': 'dict_has_key',
            r'except\s+\w+,': 'old_except',
            r'xrange\(': 'xrange_usage',
            r'unicode\(': 'unicode_type',
            r'execfile\(': 'execfile_usage',
            r'`[^`]+`': 'backticks',
            r'<>': 'not_equal_old',
            r'\.iteritems\(\)': 'dict_iteritems',
            r'\.iterkeys\(\)': 'dict_iterkeys',
            r'\.itervalues\(\)': 'dict_itervalues'
        }
        
        self.modern_patterns = {
            r'async\s+def': 'async_await',
            r'@dataclass': 'dataclasses',
            r'typing\.': 'type_hints',
            r'f["\']': 'f_strings',
            r':=': 'walrus_operator',
            r'match\s+\w+:': 'pattern_matching'
        }

    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze single agent file"""
        path = Path(file_path)
        agent_name = path.stem
        
        result = AnalysisResult(
            agent_name=agent_name,
            complexity=Complexity.LOW
        )
        
        if not path.exists():
            result.issues.append(f"File not found: {file_path}")
            return result
        
        try:
            code = path.read_text()
            
            # Parse AST
            tree = ast.parse(code)
            
            # Basic metrics
            result.metrics['lines'] = len(code.splitlines())
            result.metrics['classes'] = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
            result.metrics['functions'] = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef))
            result.metrics['imports'] = sum(1 for _ in ast.walk(tree) if isinstance(_, (ast.Import, ast.ImportFrom)))
            
            # Extract dependencies
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result.dependencies.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result.dependencies.append(node.module.split('.')[0])
            
            # Check patterns
            for pattern, name in self.legacy_patterns.items():
                if re.search(pattern, code):
                    result.patterns.add(f"legacy:{name}")
            
            for pattern, name in self.modern_patterns.items():
                if re.search(pattern, code):
                    result.patterns.add(f"modern:{name}")
            
            # Calculate complexity
            result.complexity = self._calculate_complexity(result)
            
        except SyntaxError as e:
            result.issues.append(f"Syntax error: {e}")
            result.complexity = Complexity.HIGH
        except Exception as e:
            result.issues.append(f"Analysis error: {e}")
            
        return result
    
    def _calculate_complexity(self, result: AnalysisResult) -> Complexity:
        """Calculate migration complexity"""
        score = 0
        
        # Size factors
        if result.metrics.get('lines', 0) > 500:
            score += 2
        elif result.metrics.get('lines', 0) > 200:
            score += 1
            
        # Legacy pattern factors
        legacy_count = sum(1 for p in result.patterns if p.startswith('legacy:'))
        score += min(legacy_count, 3)
        
        # Dependency factors
        external_deps = [d for d in result.dependencies if d not in ['os', 'sys', 'json', 'time']]
        score += min(len(external_deps) // 3, 2)
        
        # Determine complexity
        if score <= 2:
            return Complexity.LOW
        elif score <= 5:
            return Complexity.MEDIUM
        else:
            return Complexity.HIGH
    
    def analyze_directory(self, dir_path: str) -> List[AnalysisResult]:
        """Analyze all agents in directory"""
        results = []
        path = Path(dir_path)
        
        if not path.exists():
            return results
        
        for file in path.glob("**/*.py"):
            if not file.name.startswith('__'):
                results.append(self.analyze_file(str(file)))
        
        return results
    
    def generate_report(self, results: List[AnalysisResult]) -> Dict:
        """Generate migration report"""
        total = len(results)
        if not total:
            return {"error": "No agents analyzed"}
        
        return {
            "total_agents": total,
            "complexity_distribution": {
                "low": sum(1 for r in results if r.complexity == Complexity.LOW),
                "medium": sum(1 for r in results if r.complexity == Complexity.MEDIUM),
                "high": sum(1 for r in results if r.complexity == Complexity.HIGH)
            },
            "common_patterns": self._get_common_patterns(results),
            "common_dependencies": self._get_common_deps(results),
            "migration_effort": self._estimate_effort(results),
            "recommendations": self._get_recommendations(results)
        }
    
    def _get_common_patterns(self, results: List[AnalysisResult]) -> List[str]:
        """Get most common patterns"""
        pattern_counts = {}
        for r in results:
            for p in r.patterns:
                pattern_counts[p] = pattern_counts.get(p, 0) + 1
        
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        return [p[0] for p in sorted_patterns[:5]]
    
    def _get_common_deps(self, results: List[AnalysisResult]) -> List[str]:
        """Get most common dependencies"""
        dep_counts = {}
        for r in results:
            for d in set(r.dependencies):
                dep_counts[d] = dep_counts.get(d, 0) + 1
        
        sorted_deps = sorted(dep_counts.items(), key=lambda x: x[1], reverse=True)
        return [d[0] for d in sorted_deps[:10]]
    
    def _estimate_effort(self, results: List[AnalysisResult]) -> str:
        """Estimate migration effort"""
        complexity_points = {
            Complexity.LOW: 1,
            Complexity.MEDIUM: 3,
            Complexity.HIGH: 8
        }
        
        total_points = sum(complexity_points[r.complexity] for r in results)
        
        if total_points < 10:
            return "1-2 days"
        elif total_points < 30:
            return "3-5 days"
        elif total_points < 60:
            return "1-2 weeks"
        else:
            return "2+ weeks"
    
    def _get_recommendations(self, results: List[AnalysisResult]) -> List[str]:
        """Get migration recommendations"""
        recs = []
        
        # Check for high complexity agents
        high_complex = [r for r in results if r.complexity == Complexity.HIGH]
        if high_complex:
            recs.append(f"Prioritize {len(high_complex)} high-complexity agents")
        
        # Check for common legacy patterns
        legacy_patterns = set()
        for r in results:
            legacy_patterns.update(p for p in r.patterns if p.startswith('legacy:'))
        
        if legacy_patterns:
            recs.append(f"Address {len(legacy_patterns)} legacy patterns systematically")
        
        # Check for size issues
        large_agents = [r for r in results if r.metrics.get('lines', 0) > 500]
        if large_agents:
            recs.append(f"Consider splitting {len(large_agents)} large agents")
        
        # Check for dependency issues
        complex_deps = set()
        for r in results:
            complex_deps.update(d for d in r.dependencies if d not in ['os', 'sys', 'json'])
        
        if len(complex_deps) > 10:
            recs.append("Standardize dependencies across agents")
        
        if not recs:
            recs.append("Migration complexity is manageable")
        
        return recs


# Example usage
if __name__ == "__main__":
    analyzer = LegacyAnalyzer()
    
    # Analyze single agent
    result = analyzer.analyze_file("backend/src/agents/legacy/old_agent.py")
    print(f"Agent: {result.agent_name}")
    print(f"Complexity: {result.complexity.value}")
    print(f"Issues: {result.issues}")
    
    # Analyze directory
    results = analyzer.analyze_directory("backend/src/agents/legacy")
    report = analyzer.generate_report(results)
    print(f"Migration Report: {report}")