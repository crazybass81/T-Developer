"""
Bedrock and AgentCore Configuration
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class BedrockModel(Enum):
    """Available Bedrock models"""

    CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    CLAUDE_INSTANT = "anthropic.claude-instant-v1"
    TITAN_TEXT_EXPRESS = "amazon.titan-text-express-v1"
    TITAN_TEXT_LITE = "amazon.titan-text-lite-v1"
    COHERE_COMMAND = "cohere.command-text-v14"
    AI21_JURASSIC = "ai21.j2-ultra-v1"


@dataclass
class BedrockConfig:
    """Bedrock configuration settings"""

    region: str
    model_id: str
    max_tokens: int
    temperature: float
    top_p: float
    top_k: int
    stop_sequences: list
    retry_attempts: int
    timeout: int

    @classmethod
    def from_env(
        cls, model: BedrockModel = BedrockModel.CLAUDE_3_SONNET
    ) -> "BedrockConfig":
        """Create config from environment variables"""
        return cls(
            region=os.getenv("AWS_REGION", "us-east-1"),
            model_id=model.value,
            max_tokens=int(os.getenv("BEDROCK_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("BEDROCK_TEMPERATURE", "0.7")),
            top_p=float(os.getenv("BEDROCK_TOP_P", "0.9")),
            top_k=int(os.getenv("BEDROCK_TOP_K", "250")),
            stop_sequences=os.getenv("BEDROCK_STOP_SEQUENCES", "").split(",")
            if os.getenv("BEDROCK_STOP_SEQUENCES")
            else [],
            retry_attempts=int(os.getenv("BEDROCK_RETRY_ATTEMPTS", "3")),
            timeout=int(os.getenv("BEDROCK_TIMEOUT", "60")),
        )


@dataclass
class AgentCoreConfig:
    """AgentCore runtime configuration"""

    agent_id: str
    agent_alias_id: str
    session_ttl: int
    memory_type: str
    max_memory_size: int
    enable_tracing: bool
    enable_metrics: bool

    @classmethod
    def from_env(cls) -> "AgentCoreConfig":
        """Create config from environment variables"""
        return cls(
            agent_id=os.getenv("BEDROCK_AGENT_ID", ""),
            agent_alias_id=os.getenv("BEDROCK_AGENT_ALIAS_ID", ""),
            session_ttl=int(os.getenv("AGENT_SESSION_TTL", "3600")),
            memory_type=os.getenv("AGENT_MEMORY_TYPE", "dynamodb"),
            max_memory_size=int(os.getenv("AGENT_MAX_MEMORY_SIZE", "10000")),
            enable_tracing=os.getenv("AGENT_ENABLE_TRACING", "true").lower() == "true",
            enable_metrics=os.getenv("AGENT_ENABLE_METRICS", "true").lower() == "true",
        )


class BedrockClient:
    """Bedrock client wrapper"""

    def __init__(self, config: Optional[BedrockConfig] = None):
        """Initialize Bedrock client"""
        import boto3

        self.config = config or BedrockConfig.from_env()
        self.client = boto3.client("bedrock-runtime", region_name=self.config.region)
        self.agent_client = boto3.client(
            "bedrock-agent-runtime", region_name=self.config.region
        )

    def invoke_model(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Invoke Bedrock model"""
        import json

        # Prepare request body based on model type
        if "claude" in self.config.model_id:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "top_k": kwargs.get("top_k", self.config.top_k),
                "stop_sequences": kwargs.get(
                    "stop_sequences", self.config.stop_sequences
                ),
            }
        elif "titan" in self.config.model_id:
            body = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": kwargs.get("max_tokens", self.config.max_tokens),
                    "temperature": kwargs.get("temperature", self.config.temperature),
                    "topP": kwargs.get("top_p", self.config.top_p),
                    "stopSequences": kwargs.get(
                        "stop_sequences", self.config.stop_sequences
                    ),
                },
            }
        else:
            # Generic format for other models
            body = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "stop_sequences": kwargs.get(
                    "stop_sequences", self.config.stop_sequences
                ),
            }

        # Invoke model
        response = self.client.invoke_model(
            modelId=self.config.model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )

        # Parse response
        response_body = json.loads(response["body"].read())

        # Extract text based on model type
        if "claude" in self.config.model_id:
            return {
                "text": response_body.get("content", [{}])[0].get("text", ""),
                "usage": response_body.get("usage", {}),
                "stop_reason": response_body.get("stop_reason"),
            }
        elif "titan" in self.config.model_id:
            results = response_body.get("results", [{}])
            return {
                "text": results[0].get("outputText", "") if results else "",
                "usage": {
                    "inputTokens": response_body.get("inputTextTokenCount", 0),
                    "outputTokens": results[0].get("tokenCount", 0) if results else 0,
                },
            }
        else:
            return {
                "text": response_body.get("completion", response_body.get("text", "")),
                "usage": response_body.get("usage", {}),
            }

    def invoke_agent(
        self, agent_id: str, agent_alias_id: str, session_id: str, input_text: str
    ) -> Dict[str, Any]:
        """Invoke Bedrock agent"""
        response = self.agent_client.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=input_text,
        )

        # Process streaming response
        completion = ""
        for event in response.get("completion", []):
            chunk = event.get("chunk", {})
            if "bytes" in chunk:
                completion += chunk["bytes"].decode("utf-8")

        return {
            "sessionId": response.get("sessionId"),
            "completion": completion,
            "citations": response.get("citations", []),
            "trace": response.get("trace", {}),
        }


class AgentCoreRuntime:
    """AgentCore runtime manager"""

    def __init__(self, config: Optional[AgentCoreConfig] = None):
        """Initialize AgentCore runtime"""
        self.config = config or AgentCoreConfig.from_env()
        self.bedrock_client = BedrockClient()
        self.sessions: Dict[str, Dict] = {}

    def create_session(self, user_id: str) -> str:
        """Create new agent session"""
        import uuid
        from datetime import datetime, timedelta

        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow()
            + timedelta(seconds=self.config.session_ttl),
            "memory": [],
            "context": {},
        }

        return session_id

    def invoke(self, session_id: str, input_text: str) -> Dict[str, Any]:
        """Invoke agent with session context"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Add input to memory
        session["memory"].append({"role": "user", "content": input_text})

        # Invoke agent
        result = self.bedrock_client.invoke_agent(
            agent_id=self.config.agent_id,
            agent_alias_id=self.config.agent_alias_id,
            session_id=session_id,
            input_text=input_text,
        )

        # Add response to memory
        session["memory"].append({"role": "assistant", "content": result["completion"]})

        # Trim memory if needed
        if len(session["memory"]) > self.config.max_memory_size:
            session["memory"] = session["memory"][-self.config.max_memory_size :]

        return result

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session details"""
        return self.sessions.get(session_id)

    def end_session(self, session_id: str) -> bool:
        """End agent session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


# Export configurations
__all__ = [
    "BedrockModel",
    "BedrockConfig",
    "AgentCoreConfig",
    "BedrockClient",
    "AgentCoreRuntime",
]
