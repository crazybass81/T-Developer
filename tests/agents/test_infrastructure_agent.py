"""Tests for Infrastructure Agent - IaC generation and deployment management.

Phase 5: P5-T3 - Infrastructure Agent Tests
Tests for infrastructure as code generation and cloud deployment management.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from packages.agents.base import AgentInput, AgentOutput, AgentStatus
from packages.agents.infrastructure_agent import (
    CDKGenerator,
    CloudProvider,
    ComputeConfig,
    DatabaseConfig,
    Environment,
    EnvironmentManager,
    IaCTool,
    InfrastructureAgent,
    InfrastructureSpec,
    NetworkConfig,
    SecretsManager,
    TerraformGenerator,
)


class TestNetworkConfig:
    """Test NetworkConfig dataclass."""

    def test_network_config_defaults(self):
        """Test default network configuration."""
        config = NetworkConfig()

        assert config.vpc_cidr == "10.0.0.0/16"
        assert len(config.public_subnets) == 2
        assert len(config.private_subnets) == 2
        assert config.enable_nat is True
        assert config.enable_vpn is False

    def test_network_config_custom(self):
        """Test custom network configuration."""
        config = NetworkConfig(
            vpc_cidr="172.16.0.0/16",
            public_subnets=["172.16.1.0/24"],
            private_subnets=["172.16.10.0/24"],
            availability_zones=["us-west-2a"],
            enable_nat=False,
            enable_vpn=True,
        )

        assert config.vpc_cidr == "172.16.0.0/16"
        assert len(config.public_subnets) == 1
        assert config.enable_nat is False
        assert config.enable_vpn is True


class TestComputeConfig:
    """Test ComputeConfig dataclass."""

    def test_compute_config_defaults(self):
        """Test default compute configuration."""
        config = ComputeConfig()

        assert config.instance_type == "t3.medium"
        assert config.min_instances == 2
        assert config.max_instances == 10
        assert config.desired_capacity == 3
        assert config.container_insights is True
        assert config.spot_instances is False

    def test_compute_config_custom(self):
        """Test custom compute configuration."""
        config = ComputeConfig(
            instance_type="m5.large",
            min_instances=1,
            max_instances=5,
            desired_capacity=2,
            spot_instances=True,
        )

        assert config.instance_type == "m5.large"
        assert config.min_instances == 1
        assert config.spot_instances is True


class TestDatabaseConfig:
    """Test DatabaseConfig dataclass."""

    def test_database_config_defaults(self):
        """Test default database configuration."""
        config = DatabaseConfig()

        assert config.engine == "postgres"
        assert config.version == "15.3"
        assert config.instance_class == "db.t3.small"
        assert config.allocated_storage == 20
        assert config.multi_az is True
        assert config.backup_retention == 7
        assert config.encrypted is True


class TestEnvironment:
    """Test Environment dataclass."""

    def test_environment_defaults(self):
        """Test default environment configuration."""
        env = Environment(name="test", type="development")

        assert env.name == "test"
        assert env.type == "development"
        assert env.region == "us-east-1"
        assert env.enable_monitoring is True
        assert env.enable_logging is True
        assert env.database is None

    def test_environment_with_database(self):
        """Test environment with database configuration."""
        db_config = DatabaseConfig(engine="mysql", version="8.0")
        env = Environment(name="prod", type="production", region="us-west-2", database=db_config)

        assert env.name == "prod"
        assert env.region == "us-west-2"
        assert env.database.engine == "mysql"
        assert env.database.version == "8.0"


class TestInfrastructureSpec:
    """Test InfrastructureSpec dataclass."""

    def test_infrastructure_spec_creation(self):
        """Test creating infrastructure specification."""
        env = Environment(name="dev", type="development")

        spec = InfrastructureSpec(
            service_name="test-service",
            provider=CloudProvider.AWS,
            environments=[env],
            secrets=["api_key", "db_password"],
            parameters={"log_level": "info", "timeout": "30"},
        )

        assert spec.service_name == "test-service"
        assert spec.provider == CloudProvider.AWS
        assert len(spec.environments) == 1
        assert len(spec.secrets) == 2
        assert spec.parameters["log_level"] == "info"


class TestTerraformGenerator:
    """Test TerraformGenerator functionality."""

    @pytest.fixture
    def generator(self):
        """Create TerraformGenerator instance."""
        return TerraformGenerator()

    @pytest.fixture
    def sample_spec(self):
        """Create sample infrastructure specification."""
        env = Environment(
            name="production", type="production", region="us-east-1", database=DatabaseConfig()
        )

        return InfrastructureSpec(
            service_name="my-service",
            provider=CloudProvider.AWS,
            environments=[env],
            secrets=["api_key"],
            parameters={"environment": "production"},
        )

    def test_generate_main_tf(self, generator, sample_spec):
        """Test generating main.tf file."""
        main_tf = generator.generate_main(sample_spec)

        assert "terraform {" in main_tf
        assert "required_version" in main_tf
        assert "hashicorp/aws" in main_tf
        assert "my-service-terraform-state" in main_tf
        assert 'module "vpc"' in main_tf
        assert 'module "ecs"' in main_tf

    def test_generate_variables_tf(self, generator, sample_spec):
        """Test generating variables.tf file."""
        variables_tf = generator.generate_variables(sample_spec)

        assert 'variable "service_name"' in variables_tf
        assert 'variable "aws_region"' in variables_tf
        assert 'variable "vpc_cidr"' in variables_tf
        assert "my-service" in variables_tf
        assert "us-east-1" in variables_tf

    def test_generate_outputs_tf(self, generator, sample_spec):
        """Test generating outputs.tf file."""
        outputs_tf = generator.generate_outputs(sample_spec)

        assert 'output "vpc_id"' in outputs_tf
        assert 'output "public_subnet_ids"' in outputs_tf
        assert 'output "private_subnet_ids"' in outputs_tf
        assert 'output "ecs_cluster_id"' in outputs_tf
        assert "module.vpc.vpc_id" in outputs_tf

    def test_generate_vpc_module(self, generator, sample_spec):
        """Test generating VPC module files."""
        vpc_files = generator.generate_vpc_module(sample_spec)

        assert "modules/vpc/main.tf" in vpc_files
        assert "modules/vpc/variables.tf" in vpc_files
        assert "modules/vpc/outputs.tf" in vpc_files

        main_tf = vpc_files["modules/vpc/main.tf"]
        assert 'resource "aws_vpc" "main"' in main_tf
        assert 'resource "aws_subnet" "public"' in main_tf
        assert 'resource "aws_nat_gateway" "main"' in main_tf


class TestCDKGenerator:
    """Test CDKGenerator functionality."""

    @pytest.fixture
    def generator(self):
        """Create CDKGenerator instance."""
        return CDKGenerator()

    @pytest.fixture
    def sample_spec(self):
        """Create sample infrastructure specification."""
        env = Environment(name="prod", type="production")
        return InfrastructureSpec(
            service_name="my-cdk-service", provider=CloudProvider.AWS, environments=[env]
        )

    def test_generate_stack(self, generator, sample_spec):
        """Test generating CDK stack."""
        stack_py = generator.generate_stack(sample_spec)

        assert "from aws_cdk import" in stack_py
        assert "class MyCdkServiceStack(Stack):" in stack_py
        assert "ec2.Vpc(" in stack_py
        assert "ecs.Cluster(" in stack_py
        assert "ec2.SecurityGroup(" in stack_py
        assert "Tags.of(self).add" in stack_py


class TestSecretsManager:
    """Test SecretsManager functionality."""

    @pytest.fixture
    def manager(self):
        """Create SecretsManager instance."""
        return SecretsManager()

    @pytest.fixture
    def sample_spec(self):
        """Create sample infrastructure specification."""
        env = Environment(name="prod", type="production")
        return InfrastructureSpec(
            service_name="secret-service",
            provider=CloudProvider.AWS,
            environments=[env],
            secrets=["api_key", "database_password"],
            parameters={"log_level": "info", "timeout": "30"},
        )

    def test_generate_secrets_config(self, manager, sample_spec):
        """Test generating secrets configuration."""
        config = manager.generate_secrets_config(sample_spec)

        assert "version: '1.0'" in config
        assert "secrets:" in config
        assert "secret-service/api_key" in config
        assert "secret-service/database_password" in config
        assert "rotation:" in config

    def test_generate_parameter_store(self, manager, sample_spec):
        """Test generating parameter store configuration."""
        params = manager.generate_parameter_store(sample_spec)

        assert 'resource "aws_ssm_parameter" "log_level"' in params
        assert 'resource "aws_ssm_parameter" "timeout"' in params
        assert "/secret-service/log_level" in params
        assert "/secret-service/timeout" in params

    def test_generate_env_mapping(self, manager, sample_spec):
        """Test generating environment variable mappings."""
        env_vars = manager.generate_env_mapping(sample_spec)

        assert "API_KEY" in env_vars
        assert "DATABASE_PASSWORD" in env_vars
        assert "LOG_LEVEL" in env_vars
        assert "TIMEOUT" in env_vars

        assert env_vars["API_KEY"] == "${secrets:/secret-service/api_key}"
        assert env_vars["LOG_LEVEL"] == "${ssm:/secret-service/log_level}"


class TestEnvironmentManager:
    """Test EnvironmentManager functionality."""

    @pytest.fixture
    def manager(self):
        """Create EnvironmentManager instance."""
        return EnvironmentManager()

    @pytest.fixture
    def sample_spec(self):
        """Create sample infrastructure specification."""
        env = Environment(name="base", type="production", region="us-west-2")
        return InfrastructureSpec(
            service_name="test-service", provider=CloudProvider.AWS, environments=[env]
        )

    def test_create_ephemeral_env(self, manager, sample_spec):
        """Test creating ephemeral environment."""
        ephemeral_env = manager.create_ephemeral_env(sample_spec, pr_number=123)

        assert ephemeral_env.name == "pr-123"
        assert ephemeral_env.type == "ephemeral"
        assert ephemeral_env.region == "us-west-2"
        assert ephemeral_env.network.vpc_cidr == "10.100.0.0/16"
        assert ephemeral_env.compute.instance_type == "t3.micro"
        assert ephemeral_env.compute.spot_instances is True
        assert ephemeral_env.tags["PR"] == "123"
        assert ephemeral_env.tags["AutoDelete"] == "true"

    def test_setup_staging_pipeline(self, manager, sample_spec):
        """Test setting up staging pipeline."""
        pipeline = manager.setup_staging_pipeline(sample_spec)

        assert "name: Deploy to Staging" in pipeline
        assert "branches: [develop]" in pipeline
        assert "test-service-staging" in pipeline
        assert "aws ecs update-service" in pipeline
        assert "aws ecs wait services-stable" in pipeline

    def test_configure_production_pipeline(self, manager, sample_spec):
        """Test configuring production pipeline."""
        pipeline = manager.configure_production_pipeline(sample_spec)

        assert "name: Deploy to Production" in pipeline
        assert "types: [published]" in pipeline
        assert "environment:" in pipeline
        assert "name: production" in pipeline
        assert "./scripts/deploy-production.sh" in pipeline
        assert "./scripts/smoke-tests.sh" in pipeline


class TestInfrastructureAgent:
    """Test main InfrastructureAgent functionality."""

    @pytest.fixture
    def agent(self):
        """Create InfrastructureAgent instance."""
        return InfrastructureAgent()

    @pytest.fixture
    def sample_spec(self):
        """Create sample infrastructure specification."""
        env1 = Environment(
            name="staging", type="staging", region="us-east-1", database=DatabaseConfig()
        )
        env2 = Environment(
            name="production",
            type="production",
            region="us-east-1",
            database=DatabaseConfig(instance_class="db.r5.large"),
        )

        return InfrastructureSpec(
            service_name="my-infrastructure-service",
            provider=CloudProvider.AWS,
            environments=[env1, env2],
            secrets=["api_key", "jwt_secret"],
            parameters={"log_level": "info", "timeout": "60"},
        )

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.name == "InfrastructureAgent"
        assert agent.terraform_gen is not None
        assert agent.cdk_gen is not None
        assert agent.secrets_mgr is not None
        assert agent.env_mgr is not None

    @pytest.mark.asyncio
    async def test_generate_infrastructure_terraform(self, agent, sample_spec, tmp_path):
        """Test generating infrastructure with Terraform."""
        output_dir = tmp_path / "terraform_output"
        output_dir.mkdir()

        files = await agent.generate_infrastructure(sample_spec, output_dir, IaCTool.TERRAFORM)

        assert len(files) > 0

        # Check that Terraform files were created
        terraform_files = [f for f in files.keys() if "terraform" in f]
        assert len(terraform_files) > 0

        # Check for main Terraform files
        file_names = [Path(f).name for f in files.keys()]
        assert "main.tf" in file_names
        assert "variables.tf" in file_names
        assert "outputs.tf" in file_names

    @pytest.mark.asyncio
    async def test_generate_infrastructure_cdk(self, agent, sample_spec, tmp_path):
        """Test generating infrastructure with CDK."""
        output_dir = tmp_path / "cdk_output"
        output_dir.mkdir()

        files = await agent.generate_infrastructure(sample_spec, output_dir, IaCTool.CDK)

        assert len(files) > 0

        # Check that CDK files were created
        cdk_files = [f for f in files.keys() if "cdk" in f]
        assert len(cdk_files) > 0

        # Check for CDK files
        file_names = [Path(f).name for f in files.keys()]
        assert "stack.py" in file_names
        assert "app.py" in file_names
        assert "cdk.json" in file_names

    @pytest.mark.asyncio
    async def test_create_environment(self, agent, sample_spec):
        """Test creating different environment types."""
        # Test ephemeral environment
        ephemeral = await agent.create_environment(sample_spec, "ephemeral", pr_number=456)
        assert ephemeral.name == "pr-456"
        assert ephemeral.type == "ephemeral"

        # Test staging environment
        staging = await agent.create_environment(sample_spec, "staging")
        assert staging.name == "staging"
        assert staging.type == "staging"

        # Test production environment
        production = await agent.create_environment(sample_spec, "production")
        assert production.name == "production"
        assert production.type == "production"
        assert production.compute.instance_type == "t3.large"

    @pytest.mark.asyncio
    async def test_create_environment_invalid_type(self, agent, sample_spec):
        """Test creating environment with invalid type."""
        with pytest.raises(ValueError, match="Unknown environment type"):
            await agent.create_environment(sample_spec, "invalid_type")

    @pytest.mark.asyncio
    async def test_execute_generate_infrastructure(self, agent, sample_spec, tmp_path):
        """Test execute method with generate_infrastructure intent."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        input_data = AgentInput(
            intent="generate_infrastructure",
            task_id="test-task",
            payload={
                "specification": sample_spec,
                "output_dir": str(output_dir),
                "tool": "terraform",
            },
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) >= 2

        # Check infrastructure artifact
        infra_artifact = next((a for a in output.artifacts if a.kind == "infrastructure"), None)
        assert infra_artifact is not None
        assert infra_artifact.metadata["service_name"] == "my-infrastructure-service"
        assert infra_artifact.metadata["provider"] == "aws"
        assert infra_artifact.metadata["tool"] == "terraform"

        # Check specification artifact
        spec_artifact = next((a for a in output.artifacts if a.kind == "specification"), None)
        assert spec_artifact is not None

        # Check metrics
        assert "files_generated" in output.metrics
        assert "environments_count" in output.metrics
        assert output.metrics["environments_count"] == 2
        assert output.metrics["provider"] == "aws"

    @pytest.mark.asyncio
    async def test_execute_create_environment(self, agent, sample_spec):
        """Test execute method with create_environment intent."""
        input_data = AgentInput(
            intent="create_environment",
            task_id="test-task",
            payload={"specification": sample_spec, "env_type": "staging"},
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) == 1

        env_artifact = output.artifacts[0]
        assert env_artifact.kind == "environment"
        assert env_artifact.metadata["name"] == "staging"
        assert env_artifact.metadata["type"] == "staging"

        assert "environment_name" in output.metrics
        assert output.metrics["environment_name"] == "staging"

    @pytest.mark.asyncio
    async def test_execute_deploy_infrastructure(self, agent, tmp_path):
        """Test execute method with deploy_infrastructure intent."""
        infra_path = tmp_path / "infrastructure"
        infra_path.mkdir()

        input_data = AgentInput(
            intent="deploy_infrastructure",
            task_id="test-task",
            payload={
                "infrastructure_path": str(infra_path),
                "environment": "staging",
                "dry_run": True,
            },
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.OK
        assert len(output.artifacts) == 1

        deployment_artifact = output.artifacts[0]
        assert deployment_artifact.kind == "deployment"
        assert deployment_artifact.metadata["environment"] == "staging"
        assert deployment_artifact.metadata["dry_run"] is True

        assert "deployment_status" in output.metrics
        assert output.metrics["deployment_status"] == "planned"
        assert output.metrics["dry_run"] is True

    @pytest.mark.asyncio
    async def test_execute_invalid_intent(self, agent):
        """Test execute method with invalid intent."""
        input_data = AgentInput(intent="invalid_intent", task_id="test-task", payload={})

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.FAIL
        assert "Unknown intent" in output.error

    @pytest.mark.asyncio
    async def test_execute_missing_parameters(self, agent):
        """Test execute method with missing required parameters."""
        input_data = AgentInput(
            intent="generate_infrastructure",
            task_id="test-task",
            payload={},  # Missing required parameters
        )

        output = await agent.execute(input_data)

        assert output.status == AgentStatus.FAIL
        assert "required" in output.error.lower()

    @pytest.mark.asyncio
    async def test_validate_success(self, agent, sample_spec, tmp_path):
        """Test validate method with successful output."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a successful output
        input_data = AgentInput(
            intent="generate_infrastructure",
            task_id="test-task",
            payload={
                "specification": sample_spec,
                "output_dir": str(output_dir),
                "tool": "terraform",
            },
        )

        output = await agent.execute(input_data)
        is_valid = await agent.validate(output)

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_failure(self, agent):
        """Test validate method with failed output."""
        failed_output = AgentOutput(
            task_id="test-task",
            status=AgentStatus.FAIL,
            error="Test error",
            artifacts=[],
            metrics={},
        )

        is_valid = await agent.validate(failed_output)
        assert is_valid is False

    def test_get_capabilities(self, agent):
        """Test get_capabilities method."""
        capabilities = agent.get_capabilities()

        assert capabilities["name"] == "InfrastructureAgent"
        assert capabilities["version"] == "1.0.0"
        assert "description" in capabilities

        # Check intents
        expected_intents = [
            "generate_infrastructure",
            "create_environment",
            "deploy_infrastructure",
        ]
        assert all(intent in capabilities["intents"] for intent in expected_intents)

        # Check inputs and outputs
        assert "inputs" in capabilities
        assert "outputs" in capabilities
        assert "features" in capabilities

        # Check supported providers and tools
        assert "supported_providers" in capabilities
        assert "supported_tools" in capabilities
        assert "aws" in capabilities["supported_providers"]
        assert "terraform" in capabilities["supported_tools"]


class TestInfrastructureIntegration:
    """Integration tests for infrastructure system."""

    @pytest.mark.asyncio
    async def test_end_to_end_infrastructure_generation(self, tmp_path):
        """Test complete infrastructure generation flow."""
        # Setup
        output_dir = tmp_path / "infrastructure_output"
        output_dir.mkdir()

        # Create comprehensive infrastructure specification
        staging_env = Environment(
            name="staging",
            type="staging",
            region="us-east-1",
            network=NetworkConfig(
                vpc_cidr="10.1.0.0/16",
                public_subnets=["10.1.1.0/24", "10.1.2.0/24"],
                private_subnets=["10.1.10.0/24", "10.1.11.0/24"],
            ),
            compute=ComputeConfig(
                instance_type="t3.small", min_instances=1, max_instances=3, desired_capacity=2
            ),
            database=DatabaseConfig(
                engine="postgres", instance_class="db.t3.micro", allocated_storage=20
            ),
            enable_monitoring=True,
            enable_logging=True,
        )

        production_env = Environment(
            name="production",
            type="production",
            region="us-west-2",
            network=NetworkConfig(vpc_cidr="10.2.0.0/16", enable_nat=True, enable_vpn=True),
            compute=ComputeConfig(
                instance_type="m5.large",
                min_instances=3,
                max_instances=20,
                desired_capacity=5,
                spot_instances=False,
            ),
            database=DatabaseConfig(
                engine="postgres",
                version="15.3",
                instance_class="db.r5.large",
                allocated_storage=100,
                multi_az=True,
                backup_retention=30,
            ),
        )

        spec = InfrastructureSpec(
            service_name="comprehensive-service",
            provider=CloudProvider.AWS,
            environments=[staging_env, production_env],
            secrets=["api_key", "jwt_secret", "database_password"],
            parameters={
                "log_level": "info",
                "max_connections": "100",
                "timeout": "30",
                "cache_ttl": "3600",
            },
        )

        # Initialize agent
        agent = InfrastructureAgent()

        # Generate infrastructure with Terraform
        terraform_files = await agent.generate_infrastructure(spec, output_dir, IaCTool.TERRAFORM)

        # Verify Terraform files
        assert len(terraform_files) >= 10  # Multiple files including modules

        terraform_dir = output_dir / "infrastructure" / "terraform"
        assert terraform_dir.exists()

        # Check main Terraform files
        main_tf = terraform_dir / "main.tf"
        assert main_tf.exists()
        main_content = main_tf.read_text()
        assert "comprehensive-service" in main_content
        assert "terraform {" in main_content
        assert 'module "vpc"' in main_content

        variables_tf = terraform_dir / "variables.tf"
        assert variables_tf.exists()
        variables_content = variables_tf.read_text()
        assert 'variable "service_name"' in variables_content
        assert "comprehensive-service" in variables_content

        # Check VPC module
        vpc_main = terraform_dir / "modules" / "vpc" / "main.tf"
        assert vpc_main.exists()
        vpc_content = vpc_main.read_text()
        assert 'resource "aws_vpc" "main"' in vpc_content
        assert 'resource "aws_subnet" "public"' in vpc_content

        # Check common infrastructure files
        secrets_file = output_dir / "infrastructure" / "secrets.yaml"
        assert secrets_file.exists()
        secrets_content = secrets_file.read_text()
        assert "comprehensive-service/api_key" in secrets_content
        assert "comprehensive-service/jwt_secret" in secrets_content

        parameters_file = output_dir / "infrastructure" / "parameters.tf"
        assert parameters_file.exists()
        params_content = parameters_file.read_text()
        assert "/comprehensive-service/log_level" in params_content
        assert "/comprehensive-service/timeout" in params_content

        env_mapping_file = output_dir / "infrastructure" / "env-mapping.json"
        assert env_mapping_file.exists()
        env_content = json.loads(env_mapping_file.read_text())
        assert "API_KEY" in env_content
        assert "LOG_LEVEL" in env_content

        # Check CI/CD pipelines
        workflows_dir = output_dir / ".github" / "workflows"
        assert workflows_dir.exists()

        staging_pipeline = workflows_dir / "deploy-staging.yml"
        assert staging_pipeline.exists()
        staging_content = staging_pipeline.read_text()
        assert "Deploy to Staging" in staging_content
        assert "comprehensive-service-staging" in staging_content

        production_pipeline = workflows_dir / "deploy-production.yml"
        assert production_pipeline.exists()
        prod_content = production_pipeline.read_text()
        assert "Deploy to Production" in prod_content
        assert "comprehensive-service.example.com" in prod_content

        # Test environment creation
        ephemeral_env = await agent.create_environment(spec, "ephemeral", pr_number=789)
        assert ephemeral_env.name == "pr-789"
        assert ephemeral_env.type == "ephemeral"
        assert ephemeral_env.compute.spot_instances is True
        assert ephemeral_env.tags["AutoDelete"] == "true"

        # Test agent execution
        input_data = AgentInput(
            intent="generate_infrastructure",
            task_id="integration-test",
            payload={
                "specification": spec,
                "output_dir": str(output_dir / "agent_output"),
                "tool": "cdk",
            },
        )

        output = await agent.execute(input_data)
        assert output.status == AgentStatus.OK
        assert len(output.artifacts) >= 2
        assert output.metrics["environments_count"] == 2
        assert output.metrics["secrets_count"] == 3
        assert output.metrics["parameters_count"] == 4

        # Verify agent output validation
        is_valid = await agent.validate(output)
        assert is_valid is True

        # Test capabilities
        capabilities = agent.get_capabilities()
        assert len(capabilities["features"]) >= 10
        assert "Terraform code generation" in capabilities["features"]
        assert "Multi-environment management" in capabilities["features"]
