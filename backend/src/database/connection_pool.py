"""
T-Developer Evolution System - Database Connection Pool
최적화된 데이터베이스 연결 관리
"""

import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import asyncpg
import boto3
import psycopg2
import redis
from botocore.exceptions import ClientError
from psycopg2 import pool
from redis.sentinel import Sentinel

logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """
    데이터베이스 연결 풀 관리자
    PostgreSQL, Redis, DynamoDB 통합 관리
    """

    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.region = os.getenv("AWS_REGION", "us-east-1")

        # Connection pools
        self._pg_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._async_pg_pool: Optional[asyncpg.Pool] = None
        self._redis_pool: Optional[redis.ConnectionPool] = None
        self._redis_client: Optional[redis.Redis] = None

        # DynamoDB client
        self._dynamodb_client = None

        # Secrets Manager client
        self.secrets_client = boto3.client("secretsmanager", region_name=self.region)

        # Connection configs
        self.pg_config: Dict[str, Any] = {}
        self.redis_config: Dict[str, Any] = {}

        # Performance metrics
        self.connection_metrics = {
            "pg_active": 0,
            "pg_idle": 0,
            "redis_active": 0,
            "total_queries": 0,
            "failed_connections": 0,
        }

    async def initialize_async(self):
        """비동기 연결 풀 초기화"""
        try:
            # Load credentials from Secrets Manager
            await self._load_credentials()

            # Initialize PostgreSQL async pool
            await self._init_async_pg_pool()

            # Initialize Redis connection
            self._init_redis_pool()

            # Initialize DynamoDB client
            self._init_dynamodb_client()

            logger.info(f"Database connection pools initialized for {self.environment}")

        except Exception as e:
            logger.error(f"Failed to initialize connection pools: {e}")
            raise

    def initialize_sync(self):
        """동기 연결 풀 초기화"""
        try:
            # Load credentials
            self._load_credentials_sync()

            # Initialize PostgreSQL sync pool
            self._init_pg_pool()

            # Initialize Redis
            self._init_redis_pool()

            # Initialize DynamoDB
            self._init_dynamodb_client()

            logger.info(f"Sync database pools initialized for {self.environment}")

        except Exception as e:
            logger.error(f"Failed to initialize sync pools: {e}")
            raise

    async def _load_credentials(self):
        """Secrets Manager에서 자격 증명 로드"""
        try:
            # PostgreSQL credentials
            pg_secret = await self._get_secret(
                f"t-developer/database/{self.environment}/master-password"
            )
            if pg_secret:
                self.pg_config = json.loads(pg_secret)

            # Redis credentials
            redis_secret = await self._get_secret(
                f"t-developer/cache/{self.environment}/auth-token"
            )
            if redis_secret:
                self.redis_config = json.loads(redis_secret)

        except Exception as e:
            logger.warning(f"Could not load credentials from Secrets Manager: {e}")
            self._use_env_credentials()

    def _load_credentials_sync(self):
        """동기 방식으로 자격 증명 로드"""
        try:
            # PostgreSQL credentials
            pg_secret = self._get_secret_sync(
                f"t-developer/database/{self.environment}/master-password"
            )
            if pg_secret:
                self.pg_config = json.loads(pg_secret)

            # Redis credentials
            redis_secret = self._get_secret_sync(f"t-developer/cache/{self.environment}/auth-token")
            if redis_secret:
                self.redis_config = json.loads(redis_secret)

        except Exception as e:
            logger.warning(f"Could not load credentials: {e}")
            self._use_env_credentials()

    def _use_env_credentials(self):
        """환경 변수에서 자격 증명 로드 (fallback)"""
        self.pg_config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", 5432)),
            "dbname": os.getenv("DB_NAME", "t_developer"),
            "username": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),
        }

        self.redis_config = {
            "endpoint": os.getenv("REDIS_ENDPOINT", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "auth_token": os.getenv("REDIS_AUTH_TOKEN", ""),
            "ssl": os.getenv("REDIS_SSL", "false").lower() == "true",
        }

    async def _init_async_pg_pool(self):
        """비동기 PostgreSQL 연결 풀 초기화"""
        try:
            self._async_pg_pool = await asyncpg.create_pool(
                host=self.pg_config.get("host"),
                port=self.pg_config.get("port"),
                database=self.pg_config.get("dbname"),
                user=self.pg_config.get("username"),
                password=self.pg_config.get("password"),
                min_size=5,
                max_size=20,
                max_queries=50000,
                max_inactive_connection_lifetime=300,
                command_timeout=60,
                server_settings={
                    "application_name": f"t-developer-{self.environment}",
                    "jit": "off",
                },
            )
            logger.info("Async PostgreSQL pool created")

        except Exception as e:
            logger.error(f"Failed to create async PG pool: {e}")
            raise

    def _init_pg_pool(self):
        """동기 PostgreSQL 연결 풀 초기화"""
        try:
            self._pg_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=2,
                maxconn=20,
                host=self.pg_config.get("host"),
                port=self.pg_config.get("port"),
                database=self.pg_config.get("dbname"),
                user=self.pg_config.get("username"),
                password=self.pg_config.get("password"),
                connect_timeout=10,
                options=f"-c application_name=t-developer-{self.environment}",
            )
            logger.info("Sync PostgreSQL pool created")

        except Exception as e:
            logger.error(f"Failed to create sync PG pool: {e}")
            raise

    def _init_redis_pool(self):
        """Redis 연결 풀 초기화"""
        try:
            pool_kwargs = {
                "host": self.redis_config.get("endpoint", "localhost"),
                "port": self.redis_config.get("port", 6379),
                "db": 0,
                "max_connections": 50,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
                "retry_on_timeout": True,
                "health_check_interval": 30,
                "decode_responses": True,
            }

            # Auth token if available
            if self.redis_config.get("auth_token"):
                pool_kwargs["password"] = self.redis_config["auth_token"]

            # SSL if enabled
            if self.redis_config.get("ssl"):
                pool_kwargs["ssl"] = True
                pool_kwargs["ssl_cert_reqs"] = "required"

            self._redis_pool = redis.ConnectionPool(**pool_kwargs)
            self._redis_client = redis.Redis(connection_pool=self._redis_pool)

            # Test connection
            self._redis_client.ping()
            logger.info("Redis connection pool created")

        except Exception as e:
            logger.error(f"Failed to create Redis pool: {e}")
            # Redis is optional, don't raise

    def _init_dynamodb_client(self):
        """DynamoDB 클라이언트 초기화"""
        try:
            self._dynamodb_client = boto3.resource("dynamodb", region_name=self.region)
            logger.info("DynamoDB client initialized")

        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB: {e}")
            # DynamoDB is optional for local development

    @asynccontextmanager
    async def get_pg_connection(self):
        """PostgreSQL 연결 컨텍스트 매니저 (비동기)"""
        if not self._async_pg_pool:
            await self._init_async_pg_pool()

        conn = None
        try:
            conn = await self._async_pg_pool.acquire()
            self.connection_metrics["pg_active"] += 1
            yield conn
        finally:
            if conn:
                await self._async_pg_pool.release(conn)
                self.connection_metrics["pg_active"] -= 1
                self.connection_metrics["total_queries"] += 1

    @contextmanager
    def get_pg_connection_sync(self):
        """PostgreSQL 연결 컨텍스트 매니저 (동기)"""
        if not self._pg_pool:
            self._init_pg_pool()

        conn = None
        try:
            conn = self._pg_pool.getconn()
            self.connection_metrics["pg_active"] += 1
            yield conn
        finally:
            if conn:
                self._pg_pool.putconn(conn)
                self.connection_metrics["pg_active"] -= 1
                self.connection_metrics["total_queries"] += 1

    def get_redis_client(self) -> redis.Redis:
        """Redis 클라이언트 반환"""
        if not self._redis_client:
            self._init_redis_pool()
        return self._redis_client

    def get_dynamodb_table(self, table_name: str):
        """DynamoDB 테이블 객체 반환"""
        if not self._dynamodb_client:
            self._init_dynamodb_client()

        full_table_name = f"t-developer-{table_name}-{self.environment}"
        return self._dynamodb_client.Table(full_table_name)

    async def execute_query(self, query: str, *args, fetch: bool = True):
        """쿼리 실행 헬퍼 (비동기)"""
        async with self.get_pg_connection() as conn:
            if fetch:
                return await conn.fetch(query, *args)
            else:
                return await conn.execute(query, *args)

    def execute_query_sync(self, query: str, params: tuple = None, fetch: bool = True):
        """쿼리 실행 헬퍼 (동기)"""
        with self.get_pg_connection_sync() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount

    async def health_check(self) -> Dict[str, bool]:
        """연결 상태 확인"""
        health = {"postgresql": False, "redis": False, "dynamodb": False}

        # Check PostgreSQL
        try:
            async with self.get_pg_connection() as conn:
                await conn.fetchval("SELECT 1")
                health["postgresql"] = True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")

        # Check Redis
        try:
            if self._redis_client:
                self._redis_client.ping()
                health["redis"] = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")

        # Check DynamoDB
        try:
            if self._dynamodb_client:
                self._dynamodb_client.meta.client.describe_limits()
                health["dynamodb"] = True
        except Exception as e:
            logger.error(f"DynamoDB health check failed: {e}")

        return health

    def get_metrics(self) -> Dict[str, Any]:
        """연결 풀 메트릭 반환"""
        metrics = self.connection_metrics.copy()

        # Add pool-specific metrics
        if self._async_pg_pool:
            metrics["pg_pool_size"] = self._async_pg_pool.get_size()
            metrics["pg_pool_free"] = self._async_pg_pool.get_idle_size()

        if self._redis_pool:
            stats = self._redis_pool.connection_kwargs
            metrics["redis_max_connections"] = stats.get("max_connections", 0)

        return metrics

    async def close(self):
        """모든 연결 종료"""
        try:
            if self._async_pg_pool:
                await self._async_pg_pool.close()
                logger.info("Async PostgreSQL pool closed")

            if self._pg_pool:
                self._pg_pool.closeall()
                logger.info("Sync PostgreSQL pool closed")

            if self._redis_client:
                self._redis_client.close()
                logger.info("Redis connection closed")

        except Exception as e:
            logger.error(f"Error closing connections: {e}")

    async def _get_secret(self, secret_name: str) -> Optional[str]:
        """Secrets Manager에서 비밀 가져오기 (비동기)"""
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            return response.get("SecretString")
        except ClientError:
            return None

    def _get_secret_sync(self, secret_name: str) -> Optional[str]:
        """Secrets Manager에서 비밀 가져오기 (동기)"""
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            return response.get("SecretString")
        except ClientError:
            return None


# Singleton instance
_connection_pool: Optional[DatabaseConnectionPool] = None


def get_connection_pool(environment: str = None) -> DatabaseConnectionPool:
    """연결 풀 싱글톤 인스턴스 반환"""
    global _connection_pool

    if _connection_pool is None:
        env = environment or os.getenv("ENVIRONMENT", "development")
        _connection_pool = DatabaseConnectionPool(env)
        _connection_pool.initialize_sync()

    return _connection_pool


async def get_async_connection_pool(environment: str = None) -> DatabaseConnectionPool:
    """비동기 연결 풀 싱글톤 인스턴스 반환"""
    global _connection_pool

    if _connection_pool is None:
        env = environment or os.getenv("ENVIRONMENT", "development")
        _connection_pool = DatabaseConnectionPool(env)
        await _connection_pool.initialize_async()

    return _connection_pool
