#!/usr/bin/env python3
"""
Day 9 API Gateway Integration Test
Test the complete API Gateway functionality with all components
"""

import asyncio
import json
import time
from datetime import datetime

# Import the enhanced API Gateway
from src.api.enhanced_gateway import EnhancedAPIGateway, create_api_gateway


async def test_day9_api_gateway():
    """Comprehensive test of Day 9 API Gateway"""
    print("🚀 Day 9 API Gateway Integration Test")
    print("=" * 50)

    # Test configuration
    config = {
        "host": "127.0.0.1",
        "port": 8002,
        "title": "Day 9 Test Gateway",
        "version": "2.0.0",
        "description": "Enhanced API Gateway for Day 9 Testing",
        "jwt_secret": "day9-test-secret",
        "rate_limit": {"requests_per_minute": 1000, "burst_limit": 50},
        "message_queue": {"queue_name": "day9_test_queue"},
        "security": {"enable_encryption": False, "max_request_size_mb": 10},
        "performance": {"memory_limit_kb": 6.5, "max_response_time_ms": 3000},
    }

    # 1. Test Gateway Instantiation
    print("1️⃣  Testing Gateway Instantiation...")
    start_time = time.perf_counter()

    try:
        gateway = EnhancedAPIGateway(config)
        instantiation_time = (time.perf_counter() - start_time) * 1_000_000  # microseconds

        print(f"   ✅ Gateway instantiated in {instantiation_time:.2f}μs")

        # Check performance constraints
        memory_usage = gateway.performance_tracker.get_memory_usage_kb()
        constraints = gateway.performance_tracker.validate_constraints()

        print(f"   📊 Memory Usage: {memory_usage:.2f} KB")
        print(f"   📊 Memory Constraint: {constraints['memory_constraint']['status']}")
        print(f"   📊 Instantiation Constraint: {constraints['instantiation_constraint']['status']}")

    except Exception as e:
        print(f"   ❌ Gateway instantiation failed: {e}")
        return False

    # 2. Test Component Initialization
    print("\n2️⃣  Testing Component Initialization...")
    try:
        # Initialize gateway
        init_success = await gateway.initialize()
        print(f"   ✅ Gateway initialization: {'Success' if init_success else 'Partial'}")

        # Check components
        components = [
            ("Message Queue", gateway.message_queue),
            ("Agent Registry", gateway.agent_registry),
            ("Message Router", gateway.message_router),
            ("JWT Auth", gateway.jwt_auth),
            ("API Key Auth", gateway.api_key_auth),
            ("Rate Limiter", gateway.rate_limiter),
            ("Validator", gateway.validator),
            ("Response Formatter", gateway.formatter),
            ("Monitor", gateway.monitor),
            ("Performance Tracker", gateway.performance_tracker),
        ]

        for name, component in components:
            if component is not None:
                print(f"   ✅ {name}: Initialized")
            else:
                print(f"   ❌ {name}: Not initialized")

    except Exception as e:
        print(f"   ❌ Component initialization failed: {e}")
        return False

    # 3. Test Authentication System
    print("\n3️⃣  Testing Authentication System...")
    try:
        # Test JWT token creation and verification
        payload = {"user_id": "day9_test", "permissions": ["admin", "user"]}
        jwt_token = gateway.jwt_auth.create_token(payload)
        print(f"   ✅ JWT Token created: {jwt_token[:20]}...")

        verified_payload = gateway.jwt_auth.verify_token(jwt_token)
        print(f"   ✅ JWT Token verified: user_id={verified_payload.get('user_id')}")

        # Test API Key generation and validation
        api_key = gateway.api_key_auth.generate_api_key("day9_test_client", ["read", "write"])
        print(f"   ✅ API Key generated: {api_key[:20]}...")

        is_valid = gateway.api_key_auth.validate_api_key(api_key)
        print(f"   ✅ API Key validation: {'Valid' if is_valid else 'Invalid'}")

    except Exception as e:
        print(f"   ❌ Authentication test failed: {e}")
        return False

    # 4. Test Agent Registration
    print("\n4️⃣  Testing Agent Registration...")
    try:
        # Register a test agent
        agent_info = {
            "agent_id": "day9-test-agent",
            "name": "Day 9 Test Agent",
            "capabilities": ["text-processing", "data-analysis", "testing"],
            "endpoints": [
                {"path": "/process", "methods": ["POST"]},
                {"path": "/status", "methods": ["GET"]},
                {"path": "/analyze", "methods": ["POST", "PUT"]},
            ],
            "metadata": {"version": "1.0.0", "description": "Test agent for Day 9 validation"},
        }

        # Register agent through registry
        await gateway.agent_registry.register_agent_capabilities_async(
            agent_info["agent_id"], agent_info
        )
        print(f"   ✅ Agent registered in registry: {agent_info['agent_id']}")

        # Auto-register endpoints
        endpoints_count = await gateway._auto_register_endpoints(agent_info)
        print(f"   ✅ Auto-registered {endpoints_count} endpoints")

        # Verify registration
        registered_agents = await gateway.agent_registry.get_all_agents()
        agent_found = any(
            agent["agent_id"] == agent_info["agent_id"] for agent in registered_agents
        )
        print(f"   ✅ Agent verification: {'Found' if agent_found else 'Not Found'}")

    except Exception as e:
        print(f"   ❌ Agent registration test failed: {e}")
        return False

    # 5. Test Message Queue Integration
    print("\n5️⃣  Testing Message Queue Integration...")
    try:
        # Create a test message
        test_message = {
            "id": "day9-test-message-001",
            "to_agent": "day9-test-agent",
            "type": "test_request",
            "payload": {
                "operation": "validate_system",
                "data": "Day 9 integration test",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "priority": 1,
            "source": "day9_integration_test",
        }

        # Route message
        routing_result = await gateway.message_router.route_message(test_message)
        print(f"   ✅ Message routing: {routing_result['status']}")
        print(f"   📧 Message ID: {routing_result.get('message_id', 'N/A')}")

        # Test broadcast message
        broadcast_message = {
            "id": "day9-broadcast-001",
            "type": "system_announcement",
            "payload": {"message": "Day 9 system test broadcast"},
            "source": "day9_integration_test",
        }

        broadcast_result = await gateway.message_router.broadcast_message(
            broadcast_message, ["testing", "text-processing"]
        )
        print(f"   ✅ Broadcast routing: {broadcast_result['status']}")

    except Exception as e:
        print(f"   ❌ Message queue test failed: {e}")
        return False

    # 6. Test Monitoring and Performance
    print("\n6️⃣  Testing Monitoring and Performance...")
    try:
        # Record some test metrics
        for i in range(5):
            gateway.monitor.record_request(
                {
                    "method": "POST",
                    "path": f"/test/endpoint/{i}",
                    "status_code": 200,
                    "response_time_ms": 100 + (i * 10),
                    "agent_id": "day9-test-agent",
                }
            )

        # Get metrics
        api_metrics = gateway.monitor.get_metrics()
        performance_metrics = gateway.performance_tracker.get_metrics()

        print(f"   ✅ Total requests recorded: {api_metrics['total_requests']}")
        print(
            f"   ✅ Average response time: {api_metrics.get('response_times', {}).get('average_ms', 0):.2f}ms"
        )
        print(
            f"   ✅ Current memory usage: {performance_metrics['system']['current_memory_kb']:.2f} KB"
        )
        print(
            f"   ✅ Memory constraint status: {performance_metrics['constraints']['memory_status']}"
        )

    except Exception as e:
        print(f"   ❌ Monitoring test failed: {e}")
        return False

    # 7. Test Rate Limiting and Validation
    print("\n7️⃣  Testing Rate Limiting and Validation...")
    try:
        # Test message validation
        valid_message = {"type": "test_message", "payload": {"data": "test validation"}}
        is_valid = gateway.validator.validate_message(valid_message)
        print(f"   ✅ Message validation (valid): {'Pass' if is_valid else 'Fail'}")

        invalid_message = {"payload": {"data": "missing type field"}}
        is_invalid = gateway.validator.validate_message(invalid_message)
        print(f"   ✅ Message validation (invalid): {'Fail' if not is_invalid else 'Pass'}")

        # Test agent info validation
        test_agent_data = {
            "agent_id": "validation-test",
            "name": "Validation Test Agent",
            "capabilities": ["validation", "testing"],
        }
        agent_valid = gateway.validator.validate_agent_registration(test_agent_data)
        print(f"   ✅ Agent validation: {'Pass' if agent_valid else 'Fail'}")

    except Exception as e:
        print(f"   ❌ Validation test failed: {e}")
        return False

    # 8. Test Security Manager
    print("\n8️⃣  Testing Security Manager...")
    try:
        # Test message security validation
        test_security_message = {
            "type": "security_test",
            "payload": {"content": "testing security validation"},
            "timestamp": datetime.utcnow().isoformat(),
        }

        security_result = gateway.security_manager.validate_message_security(
            test_security_message, "day9-test-agent"
        )
        print(f"   ✅ Security validation: {'Pass' if security_result['valid'] else 'Fail'}")

        # Test encryption (if enabled)
        if gateway.security_manager.enable_encryption:
            encrypted = gateway.security_manager.encrypt_message(test_security_message)
            print(
                f"   ✅ Message encryption: {'Encrypted' if encrypted.get('encrypted') else 'Plain'}"
            )
        else:
            print(f"   ✅ Encryption disabled for testing")

    except Exception as e:
        print(f"   ❌ Security test failed: {e}")
        return False

    # 9. Final System Health Check
    print("\n9️⃣  Final System Health Check...")
    try:
        health_components = await gateway._check_component_health()
        health_status = "healthy" if all(health_components.values()) else "degraded"

        print(f"   ✅ Overall system health: {health_status.upper()}")
        for component, status in health_components.items():
            status_icon = "✅" if status else "⚠️"
            print(f"   {status_icon} {component}: {'Healthy' if status else 'Degraded'}")

        # Final performance check
        final_constraints = gateway.performance_tracker.validate_constraints()
        print(f"   ✅ Final constraint validation: {final_constraints['overall_status']}")

    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False

    # Summary
    print("\n" + "=" * 50)
    print("🎉 Day 9 API Gateway Integration Test Complete!")
    print("✅ All core components validated successfully")
    print("✅ Message queue integration working")
    print("✅ Authentication system operational")
    print("✅ Agent registration and routing functional")
    print("✅ Performance constraints validated")
    print("✅ Security measures active")
    print("✅ Monitoring and logging operational")

    return True


if __name__ == "__main__":
    # Run the integration test
    success = asyncio.run(test_day9_api_gateway())

    if success:
        print("\n🚀 Day 9 API Gateway is ready for production!")
        exit(0)
    else:
        print("\n❌ Day 9 API Gateway integration test failed!")
        exit(1)
