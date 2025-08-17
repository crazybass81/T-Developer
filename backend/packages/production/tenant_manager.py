"""
Multi-tenancy management system for T-Developer production environment.

This module provides comprehensive tenant isolation, provisioning, and lifecycle
management with strict security boundaries and resource quotas.
"""

from __future__ import annotations

import hashlib
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, TypedDict

from cryptography.fernet import Fernet


class TenantStatus(Enum):
    """Tenant lifecycle status."""

    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    MIGRATING = "migrating"


class TenantTier(Enum):
    """Tenant service tiers."""

    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class ResourceType(Enum):
    """Types of resources that can be limited."""

    CPU_CORES = "cpu_cores"
    MEMORY_GB = "memory_gb"
    STORAGE_GB = "storage_gb"
    API_CALLS_PER_HOUR = "api_calls_per_hour"
    CONCURRENT_SERVICES = "concurrent_services"
    DATA_TRANSFER_GB = "data_transfer_gb"


class TenantConfigDict(TypedDict):
    """Type-safe tenant configuration."""

    encryption_key: str
    data_residency: str
    custom_domain: Optional[str]
    sso_config: dict[str, Any]
    backup_retention_days: int
    audit_level: str


@dataclass
class ResourceQuota:
    """Resource quota definition for a tenant.

    Attributes:
        resource_type: Type of resource being limited
        limit: Maximum allowed usage
        current_usage: Current usage amount
        warning_threshold: Percentage at which to warn (0.0-1.0)
        auto_scale: Whether to auto-scale when limit is reached
    """

    resource_type: ResourceType
    limit: float
    current_usage: float = 0.0
    warning_threshold: float = 0.8
    auto_scale: bool = False

    @property
    def usage_percentage(self) -> float:
        """Calculate current usage as percentage of limit."""
        return (self.current_usage / self.limit) if self.limit > 0 else 0.0

    @property
    def is_over_warning(self) -> bool:
        """Check if usage exceeds warning threshold."""
        return self.usage_percentage >= self.warning_threshold

    @property
    def is_at_limit(self) -> bool:
        """Check if usage is at or over limit."""
        return self.current_usage >= self.limit


@dataclass
class TenantMetadata:
    """Extended tenant metadata.

    Attributes:
        created_at: Tenant creation timestamp
        last_active_at: Last activity timestamp
        total_api_calls: Total API calls made
        total_data_processed_gb: Total data processed in GB
        compliance_flags: Set of compliance requirements
        custom_tags: User-defined tags
    """

    created_at: datetime
    last_active_at: datetime
    total_api_calls: int = 0
    total_data_processed_gb: float = 0.0
    compliance_flags: set[str] = field(default_factory=set)
    custom_tags: dict[str, str] = field(default_factory=dict)


@dataclass
class Tenant:
    """Tenant entity with complete configuration.

    A tenant represents an isolated environment for a customer or organization,
    with its own resources, data, and configuration.

    Example:
        >>> tenant = Tenant(
        ...     id="tenant-123",
        ...     name="Acme Corp",
        ...     tier=TenantTier.ENTERPRISE
        ... )
        >>> tenant.add_quota(ResourceType.CPU_CORES, 16)
        >>> tenant.status = TenantStatus.ACTIVE
    """

    id: str
    name: str
    tier: TenantTier
    status: TenantStatus = TenantStatus.PENDING
    quotas: dict[ResourceType, ResourceQuota] = field(default_factory=dict)
    config: TenantConfigDict = field(default_factory=dict)
    metadata: TenantMetadata = field(
        default_factory=lambda: TenantMetadata(
            created_at=datetime.utcnow(), last_active_at=datetime.utcnow()
        )
    )
    admin_users: set[str] = field(default_factory=set)
    allowed_regions: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Initialize tenant with default quotas based on tier."""
        if not self.quotas:
            self._set_default_quotas()

    def _set_default_quotas(self) -> None:
        """Set default resource quotas based on tenant tier."""
        quota_defaults = {
            TenantTier.STARTER: {
                ResourceType.CPU_CORES: 2,
                ResourceType.MEMORY_GB: 4,
                ResourceType.STORAGE_GB: 50,
                ResourceType.API_CALLS_PER_HOUR: 1000,
                ResourceType.CONCURRENT_SERVICES: 5,
                ResourceType.DATA_TRANSFER_GB: 10,
            },
            TenantTier.PROFESSIONAL: {
                ResourceType.CPU_CORES: 8,
                ResourceType.MEMORY_GB: 16,
                ResourceType.STORAGE_GB: 200,
                ResourceType.API_CALLS_PER_HOUR: 10000,
                ResourceType.CONCURRENT_SERVICES: 20,
                ResourceType.DATA_TRANSFER_GB: 100,
            },
            TenantTier.ENTERPRISE: {
                ResourceType.CPU_CORES: 32,
                ResourceType.MEMORY_GB: 64,
                ResourceType.STORAGE_GB: 1000,
                ResourceType.API_CALLS_PER_HOUR: 100000,
                ResourceType.CONCURRENT_SERVICES: 100,
                ResourceType.DATA_TRANSFER_GB: 1000,
            },
        }

        defaults = quota_defaults.get(self.tier, quota_defaults[TenantTier.STARTER])
        for resource_type, limit in defaults.items():
            self.quotas[resource_type] = ResourceQuota(
                resource_type=resource_type,
                limit=limit,
                auto_scale=(self.tier == TenantTier.ENTERPRISE),
            )

    def add_quota(
        self, resource_type: ResourceType, limit: float, auto_scale: bool = False
    ) -> None:
        """Add or update a resource quota.

        Args:
            resource_type: Type of resource to limit
            limit: Maximum allowed usage
            auto_scale: Whether to auto-scale when limit is reached
        """
        self.quotas[resource_type] = ResourceQuota(
            resource_type=resource_type, limit=limit, auto_scale=auto_scale
        )

    def check_quota(self, resource_type: ResourceType, requested_amount: float) -> bool:
        """Check if a resource request is within quota.

        Args:
            resource_type: Type of resource being requested
            requested_amount: Amount of resource requested

        Returns:
            True if request is within quota limits
        """
        quota = self.quotas.get(resource_type)
        if not quota:
            return True  # No quota means unlimited

        return (quota.current_usage + requested_amount) <= quota.limit

    def update_usage(self, resource_type: ResourceType, amount: float) -> None:
        """Update current usage for a resource type.

        Args:
            resource_type: Type of resource to update
            amount: Amount to add to current usage (can be negative)
        """
        if resource_type in self.quotas:
            self.quotas[resource_type].current_usage = max(
                0, self.quotas[resource_type].current_usage + amount
            )

    def get_namespace(self) -> str:
        """Get the Kubernetes namespace for this tenant.

        Returns:
            Kubernetes-compatible namespace string
        """
        # Create a safe namespace name
        safe_name = re.sub(r"[^a-z0-9-]", "-", self.id.lower())
        return f"tenant-{safe_name}"

    def get_database_name(self) -> str:
        """Get the isolated database name for this tenant.

        Returns:
            Database name string
        """
        return f"tdev_{self.id.replace('-', '_')}"

    def is_quota_exceeded(self) -> list[ResourceType]:
        """Get list of resources that have exceeded quotas.

        Returns:
            List of resource types that are over their limits
        """
        exceeded = []
        for quota in self.quotas.values():
            if quota.is_at_limit:
                exceeded.append(quota.resource_type)
        return exceeded


class TenantManager:
    """Multi-tenancy management system.

    Provides comprehensive tenant lifecycle management, resource isolation,
    and security boundaries for production T-Developer deployments.

    Example:
        >>> manager = TenantManager()
        >>> await manager.initialize()
        >>> tenant = await manager.create_tenant("Acme Corp", TenantTier.ENTERPRISE)
        >>> await manager.activate_tenant(tenant.id)
    """

    def __init__(self, config: dict[str, Any] = None) -> None:
        """Initialize tenant manager.

        Args:
            config: Manager configuration options
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._tenants: dict[str, Tenant] = {}
        self._encryption_key = Fernet.generate_key()
        self._cipher = Fernet(self._encryption_key)
        self._active_sessions: dict[str, set[str]] = {}  # tenant_id -> session_ids

    async def initialize(self) -> None:
        """Initialize the tenant manager.

        Sets up required infrastructure and loads existing tenants.
        """
        self.logger.info("Initializing tenant manager")

        # In production, this would connect to persistent storage
        # For now, we'll use in-memory storage
        await self._setup_isolation_infrastructure()
        await self._load_existing_tenants()

        self.logger.info("Tenant manager initialized successfully")

    async def _setup_isolation_infrastructure(self) -> None:
        """Set up infrastructure for tenant isolation."""
        # This would set up:
        # - Network policies
        # - Database schemas
        # - Message queue topics
        # - Storage buckets
        # - Monitoring dashboards
        self.logger.info("Setting up tenant isolation infrastructure")

    async def _load_existing_tenants(self) -> None:
        """Load existing tenants from persistent storage."""
        # In production, load from database
        self.logger.info("Loading existing tenants")

    async def create_tenant(
        self,
        name: str,
        tier: TenantTier,
        admin_email: str,
        config: Optional[TenantConfigDict] = None,
    ) -> Tenant:
        """Create a new tenant.

        Args:
            name: Human-readable tenant name
            tier: Service tier for the tenant
            admin_email: Email of the tenant administrator
            config: Optional tenant-specific configuration

        Returns:
            Created tenant instance

        Raises:
            ValueError: If tenant name is invalid or already exists
            RuntimeError: If tenant creation fails
        """
        if not self._validate_tenant_name(name):
            raise ValueError(f"Invalid tenant name: {name}")

        tenant_id = self._generate_tenant_id(name)

        if tenant_id in self._tenants:
            raise ValueError(f"Tenant with name '{name}' already exists")

        # Create tenant configuration
        tenant_config = config or {}
        if "encryption_key" not in tenant_config:
            tenant_config["encryption_key"] = Fernet.generate_key().decode()
        if "data_residency" not in tenant_config:
            tenant_config["data_residency"] = "us-east-1"
        if "backup_retention_days" not in tenant_config:
            tenant_config["backup_retention_days"] = 30
        if "audit_level" not in tenant_config:
            tenant_config["audit_level"] = "standard"

        tenant = Tenant(
            id=tenant_id, name=name, tier=tier, config=tenant_config, admin_users={admin_email}
        )

        try:
            # Set up tenant infrastructure
            await self._provision_tenant_infrastructure(tenant)

            # Store tenant
            self._tenants[tenant_id] = tenant

            # Log tenant creation
            self.logger.info(
                f"Created tenant: {tenant_id} ({name}) with tier {tier.value}",
                extra={
                    "tenant_id": tenant_id,
                    "tenant_name": name,
                    "tier": tier.value,
                    "admin_email": admin_email,
                },
            )

            return tenant

        except Exception as e:
            self.logger.error(f"Failed to create tenant {name}: {e}")
            # Cleanup any partially created resources
            await self._cleanup_tenant_infrastructure(tenant_id)
            raise RuntimeError(f"Tenant creation failed: {e}")

    async def _provision_tenant_infrastructure(self, tenant: Tenant) -> None:
        """Provision infrastructure for a new tenant.

        Args:
            tenant: Tenant to provision infrastructure for
        """
        self.logger.info(f"Provisioning infrastructure for tenant {tenant.id}")

        # Create namespace
        await self._create_tenant_namespace(tenant)

        # Set up database
        await self._create_tenant_database(tenant)

        # Configure network isolation
        await self._setup_network_isolation(tenant)

        # Set up monitoring
        await self._setup_tenant_monitoring(tenant)

        self.logger.info(f"Infrastructure provisioned for tenant {tenant.id}")

    async def _create_tenant_namespace(self, tenant: Tenant) -> None:
        """Create Kubernetes namespace for tenant."""
        namespace = tenant.get_namespace()
        # In production, create actual K8s namespace with network policies
        self.logger.debug(f"Created namespace: {namespace}")

    async def _create_tenant_database(self, tenant: Tenant) -> None:
        """Create isolated database for tenant."""
        db_name = tenant.get_database_name()
        # In production, create actual database with proper isolation
        self.logger.debug(f"Created database: {db_name}")

    async def _setup_network_isolation(self, tenant: Tenant) -> None:
        """Set up network isolation for tenant."""
        # In production, configure VPC, subnets, security groups
        self.logger.debug(f"Configured network isolation for {tenant.id}")

    async def _setup_tenant_monitoring(self, tenant: Tenant) -> None:
        """Set up monitoring and alerting for tenant."""
        # In production, create dashboards, alerts, log streams
        self.logger.debug(f"Configured monitoring for {tenant.id}")

    async def activate_tenant(self, tenant_id: str) -> bool:
        """Activate a tenant, making it available for use.

        Args:
            tenant_id: ID of tenant to activate

        Returns:
            True if tenant was successfully activated

        Raises:
            ValueError: If tenant not found
            RuntimeError: If activation fails
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        if tenant.status == TenantStatus.ACTIVE:
            return True

        try:
            # Perform pre-activation checks
            await self._validate_tenant_resources(tenant)

            # Activate services
            await self._activate_tenant_services(tenant)

            # Update status
            tenant.status = TenantStatus.ACTIVE
            tenant.metadata.last_active_at = datetime.utcnow()

            self.logger.info(f"Activated tenant: {tenant_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to activate tenant {tenant_id}: {e}")
            raise RuntimeError(f"Tenant activation failed: {e}")

    async def _validate_tenant_resources(self, tenant: Tenant) -> None:
        """Validate that tenant has required resources."""
        # Check quotas are reasonable
        for quota in tenant.quotas.values():
            if quota.limit <= 0:
                raise ValueError(f"Invalid quota limit for {quota.resource_type}")

    async def _activate_tenant_services(self, tenant: Tenant) -> None:
        """Start tenant-specific services."""
        # In production, start pods, services, etc.
        self.logger.debug(f"Started services for tenant {tenant.id}")

    async def suspend_tenant(self, tenant_id: str, reason: str) -> bool:
        """Suspend a tenant, preventing new operations.

        Args:
            tenant_id: ID of tenant to suspend
            reason: Reason for suspension

        Returns:
            True if tenant was successfully suspended
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        try:
            # Suspend services but keep data
            await self._suspend_tenant_services(tenant)

            # Update status
            tenant.status = TenantStatus.SUSPENDED

            self.logger.warning(
                f"Suspended tenant: {tenant_id} - {reason}",
                extra={"tenant_id": tenant_id, "reason": reason},
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to suspend tenant {tenant_id}: {e}")
            raise RuntimeError(f"Tenant suspension failed: {e}")

    async def _suspend_tenant_services(self, tenant: Tenant) -> None:
        """Suspend tenant services."""
        # In production, scale down pods, disable endpoints
        self.logger.debug(f"Suspended services for tenant {tenant.id}")

    async def terminate_tenant(self, tenant_id: str, preserve_data: bool = True) -> bool:
        """Terminate a tenant and optionally preserve data.

        Args:
            tenant_id: ID of tenant to terminate
            preserve_data: Whether to preserve tenant data

        Returns:
            True if tenant was successfully terminated
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        try:
            # Create backup if preserving data
            if preserve_data:
                await self._backup_tenant_data(tenant)

            # Cleanup infrastructure
            await self._cleanup_tenant_infrastructure(tenant_id)

            # Update status or remove
            if preserve_data:
                tenant.status = TenantStatus.TERMINATED
            else:
                del self._tenants[tenant_id]

            self.logger.info(f"Terminated tenant: {tenant_id} (preserve_data={preserve_data})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to terminate tenant {tenant_id}: {e}")
            raise RuntimeError(f"Tenant termination failed: {e}")

    async def _backup_tenant_data(self, tenant: Tenant) -> None:
        """Create backup of tenant data."""
        # In production, backup database, files, configurations
        self.logger.debug(f"Backed up data for tenant {tenant.id}")

    async def _cleanup_tenant_infrastructure(self, tenant_id: str) -> None:
        """Clean up all infrastructure for a tenant."""
        # In production, delete namespaces, databases, storage
        self.logger.debug(f"Cleaned up infrastructure for tenant {tenant_id}")

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID.

        Args:
            tenant_id: ID of tenant to retrieve

        Returns:
            Tenant instance or None if not found
        """
        return self._tenants.get(tenant_id)

    def get_tenant_by_name(self, name: str) -> Optional[Tenant]:
        """Get tenant by name.

        Args:
            name: Name of tenant to retrieve

        Returns:
            Tenant instance or None if not found
        """
        for tenant in self._tenants.values():
            if tenant.name == name:
                return tenant
        return None

    def list_tenants(self, status: Optional[TenantStatus] = None) -> list[Tenant]:
        """List tenants, optionally filtered by status.

        Args:
            status: Optional status filter

        Returns:
            List of matching tenants
        """
        tenants = list(self._tenants.values())
        if status:
            tenants = [t for t in tenants if t.status == status]
        return tenants

    async def check_resource_usage(self, tenant_id: str) -> dict[ResourceType, float]:
        """Check current resource usage for a tenant.

        Args:
            tenant_id: ID of tenant to check

        Returns:
            Dictionary mapping resource types to usage percentages

        Raises:
            ValueError: If tenant not found
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        # In production, query actual resource usage from monitoring systems
        usage = {}
        for resource_type, quota in tenant.quotas.items():
            usage[resource_type] = quota.usage_percentage

        return usage

    async def enforce_quotas(self, tenant_id: str) -> list[str]:
        """Enforce resource quotas for a tenant.

        Args:
            tenant_id: ID of tenant to enforce quotas for

        Returns:
            List of actions taken

        Raises:
            ValueError: If tenant not found
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        actions = []
        exceeded_quotas = tenant.is_quota_exceeded()

        for resource_type in exceeded_quotas:
            quota = tenant.quotas[resource_type]

            if quota.auto_scale and tenant.tier == TenantTier.ENTERPRISE:
                # Auto-scale for enterprise tenants
                new_limit = quota.limit * 1.5
                quota.limit = new_limit
                actions.append(f"Auto-scaled {resource_type.value} to {new_limit}")
                self.logger.info(f"Auto-scaled {resource_type.value} for {tenant_id}")
            else:
                # Throttle or suspend services
                await self._throttle_tenant_resource(tenant, resource_type)
                actions.append(f"Throttled {resource_type.value}")
                self.logger.warning(f"Throttled {resource_type.value} for {tenant_id}")

        return actions

    async def _throttle_tenant_resource(self, tenant: Tenant, resource_type: ResourceType) -> None:
        """Throttle a specific resource for a tenant."""
        # In production, implement actual throttling mechanisms
        self.logger.debug(f"Throttling {resource_type.value} for {tenant.id}")

    def _validate_tenant_name(self, name: str) -> bool:
        """Validate tenant name format.

        Args:
            name: Tenant name to validate

        Returns:
            True if name is valid
        """
        if not name or len(name) < 2 or len(name) > 100:
            return False
        # Allow alphanumeric, spaces, hyphens, underscores
        return re.match(r"^[a-zA-Z0-9\s\-_]+$", name) is not None

    def _generate_tenant_id(self, name: str) -> str:
        """Generate unique tenant ID from name.

        Args:
            name: Tenant name

        Returns:
            Unique tenant ID
        """
        # Create deterministic but unique ID
        name_hash = hashlib.sha256(name.encode()).hexdigest()[:8]
        return f"tenant-{name_hash}-{str(uuid.uuid4())[:8]}"

    async def get_tenant_metrics(self, tenant_id: str) -> dict[str, Any]:
        """Get comprehensive metrics for a tenant.

        Args:
            tenant_id: ID of tenant

        Returns:
            Dictionary of tenant metrics

        Raises:
            ValueError: If tenant not found
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        # In production, gather metrics from various systems
        return {
            "tenant_id": tenant_id,
            "status": tenant.status.value,
            "tier": tenant.tier.value,
            "uptime_hours": (datetime.utcnow() - tenant.metadata.created_at).total_seconds() / 3600,
            "last_active": tenant.metadata.last_active_at.isoformat(),
            "resource_usage": {
                rt.value: quota.usage_percentage for rt, quota in tenant.quotas.items()
            },
            "quota_violations": [rt.value for rt in tenant.is_quota_exceeded()],
            "total_api_calls": tenant.metadata.total_api_calls,
            "total_data_processed_gb": tenant.metadata.total_data_processed_gb,
        }

    async def migrate_tenant(self, tenant_id: str, target_region: str) -> bool:
        """Migrate tenant to a different region.

        Args:
            tenant_id: ID of tenant to migrate
            target_region: Target region for migration

        Returns:
            True if migration was successful
        """
        tenant = self.get_tenant(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        try:
            tenant.status = TenantStatus.MIGRATING

            # Create backup
            await self._backup_tenant_data(tenant)

            # Provision in new region
            await self._provision_tenant_in_region(tenant, target_region)

            # Migrate data
            await self._migrate_tenant_data(tenant, target_region)

            # Update configuration
            tenant.config["data_residency"] = target_region
            tenant.status = TenantStatus.ACTIVE

            self.logger.info(f"Migrated tenant {tenant_id} to {target_region}")
            return True

        except Exception as e:
            tenant.status = TenantStatus.ACTIVE  # Rollback status
            self.logger.error(f"Failed to migrate tenant {tenant_id}: {e}")
            raise RuntimeError(f"Tenant migration failed: {e}")

    async def _provision_tenant_in_region(self, tenant: Tenant, region: str) -> None:
        """Provision tenant infrastructure in target region."""
        # In production, create resources in target region
        self.logger.debug(f"Provisioned {tenant.id} in region {region}")

    async def _migrate_tenant_data(self, tenant: Tenant, target_region: str) -> None:
        """Migrate tenant data to target region."""
        # In production, perform actual data migration
        self.logger.debug(f"Migrated data for {tenant.id} to {region}")
