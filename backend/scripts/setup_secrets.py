#!/usr/bin/env python3
"""
Setup AWS Secrets Manager secrets for T-Developer
This script creates all necessary secrets in AWS Secrets Manager
"""

import boto3
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecretsManager:
    """Manage AWS Secrets Manager operations"""

    def __init__(self, region: str = "us-east-1", environment: str = "dev"):
        self.region = region
        self.environment = environment
        self.sm_client = boto3.client("secretsmanager", region_name=region)
        self.kms_client = boto3.client("kms", region_name=region)

    def create_kms_key_if_not_exists(self, alias: str) -> Optional[str]:
        """Create KMS key if it doesn't exist"""
        try:
            # Check if alias exists
            response = self.kms_client.describe_key(KeyId=alias)
            logger.info(f"KMS key {alias} already exists")
            return response["KeyMetadata"]["KeyId"]
        except self.kms_client.exceptions.NotFoundException:
            # Create new KMS key
            logger.info(f"Creating new KMS key with alias {alias}")
            response = self.kms_client.create_key(
                Description=f"T-Developer {self.environment} encryption key",
                KeyUsage="ENCRYPT_DECRYPT",
                Origin="AWS_KMS",
                Tags=[
                    {"TagKey": "Project", "TagValue": "TDeveloper"},
                    {"TagKey": "Environment", "TagValue": self.environment},
                ],
            )

            key_id = response["KeyMetadata"]["KeyId"]

            # Create alias
            self.kms_client.create_alias(AliasName=alias, TargetKeyId=key_id)

            logger.info(f"Created KMS key {key_id} with alias {alias}")
            return key_id
        except Exception as e:
            logger.error(f"Error managing KMS key: {e}")
            return None

    def create_or_update_secret(
        self, secret_id: str, secret_data: Dict[str, Any]
    ) -> bool:
        """Create or update a secret in AWS Secrets Manager"""
        try:
            # Prepare secret value
            secret_value = json.dumps(secret_data.get("value", {}))
            kms_key = secret_data.get(
                "kms_key", f"alias/t-developer-{self.environment}"
            )
            tags = [
                {"Key": k, "Value": v} for k, v in secret_data.get("tags", {}).items()
            ]

            # Ensure KMS key exists
            self.create_kms_key_if_not_exists(kms_key)

            try:
                # Try to create the secret
                response = self.sm_client.create_secret(
                    Name=secret_id,
                    Description=secret_data.get("description", ""),
                    SecretString=secret_value,
                    KmsKeyId=kms_key,
                    Tags=tags,
                )
                logger.info(f"✓ Created secret: {secret_id}")
                return True

            except self.sm_client.exceptions.ResourceExistsException:
                # Secret exists, update it
                response = self.sm_client.update_secret(
                    SecretId=secret_id,
                    Description=secret_data.get("description", ""),
                    SecretString=secret_value,
                    KmsKeyId=kms_key,
                )

                # Update tags separately
                if tags:
                    self.sm_client.tag_resource(SecretId=secret_id, Tags=tags)

                logger.info(f"✓ Updated secret: {secret_id}")
                return True

        except Exception as e:
            logger.error(f"✗ Failed to create/update secret {secret_id}: {e}")
            return False

    def setup_all_secrets(self) -> Dict[str, bool]:
        """Setup all secrets for the environment"""
        # Import secrets structure
        sys.path.insert(
            0,
            os.path.join(
                os.path.dirname(__file__), "..", "infrastructure", "aws", "secrets"
            ),
        )
        from secrets_structure import (
            secrets_structure,
            staging_secrets,
            production_secrets,
        )

        # Select secrets based on environment
        if self.environment == "dev":
            secrets = secrets_structure
        elif self.environment == "staging":
            secrets = staging_secrets
        elif self.environment == "prod":
            secrets = production_secrets
        else:
            logger.error(f"Unknown environment: {self.environment}")
            return {}

        results = {}

        # Create/update each secret
        for secret_id, secret_data in secrets.items():
            # Get actual values from environment variables or use defaults
            if "api-keys/openai" in secret_id:
                secret_data["value"]["api_key"] = os.environ.get(
                    "OPENAI_API_KEY", "sk-proj-xxx"
                )
            elif "api-keys/anthropic" in secret_id:
                secret_data["value"]["api_key"] = os.environ.get(
                    "ANTHROPIC_API_KEY", "sk-ant-xxx"
                )
            elif "db/connection" in secret_id:
                secret_data["value"]["password"] = os.environ.get(
                    "DB_PASSWORD", "changeme"
                )
            elif "github/token" in secret_id:
                secret_data["value"]["token"] = os.environ.get(
                    "GITHUB_TOKEN", "ghp_xxx"
                )

            results[secret_id] = self.create_or_update_secret(secret_id, secret_data)

        return results

    def verify_secrets(self) -> Dict[str, bool]:
        """Verify that all secrets are accessible"""
        sys.path.insert(
            0,
            os.path.join(
                os.path.dirname(__file__), "..", "infrastructure", "aws", "secrets"
            ),
        )
        from secrets_structure import secrets_structure

        results = {}

        for secret_id in secrets_structure.keys():
            try:
                response = self.sm_client.get_secret_value(SecretId=secret_id)
                results[secret_id] = True
                logger.info(f"✓ Verified secret: {secret_id}")
            except Exception as e:
                results[secret_id] = False
                logger.error(f"✗ Failed to verify secret {secret_id}: {e}")

        return results


def main():
    """Main execution function"""
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Setup AWS Secrets Manager secrets")
    parser.add_argument(
        "--environment",
        "-e",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment to setup secrets for",
    )
    parser.add_argument("--region", "-r", default="us-east-1", help="AWS region")
    parser.add_argument(
        "--verify-only", "-v", action="store_true", help="Only verify existing secrets"
    )

    args = parser.parse_args()

    # Initialize SecretsManager
    sm = SecretsManager(region=args.region, environment=args.environment)

    if args.verify_only:
        # Verify secrets
        logger.info(f"Verifying secrets in {args.environment} environment...")
        results = sm.verify_secrets()
    else:
        # Setup secrets
        logger.info(
            f"Setting up secrets for {args.environment} environment in {args.region}..."
        )
        results = sm.setup_all_secrets()

    # Summary
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful

    logger.info(f"\n{'='*50}")
    logger.info(f"Summary: {successful} successful, {failed} failed")

    if failed > 0:
        logger.error("Some secrets failed to create/update")
        sys.exit(1)
    else:
        logger.info("All secrets successfully created/updated")

        # Save results to log file
        log_file = f"secrets-created-{args.environment}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
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
