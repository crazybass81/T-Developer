
import sys
import os
sys.path.append('/home/ec2-user/T-DeveloperMVP/backend/src'

try:
    from llm import ModelProviderFactory, ModelConfig, model_registry
    from llm.providers.mock_provider import MockProvider
    import asyncio
    
    async def test():
        print("1. Testing Model Registry...")
        models = model_registry.list_models()
        print(f"✅ Found {len(models)} registered models")
        
        print("\n2. Testing Mock Provider...")
        ModelProviderFactory.register("mock", MockProvider)
        
        config = ModelConfig(name="mock-model", provider="mock")
        provider = ModelProviderFactory.create("mock", config)
        await provider.initialize()
        print("✅ Mock provider initialized")
        
        print("\n3. Testing Generation...")
        response = await provider.generate("Hello")
        print(f"✅ Response: {response.text[:30]}...")
        
        print("\n4. Testing Streaming...")
        parts = []
        async for chunk in provider.stream_generate("Test"):
            parts.append(chunk)
        print(f"✅ Streamed: {''.join(parts).strip()}")
        
        print("\n5. Testing Embeddings...")
        embeddings = await provider.embed(["test"])
        print(f"✅ Embedding size: {len(embeddings[0])}")
        
        print("\n6. Testing Utils...")
        tokens = provider.estimate_tokens("test")
        cost = provider.get_cost_estimate(10, 5)
        print(f"✅ Tokens: {tokens}, Cost: {cost}")
        
        print("\n🎉 All tests passed!")
    
    asyncio.run(test())
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
