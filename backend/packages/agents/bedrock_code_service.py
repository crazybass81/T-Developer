"""AWS Bedrock for code modification."""

import json
import logging
from pathlib import Path
from typing import Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BedrockCodeService:
    """Use AWS Bedrock for code modification."""

    def __init__(self):
        """Initialize Bedrock client."""
        try:
            self.bedrock_runtime = boto3.client(
                service_name="bedrock-runtime", region_name="us-east-1"
            )
            self.available = True
            logger.info("Bedrock client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock: {e}")
            self.available = False

    async def modify_code_with_claude(self, code: str, instruction: str) -> Optional[str]:
        """Use Claude on Bedrock to modify code."""
        if not self.available:
            return None

        try:
            # Call Bedrock Claude model
            body = json.dumps(
                {
                    "prompt": f"\n\nHuman: {instruction}\n\n{code}\n\nAssistant:",
                    "max_tokens_to_sample": 2000,
                    "temperature": 0.2,
                }
            )

            response = self.bedrock_runtime.invoke_model(
                body=body,
                modelId="anthropic.claude-v2",
                accept="application/json",
                contentType="application/json",
            )

            response_body = json.loads(response.get("body").read())
            return response_body.get("completion")

        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
        except Exception as e:
            logger.error(f"Bedrock error: {e}")

        return None

    async def modify_code_with_codewhisperer(self, code: str) -> Optional[str]:
        """Use CodeWhisperer for code improvements."""
        # CodeWhisperer is IDE-integrated, not API-based
        # This is a placeholder for future implementation
        logger.info("CodeWhisperer requires IDE integration")
        return None


async def apply_bedrock_service(file_path: str) -> dict[str, Any]:
    """Apply Bedrock service to improve code."""

    results = {"success": False, "services_applied": [], "improvements": []}

    service = BedrockCodeService()

    if not service.available:
        logger.warning("Bedrock service not available")
        return results

    try:
        # Read file
        code = Path(file_path).read_text()

        # Try to improve with Claude on Bedrock
        improved_code = await service.modify_code_with_claude(
            code, "Add comprehensive docstrings and type hints to all functions and classes"
        )

        if improved_code:
            # Save improved code
            Path(file_path).write_text(improved_code)
            results["success"] = True
            results["services_applied"].append("AWS Bedrock Claude")
            results["improvements"].append("Added docstrings and type hints via Bedrock")
            logger.info(f"Successfully improved {file_path} with Bedrock")

    except Exception as e:
        logger.error(f"Bedrock service error: {e}")

    return results
