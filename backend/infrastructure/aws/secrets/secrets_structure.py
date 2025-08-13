"""
Secrets Manager Structure and Configuration
T-Developer Evolution System
"""

import json
import os
from typing import Any, Dict

# Secrets structure definition
secrets_structure = {
    "/t-developer/dev/api-keys/openai": {
        "type": "SecureString",
        "description": "OpenAI API Key for development environment",
        "value": {
            "api_key": os.environ.get(
                "OPENAI_API_KEY", "sk-proj-xxx"
            ),  # Will be replaced with actual key
            "organization_id": os.environ.get("OPENAI_ORG_ID", "org-xxx"),
            "project_id": os.environ.get("OPENAI_PROJECT_ID", "proj-xxx"),
        },
        "kms_key": "alias/t-developer-dev",
        "tags": {"Environment": "Development", "Service": "AI", "Provider": "OpenAI"},
    },
    "/t-developer/dev/api-keys/anthropic": {
        "type": "SecureString",
        "description": "Anthropic Claude API Key for development environment",
        "value": {
            "api_key": os.environ.get(
                "ANTHROPIC_API_KEY", "sk-ant-xxx"
            ),  # Will be replaced with actual key
            "model_access": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
        },
        "kms_key": "alias/t-developer-dev",
        "tags": {
            "Environment": "Development",
            "Service": "AI",
            "Provider": "Anthropic",
        },
    },
    "/t-developer/dev/api-keys/aws-bedrock": {
        "type": "SecureString",
        "description": "AWS Bedrock configuration",
        "value": {
            "region": "us-east-1",
            "model_ids": [
                "anthropic.claude-3-opus-20240229-v1:0",
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "amazon.titan-text-express-v1",
            ],
            "default_model": "anthropic.claude-3-opus-20240229-v1:0",
        },
        "kms_key": "alias/t-developer-dev",
        "tags": {"Environment": "Development", "Service": "AI", "Provider": "AWS"},
    },
    "/t-developer/dev/db/connection": {
        "type": "SecureString",
        "description": "PostgreSQL RDS connection details",
        "value": {
            "host": "t-developer-dev.cluster-xxx.us-east-1.rds.amazonaws.com",
            "port": 5432,
            "database": "t_developer",
            "username": "postgres",
            "password": os.environ.get("DB_PASSWORD", "ENCRYPTED_PASSWORD"),  # Will be encrypted
            "ssl_mode": "require",
            "connection_pool": {"min_size": 5, "max_size": 20},
        },
        "kms_key": "alias/t-developer-dev",
        "tags": {
            "Environment": "Development",
            "Service": "Database",
            "Type": "PostgreSQL",
        },
    },
    "/t-developer/dev/redis/connection": {
        "type": "SecureString",
        "description": "Redis ElastiCache connection details",
        "value": {
            "primary_endpoint": "t-developer-dev-cache.xxx.cache.amazonaws.com",
            "reader_endpoint": "t-developer-dev-cache-ro.xxx.cache.amazonaws.com",
            "port": 6379,
            "auth_token": os.environ.get("REDIS_AUTH_TOKEN", ""),
            "ssl_enabled": True,
            "cluster_mode": True,
        },
        "kms_key": "alias/t-developer-dev",
        "tags": {"Environment": "Development", "Service": "Cache", "Type": "Redis"},
    },
    "/t-developer/dev/github/token": {
        "type": "SecureString",
        "description": "GitHub personal access token for CI/CD",
        "value": {
            "token": os.environ.get("GITHUB_TOKEN", "ghp_xxx"),
            "username": "t-developer-bot",
            "permissions": ["repo", "workflow", "packages"],
        },
        "kms_key": "alias/t-developer-dev",
        "tags": {"Environment": "Development", "Service": "VCS", "Provider": "GitHub"},
    },
    "/t-developer/dev/monitoring/datadog": {
        "type": "SecureString",
        "description": "Datadog API keys for monitoring",
        "value": {
            "api_key": os.environ.get("DATADOG_API_KEY", ""),
            "app_key": os.environ.get("DATADOG_APP_KEY", ""),
            "site": "datadoghq.com",
        },
        "kms_key": "alias/t-developer-dev",
        "tags": {
            "Environment": "Development",
            "Service": "Monitoring",
            "Provider": "Datadog",
        },
    },
}

# Staging environment secrets (similar structure, different values)
staging_secrets = {
    key.replace("/dev/", "/staging/"): {
        **value,
        "tags": {**value.get("tags", {}), "Environment": "Staging"},
    }
    for key, value in secrets_structure.items()
}

# Production environment secrets (enhanced security)
production_secrets = {
    key.replace("/dev/", "/prod/"): {
        **value,
        "kms_key": "alias/t-developer-prod",  # Different KMS key for production
        "rotation_enabled": True,
        "rotation_schedule": "rate(30 days)",
        "tags": {**value.get("tags", {}), "Environment": "Production"},
    }
    for key, value in secrets_structure.items()
}


def get_all_secrets() -> Dict[str, Any]:
    """Get all secrets for all environments"""
    return {**secrets_structure, **staging_secrets, **production_secrets}


def validate_secret_structure(secret: Dict[str, Any]) -> bool:
    """Validate secret structure"""
    required_fields = ["type", "value", "kms_key"]
    return all(field in secret for field in required_fields)


def export_for_terraform() -> str:
    """Export secrets structure for Terraform"""
    terraform_secrets = {}
    for key, value in get_all_secrets().items():
        terraform_key = key.replace("/", "_").replace("-", "_")[1:]
        terraform_secrets[terraform_key] = {
            "secret_id": key,
            "secret_string": json.dumps(value.get("value", {})),
            "kms_key_id": value.get("kms_key"),
            "tags": value.get("tags", {}),
        }
    return json.dumps(terraform_secrets, indent=2)


if __name__ == "__main__":
    # Validate all secrets
    all_secrets = get_all_secrets()
    print(f"Total secrets configured: {len(all_secrets)}")

    for secret_id, secret_config in all_secrets.items():
        if validate_secret_structure(secret_config):
            print(f"✓ {secret_id}: Valid")
        else:
            print(f"✗ {secret_id}: Invalid structure")

    # Export for Terraform
    with open("secrets_terraform.json", "w") as f:
        f.write(export_for_terraform())
    print("\nTerraform configuration exported to secrets_terraform.json")
