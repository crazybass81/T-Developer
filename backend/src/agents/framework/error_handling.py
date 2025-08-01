from typing import Optional, Dict, Any, List, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    CONFIGURATION = "configuration"
    INITIALIZATION = "initialization"
    EXECUTION = "execution"
    COMMUNICATION = "communication"
    RESOURCE = "resource"
    DEPENDENCY = "dependency"
    VALIDATION = "validation"
    TIMEOUT = "timeout"

@dataclass
class AgentError(Exception):
    """Base error class for agent-related errors"""
    
    error_code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    agent_id: Optional[str] = None
    context: Dict[str, Any] = None
    recoverable: bool = True
    retry_after: Optional[int] = None  # seconds
    
    def __post_init__(self):
        super().__init__(self.message)
        if self.context is None:
            self.context = {}
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "agent_id": self.agent_id,
            "context": self.context,
            "recoverable": self.recoverable,
            "retry_after": self.retry_after,
            "timestamp": datetime.utcnow().isoformat()
        }

# Specific error types
class ConfigurationError(AgentError):
    def __init__(self, message: str, **kwargs):
        super().__init__(
            error_code="AGENT_CONFIG_ERROR",
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )

class InitializationError(AgentError):
    def __init__(self, message: str, **kwargs):
        super().__init__(
            error_code="AGENT_INIT_ERROR",
            message=message,
            category=ErrorCategory.INITIALIZATION,
            severity=ErrorSeverity.CRITICAL,
            **kwargs
        )

class ExecutionError(AgentError):
    def __init__(self, message: str, **kwargs):
        super().__init__(
            error_code="AGENT_EXEC_ERROR",
            message=message,
            category=ErrorCategory.EXECUTION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )

@dataclass
class ErrorContext:
    agent_id: str
    operation: str
    timestamp: datetime
    additional_info: Dict[str, Any] = None

@dataclass
class ErrorHandlingResult:
    handled: bool
    action_taken: str
    retry_recommended: bool = False
    retry_delay: int = 0

class AgentErrorHandler:
    """Handles errors in agent operations"""
    
    def __init__(self):
        self.error_handlers: Dict[str, List[Callable]] = {}
        self.error_history: List[Dict[str, Any]] = []
        self.max_history = 1000
    
    def register_handler(
        self, 
        error_pattern: str, 
        handler: Callable,
        priority: int = 0
    ) -> None:
        """Register an error handler"""
        if error_pattern not in self.error_handlers:
            self.error_handlers[error_pattern] = []
        
        self.error_handlers[error_pattern].append({
            'handler': handler,
            'priority': priority
        })
        
        # Sort by priority
        self.error_handlers[error_pattern].sort(
            key=lambda x: x['priority'], 
            reverse=True
        )
    
    async def handle_error(
        self, 
        error: AgentError, 
        context: ErrorContext
    ) -> ErrorHandlingResult:
        """Handle an agent error"""
        
        # Record error
        self._record_error(error, context)
        
        # Find matching handlers
        handlers = self._find_matching_handlers(error)
        
        # Execute handlers in priority order
        for handler_info in handlers:
            try:
                result = await handler_info['handler'](error, context)
                if result.handled:
                    return result
            except Exception as handler_error:
                print(f"Error in error handler: {handler_error}")
        
        # Default handling
        return self._default_error_handling(error, context)
    
    def _record_error(self, error: AgentError, context: ErrorContext) -> None:
        """Record error in history"""
        error_record = {
            **error.to_dict(),
            "context": {
                "agent_id": context.agent_id,
                "operation": context.operation,
                "timestamp": context.timestamp.isoformat(),
                "additional_info": context.additional_info or {}
            }
        }
        
        self.error_history.append(error_record)
        
        # Maintain history size
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
    
    def _find_matching_handlers(self, error: AgentError) -> List[Dict[str, Any]]:
        """Find handlers that match the error"""
        matching = []
        
        for pattern, handlers in self.error_handlers.items():
            if self._matches_pattern(error, pattern):
                matching.extend(handlers)
        
        return sorted(matching, key=lambda x: x['priority'], reverse=True)
    
    def _matches_pattern(self, error: AgentError, pattern: str) -> bool:
        """Check if error matches pattern"""
        # Match by error code
        if error.error_code == pattern:
            return True
        
        # Match by category
        if error.category.value == pattern:
            return True
        
        # Match by severity
        if error.severity.value == pattern:
            return True
        
        return False
    
    def _default_error_handling(
        self, 
        error: AgentError, 
        context: ErrorContext
    ) -> ErrorHandlingResult:
        """Default error handling strategy"""
        
        if error.recoverable and error.severity != ErrorSeverity.CRITICAL:
            return ErrorHandlingResult(
                handled=True,
                action_taken="logged_and_ignored",
                retry_recommended=True,
                retry_delay=error.retry_after or 5
            )
        else:
            return ErrorHandlingResult(
                handled=True,
                action_taken="logged_and_failed",
                retry_recommended=False
            )
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_history:
            return {"total_errors": 0}
        
        # Count by category
        by_category = {}
        by_severity = {}
        
        for error in self.error_history:
            category = error.get("category", "unknown")
            severity = error.get("severity", "unknown")
            
            by_category[category] = by_category.get(category, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "by_category": by_category,
            "by_severity": by_severity,
            "recent_errors": self.error_history[-10:]  # Last 10 errors
        }