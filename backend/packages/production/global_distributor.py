"""
Global distribution and edge computing system for T-Developer.

This module provides multi-region deployment orchestration, data replication,
edge function deployment, and geo-routing capabilities for global scale.
"""

from __future__ import annotations

import asyncio
import logging
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional


class RegionType(Enum):
    """Types of deployment regions."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    EDGE = "edge"
    DISASTER_RECOVERY = "disaster_recovery"


class ReplicationStrategy(Enum):
    """Data replication strategies."""

    SYNC = "synchronous"
    ASYNC = "asynchronous"
    EVENTUAL = "eventual_consistency"
    HYBRID = "hybrid"


class DistributionStatus(Enum):
    """Status of distributed deployments."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    FULL_OUTAGE = "full_outage"
    MAINTENANCE = "maintenance"


class FailoverMode(Enum):
    """Failover modes for regions."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"
    ASSISTED = "assisted"


class EdgeFunctionType(Enum):
    """Types of edge functions."""

    COMPUTE = "compute"
    CACHE = "cache"
    TRANSFORM = "transform"
    VALIDATE = "validate"
    ROUTE = "route"


@dataclass
class LatencyMetrics:
    """Network latency metrics between regions.

    Attributes:
        p50_ms: 50th percentile latency in milliseconds
        p95_ms: 95th percentile latency in milliseconds
        p99_ms: 99th percentile latency in milliseconds
        avg_ms: Average latency in milliseconds
        packet_loss: Packet loss percentage (0.0-1.0)
        last_measured: When metrics were last updated
    """

    p50_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    packet_loss: float = 0.0
    last_measured: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_healthy(self) -> bool:
        """Check if latency metrics indicate healthy connection."""
        return (
            self.p95_ms < 200
            and self.packet_loss < 0.01  # 200ms threshold
            and (datetime.utcnow() - self.last_measured).total_seconds()  # 1% packet loss threshold
            < 300  # 5 min fresh
        )


@dataclass
class RegionConfig:
    """Configuration for a deployment region.

    Attributes:
        region_id: Unique identifier for the region
        name: Human-readable region name
        type: Type of region (primary, secondary, edge, etc.)
        location: Geographic location information
        capacity: Available compute capacity
        endpoints: Service endpoints in this region
        replication_targets: Regions to replicate data to
        failover_targets: Regions to failover to
        edge_locations: Edge locations served by this region
    """

    region_id: str
    name: str
    type: RegionType
    location: dict[str, Any]  # lat, lng, country, timezone
    capacity: dict[str, float]  # cpu, memory, storage
    endpoints: dict[str, str] = field(default_factory=dict)
    replication_targets: set[str] = field(default_factory=set)
    failover_targets: list[str] = field(default_factory=list)
    edge_locations: set[str] = field(default_factory=set)
    status: DistributionStatus = DistributionStatus.HEALTHY
    last_health_check: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_available(self) -> bool:
        """Check if region is available for deployments."""
        return self.status in [DistributionStatus.HEALTHY, DistributionStatus.DEGRADED]


@dataclass
class EdgeFunction:
    """Edge function definition for distributed execution.

    Attributes:
        function_id: Unique identifier for the function
        name: Human-readable function name
        type: Type of edge function
        code: Function code or reference
        runtime: Runtime environment
        regions: Regions where function is deployed
        triggers: Events that trigger the function
        config: Function-specific configuration
        metrics: Performance metrics
    """

    function_id: str
    name: str
    type: EdgeFunctionType
    code: str
    runtime: str
    regions: set[str] = field(default_factory=set)
    triggers: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_deployed: Optional[datetime] = None

    def get_deployment_key(self, region: str) -> str:
        """Get deployment key for this function in a region."""
        return f"{self.function_id}-{region}-{int(time.time())}"


@dataclass
class ReplicationJob:
    """Data replication job between regions.

    Attributes:
        job_id: Unique identifier for the job
        source_region: Source region for replication
        target_region: Target region for replication
        strategy: Replication strategy to use
        data_types: Types of data to replicate
        schedule: Replication schedule
        last_run: When replication last ran
        next_run: When replication is next scheduled
        status: Current status of replication
        errors: Any replication errors
    """

    job_id: str
    source_region: str
    target_region: str
    strategy: ReplicationStrategy
    data_types: set[str]
    schedule: str  # cron expression
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: str = "pending"
    errors: list[str] = field(default_factory=list)
    bytes_replicated: int = 0

    @property
    def is_due(self) -> bool:
        """Check if replication job is due to run."""
        if not self.next_run:
            return True
        return datetime.utcnow() >= self.next_run


class GlobalDistributor:
    """Global distribution and edge computing system.

    Manages multi-region deployments, data replication, edge functions,
    and geo-routing for T-Developer's global infrastructure.

    Example:
        >>> distributor = GlobalDistributor()
        >>> await distributor.initialize()
        >>> await distributor.add_region("us-east-1", RegionType.PRIMARY)
        >>> await distributor.deploy_service("service-1", ["us-east-1", "eu-west-1"])
    """

    def __init__(self, config: dict[str, Any] = None) -> None:
        """Initialize global distributor.

        Args:
            config: Distributor configuration options
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        self._regions: dict[str, RegionConfig] = {}
        self._edge_functions: dict[str, EdgeFunction] = {}
        self._replication_jobs: dict[str, ReplicationJob] = {}
        self._latency_matrix: dict[tuple, LatencyMetrics] = {}
        self._routing_table: dict[str, list[str]] = {}  # client_location -> regions
        self._health_check_interval = 60  # seconds
        self._replication_interval = 300  # seconds

    async def initialize(self) -> None:
        """Initialize the global distributor.

        Sets up monitoring, health checks, and initial regions.
        """
        self.logger.info("Initializing global distributor")

        await self._load_region_configs()
        await self._setup_health_monitoring()
        await self._initialize_latency_monitoring()
        await self._start_replication_scheduler()

        self.logger.info("Global distributor initialized successfully")

    async def _load_region_configs(self) -> None:
        """Load existing region configurations."""
        # In production, load from configuration store
        default_regions = [
            {
                "region_id": "us-east-1",
                "name": "US East (Virginia)",
                "type": RegionType.PRIMARY,
                "location": {"lat": 39.0458, "lng": -76.6413, "country": "US", "timezone": "EST"},
            },
            {
                "region_id": "eu-west-1",
                "name": "Europe (Ireland)",
                "type": RegionType.SECONDARY,
                "location": {"lat": 53.3498, "lng": -6.2603, "country": "IE", "timezone": "GMT"},
            },
            {
                "region_id": "ap-southeast-1",
                "name": "Asia Pacific (Singapore)",
                "type": RegionType.SECONDARY,
                "location": {"lat": 1.3521, "lng": 103.8198, "country": "SG", "timezone": "SGT"},
            },
        ]

        for region_data in default_regions:
            region = RegionConfig(
                region_id=region_data["region_id"],
                name=region_data["name"],
                type=region_data["type"],
                location=region_data["location"],
                capacity={"cpu": 1000, "memory": 2000, "storage": 10000},
            )
            self._regions[region.region_id] = region

        self.logger.info(f"Loaded {len(self._regions)} regions")

    async def _setup_health_monitoring(self) -> None:
        """Set up continuous health monitoring for all regions."""
        asyncio.create_task(self._health_check_loop())

    async def _health_check_loop(self) -> None:
        """Continuous health check loop."""
        while True:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self._health_check_interval)
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(10)  # Short retry delay

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all regions."""
        tasks = []
        for region in self._regions.values():
            tasks.append(self._check_region_health(region))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_region_health(self, region: RegionConfig) -> None:
        """Check health of a specific region.

        Args:
            region: Region to check
        """
        try:
            # In production, perform actual health checks
            # - API endpoint availability
            # - Database connectivity
            # - Storage accessibility
            # - Compute resource availability

            # Simulate health check
            await asyncio.sleep(0.1)

            region.last_health_check = datetime.utcnow()

            # Update status based on checks
            if region.status == DistributionStatus.FULL_OUTAGE:
                region.status = DistributionStatus.HEALTHY
                self.logger.info(f"Region {region.region_id} recovered")

        except Exception as e:
            region.status = DistributionStatus.DEGRADED
            self.logger.warning(f"Health check failed for {region.region_id}: {e}")

    async def _initialize_latency_monitoring(self) -> None:
        """Initialize latency monitoring between regions."""
        asyncio.create_task(self._latency_monitoring_loop())

    async def _latency_monitoring_loop(self) -> None:
        """Continuous latency monitoring loop."""
        while True:
            try:
                await self._measure_inter_region_latency()
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                self.logger.error(f"Latency monitoring error: {e}")
                await asyncio.sleep(60)

    async def _measure_inter_region_latency(self) -> None:
        """Measure latency between all region pairs."""
        regions = list(self._regions.keys())

        for i, source in enumerate(regions):
            for target in regions[i + 1 :]:
                try:
                    metrics = await self._measure_latency(source, target)
                    self._latency_matrix[(source, target)] = metrics
                    self._latency_matrix[(target, source)] = metrics
                except Exception as e:
                    self.logger.warning(f"Failed to measure latency {source}->{target}: {e}")

    async def _measure_latency(self, source: str, target: str) -> LatencyMetrics:
        """Measure latency between two regions.

        Args:
            source: Source region ID
            target: Target region ID

        Returns:
            Latency metrics
        """
        # In production, perform actual network measurements
        # For now, simulate based on geographic distance
        source_region = self._regions[source]
        target_region = self._regions[target]

        distance = self._calculate_distance(source_region.location, target_region.location)

        # Simulate latency based on distance
        base_latency = distance / 200  # Rough speed of light approximation

        return LatencyMetrics(
            p50_ms=base_latency * 1.2,
            p95_ms=base_latency * 1.8,
            p99_ms=base_latency * 2.5,
            avg_ms=base_latency * 1.3,
            packet_loss=0.001,  # 0.1%
        )

    def _calculate_distance(self, loc1: dict[str, float], loc2: dict[str, float]) -> float:
        """Calculate great circle distance between two locations.

        Args:
            loc1: First location with lat/lng
            loc2: Second location with lat/lng

        Returns:
            Distance in kilometers
        """
        # Haversine formula
        lat1, lng1 = math.radians(loc1["lat"]), math.radians(loc1["lng"])
        lat2, lng2 = math.radians(loc2["lat"]), math.radians(loc2["lng"])

        dlat = lat2 - lat1
        dlng = lng2 - lng1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        return 6371 * c  # Earth radius in km

    async def _start_replication_scheduler(self) -> None:
        """Start the data replication scheduler."""
        asyncio.create_task(self._replication_scheduler_loop())

    async def _replication_scheduler_loop(self) -> None:
        """Continuous replication scheduler loop."""
        while True:
            try:
                await self._process_replication_jobs()
                await asyncio.sleep(self._replication_interval)
            except Exception as e:
                self.logger.error(f"Replication scheduler error: {e}")
                await asyncio.sleep(60)

    async def _process_replication_jobs(self) -> None:
        """Process due replication jobs."""
        due_jobs = [job for job in self._replication_jobs.values() if job.is_due]

        for job in due_jobs:
            try:
                await self._execute_replication_job(job)
            except Exception as e:
                job.errors.append(str(e))
                self.logger.error(f"Replication job {job.job_id} failed: {e}")

    async def _execute_replication_job(self, job: ReplicationJob) -> None:
        """Execute a replication job.

        Args:
            job: Replication job to execute
        """
        self.logger.info(f"Executing replication job {job.job_id}")

        job.status = "running"
        job.last_run = datetime.utcnow()

        try:
            # In production, perform actual data replication
            bytes_replicated = await self._replicate_data(
                job.source_region, job.target_region, job.data_types, job.strategy
            )

            job.bytes_replicated += bytes_replicated
            job.status = "completed"
            job.next_run = datetime.utcnow() + timedelta(minutes=5)  # Next run in 5 min

            self.logger.info(f"Replication job {job.job_id} completed: {bytes_replicated} bytes")

        except Exception as e:
            job.status = "failed"
            job.errors.append(str(e))
            raise e

    async def _replicate_data(
        self, source: str, target: str, data_types: set[str], strategy: ReplicationStrategy
    ) -> int:
        """Replicate data between regions.

        Args:
            source: Source region ID
            target: Target region ID
            data_types: Types of data to replicate
            strategy: Replication strategy

        Returns:
            Number of bytes replicated
        """
        # In production, implement actual data replication
        # - Database replication
        # - File synchronization
        # - Configuration sync

        # Simulate replication
        await asyncio.sleep(0.5)
        return 1024 * 1024  # 1MB simulated

    async def add_region(
        self,
        region_id: str,
        region_type: RegionType,
        name: str,
        location: dict[str, Any],
        capacity: dict[str, float] = None,
    ) -> RegionConfig:
        """Add a new deployment region.

        Args:
            region_id: Unique identifier for the region
            region_type: Type of region
            name: Human-readable name
            location: Geographic location information
            capacity: Available compute capacity

        Returns:
            Created region configuration

        Raises:
            ValueError: If region already exists or invalid parameters
        """
        if region_id in self._regions:
            raise ValueError(f"Region {region_id} already exists")

        if not location or "lat" not in location or "lng" not in location:
            raise ValueError("Location must include lat and lng coordinates")

        region = RegionConfig(
            region_id=region_id,
            name=name,
            type=region_type,
            location=location,
            capacity=capacity or {"cpu": 100, "memory": 200, "storage": 1000},
        )

        self._regions[region_id] = region

        # Update latency measurements
        await self._measure_latency_to_new_region(region_id)

        self.logger.info(f"Added region: {region_id} ({name})")
        return region

    async def _measure_latency_to_new_region(self, new_region_id: str) -> None:
        """Measure latency from new region to all existing regions."""
        for existing_region_id in self._regions.keys():
            if existing_region_id != new_region_id:
                try:
                    metrics = await self._measure_latency(new_region_id, existing_region_id)
                    self._latency_matrix[(new_region_id, existing_region_id)] = metrics
                    self._latency_matrix[(existing_region_id, new_region_id)] = metrics
                except Exception as e:
                    self.logger.warning(f"Failed to measure latency to new region: {e}")

    async def deploy_service(
        self, service_id: str, target_regions: list[str], deployment_config: dict[str, Any] = None
    ) -> dict[str, bool]:
        """Deploy a service to multiple regions.

        Args:
            service_id: ID of service to deploy
            target_regions: List of regions to deploy to
            deployment_config: Service-specific deployment configuration

        Returns:
            Dictionary mapping region IDs to deployment success status

        Raises:
            ValueError: If invalid regions specified
        """
        # Validate regions
        invalid_regions = [r for r in target_regions if r not in self._regions]
        if invalid_regions:
            raise ValueError(f"Invalid regions: {invalid_regions}")

        config = deployment_config or {}
        results = {}

        # Deploy to each region
        for region_id in target_regions:
            try:
                success = await self._deploy_to_region(service_id, region_id, config)
                results[region_id] = success

                if success:
                    self.logger.info(f"Deployed {service_id} to {region_id}")
                else:
                    self.logger.error(f"Failed to deploy {service_id} to {region_id}")

            except Exception as e:
                results[region_id] = False
                self.logger.error(f"Deploy error for {service_id} in {region_id}: {e}")

        return results

    async def _deploy_to_region(
        self, service_id: str, region_id: str, config: dict[str, Any]
    ) -> bool:
        """Deploy service to a specific region.

        Args:
            service_id: Service to deploy
            region_id: Target region
            config: Deployment configuration

        Returns:
            True if deployment successful
        """
        region = self._regions[region_id]

        if not region.is_available:
            self.logger.warning(f"Region {region_id} not available for deployment")
            return False

        # In production, perform actual deployment
        # - Create Kubernetes resources
        # - Configure load balancers
        # - Set up monitoring
        # - Configure networking

        # Simulate deployment
        await asyncio.sleep(1.0)

        # Update region endpoints
        region.endpoints[service_id] = f"https://{service_id}.{region_id}.tdev.ai"

        return True

    async def deploy_edge_function(
        self, function: EdgeFunction, target_regions: list[str] = None
    ) -> dict[str, bool]:
        """Deploy an edge function to specified regions.

        Args:
            function: Edge function to deploy
            target_regions: Regions to deploy to (default: all edge regions)

        Returns:
            Dictionary mapping region IDs to deployment success
        """
        if target_regions is None:
            target_regions = [
                r.region_id for r in self._regions.values() if r.type == RegionType.EDGE
            ]

        results = {}

        for region_id in target_regions:
            try:
                success = await self._deploy_edge_function_to_region(function, region_id)
                results[region_id] = success

                if success:
                    function.regions.add(region_id)
                    self.logger.info(
                        f"Deployed edge function {function.function_id} to {region_id}"
                    )

            except Exception as e:
                results[region_id] = False
                self.logger.error(f"Edge function deploy error in {region_id}: {e}")

        # Store function definition
        self._edge_functions[function.function_id] = function
        function.last_deployed = datetime.utcnow()

        return results

    async def _deploy_edge_function_to_region(self, function: EdgeFunction, region_id: str) -> bool:
        """Deploy edge function to specific region.

        Args:
            function: Function to deploy
            region_id: Target region

        Returns:
            True if deployment successful
        """
        # In production, deploy to edge compute infrastructure
        # - Package function code
        # - Deploy to edge runtime
        # - Configure triggers
        # - Set up monitoring

        await asyncio.sleep(0.5)  # Simulate deployment
        return True

    def route_request(self, client_location: dict[str, float], service_id: str) -> Optional[str]:
        """Route a request to the optimal region based on client location.

        Args:
            client_location: Client's geographic location (lat, lng)
            service_id: Service being requested

        Returns:
            Optimal region ID or None if no suitable region found
        """
        # Find regions that have the service deployed
        available_regions = [
            region
            for region in self._regions.values()
            if (region.is_available and service_id in region.endpoints)
        ]

        if not available_regions:
            return None

        # Calculate distances to available regions
        region_scores = []
        for region in available_regions:
            distance = self._calculate_distance(client_location, region.location)

            # Apply region type weighting
            weight = {
                RegionType.PRIMARY: 1.0,
                RegionType.SECONDARY: 0.9,
                RegionType.EDGE: 1.2,  # Prefer edge locations
                RegionType.DISASTER_RECOVERY: 0.5,
            }.get(region.type, 1.0)

            # Consider region health
            health_penalty = 0 if region.status == DistributionStatus.HEALTHY else 1000

            score = distance + health_penalty - (weight * 100)
            region_scores.append((score, region.region_id))

        # Return region with best score (lowest)
        region_scores.sort()
        return region_scores[0][1]

    async def setup_replication(
        self,
        source_region: str,
        target_region: str,
        strategy: ReplicationStrategy,
        data_types: set[str],
        schedule: str = "*/5 * * * *",
    ) -> ReplicationJob:
        """Set up data replication between regions.

        Args:
            source_region: Source region for replication
            target_region: Target region for replication
            strategy: Replication strategy to use
            data_types: Types of data to replicate
            schedule: Cron schedule for replication

        Returns:
            Created replication job

        Raises:
            ValueError: If regions don't exist
        """
        if source_region not in self._regions:
            raise ValueError(f"Source region not found: {source_region}")
        if target_region not in self._regions:
            raise ValueError(f"Target region not found: {target_region}")

        job_id = f"repl-{source_region}-{target_region}-{int(time.time())}"

        job = ReplicationJob(
            job_id=job_id,
            source_region=source_region,
            target_region=target_region,
            strategy=strategy,
            data_types=data_types,
            schedule=schedule,
            next_run=datetime.utcnow() + timedelta(minutes=1),
        )

        self._replication_jobs[job_id] = job

        self.logger.info(f"Set up replication job: {job_id}")
        return job

    async def failover_region(
        self, failed_region: str, mode: FailoverMode = FailoverMode.AUTOMATIC
    ) -> dict[str, Any]:
        """Perform failover from a failed region.

        Args:
            failed_region: Region that has failed
            mode: Failover mode to use

        Returns:
            Failover results and actions taken
        """
        if failed_region not in self._regions:
            raise ValueError(f"Region not found: {failed_region}")

        region = self._regions[failed_region]
        region.status = DistributionStatus.FULL_OUTAGE

        results = {
            "failed_region": failed_region,
            "mode": mode.value,
            "actions": [],
            "new_endpoints": {},
            "affected_services": list(region.endpoints.keys()),
        }

        # Find failover targets
        failover_targets = region.failover_targets or self._get_default_failover_targets(
            failed_region
        )

        for service_id in region.endpoints.keys():
            # Find best failover target for each service
            target_region = self._select_failover_target(service_id, failover_targets)

            if target_region:
                # Update routing to point to failover region
                old_endpoint = region.endpoints[service_id]
                new_endpoint = self._regions[target_region].endpoints.get(service_id)

                if new_endpoint:
                    results["new_endpoints"][service_id] = new_endpoint
                    results["actions"].append(f"Rerouted {service_id} to {target_region}")
                else:
                    # Deploy service to failover region if not already there
                    success = await self._deploy_to_region(service_id, target_region, {})
                    if success:
                        new_endpoint = self._regions[target_region].endpoints[service_id]
                        results["new_endpoints"][service_id] = new_endpoint
                        results["actions"].append(
                            f"Deployed and rerouted {service_id} to {target_region}"
                        )

        self.logger.critical(f"Performed failover from {failed_region}: {results}")
        return results

    def _get_default_failover_targets(self, failed_region: str) -> list[str]:
        """Get default failover targets for a failed region."""
        # Select healthy regions with similar characteristics
        failed_region_config = self._regions[failed_region]
        candidates = []

        for region_id, region in self._regions.items():
            if (
                region_id != failed_region
                and region.is_available
                and region.type in [RegionType.PRIMARY, RegionType.SECONDARY]
            ):
                # Calculate preference score based on latency and capacity
                latency_key = (failed_region, region_id)
                latency = self._latency_matrix.get(latency_key)
                latency_score = latency.avg_ms if latency else 1000

                capacity_score = sum(region.capacity.values())
                candidates.append((latency_score - capacity_score, region_id))

        candidates.sort()
        return [region_id for _, region_id in candidates[:3]]  # Top 3

    def _select_failover_target(self, service_id: str, candidates: list[str]) -> Optional[str]:
        """Select best failover target for a service."""
        for region_id in candidates:
            region = self._regions[region_id]
            if region.is_available and service_id in region.endpoints:
                return region_id

        # If service not deployed to any candidate, return first available
        for region_id in candidates:
            region = self._regions[region_id]
            if region.is_available:
                return region_id

        return None

    async def get_global_status(self) -> dict[str, Any]:
        """Get global distribution status and metrics.

        Returns:
            Comprehensive status information
        """
        healthy_regions = sum(
            1 for r in self._regions.values() if r.status == DistributionStatus.HEALTHY
        )
        total_regions = len(self._regions)

        # Calculate average latencies
        latencies = [m.avg_ms for m in self._latency_matrix.values()]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0

        # Count edge functions
        total_edge_functions = len(self._edge_functions)
        active_replications = sum(
            1 for j in self._replication_jobs.values() if j.status == "running"
        )

        return {
            "regions": {
                "total": total_regions,
                "healthy": healthy_regions,
                "degraded": sum(
                    1 for r in self._regions.values() if r.status == DistributionStatus.DEGRADED
                ),
                "outage": sum(
                    1 for r in self._regions.values() if r.status == DistributionStatus.FULL_OUTAGE
                ),
            },
            "performance": {
                "avg_latency_ms": avg_latency,
                "max_latency_ms": max(latencies) if latencies else 0,
                "healthy_connections": sum(
                    1 for m in self._latency_matrix.values() if m.is_healthy
                ),
            },
            "edge_functions": {
                "total": total_edge_functions,
                "deployed_regions": sum(len(f.regions) for f in self._edge_functions.values()),
            },
            "replication": {
                "active_jobs": active_replications,
                "total_jobs": len(self._replication_jobs),
                "total_bytes_replicated": sum(
                    j.bytes_replicated for j in self._replication_jobs.values()
                ),
            },
            "last_updated": datetime.utcnow().isoformat(),
        }

    def get_region_info(self, region_id: str) -> Optional[dict[str, Any]]:
        """Get detailed information about a specific region.

        Args:
            region_id: Region to get information for

        Returns:
            Region information or None if not found
        """
        region = self._regions.get(region_id)
        if not region:
            return None

        # Get latency to other regions
        latencies = {}
        for other_region_id in self._regions.keys():
            if other_region_id != region_id:
                latency_key = (region_id, other_region_id)
                latency = self._latency_matrix.get(latency_key)
                if latency:
                    latencies[other_region_id] = latency.avg_ms

        return {
            "region_id": region.region_id,
            "name": region.name,
            "type": region.type.value,
            "status": region.status.value,
            "location": region.location,
            "capacity": region.capacity,
            "services": list(region.endpoints.keys()),
            "latencies": latencies,
            "last_health_check": region.last_health_check.isoformat(),
        }
