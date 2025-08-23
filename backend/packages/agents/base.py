"""베이스 에이전트 인터페이스 (BaseAgent)

이 모듈은 T-Developer v2의 모든 에이전트의 기반이 되는 추상 베이스 클래스를 정의합니다.
SOLID 원칙을 준수하며 Memory Hub와 AI Provider와의 통합을 제공합니다.
모든 에이전트가 상속받아야 하는 핵심 인터페이스입니다.

주요 기능:
1. 에이전트 표준 인터페이스 정의
2. 태스크 실행 라이프사이클 관리
3. Memory Hub 통합
4. AI Provider 추상화
5. 에러 처리 및 복구 메커니즘
6. 실행 추적 및 감사(Audit)
7. 비동기 실행 지원
8. 정책 기반 실행 제어

핵심 클래스:
- BaseAgent: 모든 에이전트의 추상 베이스 클래스
- AgentTask: 에이전트 입력 태스크 정의
- AgentResult: 에이전트 실행 결과
- TaskStatus: 태스크 상태 열거형

SOLID 원칙 적용:
- Single Responsibility: 각 에이전트는 하나의 책임만 가짐
- Open-Closed: 확장에는 열려있고 수정에는 닫혀있음
- Liskov Substitution: 모든 에이전트는 BaseAgent로 대체 가능
- Interface Segregation: 필요한 인터페이스만 구현
- Dependency Inversion: AI Provider는 추상화에 의존

사용 예시:
    class MyAgent(BaseAgent):
        async def execute(self, task: AgentTask) -> AgentResult:
            # 에이전트 로직 구현
            return AgentResult(success=True, data=result)

중요: 모든 에이전트는 이 베이스 클래스를 상속받아야 하며,
      execute 메소드를 반드시 구현해야 합니다.

작성자: T-Developer v2
버전: 2.0.0
최종 수정: 2024-12-20
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
from uuid import uuid4
import json
import logging

from pydantic import BaseModel, Field

from ..memory import MemoryHub
from ..memory.contexts import ContextType
from ..memory.document_context import SharedDocumentContext

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of an agent task execution."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AgentTask(BaseModel):
    """Input task for an agent.
    
    This follows the standard message format from the architecture docs.
    """
    
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    intent: str = Field(description="What the agent should do")
    inputs: Dict[str, Any] = Field(default_factory=dict)
    policy: Dict[str, Any] = Field(default_factory=dict)
    trace_id: Optional[str] = None
    deadline_seconds: int = Field(default=300)
    context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "analyze_code",
                "inputs": {
                    "file_path": "/path/to/file.py",
                    "analysis_type": "security"
                },
                "policy": {
                    "ai_mode": "auto",
                    "ai_first": True,
                    "dedup": True
                },
                "deadline_seconds": 300
            }
        }


@dataclass
class AgentResult:
    """Result from an agent execution.
    
    Attributes:
        success: Whether the execution was successful
        status: Current status of the task
        data: The actual result data
        error: Error message if failed
        metadata: Additional metadata
        artifacts: List of generated artifacts (files, reports, etc.)
        cost: Estimated cost of the operation
        tokens_used: Number of AI tokens used
        execution_time_ms: Time taken to execute
    """
    
    success: bool
    status: TaskStatus
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    cost: float = 0.0
    tokens_used: int = 0
    execution_time_ms: int = 0


class AIProvider(Protocol):
    """Protocol for AI providers (Claude, OpenAI, etc.).
    
    This follows the Dependency Inversion Principle (DIP).
    """
    
    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7
    ) -> str:
        """Generate AI completion.
        
        Args:
            prompt: The user prompt
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            
        Returns:
            The generated text
        """
        ...
    
    async def analyze_code(
        self,
        code: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze code using AI.
        
        Args:
            code: The code to analyze
            analysis_type: Type of analysis (security, performance, etc.)
            
        Returns:
            Analysis results
        """
        ...


class BaseAgent(ABC):
    """Abstract base class for all agents in T-Developer v2.
    
    This class provides:
    - Memory Hub integration for reading/writing context
    - AI provider integration for intelligent processing
    - Standard input/output format
    - Error handling and retry logic
    
    All agents must inherit from this class and implement the execute method.
    
    Attributes:
        agent_id: Unique identifier for this agent
        name: Human-readable name
        version: Semantic version
        memory_hub: Reference to the Memory Hub
        ai_provider: Optional AI provider for intelligent processing
        max_retries: Maximum number of retry attempts
        timeout_seconds: Default timeout for operations
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "BaseAgent",
        version: str = "1.0.0",
        memory_hub: Optional[MemoryHub] = None,
        ai_provider: Optional[AIProvider] = None,
        max_retries: int = 3,
        timeout_seconds: int = 300,
        document_context: Optional[SharedDocumentContext] = None,
        persona: Optional['AgentPersona'] = None
    ) -> None:
        """Initialize the base agent.
        
        Args:
            agent_id: Unique identifier (auto-generated if not provided)
            name: Human-readable name
            version: Semantic version
            memory_hub: Memory Hub instance
            ai_provider: AI provider for intelligent processing
            max_retries: Maximum retry attempts
            timeout_seconds: Default timeout
            document_context: Shared document context for all agents
            persona: Agent persona for consistent behavior
        """
        self.agent_id = agent_id or str(uuid4())
        self.name = name
        self.version = version
        self.memory_hub = memory_hub
        self.ai_provider = ai_provider
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.document_context = document_context
        self.persona = persona
        
        # 페르소나가 없으면 자동으로 로드
        if not self.persona and name != "BaseAgent":
            from .personas import get_persona
            self.persona = get_persona(name)
    
    async def generate_report(self, analysis_result: AgentResult, report_format: str = "markdown") -> Dict[str, Any]:
        """Generate a report from analysis results using real AI analysis.
        
        Each agent can generate its own report after analysis with AI-powered insights.
        
        Args:
            analysis_result: The result from execute()
            report_format: Format of the report (markdown, json, html)
            
        Returns:
            Dictionary with report path and content
        """
        from pathlib import Path
        import json
        from datetime import datetime
        
        # Generate AI-enhanced report content if AI provider is available
        if self.ai_provider:
            report_content = await self._generate_ai_report(analysis_result, report_format)
        else:
            # Fallback to basic formatting
            report_content = self._format_report(analysis_result, report_format)
        
        timestamp = datetime.now()
        
        # Save to memory hub if available
        if self.memory_hub:
            # Store in A_CTX (Agent Context) 
            report_key = f"{self.name}/reports/{timestamp.strftime('%Y%m%d_%H%M%S')}/{report_format}"
            await self.memory_hub.put(
                key=report_key,
                value={
                    "agent": self.name,
                    "format": report_format,
                    "content": report_content,
                    "analysis_result": analysis_result.data,
                    "timestamp": timestamp.isoformat()
                },
                context_type=ContextType.A_CTX
            )
            
            # Also save to filesystem for now (temporary until full memory integration)
            report_dir = Path("reports") / self.name / timestamp.strftime("%Y%m%d_%H%M%S")
        else:
            # Fallback to filesystem only
            report_dir = Path("reports") / self.name / timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Create report directory (temporary - will be removed when fully memory-based)
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # Save report to filesystem (temporary)
        extension = "md" if report_format == "markdown" else report_format
        report_path = report_dir / f"{self.name}_report.{extension}"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            if report_format == "json":
                json.dump(report_content, f, indent=2, ensure_ascii=False)
            else:
                f.write(report_content)
        
        return {
            "path": str(report_path),  # 나중에 memory_key로 변경
            "memory_key": f"{self.name}/reports/{timestamp.strftime('%Y%m%d_%H%M%S')}/{report_format}" if self.memory_hub else None,
            "format": report_format,
            "content": report_content,
            "timestamp": timestamp.isoformat()
        }
    
    def _format_report(self, result: AgentResult, format_type: str) -> Any:
        """Format the report based on type.
        
        Args:
            result: Analysis result
            format_type: Report format
            
        Returns:
            Formatted report content
        """
        from datetime import datetime
        
        if format_type == "json":
            return {
                "agent": self.name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "success": result.success,
                "status": str(result.status),
                "data": result.data,
                "metadata": result.metadata
            }
        
        elif format_type == "markdown":
            content = f"""# {self.name} Analysis Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Agent Version**: {self.version}
**Status**: {result.status}
**Success**: {'✅' if result.success else '❌'}

## Analysis Results

"""
            if result.data:
                for key, value in result.data.items():
                    content += f"### {key.replace('_', ' ').title()}\n\n"
                    if isinstance(value, list):
                        for item in value:
                            content += f"- {item}\n"
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            content += f"- **{k}**: {v}\n"
                    else:
                        content += f"{value}\n"
                    content += "\n"
            
            if result.error:
                content += f"\n## Errors\n\n{result.error}\n"
            
            return content
        
        elif format_type == "html":
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.name} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .metadata {{ background: #f0f0f0; padding: 10px; }}
    </style>
</head>
<body>
    <h1>{self.name} Analysis Report</h1>
    <div class="metadata">
        <p><strong>Generated</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Status</strong>: <span class="{'success' if result.success else 'failure'}">{result.status}</span></p>
    </div>
    <h2>Results</h2>
    <pre>{self._json_dumps(result.data) if result.data else 'No data'}</pre>
</body>
</html>"""
            return html
        
        return str(result)
    
    def _json_dumps(self, data: Any) -> str:
        """Safely dump data to JSON string."""
        import json
        return json.dumps(data, indent=2, default=str, ensure_ascii=False)
    
    async def _generate_ai_report(self, result: AgentResult, format_type: str) -> Any:
        """Generate an AI-enhanced report with insights and recommendations.
        
        Args:
            result: Analysis result
            format_type: Report format (markdown, json, html)
            
        Returns:
            AI-generated report content
        """
        from datetime import datetime
        import json
        
        # Prepare data summary for AI
        data_summary = json.dumps(result.data, indent=2, default=str) if result.data else "No data"
        
        # Create comprehensive prompt for AI report generation
        prompt = f"""You are an expert technical analyst generating a comprehensive report for the {self.name} agent.

Analysis Results:
{data_summary}

Status: {result.status}
Success: {result.success}
Metadata: {json.dumps(result.metadata, indent=2, default=str)}

Generate a comprehensive report in {format_type} format that includes:

1. **Executive Summary**: High-level overview of findings
2. **Key Insights**: Most important discoveries and patterns
3. **Risk Assessment**: Identify potential risks and their severity
4. **Performance Metrics**: Quantitative analysis where applicable
5. **Recommendations**: Actionable next steps with priority levels
6. **Technical Details**: Deep dive into specific findings
7. **Impact Analysis**: How these findings affect the system
8. **Quality Metrics**: Code quality, test coverage, security posture
9. **Improvement Roadmap**: Phased approach to address issues

Make the report:
- Data-driven with specific metrics and examples
- Actionable with clear prioritized recommendations
- Professional and suitable for technical stakeholders
- Include severity indicators (🔴 Critical, 🟡 Warning, 🟢 Good)

Format requirements:
- For markdown: Use proper headers, lists, and emphasis
- For json: Structured data with sections as keys
- For html: Include styling and proper semantic markup

Generate the complete report now:"""

        system_prompt = f"""You are a senior technical analyst specialized in {self.name.replace('_', ' ')} analysis.
Your reports are known for being comprehensive, insightful, and actionable.
You always base your analysis on actual data and provide specific, measurable recommendations."""

        try:
            # Get AI-generated report
            ai_response = await self.ai_provider.complete(
                prompt=prompt,
                system=system_prompt,
                max_tokens=4096,
                temperature=0.3  # Lower temperature for consistent, factual reports
            )
            
            # Post-process based on format
            if format_type == "json":
                # Try to parse and validate JSON
                try:
                    if "```json" in ai_response:
                        json_start = ai_response.find("```json") + 7
                        json_end = ai_response.find("```", json_start)
                        ai_response = ai_response[json_start:json_end].strip()
                    
                    parsed = json.loads(ai_response)
                    # Add metadata
                    parsed["metadata"] = {
                        "agent": self.name,
                        "version": self.version,
                        "generated_at": datetime.now().isoformat(),
                        "ai_enhanced": True
                    }
                    return parsed
                except json.JSONDecodeError:
                    # Fallback to structured format
                    return {
                        "report": ai_response,
                        "metadata": {
                            "agent": self.name,
                            "version": self.version,
                            "generated_at": datetime.now().isoformat(),
                            "ai_enhanced": True,
                            "format_error": "Could not parse as JSON"
                        }
                    }
            
            elif format_type == "html":
                # Wrap in proper HTML if not already
                if not ai_response.startswith("<!DOCTYPE"):
                    ai_response = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.name} AI Analysis Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .report-container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        .critical {{ color: #dc3545; font-weight: bold; }}
        .warning {{ color: #ffc107; font-weight: bold; }}
        .good {{ color: #28a745; font-weight: bold; }}
        .metric {{ 
            display: inline-block;
            padding: 5px 10px;
            margin: 5px;
            border-radius: 5px;
            background: #e9ecef;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }}
        th {{ background: #f8f9fa; }}
    </style>
</head>
<body>
    <div class="report-container">
        <h1>{self.name} AI-Enhanced Analysis Report</h1>
        <p><em>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</em></p>
        {ai_response}
    </div>
</body>
</html>"""
            
            return ai_response
            
        except Exception as e:
            # Fallback to basic report if AI fails
            print(f"AI report generation failed: {e}, falling back to basic format")
            return self._format_report(result, format_type)
    
    def get_all_context_for_prompt(self) -> str:
        """모든 공유 문서를 AI 프롬프트용으로 가져오기
        
        Returns:
            AI가 참조할 수 있는 모든 문서 컨텍스트
        """
        if self.document_context:
            return self.document_context.get_context_for_ai(include_history=True, max_history_loops=2)
        return "{}"
    
    def add_document_to_context(self, document: Dict[str, Any], document_type: str = "analysis") -> None:
        """현재 에이전트의 문서를 공유 컨텍스트에 추가
        
        Args:
            document: 추가할 문서
            document_type: 문서 타입
        """
        if self.document_context:
            self.document_context.add_document(self.name, document, document_type)
            logger.info(f"{self.name} added {document_type} document to shared context")
    
    async def execute_with_context(self, task: AgentTask) -> AgentResult:
        """모든 공유 문서 컨텍스트를 활용하여 태스크 실행
        
        이 메서드는 execute()를 래핑하여 모든 공유 문서를 참조할 수 있게 합니다.
        
        Args:
            task: 실행할 태스크
            
        Returns:
            실행 결과
        """
        # 태스크에 모든 공유 문서 컨텍스트 추가
        if self.document_context:
            all_docs = self.document_context.get_all_documents()
            task.context["shared_documents"] = all_docs
            task.context["document_summary"] = self.document_context.get_analysis_summary()
            
            logger.info(f"{self.name} has access to {len(all_docs)} shared documents")
        
        # 실제 execute 메서드 호출
        result = await self.execute(task)
        
        # 결과를 공유 컨텍스트에 추가
        if result.success and result.data:
            self.add_document_to_context(result.data, document_type="analysis")
        
        return result
    
    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """Execute the agent's main task.
        
        This is the core method that each agent must implement.
        It should:
        1. Validate the input
        2. Read relevant context from memory
        3. Perform the agent's specific work
        4. Write results to memory
        5. Return a standardized result
        
        Args:
            task: The task to execute
            
        Returns:
            The execution result
        """
        pass
    
    async def validate_input(self, task: AgentTask) -> bool:
        """Validate the input task.
        
        Override this method to add agent-specific validation.
        
        Args:
            task: The task to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation
        if not task.intent:
            return False
        
        # Check deadline is reasonable
        if task.deadline_seconds <= 0:
            return False
        
        return True
    
    async def read_memory(
        self,
        context_type: ContextType,
        key: str
    ) -> Optional[Any]:
        """Read from Memory Hub.
        
        Args:
            context_type: The context to read from
            key: The key to look up
            
        Returns:
            The stored value or None
        """
        if not self.memory_hub:
            return None
        
        try:
            return await self.memory_hub.get(context_type, key)
        except Exception as e:
            # In production, use proper logging
            print(f"Error reading memory: {e}")
            return None
    
    async def write_memory(
        self,
        context_type: ContextType,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Write to Memory Hub.
        
        Args:
            context_type: The context to write to
            key: The key to store under
            value: The value to store
            ttl_seconds: Optional TTL
            tags: Optional tags for categorization
            
        Returns:
            True if successful, False otherwise
        """
        if not self.memory_hub:
            return False
        
        try:
            return await self.memory_hub.put(
                context_type,
                key,
                value,
                ttl_seconds=ttl_seconds,
                tags=tags,
                metadata={"agent_id": self.agent_id, "timestamp": datetime.utcnow().isoformat()}
            )
        except Exception as e:
            # In production, use proper logging
            print(f"Error writing memory: {e}")
            return False
    
    async def search_memory(
        self,
        context_type: ContextType,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search Memory Hub for relevant entries.
        
        Args:
            context_type: The context to search
            tags: Optional tags to filter by
            limit: Maximum results
            
        Returns:
            List of matching entries
        """
        if not self.memory_hub:
            return []
        
        try:
            return await self.memory_hub.search(context_type, tags, limit)
        except Exception as e:
            # In production, use proper logging
            print(f"Error searching memory: {e}")
            return []
    
    async def use_ai(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096
    ) -> Optional[str]:
        """Use AI provider for intelligent processing.
        
        Args:
            prompt: The prompt to send
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            
        Returns:
            The AI response or None if no provider
        """
        if not self.ai_provider:
            return None
        
        try:
            return await self.ai_provider.complete(
                prompt=prompt,
                system=system,
                max_tokens=max_tokens
            )
        except Exception as e:
            # In production, use proper logging
            print(f"Error using AI: {e}")
            return None
    
    def format_result(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
        **kwargs: Any
    ) -> AgentResult:
        """Format a standardized result.
        
        Args:
            success: Whether the operation was successful
            data: The result data
            error: Error message if failed
            **kwargs: Additional fields for AgentResult
            
        Returns:
            Formatted AgentResult
        """
        status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        
        return AgentResult(
            success=success,
            status=status,
            data=data,
            error=error,
            **kwargs
        )
    
    async def log_execution(
        self,
        task: AgentTask,
        result: AgentResult
    ) -> None:
        """Log execution to Memory Hub.
        
        Args:
            task: The executed task
            result: The execution result
        """
        if not self.memory_hub:
            return
        
        # Log to agent's personal context
        await self.write_memory(
            ContextType.A_CTX,
            f"{self.agent_id}_execution_{task.task_id}",
            {
                "task": task.dict(),
                "result": {
                    "success": result.success,
                    "status": result.status.value,
                    "error": result.error,
                    "execution_time_ms": result.execution_time_ms,
                    "tokens_used": result.tokens_used,
                }
            },
            ttl_seconds=86400,  # Keep for 24 hours
            tags=["execution", self.name]
        )
        
        # Log summary to shared context
        await self.write_memory(
            ContextType.S_CTX,
            f"latest_execution_{self.agent_id}",
            {
                "agent": self.name,
                "task_intent": task.intent,
                "success": result.success,
                "timestamp": datetime.utcnow().isoformat()
            },
            ttl_seconds=3600,  # Keep for 1 hour
            tags=["latest", self.name]
        )