from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from .providers import ModelProviderFactory, ModelConfig, ModelResponse

class ModelFallbackManager:
    def __init__(self):
        self.health_checker = ModelHealthChecker()
        self.load_balancer = ModelLoadBalancer()
        self.fallback_chains = self._define_fallback_chains()
    
    def _define_fallback_chains(self) -> Dict[str, List[str]]:
        return {
            'gpt-4': ['gpt-4-turbo', 'claude-3-opus', 'gpt-3.5-turbo'],
            'claude-3-opus': ['claude-3-sonnet', 'gpt-4', 'claude-2.1'],
            'bedrock-claude': ['bedrock-titan', 'claude-3-opus', 'gpt-4'],
            'gpt-3.5-turbo': ['gpt-4', 'claude-3-haiku'],
            'claude-3-sonnet': ['claude-3-opus', 'gpt-4', 'gpt-3.5-turbo']
        }
    
    async def execute_with_fallback(
        self, 
        primary_model: str, 
        prompt: str, 
        options: Dict[str, Any]
    ) -> ModelResponse:
        fallback_chain = [primary_model] + self.fallback_chains.get(primary_model, [])
        last_error = None
        
        for model in fallback_chain:
            try:
                if not await self.health_checker.is_healthy(model):
                    continue
                
                if not await self.load_balancer.can_handle_request(model):
                    continue
                
                provider_name = model.split('-')[0]
                provider = ModelProviderFactory.create(
                    provider_name, 
                    ModelConfig(name=model, **options)
                )
                
                await provider.initialize()
                response = await provider.generate(prompt, options)
                
                await self._record_success(model)
                return response
                
            except Exception as e:
                last_error = e
                await self._record_failure(model, e)
                
                if not self._is_retryable_error(e):
                    raise
                
                continue
        
        raise Exception(f"All models in fallback chain failed. Last error: {last_error}")
    
    def _is_retryable_error(self, error: Exception) -> bool:
        retryable_errors = ['rate_limit', 'timeout', 'service_unavailable', 'internal_server_error']
        error_message = str(error).lower()
        return any(err in error_message for err in retryable_errors)
    
    async def _record_success(self, model: str) -> None:
        pass
    
    async def _record_failure(self, model: str, error: Exception) -> None:
        pass

class ModelHealthChecker:
    def __init__(self):
        self.health_status = defaultdict(lambda: {'healthy': True, 'last_check': datetime.now()})
    
    async def is_healthy(self, model: str) -> bool:
        status = self.health_status[model]
        
        # Check if we need to refresh health status
        if datetime.now() - status['last_check'] > timedelta(minutes=5):
            status['healthy'] = await self._check_model_health(model)
            status['last_check'] = datetime.now()
        
        return status['healthy']
    
    async def _check_model_health(self, model: str) -> bool:
        # Simple health check implementation
        return True

class ModelLoadBalancer:
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.rate_limits = self._load_rate_limits()
    
    def _load_rate_limits(self) -> Dict[str, int]:
        return {
            'gpt-4': 500,
            'gpt-3.5-turbo': 3500,
            'claude-3-opus': 400,
            'claude-3-sonnet': 1000,
            'bedrock-claude': 200
        }
    
    async def can_handle_request(self, model: str) -> bool:
        current_count = self.request_counts[model]
        rate_limit = self.rate_limits.get(model, float('inf'))
        
        return current_count < rate_limit * 0.8  # 80% threshold