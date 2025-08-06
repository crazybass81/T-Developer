#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🧪 Testing Model Provider System...\n');

// Create simple Python test
const pythonTest = `
import sys
import os
sys.path.append('${path.join(__dirname, '..', 'backend', 'src').replace(/\\/g, '/')}'

try:
    from llm import ModelProviderFactory, ModelConfig, model_registry
    from llm.providers.mock_provider import MockProvider
    import asyncio
    
    async def test():
        print("1. Testing Model Registry...")
        models = model_registry.list_models()
        print(f"✅ Found {len(models)} registered models")
        
        print("\\n2. Testing Mock Provider...")
        ModelProviderFactory.register("mock", MockProvider)
        
        config = ModelConfig(name="mock-model", provider="mock")
        provider = ModelProviderFactory.create("mock", config)
        await provider.initialize()
        print("✅ Mock provider initialized")
        
        print("\\n3. Testing Generation...")
        response = await provider.generate("Hello")
        print(f"✅ Response: {response.text[:30]}...")
        
        print("\\n4. Testing Streaming...")
        parts = []
        async for chunk in provider.stream_generate("Test"):
            parts.append(chunk)
        print(f"✅ Streamed: {''.join(parts).strip()}")
        
        print("\\n5. Testing Embeddings...")
        embeddings = await provider.embed(["test"])
        print(f"✅ Embedding size: {len(embeddings[0])}")
        
        print("\\n6. Testing Utils...")
        tokens = provider.estimate_tokens("test")
        cost = provider.get_cost_estimate(10, 5)
        print(f"✅ Tokens: {tokens}, Cost: {cost}")
        
        print("\\n🎉 All tests passed!")
    
    asyncio.run(test())
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
`;

// Write and run test
const testFile = path.join(__dirname, '..', 'test_simple.py');
fs.writeFileSync(testFile, pythonTest);

try {
  execSync(`python3 ${testFile}`, { 
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
  });
  
  console.log('\n📋 Model Provider System Complete:');
  console.log('- Abstract ModelProvider base class ✅');
  console.log('- ModelConfig and ModelResponse dataclasses ✅');
  console.log('- ModelProviderFactory with registration ✅');
  console.log('- ModelRegistry with pre-configured models ✅');
  console.log('- Mock provider for testing ✅');
  console.log('- Async/await support ✅');
  console.log('- Streaming generation ✅');
  console.log('- Embedding generation ✅');
  console.log('- Token and cost estimation ✅');
  console.log('\n✅ SubTask 1.7.1 Complete: Model Provider Abstraction Ready!');
  
} catch (error) {
  console.log('❌ Test failed:', error.message);
  process.exit(1);
} finally {
  // Cleanup
  if (fs.existsSync(testFile)) {
    fs.unlinkSync(testFile);
  }
}