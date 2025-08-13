"""
AWS Secrets Manager and Parameter Store integration
Securely loads API keys and configuration from AWS services
"""
import json
import logging
import os
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AWSSecretsManager:
    """Manages secrets from AWS Secrets Manager and Parameter Store"""

    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.secrets_client = boto3.client("secretsmanager", region_name=region)
        self.ssm_client = boto3.client("ssm", region_name=region)
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.secrets_cache = {}
        self.parameters_cache = {}

    def get_secret(self, secret_name: str) -> Optional[Dict[str, Any]]:
        """Get secret from AWS Secrets Manager"""

        # Check cache
        if secret_name in self.secrets_cache:
            return self.secrets_cache[secret_name]

        # Full secret name with environment
        full_secret_name = f"t-developer/{self.environment}/{secret_name}"

        try:
            response = self.secrets_client.get_secret_value(SecretId=full_secret_name)

            # Parse secret string
            if "SecretString" in response:
                secret = json.loads(response["SecretString"])
                self.secrets_cache[secret_name] = secret
                logger.info(f"✅ Loaded secret: {secret_name}")
                return secret
            else:
                # Binary secret
                return {"binary": response["SecretBinary"]}

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                logger.warning(f"Secret not found: {full_secret_name}")
            else:
                logger.error(f"Error retrieving secret {full_secret_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving secret: {e}")
            return None

    def get_parameter(self, parameter_name: str, decrypt: bool = True) -> Optional[str]:
        """Get parameter from AWS Systems Manager Parameter Store"""

        # Check cache
        if parameter_name in self.parameters_cache:
            return self.parameters_cache[parameter_name]

        # Full parameter name with environment
        full_parameter_name = f"/t-developer/{self.environment}/{parameter_name}"

        try:
            response = self.ssm_client.get_parameter(
                Name=full_parameter_name, WithDecryption=decrypt
            )

            value = response["Parameter"]["Value"]
            self.parameters_cache[parameter_name] = value
            logger.info(f"✅ Loaded parameter: {parameter_name}")
            return value

        except ClientError as e:
            if e.response["Error"]["Code"] == "ParameterNotFound":
                logger.warning(f"Parameter not found: {full_parameter_name}")
            else:
                logger.error(f"Error retrieving parameter {full_parameter_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving parameter: {e}")
            return None

    def get_parameters_by_path(self, path: str, decrypt: bool = True) -> Dict[str, str]:
        """Get all parameters under a path"""

        full_path = f"/t-developer/{self.environment}/{path}"
        parameters = {}

        try:
            paginator = self.ssm_client.get_paginator("get_parameters_by_path")
            pages = paginator.paginate(Path=full_path, Recursive=True, WithDecryption=decrypt)

            for page in pages:
                for parameter in page["Parameters"]:
                    # Extract parameter name without path
                    name = parameter["Name"].replace(full_path + "/", "")
                    parameters[name] = parameter["Value"]

            logger.info(f"✅ Loaded {len(parameters)} parameters from path: {path}")
            return parameters

        except Exception as e:
            logger.error(f"Error retrieving parameters by path {full_path}: {e}")
            return {}

    def set_parameter(self, parameter_name: str, value: str, secure: bool = True) -> bool:
        """Set parameter in Parameter Store"""

        full_parameter_name = f"/t-developer/{self.environment}/{parameter_name}"

        try:
            self.ssm_client.put_parameter(
                Name=full_parameter_name,
                Value=value,
                Type="SecureString" if secure else "String",
                Overwrite=True,
            )

            # Update cache
            self.parameters_cache[parameter_name] = value
            logger.info(f"✅ Set parameter: {parameter_name}")
            return True

        except Exception as e:
            logger.error(f"Error setting parameter {full_parameter_name}: {e}")
            return False

    def set_secret(self, secret_name: str, secret_value: Dict[str, Any]) -> bool:
        """Set secret in Secrets Manager"""

        full_secret_name = f"t-developer/{self.environment}/{secret_name}"

        try:
            # Try to update existing secret
            try:
                self.secrets_client.update_secret(
                    SecretId=full_secret_name, SecretString=json.dumps(secret_value)
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    # Create new secret
                    self.secrets_client.create_secret(
                        Name=full_secret_name, SecretString=json.dumps(secret_value)
                    )
                else:
                    raise e

            # Update cache
            self.secrets_cache[secret_name] = secret_value
            logger.info(f"✅ Set secret: {secret_name}")
            return True

        except Exception as e:
            logger.error(f"Error setting secret {full_secret_name}: {e}")
            return False

    def load_ai_credentials(self) -> Dict[str, Any]:
        """Load all AI provider credentials"""

        credentials = {}

        # Load from Secrets Manager (sensitive data)
        ai_secrets = self.get_secret("ai-credentials")
        if ai_secrets:
            credentials.update(ai_secrets)

        # Individual API keys from Secrets Manager
        openai_key = self.get_secret("openai-api-key")
        if openai_key and isinstance(openai_key, dict):
            credentials["OPENAI_API_KEY"] = openai_key.get("api_key")

        anthropic_key = self.get_secret("anthropic-api-key")
        if anthropic_key and isinstance(anthropic_key, dict):
            credentials["ANTHROPIC_API_KEY"] = anthropic_key.get("api_key")

        # Load from Parameter Store (configuration)
        ai_config = self.get_parameters_by_path("ai-config")
        credentials.update(ai_config)

        # Individual parameters
        params = [
            "openai_model",
            "anthropic_model",
            "bedrock_model_id",
            "ai_provider",
            "ai_temperature",
            "ai_max_tokens",
        ]

        for param in params:
            value = self.get_parameter(param)
            if value:
                credentials[param.upper()] = value

        return credentials

    def initialize_environment(self) -> Dict[str, str]:
        """Initialize environment variables from AWS"""

        env_vars = {}

        # Load AI credentials
        ai_creds = self.load_ai_credentials()
        for key, value in ai_creds.items():
            if value:
                os.environ[key] = str(value)
                env_vars[key] = str(value)

        # Load general configuration from Parameter Store
        config_params = self.get_parameters_by_path("config")
        for key, value in config_params.items():
            env_key = key.upper().replace("-", "_")
            os.environ[env_key] = value
            env_vars[env_key] = value

        logger.info(f"✅ Loaded {len(env_vars)} environment variables from AWS")
        return env_vars


# Global instance
aws_secrets = AWSSecretsManager()

# Initialize on import
try:
    aws_secrets.initialize_environment()
    logger.info("AWS Secrets Manager initialized and environment loaded")
except Exception as e:
    logger.warning(f"Failed to initialize AWS Secrets Manager: {e}")
