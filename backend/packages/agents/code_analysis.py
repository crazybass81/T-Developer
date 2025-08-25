"""Code Analysis Agent supporting both AI and dynamic analysis.

This agent analyzes code through multiple approaches:
1. AI-based analysis using AWS Bedrock (Claude)
2. Dynamic analysis through code execution and profiling
3. Integration with static analyzer for comprehensive insights
"""

from __future__ import annotations

import ast
import os
import sys
import time
import tempfile
import subprocess
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import cProfile
import pstats
import io
from contextlib import redirect_stdout, redirect_stderr

from .ai_providers import BedrockAIProvider
from .base import AgentResult, AgentTask, BaseAgent, TaskStatus
from ..memory import ContextType, MemoryHub


class CodeAnalysisAgent(BaseAgent):
    """Agent that analyzes code using AI and dynamic analysis.
    
    This agent provides three types of analysis:
    
    1. AI Analysis (using AWS Bedrock/Claude):
       - Code quality and suggestions
       - Security vulnerability detection
       - Performance recommendations
       - Test coverage analysis
    
    2. Dynamic Analysis (code execution):
       - Runtime profiling
       - Memory usage tracking
       - Execution path analysis
       - Performance benchmarking
       - Real behavior testing
    
    3. Hybrid Analysis:
       - Combines AI insights with runtime data
       - Validates AI suggestions with actual execution
       - Provides comprehensive reports
    
    The agent intelligently chooses between static (via StaticAnalyzer),
    AI, and dynamic approaches based on the code and requirements.
    """
    
    def __init__(
        self,
        memory_hub: Optional[MemoryHub] = None,
        model: str = "claude-3-haiku",
        region: str = "us-east-1",
        **kwargs: Any
    ) -> None:
        """Initialize the Code Analysis Agent.
        
        Args:
            memory_hub: Memory Hub instance
            model: Bedrock model to use
            region: AWS region
            **kwargs: Additional arguments for BaseAgent
        """
        # Initialize AI provider
        ai_provider = BedrockAIProvider(model="claude-3-sonnet", region=region)
        
        super().__init__(
            name="CodeAnalysisAgent",
            version="1.0.0",
            memory_hub=memory_hub,
            ai_provider=ai_provider,
            **kwargs
        )
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute code analysis task.
        
        Args:
            task: The analysis task containing:
                - inputs.file_path: Path to code file (optional)
                - inputs.code: Direct code string (optional)
                - inputs.analysis_type: Type of analysis (general/security/performance/test)
                - inputs.language: Programming language (default: python)
                - inputs.use_history: Whether to use previous analyses (default: true)
            
        Returns:
            AgentResult containing the analysis
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not await self.validate_input(task):
                return self.format_result(
                    success=False,
                    error="Invalid input: missing file_path or code"
                )
            
            # Handle both dict and AgentTask inputs
            if isinstance(task, dict):
                inputs = task
            else:
                inputs = task.inputs
            
            # Extract parameters
            file_path = inputs.get("file_path")
            code = inputs.get("code")
            analysis_type = inputs.get("analysis_type", "general")
            language = inputs.get("language", "python")
            use_history = inputs.get("use_history", True)
            enable_dynamic = inputs.get("enable_dynamic", False)
            safe_mode = inputs.get("safe_mode", True)
            
            # Get code to analyze
            if file_path and not code:
                code = await self._read_file(file_path)
                if not code:
                    return self.format_result(
                        success=False,
                        error=f"Could not read file: {file_path}"
                    )
            
            if not code:
                return self.format_result(
                    success=False,
                    error="No code provided for analysis"
                )
            
            # Check memory for previous analyses if enabled
            previous_analyses = []
            if use_history and self.memory_hub:
                previous_analyses = await self._get_previous_analyses(
                    file_path or "inline_code",
                    analysis_type
                )
            
            # Build enhanced prompt with history
            enhanced_code = code
            if previous_analyses:
                context = self._build_historical_context(previous_analyses)
                enhanced_code = f"""Previous analyses of this code:
{context}

Current code to analyze:
```{language}
{code}
```"""
            
            # Initialize results dictionary
            analysis = {}
            
            # Perform AI analysis
            if self.ai_provider:
                ai_analysis = await self.ai_provider.analyze_code(
                    enhanced_code if previous_analyses else code,
                    analysis_type,
                    language
                )
                analysis["ai_analysis"] = ai_analysis
            
            # Perform dynamic analysis if enabled and language is Python
            if enable_dynamic and language == "python":
                dynamic_results = await self._perform_dynamic_analysis(
                    code, 
                    file_path,
                    safe_mode
                )
                analysis["dynamic_analysis"] = dynamic_results
                
                # Combine insights if both analyses are available
                if "ai_analysis" in analysis and dynamic_results.get("success"):
                    analysis["combined_insights"] = self._combine_analyses(
                        analysis["ai_analysis"],
                        dynamic_results
                    )
            
            # Store analysis in memory
            if self.memory_hub:
                await self._store_analysis(
                    file_path or "inline_code",
                    analysis_type,
                    analysis,
                    code
                )
            
            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Prepare result
            result_data = {
                "analysis": analysis,
                "file_path": file_path,
                "language": language,
                "analysis_type": analysis_type,
                "code_stats": {
                    "lines": len(code.split("\n")),
                    "size_bytes": len(code.encode())
                },
                "used_history": len(previous_analyses) > 0,
                "history_count": len(previous_analyses)
            }
            
            # Log execution
            await self.log_execution(task, AgentResult(
                success=True,
                status=TaskStatus.COMPLETED,
                data=result_data,
                execution_time_ms=execution_time_ms
            ))
            
            return self.format_result(
                success=True,
                data=result_data,
                execution_time_ms=execution_time_ms,
                metadata={"agent": self.name, "version": self.version}
            )
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            
            # Log failure
            await self.log_execution(task, AgentResult(
                success=False,
                status=TaskStatus.FAILED,
                error=error_msg
            ))
            
            return self.format_result(
                success=False,
                error=error_msg
            )
    
    async def validate_input(self, task: AgentTask) -> bool:
        """Validate the analysis task input.
        
        Args:
            task: The task to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Handle both dict and AgentTask
        if isinstance(task, dict):
            inputs = task
        else:
            # Call parent validation for AgentTask
            if not await super().validate_input(task):
                return False
            inputs = task.inputs if hasattr(task, 'inputs') else task
        
        # Check for code or file path
        has_file = "file_path" in inputs
        has_code = "code" in inputs
        
        if not has_file and not has_code:
            return False
        
        # Validate analysis type
        valid_types = ["general", "security", "performance", "test", "comprehensive"]
        analysis_type = inputs.get("analysis_type", "general")
        if analysis_type not in valid_types:
            return False
        
        return True
    
    async def _read_file(self, file_path: str) -> Optional[str]:
        """Read code from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File contents or None if error
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    async def _get_previous_analyses(
        self,
        file_identifier: str,
        analysis_type: str,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """Get previous analyses from memory.
        
        Args:
            file_identifier: File path or identifier
            analysis_type: Type of analysis
            limit: Maximum number of previous analyses
            
        Returns:
            List of previous analysis results
        """
        if not self.memory_hub:
            return []
        
        # Search for previous analyses in agent context
        tags = [
            "code_analysis",
            analysis_type,
            file_identifier.replace("/", "_")
        ]
        
        results = await self.search_memory(
            ContextType.A_CTX,
            tags=tags,
            limit=limit
        )
        
        return results
    
    def _build_historical_context(
        self,
        previous_analyses: List[Dict[str, Any]]
    ) -> str:
        """Build context from previous analyses.
        
        Args:
            previous_analyses: List of previous analysis results
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, analysis in enumerate(previous_analyses, 1):
            timestamp = analysis.get("updated_at", "unknown")
            value = analysis.get("value", {})
            
            # Extract key findings from previous analysis
            if isinstance(value, dict):
                analysis_data = value.get("analysis", {})
                summary = analysis_data.get("summary", "No summary available")
                issues = analysis_data.get("issues", [])
                
                context_parts.append(f"""Analysis {i} ({timestamp}):
- Summary: {summary}
- Issues found: {len(issues) if isinstance(issues, list) else 'Unknown'}""")
        
        return "\n\n".join(context_parts)
    
    async def _store_analysis(
        self,
        file_identifier: str,
        analysis_type: str,
        analysis: Dict[str, Any],
        code: str
    ) -> None:
        """Store analysis results in memory.
        
        Args:
            file_identifier: File path or identifier
            analysis_type: Type of analysis
            analysis: The analysis results
            code: The analyzed code
        """
        if not self.memory_hub:
            return
        
        # Prepare memory key
        key = f"analysis_{file_identifier.replace('/', '_')}_{analysis_type}_{time.time()}"
        
        # Store in agent context with TTL
        await self.write_memory(
            ContextType.A_CTX,
            key,
            {
                "file": file_identifier,
                "analysis_type": analysis_type,
                "analysis": analysis,
                "code_hash": hash(code),  # Store hash to detect changes
                "code_lines": len(code.split("\n"))
            },
            ttl_seconds=86400 * 7,  # Keep for 7 days
            tags=[
                "code_analysis",
                analysis_type,
                file_identifier.replace("/", "_")
            ]
        )
        
        # Store summary in shared context
        summary_key = f"latest_analysis_{self.agent_id}"
        await self.write_memory(
            ContextType.S_CTX,
            summary_key,
            {
                "file": file_identifier,
                "type": analysis_type,
                "summary": analysis.get("summary", "Analysis completed"),
                "quality_score": analysis.get("quality_score"),
                "issues_count": len(analysis.get("issues", [])) if "issues" in analysis else None
            },
            ttl_seconds=3600,  # Keep for 1 hour
            tags=["latest", "analysis", self.name]
        )
    
    async def _perform_dynamic_analysis(
        self,
        code: str,
        file_path: Optional[str],
        safe_mode: bool = True
    ) -> Dict[str, Any]:
        """Perform dynamic analysis by executing the code.
        
        Args:
            code: Python code to analyze
            file_path: Original file path (for context)
            safe_mode: Whether to run in sandboxed environment
            
        Returns:
            Dynamic analysis results
        """
        results = {
            "success": False,
            "execution_time": None,
            "profile_data": None,
            "memory_usage": None,
            "output": None,
            "errors": None,
            "execution_paths": [],
            "performance_metrics": {}
        }
        
        try:
            # Create temporary file for code execution
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as tmp_file:
                tmp_file.write(code)
                tmp_path = tmp_file.name
            
            # Profile the code execution
            profile_results = await self._profile_code(tmp_path, safe_mode)
            results.update(profile_results)
            
            # Analyze execution paths
            execution_paths = await self._analyze_execution_paths(code)
            results["execution_paths"] = execution_paths
            
            # Benchmark performance
            if profile_results.get("success"):
                perf_metrics = await self._benchmark_performance(tmp_path)
                results["performance_metrics"] = perf_metrics
            
            results["success"] = True
            
        except Exception as e:
            results["errors"] = str(e)
            results["error_trace"] = traceback.format_exc()
        finally:
            # Clean up temporary file
            if 'tmp_path' in locals():
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        return results
    
    async def _profile_code(
        self,
        file_path: str,
        safe_mode: bool = True
    ) -> Dict[str, Any]:
        """Profile code execution for performance analysis.
        
        Args:
            file_path: Path to Python file to profile
            safe_mode: Whether to use sandboxed execution
            
        Returns:
            Profiling results
        """
        results = {
            "success": False,
            "execution_time": 0,
            "function_calls": [],
            "hotspots": [],
            "memory_peak": 0,
            "output": "",
            "errors": ""
        }
        
        try:
            if safe_mode:
                # Run in subprocess for isolation
                import resource
                
                # Create profiling script
                profile_script = f"""
import cProfile
import pstats
import io
import sys
import tracemalloc

tracemalloc.start()
pr = cProfile.Profile()
pr.enable()

try:
    exec(open('{file_path}').read())
except Exception as e:
    print(f"ERROR: {{e}}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)

pr.disable()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(20)
print(s.getvalue())
print(f"MEMORY_PEAK: {{peak / 1024 / 1024:.2f}} MB")
"""
                
                # Write profile script
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='_profile.py',
                    delete=False
                ) as profile_file:
                    profile_file.write(profile_script)
                    profile_script_path = profile_file.name
                
                # Execute with resource limits
                start_time = time.time()
                result = subprocess.run(
                    [sys.executable, profile_script_path],
                    capture_output=True,
                    text=True,
                    timeout=10  # 10 second timeout
                )
                execution_time = time.time() - start_time
                
                results["execution_time"] = execution_time
                results["output"] = result.stdout
                results["errors"] = result.stderr
                
                # Parse profiling output
                if "cumulative" in result.stdout:
                    lines = result.stdout.split('\n')
                    function_calls = []
                    for line in lines:
                        if '/' in line and '.py' in line:
                            parts = line.split()
                            if len(parts) >= 6:
                                function_calls.append({
                                    "calls": parts[0],
                                    "tottime": parts[1],
                                    "cumtime": parts[3],
                                    "function": ' '.join(parts[5:])
                                })
                    results["function_calls"] = function_calls[:10]
                
                # Extract memory usage
                if "MEMORY_PEAK:" in result.stdout:
                    memory_line = [l for l in result.stdout.split('\n') 
                                  if "MEMORY_PEAK:" in l][0]
                    results["memory_peak"] = float(
                        memory_line.split(":")[1].replace("MB", "").strip()
                    )
                
                results["success"] = result.returncode == 0
                
                # Clean up
                os.unlink(profile_script_path)
                
            else:
                # Direct execution (less safe)
                pr = cProfile.Profile()
                pr.enable()
                
                start_time = time.time()
                exec(open(file_path).read())
                execution_time = time.time() - start_time
                
                pr.disable()
                
                # Get stats
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
                ps.print_stats(10)
                
                results["execution_time"] = execution_time
                results["profile_output"] = s.getvalue()
                results["success"] = True
                
        except subprocess.TimeoutExpired:
            results["errors"] = "Execution timeout (10 seconds)"
        except Exception as e:
            results["errors"] = str(e)
            
        return results
    
    async def _analyze_execution_paths(self, code: str) -> List[Dict[str, Any]]:
        """Analyze possible execution paths in the code.
        
        Args:
            code: Python code to analyze
            
        Returns:
            List of execution paths with coverage info
        """
        paths = []
        
        try:
            tree = ast.parse(code)
            
            # Find all conditional branches
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    paths.append({
                        "type": "conditional",
                        "line": node.lineno,
                        "condition": ast.unparse(node.test) if hasattr(ast, 'unparse') else "condition",
                        "branches": ["if", "else"] if node.orelse else ["if"]
                    })
                elif isinstance(node, (ast.For, ast.While)):
                    loop_type = "for" if isinstance(node, ast.For) else "while"
                    paths.append({
                        "type": "loop",
                        "line": node.lineno,
                        "loop_type": loop_type,
                        "has_break": any(isinstance(n, ast.Break) for n in ast.walk(node)),
                        "has_continue": any(isinstance(n, ast.Continue) for n in ast.walk(node))
                    })
                elif isinstance(node, ast.Try):
                    paths.append({
                        "type": "exception",
                        "line": node.lineno,
                        "handlers": len(node.handlers),
                        "has_finally": bool(node.finalbody)
                    })
                    
        except Exception as e:
            paths.append({"error": f"Failed to analyze paths: {str(e)}"})
            
        return paths
    
    async def _benchmark_performance(self, file_path: str) -> Dict[str, Any]:
        """Benchmark code performance with multiple runs.
        
        Args:
            file_path: Path to Python file to benchmark
            
        Returns:
            Performance metrics
        """
        metrics = {
            "runs": 5,
            "avg_time": 0,
            "min_time": float('inf'),
            "max_time": 0,
            "std_dev": 0
        }
        
        times = []
        for _ in range(metrics["runs"]):
            try:
                start = time.perf_counter()
                result = subprocess.run(
                    [sys.executable, file_path],
                    capture_output=True,
                    timeout=5
                )
                elapsed = time.perf_counter() - start
                
                if result.returncode == 0:
                    times.append(elapsed)
                    metrics["min_time"] = min(metrics["min_time"], elapsed)
                    metrics["max_time"] = max(metrics["max_time"], elapsed)
            except:
                break
        
        if times:
            metrics["avg_time"] = sum(times) / len(times)
            if len(times) > 1:
                variance = sum((t - metrics["avg_time"]) ** 2 for t in times) / len(times)
                metrics["std_dev"] = variance ** 0.5
        
        return metrics
    
    def _combine_analyses(
        self,
        ai_analysis: Dict[str, Any],
        dynamic_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine AI and dynamic analysis results.
        
        Args:
            ai_analysis: Results from AI analysis
            dynamic_results: Results from dynamic analysis
            
        Returns:
            Combined insights and recommendations
        """
        combined = {
            "validation_status": "verified" if dynamic_results.get("success") else "unverified",
            "performance_validated": False,
            "issues_confirmed": [],
            "new_findings": [],
            "recommendations": []
        }
        
        # Validate performance claims
        if dynamic_results.get("execution_time"):
            exec_time = dynamic_results["execution_time"]
            if exec_time > 1.0:
                combined["new_findings"].append({
                    "type": "performance",
                    "severity": "warning",
                    "message": f"Actual execution time ({exec_time:.2f}s) may be slow"
                })
        
        # Check memory usage
        if dynamic_results.get("memory_peak", 0) > 100:  # MB
            combined["new_findings"].append({
                "type": "memory",
                "severity": "warning",
                "message": f"High memory usage detected: {dynamic_results['memory_peak']:.2f} MB"
            })
        
        # Validate AI findings with runtime data
        if isinstance(ai_analysis, dict) and "issues" in ai_analysis:
            for issue in ai_analysis.get("issues", []):
                # Check if issue type matches runtime behavior
                if "performance" in str(issue).lower() and dynamic_results.get("execution_time"):
                    if dynamic_results["execution_time"] > 0.5:
                        combined["issues_confirmed"].append(issue)
                        combined["performance_validated"] = True
        
        # Add recommendations based on combined analysis
        if dynamic_results.get("execution_paths"):
            uncovered_paths = [p for p in dynamic_results["execution_paths"] 
                             if p.get("type") == "conditional"]
            if uncovered_paths:
                combined["recommendations"].append(
                    f"Consider adding tests for {len(uncovered_paths)} conditional branches"
                )
        
        # Performance recommendations from profiling
        if dynamic_results.get("function_calls"):
            hotspots = dynamic_results["function_calls"][:3]
            for hotspot in hotspots:
                if float(hotspot.get("cumtime", 0)) > 0.1:
                    combined["recommendations"].append(
                        f"Optimize function {hotspot.get('function', 'unknown')} "
                        f"(taking {hotspot.get('cumtime', 0)}s)"
                    )
        
        return combined