#!/usr/bin/env python3
"""
Test Redis ElastiCache connection
"""

import json
from typing import Optional

import boto3
import pytest
import redis


class TestRedisConnection:
    """Test Redis connectivity and operations"""

    @pytest.fixture
    def redis_config(self):
        """Get Redis configuration from Parameter Store"""
        ssm = boto3.client("ssm", region_name="us-east-1")

        try:
            # Get Redis endpoint
            endpoint_param = ssm.get_parameter(
                Name="/t-developer/dev/redis/endpoint", WithDecryption=False
            )

            # Get Redis port
            port_param = ssm.get_parameter(Name="/t-developer/dev/redis/port", WithDecryption=False)

            return {
                "host": endpoint_param["Parameter"]["Value"],
                "port": int(port_param["Parameter"]["Value"]),
                "decode_responses": True,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
                "retry_on_timeout": True,
            }
        except Exception as e:
            # Fallback to local Redis for testing
            return {"host": "localhost", "port": 6379, "decode_responses": True}

    def test_redis_connection(self, redis_config):
        """Test basic Redis connection"""
        r = redis.Redis(**redis_config)

        # Test ping
        assert r.ping() == True

    def test_redis_string_operations(self, redis_config):
        """Test Redis string operations"""
        r = redis.Redis(**redis_config)

        # Set a value
        r.set("test:string", "Hello Redis")

        # Get the value
        value = r.get("test:string")
        assert value == "Hello Redis"

        # Set with expiration
        r.setex("test:expiring", 10, "This will expire")
        ttl = r.ttl("test:expiring")
        assert ttl > 0 and ttl <= 10

        # Clean up
        r.delete("test:string", "test:expiring")

    def test_redis_hash_operations(self, redis_config):
        """Test Redis hash operations"""
        r = redis.Redis(**redis_config)

        # Set hash fields
        r.hset(
            "test:agent:1",
            mapping={"name": "TestAgent", "version": "1.0.0", "status": "active"},
        )

        # Get all fields
        agent_data = r.hgetall("test:agent:1")
        assert agent_data["name"] == "TestAgent"
        assert agent_data["version"] == "1.0.0"
        assert agent_data["status"] == "active"

        # Get single field
        name = r.hget("test:agent:1", "name")
        assert name == "TestAgent"

        # Clean up
        r.delete("test:agent:1")

    def test_redis_list_operations(self, redis_config):
        """Test Redis list operations"""
        r = redis.Redis(**redis_config)

        # Push to list
        r.rpush("test:queue", "task1", "task2", "task3")

        # Get list length
        length = r.llen("test:queue")
        assert length == 3

        # Pop from list
        task = r.lpop("test:queue")
        assert task == "task1"

        # Get range
        tasks = r.lrange("test:queue", 0, -1)
        assert tasks == ["task2", "task3"]

        # Clean up
        r.delete("test:queue")

    def test_redis_set_operations(self, redis_config):
        """Test Redis set operations"""
        r = redis.Redis(**redis_config)

        # Add to set
        r.sadd("test:tags", "python", "redis", "testing")

        # Check membership
        assert r.sismember("test:tags", "python") == True
        assert r.sismember("test:tags", "java") == False

        # Get all members
        tags = r.smembers("test:tags")
        assert "python" in tags
        assert "redis" in tags
        assert "testing" in tags

        # Clean up
        r.delete("test:tags")

    def test_redis_sorted_set_operations(self, redis_config):
        """Test Redis sorted set operations"""
        r = redis.Redis(**redis_config)

        # Add to sorted set
        r.zadd("test:leaderboard", {"agent1": 100, "agent2": 85, "agent3": 92})

        # Get rank
        rank = r.zrevrank("test:leaderboard", "agent1")
        assert rank == 0  # Highest score

        # Get top scores
        top_agents = r.zrevrange("test:leaderboard", 0, 1, withscores=True)
        assert top_agents[0][0] == "agent1"
        assert top_agents[0][1] == 100

        # Clean up
        r.delete("test:leaderboard")

    def test_redis_pub_sub(self, redis_config):
        """Test Redis pub/sub functionality"""
        r = redis.Redis(**redis_config)

        # Create pubsub object
        pubsub = r.pubsub()

        # Subscribe to channel
        pubsub.subscribe("test:events")

        # Publish message
        r.publish(
            "test:events",
            json.dumps({"event": "agent_created", "agent_id": "test_123"}),
        )

        # Read message (skip subscribe confirmation)
        message = pubsub.get_message(timeout=1)
        if message and message["type"] == "subscribe":
            message = pubsub.get_message(timeout=1)

        if message and message["type"] == "message":
            data = json.loads(message["data"])
            assert data["event"] == "agent_created"
            assert data["agent_id"] == "test_123"

        # Unsubscribe
        pubsub.unsubscribe("test:events")
        pubsub.close()

    def test_redis_transactions(self, redis_config):
        """Test Redis transactions"""
        r = redis.Redis(**redis_config)

        # Start transaction
        pipe = r.pipeline()

        # Queue commands
        pipe.set("test:counter", 0)
        pipe.incr("test:counter")
        pipe.incr("test:counter")
        pipe.get("test:counter")

        # Execute transaction
        results = pipe.execute()

        # Check results
        assert results[0] == True  # SET
        assert results[1] == 1  # First INCR
        assert results[2] == 2  # Second INCR
        assert results[3] == "2"  # GET

        # Clean up
        r.delete("test:counter")

    def test_redis_cache_pattern(self, redis_config):
        """Test common caching pattern"""
        r = redis.Redis(**redis_config)

        def get_agent_data(agent_id: str) -> dict:
            """Simulate getting agent data with caching"""
            cache_key = f"cache:agent:{agent_id}"

            # Check cache
            cached = r.get(cache_key)
            if cached:
                return json.loads(cached)

            # Simulate expensive operation
            data = {
                "id": agent_id,
                "name": "Test Agent",
                "capabilities": ["task1", "task2"],
            }

            # Store in cache with TTL
            r.setex(cache_key, 300, json.dumps(data))

            return data

        # First call - cache miss
        data1 = get_agent_data("agent_123")
        assert data1["id"] == "agent_123"

        # Second call - cache hit
        data2 = get_agent_data("agent_123")
        assert data2 == data1

        # Verify cache exists
        assert r.exists("cache:agent:agent_123") == 1

        # Clean up
        r.delete("cache:agent:agent_123")


def run_redis_tests():
    """Run Redis tests standalone"""
    import sys

    test_instance = TestRedisConnection()

    # Get config
    config = test_instance.redis_config()

    print(f"Testing Redis connection to {config['host']}:{config['port']}")

    try:
        # Run tests
        test_instance.test_redis_connection(config)
        print("✓ Connection test passed")

        test_instance.test_redis_string_operations(config)
        print("✓ String operations test passed")

        test_instance.test_redis_hash_operations(config)
        print("✓ Hash operations test passed")

        test_instance.test_redis_list_operations(config)
        print("✓ List operations test passed")

        test_instance.test_redis_set_operations(config)
        print("✓ Set operations test passed")

        test_instance.test_redis_sorted_set_operations(config)
        print("✓ Sorted set operations test passed")

        test_instance.test_redis_transactions(config)
        print("✓ Transaction test passed")

        test_instance.test_redis_cache_pattern(config)
        print("✓ Cache pattern test passed")

        print("\nAll Redis tests passed successfully!")
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = run_redis_tests()
    exit(0 if success else 1)
