"""🧬 T-Developer Sandbox <6.5KB"""
import io
import signal
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ExecConfig:
    timeout_sec: float = 5.0
    memory_mb: int = 50
    allowed_modules: List[str] = None


@dataclass
class ExecResult:
    success: bool
    output: str
    error: str = None
    return_val: Any = None
    exec_time_ms: float = 0.0
    memory_kb: int = 0
    timeout: bool = False


class TimeoutError(Exception):
    pass


class SandboxExecutor:
    def __init__(self, config: ExecConfig = None):
        self.config = config or ExecConfig()
        self.blocked = {"open", "input", "__import__", "exec", "eval", "exit", "quit"}

    def execute_code(self, code: str, context: Dict[str, Any] = None) -> ExecResult:
        start = time.perf_counter()

        try:
            with self._sandbox():
                stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
                safe_globals = self._safe_globals(context or {})

                return_val = None
                with self._timeout(self.config.timeout_sec):
                    with self._redirect_io(stdout_buf, stderr_buf):
                        exec(compile(code, "<sandbox>", "exec"), safe_globals)
                        if "main" in safe_globals and callable(safe_globals["main"]):
                            return_val = safe_globals["main"]()

                return ExecResult(
                    success=True,
                    output=stdout_buf.getvalue(),
                    return_val=return_val,
                    exec_time_ms=(time.perf_counter() - start) * 1000,
                    memory_kb=self._memory_usage(),
                )
        except TimeoutError as e:
            return ExecResult(
                success=False,
                output="",
                error=str(e),
                timeout=True,
                exec_time_ms=(time.perf_counter() - start) * 1000,
            )
        except Exception as e:
            return ExecResult(
                success=False,
                output="",
                error=str(e),
                exec_time_ms=(time.perf_counter() - start) * 1000,
            )

    def execute_function(self, func: Callable, *args, **kwargs) -> ExecResult:
        start = time.perf_counter()

        try:
            with self._sandbox():
                stdout_buf, stderr_buf = io.StringIO(), io.StringIO()
                with self._timeout(self.config.timeout_sec):
                    with self._redirect_io(stdout_buf, stderr_buf):
                        return_val = func(*args, **kwargs)

                return ExecResult(
                    success=True,
                    output=stdout_buf.getvalue(),
                    return_val=return_val,
                    exec_time_ms=(time.perf_counter() - start) * 1000,
                    memory_kb=self._memory_usage(),
                )
        except Exception as e:
            return ExecResult(
                success=False,
                output="",
                error=str(e),
                exec_time_ms=(time.perf_counter() - start) * 1000,
            )

    def test_instantiation(self, agent_class: type, *args, **kwargs) -> ExecResult:
        old_timeout = self.config.timeout_sec
        self.config.timeout_sec = 0.01

        result = self.execute_function(lambda: agent_class(*args, **kwargs))

        if result.success and result.exec_time_ms * 1000 > 3.0:
            result.error = f"{result.exec_time_ms * 1000:.1f}μs > 3μs"
            result.success = False

        self.config.timeout_sec = old_timeout
        return result

    @contextmanager
    def _sandbox(self):
        orig_builtins = sys.modules["builtins"].__dict__.copy()

        try:
            for blocked in self.blocked:
                if blocked in sys.modules["builtins"].__dict__:
                    del sys.modules["builtins"].__dict__[blocked]
            yield
        finally:
            sys.modules["builtins"].__dict__.update(orig_builtins)

    @contextmanager
    def _timeout(self, timeout_sec: float):
        if hasattr(signal, "SIGALRM"):

            def handler(s, f):
                raise TimeoutError(f"Timeout {timeout_sec}s")

            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(int(timeout_sec))
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old)
        else:
            evt = threading.Event()
            timer = threading.Timer(timeout_sec, evt.set)
            timer.start()
            try:
                yield
                if evt.is_set():
                    raise TimeoutError(f"Timeout {timeout_sec}s")
            finally:
                timer.cancel()

    @contextmanager
    def _redirect_io(self, stdout_buf: io.StringIO, stderr_buf: io.StringIO):
        old_out, old_err = sys.stdout, sys.stderr
        try:
            sys.stdout, sys.stderr = stdout_buf, stderr_buf
            yield
        finally:
            sys.stdout, sys.stderr = old_out, old_err

    def _safe_globals(self, context: Dict[str, Any]) -> Dict[str, Any]:
        g = {
            "__builtins__": {
                "len",
                "str",
                "int",
                "float",
                "bool",
                "list",
                "dict",
                "print",
                "type",
                "isinstance",
            }
        }
        g.update(context)
        for m in ["json", "math"]:
            try:
                g[m] = __import__(m)
            except:
                pass
        return g

    def _memory_usage(self) -> int:
        return 0

    def validate_safety(self, code: str) -> List[str]:
        violations = []
        for pattern in ["__import__", "exec(", "eval(", "open(", "subprocess"]:
            if pattern in code:
                violations.append(pattern)
        return violations


# Factory and global instance
_executor = None


def get_executor() -> SandboxExecutor:
    global _executor
    if _executor is None:
        _executor = SandboxExecutor()
    return _executor


def execute_code(code: str, context: Dict[str, Any] = None, timeout: float = 5.0) -> ExecResult:
    config = ExecConfig(timeout_sec=timeout)
    executor = SandboxExecutor(config)
    return executor.execute_code(code, context)


def execute_safe(func: Callable, *args, **kwargs) -> ExecResult:
    return get_executor().execute_function(func, *args, **kwargs)


def quick_test(code: str) -> Dict[str, Any]:
    executor = get_executor()
    violations = executor.validate_safety(code)
    result = executor.execute_code(code)
    return {
        "safe": len(violations) == 0 and result.success,
        "violations": violations,
        "exec_time_ms": result.exec_time_ms,
    }
