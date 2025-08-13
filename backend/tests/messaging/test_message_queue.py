"""
Test suite for Message Queue System
Day 8: Message Queue System - TDD Implementation
Generated: 2024-11-18

Testing requirements:
1. Redis-based message queuing with priority support
2. Agent-to-agent communication protocols
3. Event-driven architecture with pub/sub patterns
4. Dead letter queue handling and retry mechanisms
5. Message persistence and delivery guarantees
"""

import json
import time
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest


class TestMessageQueue:
    """Test core message queue functionality"""

    def test_message_queue_creation(self):
        """Test creating a message queue with configuration"""
        from src.messaging.message_queue import MessageQueue

        config = {
            "redis_url": "redis://localhost:6379",
            "max_retries": 3,
            "retry_delay": 1.0,
            "enable_persistence": True,
        }

        queue = MessageQueue("test_queue", config)

        assert queue.queue_name == "test_queue"
        assert queue.config["max_retries"] == 3
        assert queue.config["enable_persistence"] is True

    @pytest.mark.asyncio
    async def test_message_enqueue_dequeue(self):
        """Test basic message enqueue and dequeue operations"""
        from src.messaging.message_queue import MessageQueue

        queue = MessageQueue("test_queue")

        # Mock Redis operations
        with patch.object(queue, "_redis_client") as mock_redis:
            mock_redis.lpush = AsyncMock(return_value=1)
            mock_redis.brpop = AsyncMock(
                return_value=(
                    "test_queue",
                    json.dumps(
                        {
                            "id": "msg_001",
                            "type": "agent_request",
                            "payload": {"action": "analyze", "agent_id": "test_agent"},
                            "timestamp": datetime.utcnow().isoformat(),
                            "priority": 1,
                        }
                    ),
                )
            )

            # Enqueue message
            message = {
                "type": "agent_request",
                "payload": {"action": "analyze", "agent_id": "test_agent"},
                "priority": 1,
            }

            message_id = await queue.enqueue(message)
            assert message_id is not None

            # Dequeue message
            received_message = await queue.dequeue()
            assert received_message["type"] == "agent_request"
            assert received_message["payload"]["action"] == "analyze"

    def test_message_priority_ordering(self):
        """Test that messages are processed in priority order"""
        from src.messaging.priority_queue import PriorityMessageQueue

        queue = PriorityMessageQueue("priority_test")

        # Add messages with different priorities
        messages = [
            {"content": "low priority", "priority": 3},
            {"content": "high priority", "priority": 1},
            {"content": "medium priority", "priority": 2},
        ]

        for msg in messages:
            queue.add_message(msg)

        # Should get high priority first
        next_msg = queue.get_next_message()
        assert next_msg["priority"] == 1
        assert next_msg["content"] == "high priority"

        # Then medium priority
        next_msg = queue.get_next_message()
        assert next_msg["priority"] == 2

    @pytest.mark.asyncio
    async def test_message_retry_mechanism(self):
        """Test message retry on processing failure"""
        from src.messaging.message_queue import MessageQueue

        queue = MessageQueue("retry_test", {"max_retries": 3})

        message = {
            "id": "retry_msg_001",
            "type": "agent_task",
            "payload": {"action": "process"},
            "retry_count": 0,
        }

        # Simulate processing failure
        with patch.object(queue, "_process_message") as mock_process:
            mock_process.side_effect = Exception("Processing failed")

            # Should retry up to max_retries times
            result = await queue.handle_message_with_retry(message)

            assert result["status"] == "failed"
            assert result["retry_count"] == 3
            assert mock_process.call_count == 3

    def test_dead_letter_queue_handling(self):
        """Test moving failed messages to dead letter queue"""
        from src.messaging.dead_letter_queue import DeadLetterQueue

        dlq = DeadLetterQueue("test_dlq")

        failed_message = {
            "id": "failed_msg_001",
            "type": "agent_task",
            "payload": {"action": "invalid_action"},
            "failure_reason": "Unknown action type",
            "failed_at": datetime.utcnow().isoformat(),
            "retry_count": 3,
        }

        dlq.add_failed_message(failed_message)

        # Should be able to retrieve failed messages
        failed_messages = dlq.get_failed_messages()
        assert len(failed_messages) == 1
        assert failed_messages[0]["id"] == "failed_msg_001"

        # Should be able to requeue for retry
        requeued = dlq.requeue_message("failed_msg_001")
        assert requeued["retry_count"] == 0  # Reset retry count


class TestAgentCommunication:
    """Test agent-to-agent communication patterns"""

    @pytest.mark.asyncio
    async def test_agent_message_routing(self):
        """Test routing messages between agents"""
        from src.messaging.agent_router import AgentMessageRouter

        router = AgentMessageRouter()

        # Register agents
        await router.register_agent("agent_001", "nl_input")
        await router.register_agent("agent_002", "parser")

        # Send message from one agent to another
        message = {
            "from_agent": "agent_001",
            "to_agent": "agent_002",
            "type": "task_request",
            "payload": {"text": "Parse this input", "format": "json"},
        }

        with patch.object(router, "_deliver_message") as mock_deliver:
            mock_deliver.return_value = {"status": "delivered", "message_id": "msg_123"}

            result = await router.route_message(message)

            assert result["status"] == "delivered"
            assert mock_deliver.called

    def test_agent_capability_discovery(self):
        """Test discovering agent capabilities for routing"""
        from src.messaging.agent_registry import AgentCapabilityRegistry

        registry = AgentCapabilityRegistry()

        # Register agent capabilities
        registry.register_agent_capabilities(
            "agent_001",
            {
                "type": "nl_input",
                "capabilities": ["text_processing", "intent_extraction"],
                "input_types": ["text", "voice"],
                "output_types": ["structured_data"],
            },
        )

        # Find agents by capability
        agents = registry.find_agents_by_capability("text_processing")
        assert "agent_001" in agents

        # Find agents by input type
        agents = registry.find_agents_by_input_type("text")
        assert "agent_001" in agents

    @pytest.mark.asyncio
    async def test_broadcast_messaging(self):
        """Test broadcasting messages to multiple agents"""
        from src.messaging.broadcast_manager import BroadcastManager

        manager = BroadcastManager()

        # Setup agent group
        agents = ["agent_001", "agent_002", "agent_003"]
        await manager.create_agent_group("processing_group", agents)

        # Broadcast message to group
        broadcast_message = {
            "type": "system_update",
            "payload": {"version": "1.2.0", "restart_required": False},
            "group": "processing_group",
        }

        with patch.object(manager, "_send_to_agent") as mock_send:
            mock_send.return_value = {"status": "sent"}

            results = await manager.broadcast_to_group("processing_group", broadcast_message)

            assert len(results) == 3
            assert all(r["status"] == "sent" for r in results)
            assert mock_send.call_count == 3


class TestEventDrivenArchitecture:
    """Test event-driven messaging patterns"""

    def test_event_publisher_subscriber(self):
        """Test pub/sub event system"""
        from src.messaging.event_bus import EventBus

        event_bus = EventBus()

        # Track received events
        received_events = []

        def event_handler(event):
            received_events.append(event)

        # Subscribe to events
        event_bus.subscribe("agent.evolution.started", event_handler)
        event_bus.subscribe("agent.evolution.*", event_handler)  # Wildcard

        # Publish event
        event = {
            "type": "agent.evolution.started",
            "agent_id": "agent_001",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"generation": 1, "fitness_score": 0.85},
        }

        event_bus.publish("agent.evolution.started", event)

        # Should have received event twice (specific + wildcard)
        assert len(received_events) == 2
        assert all(e["agent_id"] == "agent_001" for e in received_events)

    @pytest.mark.asyncio
    async def test_event_streaming(self):
        """Test real-time event streaming"""
        from src.messaging.event_stream import EventStream

        stream = EventStream("evolution_events")

        # Mock Redis stream operations
        with patch.object(stream, "_redis_client") as mock_redis:
            mock_redis.xadd = AsyncMock(return_value="1234567890-0")
            mock_redis.xread = AsyncMock(
                return_value={
                    "evolution_events": [
                        (
                            "1234567890-0",
                            {
                                "event_type": "agent_fitness_update",
                                "agent_id": "agent_001",
                                "fitness_score": "0.92",
                            },
                        )
                    ]
                }
            )

            # Add event to stream
            event_id = await stream.add_event(
                {
                    "event_type": "agent_fitness_update",
                    "agent_id": "agent_001",
                    "fitness_score": 0.92,
                }
            )

            assert event_id == "1234567890-0"

            # Read events from stream
            events = await stream.read_events(count=1)
            assert len(events) == 1
            assert events[0]["data"]["agent_id"] == "agent_001"

    def test_event_filtering_and_routing(self):
        """Test filtering events based on criteria"""
        from src.messaging.event_filter import EventFilter

        event_filter = EventFilter()

        # Setup filtering rules
        rules = [
            {
                "name": "high_priority_only",
                "condition": lambda event: event.get("priority", 0) >= 3,
                "action": "route_to_priority_queue",
            },
            {
                "name": "agent_evolution_events",
                "condition": lambda event: event.get("type", "").startswith("agent.evolution"),
                "action": "route_to_evolution_handler",
            },
        ]

        for rule in rules:
            event_filter.add_rule(rule)

        # Test high priority event
        high_priority_event = {"type": "system.alert", "priority": 4, "message": "Critical error"}
        matches = event_filter.apply_filters(high_priority_event)
        assert "high_priority_only" in [m["rule"] for m in matches]

        # Test evolution event
        evolution_event = {"type": "agent.evolution.completed", "agent_id": "agent_001"}
        matches = event_filter.apply_filters(evolution_event)
        assert "agent_evolution_events" in [m["rule"] for m in matches]


class TestMessagePersistence:
    """Test message persistence and recovery"""

    @pytest.mark.asyncio
    async def test_message_persistence_to_database(self):
        """Test persisting messages to database"""
        from src.messaging.message_persistence import MessagePersister

        persister = MessagePersister("postgresql://localhost/test_db")

        message = {
            "id": "persist_msg_001",
            "type": "agent_task",
            "payload": {"action": "analyze", "data": "test data"},
            "timestamp": datetime.utcnow(),
            "status": "pending",
        }

        with patch.object(persister, "_db_connection") as mock_db:
            mock_db.execute = AsyncMock(return_value=True)

            # Persist message
            result = await persister.persist_message(message)
            assert result is True

            # Should be able to retrieve persisted message
            mock_db.fetch_one = AsyncMock(
                return_value={"id": "persist_msg_001", "type": "agent_task", "status": "pending"}
            )

            retrieved = await persister.get_message("persist_msg_001")
            assert retrieved["id"] == "persist_msg_001"

    def test_message_backup_and_recovery(self):
        """Test backup and recovery of message queues"""
        from src.messaging.backup_manager import MessageBackupManager

        backup_manager = MessageBackupManager("./backups")

        # Mock queue state
        queue_state = {
            "queue_name": "test_queue",
            "messages": [
                {"id": "msg_001", "type": "task", "payload": "data1"},
                {"id": "msg_002", "type": "task", "payload": "data2"},
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Create backup
        backup_file = backup_manager.create_backup(queue_state)
        assert backup_file.endswith(".json")

        # Restore from backup
        with patch.object(backup_manager, "_load_backup_file") as mock_load:
            mock_load.return_value = queue_state

            restored_state = backup_manager.restore_from_backup(backup_file)
            assert restored_state["queue_name"] == "test_queue"
            assert len(restored_state["messages"]) == 2

    @pytest.mark.asyncio
    async def test_transaction_message_handling(self):
        """Test transactional message processing"""
        from src.messaging.transaction_manager import TransactionMessageManager

        tx_manager = TransactionMessageManager()

        # Start transaction
        tx_id = await tx_manager.begin_transaction()
        assert tx_id is not None

        messages = [
            {"id": "tx_msg_001", "type": "task", "payload": "step1"},
            {"id": "tx_msg_002", "type": "task", "payload": "step2"},
            {"id": "tx_msg_003", "type": "task", "payload": "step3"},
        ]

        with patch.object(tx_manager, "_process_message") as mock_process:
            # All messages succeed
            mock_process.return_value = {"status": "success"}

            # Process messages in transaction
            for msg in messages:
                await tx_manager.add_message_to_transaction(tx_id, msg)

            # Commit transaction
            result = await tx_manager.commit_transaction(tx_id)
            assert result["status"] == "committed"
            assert result["processed_count"] == 3


class TestMessageSecurity:
    """Test message security and authentication"""

    def test_message_encryption_decryption(self):
        """Test encrypting and decrypting sensitive messages"""
        from src.messaging.security import MessageEncryption

        encryption = MessageEncryption("test_secret_key_32_bytes_long!!")

        sensitive_message = {
            "type": "agent_credentials",
            "payload": {
                "api_key": "secret_api_key_12345",
                "database_password": "super_secret_password",
            },
        }

        # Encrypt message
        encrypted_data = encryption.encrypt_message(sensitive_message)
        assert encrypted_data != sensitive_message
        assert "encrypted_payload" in encrypted_data

        # Decrypt message
        decrypted_message = encryption.decrypt_message(encrypted_data)
        assert decrypted_message["payload"]["api_key"] == "secret_api_key_12345"

    def test_message_authentication(self):
        """Test message authentication and validation"""
        from src.messaging.security import MessageAuthenticator

        authenticator = MessageAuthenticator("hmac_secret_key")

        message = {
            "from_agent": "agent_001",
            "to_agent": "agent_002",
            "type": "task_request",
            "payload": {"action": "process_data"},
        }

        # Sign message
        signed_message = authenticator.sign_message(message)
        assert "signature" in signed_message
        assert "timestamp" in signed_message

        # Verify message
        is_valid = authenticator.verify_message(signed_message)
        assert is_valid is True

        # Tampered message should fail verification
        signed_message["payload"]["action"] = "malicious_action"
        is_valid = authenticator.verify_message(signed_message)
        assert is_valid is False

    def test_rate_limiting_and_throttling(self):
        """Test rate limiting for message sending"""
        from src.messaging.security import MessageRateLimiter

        rate_limiter = MessageRateLimiter(max_messages=5, time_window=60)  # 5 messages per minute

        agent_id = "agent_001"

        # Send messages up to limit
        for i in range(5):
            allowed = rate_limiter.check_rate_limit(agent_id)
            assert allowed is True

        # Next message should be rate limited
        allowed = rate_limiter.check_rate_limit(agent_id)
        assert allowed is False

        # After time window, should be allowed again
        with patch("time.time", return_value=time.time() + 61):  # Advance time
            allowed = rate_limiter.check_rate_limit(agent_id)
            assert allowed is True


@pytest.mark.integration
class TestMessageQueueIntegration:
    """Integration tests for complete message queue system"""

    @pytest.mark.asyncio
    async def test_end_to_end_agent_communication(self):
        """Test complete agent communication workflow"""
        from src.messaging.agent_router import AgentMessageRouter
        from src.messaging.message_queue import MessageQueue
        from src.models.agent import Agent

        # Setup agents
        nl_agent = Agent(name="nl_input_agent", size_kb=5.2, instantiation_us=2.1)
        parser_agent = Agent(name="parser_agent", size_kb=6.0, instantiation_us=2.8)

        # Setup message queue and router
        queue = MessageQueue("agent_communication")
        router = AgentMessageRouter()

        await router.register_agent(nl_agent.id, "nl_input")
        await router.register_agent(parser_agent.id, "parser")

        # Simulate agent communication
        with patch.object(queue, "_redis_client") as mock_redis, patch.object(
            router, "_deliver_message"
        ) as mock_deliver:
            mock_redis.lpush = AsyncMock(return_value=1)
            mock_deliver.return_value = {"status": "delivered"}

            # NL agent sends task to parser agent
            message = {
                "from_agent": nl_agent.id,
                "to_agent": parser_agent.id,
                "type": "parse_request",
                "payload": {
                    "text": "Create a simple web app with user authentication",
                    "expected_format": "structured_requirements",
                },
            }

            # Enqueue and route message
            message_id = await queue.enqueue(message)
            result = await router.route_message(message)

            assert message_id is not None
            assert result["status"] == "delivered"

    def test_message_queue_performance_under_load(self):
        """Test message queue performance with high message volume"""
        from src.messaging.performance_tester import MessageQueuePerformanceTester

        tester = MessageQueuePerformanceTester()

        # Test configuration
        test_config = {
            "message_count": 1000,
            "concurrent_producers": 5,
            "concurrent_consumers": 3,
            "message_size_kb": 1.0,
            "test_duration_seconds": 30,
        }

        # Run performance test
        with patch.object(tester, "_simulate_message_processing") as mock_process:
            mock_process.return_value = {"status": "processed", "duration_ms": 10}

            results = tester.run_performance_test(test_config)

            assert results["messages_processed"] > 0
            assert results["average_latency_ms"] < 100  # Should be fast
            assert results["throughput_msg_per_sec"] > 10
            assert results["error_rate"] < 0.01  # Less than 1% errors

    @pytest.mark.asyncio
    async def test_message_queue_resilience(self):
        """Test message queue resilience and failure recovery"""
        from src.messaging.resilience_tester import MessageQueueResilienceTester

        tester = MessageQueueResilienceTester()

        # Test scenarios
        scenarios = [
            "redis_connection_loss",
            "high_memory_usage",
            "network_partition",
            "message_corruption",
        ]

        for scenario in scenarios:
            with patch.object(tester, f"_simulate_{scenario}") as mock_scenario:
                mock_scenario.return_value = {"recovered": True, "recovery_time_ms": 500}

                result = await tester.test_scenario(scenario)

                assert result["recovered"] is True
                assert result["recovery_time_ms"] < 5000  # Should recover within 5 seconds
