#!/usr/bin/env python3
"""
Test script for real agent implementations
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.agentcore.nl_input.main import NLInputAgent  # noqa: E402
from src.agents.agentcore.search.main import SearchAgent  # noqa: E402


def test_search_agent():
    """Test Search Agent with real search functionality"""
    print("\n=== Testing Search Agent ===")
    agent = SearchAgent()

    # Test 1: Search for Python
    request = {"input": "test", "query": "python", "limit": 5}
    result = agent.process(request)
    print(f"Search for 'python': {result}")

    # Test 2: Search with filter
    request = {"input": "test", "query": "aws", "filters": {"category": "cloud"}, "limit": 3}
    result = agent.process(request)
    print(f"Search for 'aws' with filter: {result}")

    # Test 3: Empty search (should return all)
    request = {"input": "test", "query": "", "limit": 10}
    result = agent.process(request)
    print(f"Empty search: Found {len(result['result']['results'])} results")


def test_nl_input_agent():
    """Test NL Input Agent with real NLP processing"""
    print("\n=== Testing NL Input Agent ===")
    agent = NLInputAgent()

    # Test 1: Complex request
    request = {
        "input": "I need to create a web application with Python backend and React frontend. It must have secure authentication and fast performance. The database should use PostgreSQL."
    }
    result = agent.process(request)
    print("Complex request analysis:")
    print(f"  Intent: {result['result']['intent']}")
    print(f"  Entities: {result['result']['entities']}")
    print(f"  Requirements: {len(result['result']['requirements'])} found")

    # Test 2: Simple request
    request = {"input": "Fix the login bug"}
    result = agent.process(request)
    print("\nSimple request analysis:")
    print(f"  Intent: {result['result']['intent']}")
    print(f"  Entities: {result['result']['entities']}")

    # Test 3: Deploy request
    request = {"input": "Deploy the application to AWS cloud with high availability"}
    result = agent.process(request)
    print("\nDeploy request analysis:")
    print(f"  Intent: {result['result']['intent']}")
    print(f"  Entities: {result['result']['entities']}")


def main():
    """Run all tests"""
    test_search_agent()
    test_nl_input_agent()
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()
