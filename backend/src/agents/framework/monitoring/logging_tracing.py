# backend/src/agents/framework/logging_tracing.py
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json
import uuid
from contextlib import contextmanager
import threading

@dataclass
class TraceSpan:
    span_id: str
    trace_id: str
    parent_span_id: Optional[str]
    operation_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"  # ok, error, timeout

class AgentLogger:
    def __init__(self, agent_id: str, log_level: str = "INFO"):
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Context storage
        self.context = threading.local()
    
    def set_context(self, **kwargs):
        """Set logging context"""
        if not hasattr(self.context, 'data'):
            self.context.data = {}
        self.context.data.update(kwargs)
    
    def get_context(self) -> Dict[str, Any]:
        """Get current logging context"""
        return getattr(self.context, 'data', {})
    
    def _format_message(self, message: str, extra: Dict[str, Any] = None) -> str:
        """Format message with context"""
        context = self.get_context()
        if extra:
            context.update(extra)
        
        if context:
            context_str = json.dumps(context, default=str)
            return f"{message} | Context: {context_str}"
        return message
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message(message, kwargs))
    
    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message(message, kwargs))
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message(message, kwargs))
    
    def error(self, message: str, **kwargs):
        self.logger.error(self._format_message(message, kwargs))
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(self._format_message(message, kwargs))

class DistributedTracer:
    def __init__(self):
        self.spans: Dict[str, TraceSpan] = {}
        self.active_spans: Dict[str, str] = {}  # thread_id -> span_id
        self.trace_handlers: List[Callable] = []
    
    def add_trace_handler(self, handler: Callable):
        """Add handler for completed traces"""
        self.trace_handlers.append(handler)
    
    def start_trace(self, operation_name: str, parent_span_id: Optional[str] = None) -> str:
        """Start a new trace span"""
        span_id = str(uuid.uuid4())
        trace_id = parent_span_id or str(uuid.uuid4())
        
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            start_time=datetime.utcnow()
        )
        
        self.spans[span_id] = span
        
        # Set as active span for current thread
        thread_id = threading.get_ident()
        self.active_spans[thread_id] = span_id
        
        return span_id
    
    def finish_trace(self, span_id: str, status: str = "ok"):
        """Finish a trace span"""
        if span_id not in self.spans:
            return
        
        span = self.spans[span_id]
        span.end_time = datetime.utcnow()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        
        # Remove from active spans
        thread_id = threading.get_ident()
        if self.active_spans.get(thread_id) == span_id:
            del self.active_spans[thread_id]
        
        # Notify handlers
        for handler in self.trace_handlers:
            try:
                handler(span)
            except Exception as e:
                print(f"Trace handler error: {e}")
    
    def add_tag(self, span_id: str, key: str, value: Any):
        """Add tag to span"""
        if span_id in self.spans:
            self.spans[span_id].tags[key] = value
    
    def add_log(self, span_id: str, message: str, level: str = "info", **kwargs):
        """Add log entry to span"""
        if span_id in self.spans:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": level,
                "message": message,
                **kwargs
            }
            self.spans[span_id].logs.append(log_entry)
    
    def get_active_span_id(self) -> Optional[str]:
        """Get active span ID for current thread"""
        thread_id = threading.get_ident()
        return self.active_spans.get(thread_id)
    
    @contextmanager
    def trace(self, operation_name: str, **tags):
        """Context manager for tracing"""
        span_id = self.start_trace(operation_name)
        
        # Add tags
        for key, value in tags.items():
            self.add_tag(span_id, key, value)
        
        try:
            yield span_id
            self.finish_trace(span_id, "ok")
        except Exception as e:
            self.add_tag(span_id, "error", str(e))
            self.add_log(span_id, f"Exception: {str(e)}", "error")
            self.finish_trace(span_id, "error")
            raise
    
    def get_trace_summary(self, trace_id: str) -> Dict[str, Any]:
        """Get summary of a trace"""
        trace_spans = [s for s in self.spans.values() if s.trace_id == trace_id]
        
        if not trace_spans:
            return {}
        
        total_duration = sum(s.duration_ms or 0 for s in trace_spans)
        error_count = sum(1 for s in trace_spans if s.status == "error")
        
        return {
            "trace_id": trace_id,
            "total_spans": len(trace_spans),
            "total_duration_ms": total_duration,
            "error_count": error_count,
            "success_rate": (len(trace_spans) - error_count) / len(trace_spans),
            "spans": [
                {
                    "span_id": s.span_id,
                    "operation": s.operation_name,
                    "duration_ms": s.duration_ms,
                    "status": s.status
                }
                for s in trace_spans
            ]
        }

class AgentLoggingMixin:
    def __init__(self):
        self.logger = AgentLogger(getattr(self, 'agent_id', 'unknown'))
        self.tracer = DistributedTracer()
    
    def log_info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, **kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, **kwargs)
    
    def start_operation_trace(self, operation_name: str, **tags) -> str:
        """Start tracing an operation"""
        span_id = self.tracer.start_trace(operation_name)
        
        # Add agent context
        self.tracer.add_tag(span_id, "agent_id", getattr(self, 'agent_id', 'unknown'))
        self.tracer.add_tag(span_id, "agent_type", getattr(self, 'agent_type', 'unknown'))
        
        # Add custom tags
        for key, value in tags.items():
            self.tracer.add_tag(span_id, key, value)
        
        return span_id
    
    def finish_operation_trace(self, span_id: str, success: bool = True):
        """Finish tracing an operation"""
        status = "ok" if success else "error"
        self.tracer.finish_trace(span_id, status)
    
    def trace_operation(self, operation_name: str, **tags):
        """Context manager for tracing operations"""
        return self.tracer.trace(operation_name, **tags)

# Global instances
_global_tracer = DistributedTracer()

def get_global_tracer() -> DistributedTracer:
    """Get global tracer instance"""
    return _global_tracer

def trace_agent_operation(operation_name: str, agent_id: str = None, **tags):
    """Decorator for tracing agent operations"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            with _global_tracer.trace(operation_name, agent_id=agent_id, **tags) as span_id:
                # Add function info
                _global_tracer.add_tag(span_id, "function", func.__name__)
                _global_tracer.add_tag(span_id, "module", func.__module__)
                
                return func(*args, **kwargs)
        return wrapper
    return decorator