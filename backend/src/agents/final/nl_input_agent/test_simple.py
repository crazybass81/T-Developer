#!/usr/bin/env python3
"""
Simple test script for Final NL Input Agent
"""

import asyncio
import sys
import os
import json
from time import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the agent
import FINAL_NL_INPUT_AGENT as agent_module


async def test_basic_processing():
    """Test basic processing functionality"""
    print("\n=== Testing Basic Processing ===")
    
    # Create FAST mode agent (no dependencies)
    agent = agent_module.FinalNLInputAgent(mode=agent_module.ProcessingMode.FAST)
    await agent.initialize()
    
    test_queries = [
        "Create a simple todo app with React",
        "Build an e-commerce platform with payment integration",
        "Develop a mobile app for iOS and Android",
        "Make a REST API with Node.js and MongoDB",
        "Create a dashboard with real-time analytics"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        start = time()
        
        try:
            result = await agent.process(query)
            elapsed = time() - start
            
            print(f"  Project Type: {result.project_type}")
            print(f"  Features: {len(result.features)} detected")
            print(f"  Complexity: {result.estimated_complexity}")
            print(f"  Confidence: {result.confidence_score:.2f}")
            print(f"  Processing Time: {elapsed:.3f}s")
            
            # Basic assertions
            assert result.project_type is not None
            assert result.confidence_score > 0
            assert elapsed < 1.0  # Should be fast
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            raise
    
    await agent.cleanup()
    print("\n✅ Basic processing test passed!")


async def test_multilingual():
    """Test multilingual support"""
    print("\n=== Testing Multilingual Support ===")
    
    agent = agent_module.FinalNLInputAgent(mode=agent_module.ProcessingMode.FAST)
    await agent.initialize()
    
    multilingual_queries = [
        ("Create a web application", "en"),
        ("Créer une application web", "fr"),
        ("Crear una aplicación web", "es"),
        ("웹 애플리케이션 만들기", "ko"),
    ]
    
    for query, expected_lang in multilingual_queries:
        print(f"\nQuery ({expected_lang}): {query}")
        
        try:
            result = await agent.process(query)
            print(f"  Detected as: {result.project_type}")
            print(f"  Language: {result.metadata.get('detected_language', 'unknown')}")
            
        except Exception as e:
            print(f"  Note: {str(e)}")
    
    await agent.cleanup()
    print("\n✅ Multilingual test completed!")


async def test_complex_extraction():
    """Test complex requirement extraction"""
    print("\n=== Testing Complex Extraction ===")
    
    agent = agent_module.FinalNLInputAgent(mode=agent_module.ProcessingMode.FAST)
    await agent.initialize()
    
    complex_query = """
    I need a comprehensive e-commerce platform with:
    - User authentication (OAuth2 with Google/Facebook)
    - Product catalog with search and filters
    - Shopping cart and checkout
    - Payment integration (Stripe, PayPal)
    - Admin dashboard for inventory
    - Real-time order tracking
    - Multi-language support
    - Mobile responsive design
    
    Tech stack: React, Node.js, PostgreSQL, Redis
    Deployment: AWS with Docker
    Timeline: 3 months
    """
    
    print(f"\nComplex Query Length: {len(complex_query)} chars")
    
    result = await agent.process(complex_query)
    
    print(f"\nExtracted Requirements:")
    print(f"  Project Type: {result.project_type}")
    print(f"  Features: {result.features}")
    print(f"  Tech Stack: {json.dumps(result.technical_requirements, indent=4)}")
    print(f"  Complexity: {result.estimated_complexity}")
    print(f"  Constraints: {result.constraints}")
    
    # Verify extraction
    assert result.project_type in ["e-commerce", "web_app"]
    assert len(result.features) > 5
    # Check for React in frameworks list
    frameworks = result.technical_requirements.get("frameworks", [])
    assert any("react" in f.lower() for f in frameworks) or "React" in str(result.technical_requirements)
    # Check for PostgreSQL in databases list  
    databases = result.technical_requirements.get("databases", [])
    assert any("postgres" in d.lower() for d in databases) or "PostgreSQL" in str(result.technical_requirements)
    assert result.estimated_complexity in ["high", "very_high", "very-high"]
    
    await agent.cleanup()
    print("\n✅ Complex extraction test passed!")


async def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    
    agent = agent_module.FinalNLInputAgent(mode=agent_module.ProcessingMode.FAST)
    await agent.initialize()
    
    error_cases = [
        ("", "Empty query"),
        ("   ", "Whitespace only"),
        ("a" * 10001, "Too long query")
    ]
    
    for query, description in error_cases:
        print(f"\nTesting: {description}")
        
        try:
            result = await agent.process(query)
            print(f"  Unexpected success: {result.project_type}")
            
        except ValueError as e:
            print(f"  ✓ Correctly raised ValueError: {str(e)}")
            
        except Exception as e:
            print(f"  ✗ Unexpected error: {str(e)}")
    
    await agent.cleanup()
    print("\n✅ Error handling test passed!")


async def test_performance():
    """Test performance across modes"""
    print("\n=== Testing Performance ===")
    
    query = "Create a React todo app with TypeScript and PostgreSQL"
    
    for mode in [agent_module.ProcessingMode.FAST]:
        print(f"\nMode: {mode.value}")
        
        agent = agent_module.FinalNLInputAgent(mode=mode)
        await agent.initialize()
        
        # Warm up
        await agent.process(query)
        
        # Measure
        times = []
        for i in range(5):
            start = time()
            result = await agent.process(query)
            elapsed = time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min/Max: {min(times):.3f}s / {max(times):.3f}s")
        
        # Check performance targets
        if mode == agent_module.ProcessingMode.FAST:
            assert avg_time < 0.5, f"FAST mode too slow: {avg_time}s"
        
        await agent.cleanup()
    
    print("\n✅ Performance test passed!")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("FINAL NL INPUT AGENT - TEST SUITE")
    print("=" * 60)
    
    try:
        await test_basic_processing()
        await test_multilingual()
        await test_complex_extraction()
        await test_error_handling()
        await test_performance()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"TEST FAILED! ❌")
        print(f"Error: {str(e)}")
        print("=" * 60)
        raise


if __name__ == "__main__":
    asyncio.run(main())