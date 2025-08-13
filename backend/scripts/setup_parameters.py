#!/usr/bin/env python3
"""
Setup AWS Systems Manager Parameter Store parameters for T-Developer
This script creates all necessary configuration parameters
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List

import boto3

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ParameterStoreManager:
    """Manage AWS Systems Manager Parameter Store operations"""

    def __init__(self, region: str = "us-east-1", environment: str = "dev"):
        self.region = region
        self.environment = environment
        self.ssm_client = boto3.client("ssm", region_name=region)

    def get_parameters_config(self) -> List[Dict[str, Any]]:
        """Get all parameters configuration for the environment"""

        base_path = f"/t-developer/{self.environment}"

        parameters = [
            # Agent Configuration
            {
                "Name": f"{base_path}/config/max_agents",
                "Value": "100",
                "Type": "String",
                "Description": "Maximum number of agents allowed in the system",
            },
            {
                "Name": f"{base_path}/config/agent_timeout",
                "Value": "300",
                "Type": "String",
                "Description": "Default agent execution timeout in seconds",
            },
            {
                "Name": f"{base_path}/config/agent_retry_count",
                "Value": "3",
                "Type": "String",
                "Description": "Default number of retries for failed agent executions",
            },
            # Evolution Configuration
            {
                "Name": f"{base_path}/config/evolution/enabled",
                "Value": "true",
                "Type": "String",
                "Description": "Enable/disable evolution engine",
            },
            {
                "Name": f"{base_path}/config/evolution/population_size",
                "Value": "50",
                "Type": "String",
                "Description": "Population size for genetic algorithm",
            },
            {
                "Name": f"{base_path}/config/evolution/mutation_rate",
                "Value": "0.1",
                "Type": "String",
                "Description": "Mutation rate for genetic algorithm (0.0-1.0)",
            },
            {
                "Name": f"{base_path}/config/evolution/crossover_rate",
                "Value": "0.7",
                "Type": "String",
                "Description": "Crossover rate for genetic algorithm (0.0-1.0)",
            },
            {
                "Name": f"{base_path}/config/evolution/elite_size",
                "Value": "5",
                "Type": "String",
                "Description": "Number of elite individuals to preserve",
            },
            {
                "Name": f"{base_path}/config/evolution/generation_interval",
                "Value": "3600",
                "Type": "String",
                "Description": "Time between evolution generations in seconds",
            },
            # AI Configuration - GPT-4
            {
                "Name": f"{base_path}/config/ai/gpt4_model",
                "Value": "gpt-4-turbo-preview",
                "Type": "String",
                "Description": "GPT-4 model identifier",
            },
            {
                "Name": f"{base_path}/config/ai/gpt4_temperature",
                "Value": "0.3",
                "Type": "String",
                "Description": "GPT-4 temperature setting (0.0-2.0)",
            },
            {
                "Name": f"{base_path}/config/ai/gpt4_max_tokens",
                "Value": "4096",
                "Type": "String",
                "Description": "Maximum tokens for GPT-4 responses",
            },
            {
                "Name": f"{base_path}/config/ai/gpt4_timeout",
                "Value": "60",
                "Type": "String",
                "Description": "GPT-4 API timeout in seconds",
            },
            # AI Configuration - Claude
            {
                "Name": f"{base_path}/config/ai/claude_model",
                "Value": "claude-3-opus-20240229",
                "Type": "String",
                "Description": "Claude model identifier",
            },
            {
                "Name": f"{base_path}/config/ai/claude_temperature",
                "Value": "0.2",
                "Type": "String",
                "Description": "Claude temperature setting (0.0-1.0)",
            },
            {
                "Name": f"{base_path}/config/ai/claude_max_tokens",
                "Value": "4096",
                "Type": "String",
                "Description": "Maximum tokens for Claude responses",
            },
            {
                "Name": f"{base_path}/config/ai/claude_timeout",
                "Value": "60",
                "Type": "String",
                "Description": "Claude API timeout in seconds",
            },
            # Workflow Configuration
            {
                "Name": f"{base_path}/config/workflow/max_nodes",
                "Value": "50",
                "Type": "String",
                "Description": "Maximum nodes allowed in a workflow",
            },
            {
                "Name": f"{base_path}/config/workflow/max_depth",
                "Value": "10",
                "Type": "String",
                "Description": "Maximum depth of workflow DAG",
            },
            {
                "Name": f"{base_path}/config/workflow/parallel_execution",
                "Value": "true",
                "Type": "String",
                "Description": "Enable parallel execution of workflow nodes",
            },
            {
                "Name": f"{base_path}/config/workflow/max_parallel_tasks",
                "Value": "10",
                "Type": "String",
                "Description": "Maximum number of parallel tasks",
            },
            # Database Configuration
            {
                "Name": f"{base_path}/db/endpoint",
                "Value": f"t-developer-{self.environment}.cluster-xxx.us-east-1.rds.amazonaws.com",
                "Type": "String",
                "Description": "RDS cluster endpoint",
            },
            {
                "Name": f"{base_path}/db/port",
                "Value": "5432",
                "Type": "String",
                "Description": "Database port",
            },
            {
                "Name": f"{base_path}/db/name",
                "Value": "t_developer",
                "Type": "String",
                "Description": "Database name",
            },
            {
                "Name": f"{base_path}/db/pool_size",
                "Value": "20",
                "Type": "String",
                "Description": "Database connection pool size",
            },
            # Redis Configuration
            {
                "Name": f"{base_path}/redis/endpoint",
                "Value": f"t-developer-{self.environment}-cache.xxx.cache.amazonaws.com",
                "Type": "String",
                "Description": "Redis primary endpoint",
            },
            {
                "Name": f"{base_path}/redis/port",
                "Value": "6379",
                "Type": "String",
                "Description": "Redis port",
            },
            {
                "Name": f"{base_path}/redis/ttl",
                "Value": "3600",
                "Type": "String",
                "Description": "Default cache TTL in seconds",
            },
            # S3 Configuration
            {
                "Name": f"{base_path}/s3/bucket",
                "Value": f"t-developer-{self.environment}-data",
                "Type": "String",
                "Description": "Primary S3 bucket for data storage",
            },
            {
                "Name": f"{base_path}/s3/logs_bucket",
                "Value": f"t-developer-{self.environment}-logs",
                "Type": "String",
                "Description": "S3 bucket for logs storage",
            },
            # Monitoring Configuration
            {
                "Name": f"{base_path}/monitoring/enabled",
                "Value": "true",
                "Type": "String",
                "Description": "Enable monitoring and metrics collection",
            },
            {
                "Name": f"{base_path}/monitoring/metrics_interval",
                "Value": "60",
                "Type": "String",
                "Description": "Metrics collection interval in seconds",
            },
            {
                "Name": f"{base_path}/monitoring/log_level",
                "Value": "INFO",
                "Type": "String",
                "Description": "Logging level (DEBUG, INFO, WARNING, ERROR)",
            },
            # Security Configuration
            {
                "Name": f"{base_path}/security/encryption_enabled",
                "Value": "true",
                "Type": "String",
                "Description": "Enable encryption for sensitive data",
            },
            {
                "Name": f"{base_path}/security/audit_enabled",
                "Value": "true",
                "Type": "String",
                "Description": "Enable audit logging",
            },
            {
                "Name": f"{base_path}/security/session_timeout",
                "Value": "3600",
                "Type": "String",
                "Description": "Session timeout in seconds",
            },
            # Rate Limiting
            {
                "Name": f"{base_path}/ratelimit/enabled",
                "Value": "true",
                "Type": "String",
                "Description": "Enable rate limiting",
            },
            {
                "Name": f"{base_path}/ratelimit/requests_per_minute",
                "Value": "100",
                "Type": "String",
                "Description": "Maximum requests per minute per user",
            },
            {
                "Name": f"{base_path}/ratelimit/burst_size",
                "Value": "20",
                "Type": "String",
                "Description": "Burst size for rate limiting",
            },
        ]

        # Add environment-specific tags
        for param in parameters:
            param["Tags"] = [
                {"Key": "Project", "Value": "TDeveloper"},
                {"Key": "Environment", "Value": self.environment},
                {"Key": "ManagedBy", "Value": "Automation"},
                {"Key": "CreatedAt", "Value": datetime.now().isoformat()},
            ]

        return parameters

    def create_or_update_parameter(self, param_config: Dict[str, Any]) -> bool:
        """Create or update a parameter in Parameter Store"""
        try:
            # Extract tags for separate API call
            tags = param_config.pop("Tags", [])

            # Try to put parameter (will create or update)
            response = self.ssm_client.put_parameter(
                **param_config, Overwrite=True, Tier="Standard"
            )

            # Add tags if provided
            if tags:
                self.ssm_client.add_tags_to_resource(
                    ResourceType="Parameter", ResourceId=param_config["Name"], Tags=tags
                )

            logger.info(f"✓ Created/Updated parameter: {param_config['Name']}")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to create/update parameter {param_config['Name']}: {e}")
            return False

    def setup_all_parameters(self) -> Dict[str, bool]:
        """Setup all parameters for the environment"""
        parameters = self.get_parameters_config()
        results = {}

        for param in parameters:
            # Make a copy to avoid modifying the original
            param_copy = param.copy()
            results[param["Name"]] = self.create_or_update_parameter(param_copy)

        return results

    def verify_parameters(self) -> Dict[str, bool]:
        """Verify that all parameters are accessible"""
        parameters = self.get_parameters_config()
        results = {}

        for param in parameters:
            try:
                response = self.ssm_client.get_parameter(Name=param["Name"], WithDecryption=True)
                results[param["Name"]] = True
                logger.info(
                    f"✓ Verified parameter: {param['Name']} = {response['Parameter']['Value']}"
                )
            except Exception as e:
                results[param["Name"]] = False
                logger.error(f"✗ Failed to verify parameter {param['Name']}: {e}")

        return results

    def export_parameters(self, format: str = "env") -> str:
        """Export parameters in different formats"""
        parameters = self.get_parameters_config()

        if format == "env":
            # Export as environment variables
            lines = []
            for param in parameters:
                env_name = param["Name"].replace("/t-developer/", "").replace("/", "_").upper()
                lines.append(f"export {env_name}={param['Value']}")
            return "\n".join(lines)

        elif format == "json":
            # Export as JSON
            params_dict = {param["Name"]: param["Value"] for param in parameters}
            return json.dumps(params_dict, indent=2)

        elif format == "terraform":
            # Export for Terraform
            tf_params = {}
            for param in parameters:
                tf_key = param["Name"].replace("/", "_").replace("-", "_")[1:]
                tf_params[tf_key] = {
                    "name": param["Name"],
                    "value": param["Value"],
                    "type": param["Type"],
                    "description": param.get("Description", ""),
                }
            return json.dumps(tf_params, indent=2)

        else:
            raise ValueError(f"Unknown export format: {format}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup AWS Parameter Store parameters")
    parser.add_argument(
        "--environment",
        "-e",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment to setup parameters for",
    )
    parser.add_argument("--region", "-r", default="us-east-1", help="AWS region")
    parser.add_argument(
        "--verify-only",
        "-v",
        action="store_true",
        help="Only verify existing parameters",
    )
    parser.add_argument(
        "--export",
        "-x",
        choices=["env", "json", "terraform"],
        help="Export parameters in specified format",
    )

    args = parser.parse_args()

    # Initialize ParameterStoreManager
    psm = ParameterStoreManager(region=args.region, environment=args.environment)

    if args.export:
        # Export parameters
        output = psm.export_parameters(format=args.export)
        print(output)

        # Save to file
        filename = f"parameters-{args.environment}.{args.export}"
        with open(filename, "w") as f:
            f.write(output)
        logger.info(f"Parameters exported to {filename}")

    elif args.verify_only:
        # Verify parameters
        logger.info(f"Verifying parameters in {args.environment} environment...")
        results = psm.verify_parameters()
    else:
        # Setup parameters
        logger.info(f"Setting up parameters for {args.environment} environment in {args.region}...")
        results = psm.setup_all_parameters()

    if not args.export:
        # Summary
        successful = sum(1 for v in results.values() if v)
        failed = len(results) - successful

        logger.info(f"\n{'='*50}")
        logger.info(f"Summary: {successful} successful, {failed} failed")

        if failed > 0:
            logger.error("Some parameters failed to create/update")
            sys.exit(1)
        else:
            logger.info("All parameters successfully created/updated")

            # Save results to log file
            log_file = f"parameters-created-{args.environment}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
            with open(log_file, "w") as f:
                json.dump(
                    {
                        "environment": args.environment,
                        "region": args.region,
                        "timestamp": datetime.now().isoformat(),
                        "results": results,
                    },
                    f,
                    indent=2,
                )

            logger.info(f"Results saved to {log_file}")


if __name__ == "__main__":
    main()
