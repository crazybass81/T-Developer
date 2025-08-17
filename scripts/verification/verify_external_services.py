#!/usr/bin/env python3
"""
Verify external services integration for T-Developer v2.
Checks AWS Bedrock, formatting tools, and other external dependencies.
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add backend to path
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExternalServiceVerifier:
    """Verifies external service integrations."""

    def __init__(self):
        self.results = {}

    def check_aws_credentials(self) -> dict[str, Any]:
        """Check AWS credentials configuration."""
        result = {"configured": False, "credentials": {}, "issues": []}

        # Check environment variables
        aws_keys = {
            "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
            "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        }

        # Check if all required keys are present
        if aws_keys["AWS_ACCESS_KEY_ID"] and aws_keys["AWS_SECRET_ACCESS_KEY"]:
            result["configured"] = True
            result["credentials"] = {
                "access_key": aws_keys["AWS_ACCESS_KEY_ID"][:10] + "...",  # Partial for security
                "region": aws_keys["AWS_DEFAULT_REGION"],
            }
        else:
            missing = [k for k, v in aws_keys.items() if not v and k != "AWS_DEFAULT_REGION"]
            result["issues"] = missing

        # Check .env file
        env_file = Path(".env")
        if env_file.exists():
            result["env_file"] = True
            with open(env_file) as f:
                env_content = f.read()
                if "AWS_ACCESS_KEY_ID" in env_content:
                    result["env_has_aws"] = True

        return result

    async def check_aws_bedrock(self) -> dict[str, Any]:
        """Check AWS Bedrock connectivity."""
        result = {"available": False, "models": [], "error": None}

        try:
            import boto3

            # Create Bedrock client
            bedrock = boto3.client(
                service_name="bedrock",
                region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            )

            # List foundation models
            response = bedrock.list_foundation_models()
            models = response.get("modelSummaries", [])

            # Filter for Claude models
            claude_models = [m for m in models if "claude" in m.get("modelId", "").lower()]

            result["available"] = True
            result["models"] = [m["modelId"] for m in claude_models[:5]]

        except Exception as e:
            result["error"] = str(e)

        return result

    def check_python_formatter(self, tool: str) -> dict[str, Any]:
        """Check if Python formatting tool is available."""
        result = {"installed": False, "version": None, "path": None}

        try:
            # Check if tool is installed
            which_result = subprocess.run(["which", tool], capture_output=True, text=True)

            if which_result.returncode == 0:
                result["installed"] = True
                result["path"] = which_result.stdout.strip()

                # Get version
                version_result = subprocess.run([tool, "--version"], capture_output=True, text=True)

                if version_result.returncode == 0:
                    result["version"] = version_result.stdout.strip()

        except Exception as e:
            result["error"] = str(e)

        return result

    def check_formatting_tools(self) -> dict[str, Any]:
        """Check all formatting tools."""
        tools = ["black", "autopep8", "doq", "pyupgrade", "isort", "autoflake"]
        results = {}

        for tool in tools:
            results[tool] = self.check_python_formatter(tool)

        return results

    def check_git(self) -> dict[str, Any]:
        """Check git configuration."""
        result = {
            "installed": False,
            "version": None,
            "user_configured": False,
            "repo_initialized": False,
        }

        try:
            # Check git installation
            version_result = subprocess.run(["git", "--version"], capture_output=True, text=True)

            if version_result.returncode == 0:
                result["installed"] = True
                result["version"] = version_result.stdout.strip()

                # Check user configuration
                user_result = subprocess.run(
                    ["git", "config", "user.name"], capture_output=True, text=True
                )

                email_result = subprocess.run(
                    ["git", "config", "user.email"], capture_output=True, text=True
                )

                if user_result.returncode == 0 and email_result.returncode == 0:
                    result["user_configured"] = True
                    result["user"] = {
                        "name": user_result.stdout.strip(),
                        "email": email_result.stdout.strip(),
                    }

                # Check if current directory is a git repo
                status_result = subprocess.run(
                    ["git", "status"], capture_output=True, text=True, cwd="."
                )

                result["repo_initialized"] = status_result.returncode == 0

        except Exception as e:
            result["error"] = str(e)

        return result

    def check_python_packages(self) -> dict[str, Any]:
        """Check required Python packages."""
        required = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "httpx",
            "boto3",
            "radon",
            "interrogate",
            "pytest",
            "pytest-cov",
            "black",
            "mypy",
        ]

        results = {}

        for package in required:
            try:
                __import__(package.replace("-", "_"))
                results[package] = {"installed": True}
            except ImportError:
                results[package] = {"installed": False}

        return results

    async def test_api_endpoint(self) -> dict[str, Any]:
        """Test if backend API is accessible."""
        result = {"available": False, "endpoints": [], "error": None}

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                # Check health endpoint
                response = await client.get("http://localhost:8000/health")

                if response.status_code == 200:
                    result["available"] = True

                    # Check other endpoints
                    endpoints_to_check = [
                        "/api/evolution/status",
                        "/api/agents/list",
                        "/api/context/current",
                        "/docs",
                    ]

                    for endpoint in endpoints_to_check:
                        try:
                            resp = await client.get(f"http://localhost:8000{endpoint}")
                            result["endpoints"].append(
                                {"path": endpoint, "status": resp.status_code}
                            )
                        except:
                            pass

        except Exception as e:
            result["error"] = str(e)

        return result

    def test_formatting_tool(self, tool: str) -> dict[str, Any]:
        """Test a formatting tool with sample code."""
        result = {"works": False, "test": None}

        # Create test file
        test_file = Path("/tmp/test_format.py")
        test_content = """
def poorly_formatted_function(    x,y,   z ):
    return x+y+z


class TestClass:
    def method(self):
        pass
"""

        try:
            # Write test file
            test_file.write_text(test_content)

            # Run formatter
            if tool == "black":
                cmd = [tool, str(test_file), "--quiet"]
            elif tool == "autopep8":
                cmd = [tool, str(test_file), "--in-place"]
            elif tool == "pyupgrade":
                cmd = [tool, str(test_file), "--py38-plus"]
            else:
                return result

            result_run = subprocess.run(cmd, capture_output=True, text=True)

            if result_run.returncode == 0:
                result["works"] = True
                result["test"] = "Successfully formatted test file"

            # Clean up
            test_file.unlink(missing_ok=True)

        except Exception as e:
            result["error"] = str(e)

        return result

    async def run_verification(self):
        """Run complete external service verification."""
        logger.info("=" * 60)
        logger.info("🔍 EXTERNAL SERVICE VERIFICATION")
        logger.info("=" * 60)
        logger.info("")

        # 1. Check AWS
        logger.info("☁️  AWS Configuration:")
        aws_creds = self.check_aws_credentials()
        if aws_creds["configured"]:
            logger.info("  ✅ Credentials configured")
            logger.info(f"     Access Key: {aws_creds['credentials']['access_key']}")
            logger.info(f"     Region: {aws_creds['credentials']['region']}")
        else:
            logger.info(f"  ❌ Missing credentials: {', '.join(aws_creds['issues'])}")

        # Check Bedrock
        logger.info("\n🤖 AWS Bedrock:")
        bedrock = await self.check_aws_bedrock()
        if bedrock["available"]:
            logger.info("  ✅ Bedrock available")
            logger.info(f"     Claude models: {len(bedrock['models'])}")
            for model in bedrock["models"][:3]:
                logger.info(f"       • {model}")
        else:
            logger.info("  ❌ Bedrock not available")
            if bedrock["error"]:
                logger.info(f"     Error: {bedrock['error'][:100]}")

        # 2. Check formatting tools
        logger.info("\n🛠️  Formatting Tools:")
        tools = self.check_formatting_tools()

        required_tools = ["black", "autopep8", "doq", "pyupgrade"]
        for tool, info in tools.items():
            if tool in required_tools:
                if info["installed"]:
                    logger.info(f"  ✅ {tool}: {info.get('version', 'installed')}")

                    # Test the tool
                    if tool in ["black", "autopep8", "pyupgrade"]:
                        test = self.test_formatting_tool(tool)
                        if test["works"]:
                            logger.info("     ✓ Test passed")
                else:
                    logger.info(f"  ❌ {tool}: not installed")
            else:
                if info["installed"]:
                    logger.info(f"  ℹ️  {tool}: {info.get('version', 'installed')} (optional)")

        # 3. Check Git
        logger.info("\n📦 Git Configuration:")
        git = self.check_git()
        if git["installed"]:
            logger.info(f"  ✅ Git installed: {git['version']}")
            if git["user_configured"]:
                logger.info(f"  ✅ User configured: {git['user']['name']} <{git['user']['email']}>")
            else:
                logger.info("  ⚠️  User not configured")
            if git["repo_initialized"]:
                logger.info("  ✅ Repository initialized")
            else:
                logger.info("  ⚠️  Not a git repository")
        else:
            logger.info("  ❌ Git not installed")

        # 4. Check Python packages
        logger.info("\n📚 Python Packages:")
        packages = self.check_python_packages()

        critical = ["fastapi", "uvicorn", "pydantic", "httpx", "boto3"]
        missing_critical = []

        for pkg, info in packages.items():
            if info["installed"]:
                logger.info(f"  ✅ {pkg}")
            else:
                logger.info(f"  ❌ {pkg}")
                if pkg in critical:
                    missing_critical.append(pkg)

        # 5. Check API
        logger.info("\n🌐 Backend API:")
        api = await self.test_api_endpoint()
        if api["available"]:
            logger.info("  ✅ API available at http://localhost:8000")
            for endpoint in api["endpoints"]:
                status_icon = "✅" if endpoint["status"] < 400 else "⚠️"
                logger.info(f"    {status_icon} {endpoint['path']}: {endpoint['status']}")
        else:
            logger.info("  ❌ API not available")
            if api["error"]:
                logger.info(f"     Error: {api['error']}")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("=" * 60)

        all_good = True

        if not aws_creds["configured"]:
            logger.info("  ❌ AWS credentials not configured")
            all_good = False

        if not bedrock["available"]:
            logger.info("  ⚠️  AWS Bedrock not accessible")

        missing_tools = [t for t in required_tools if not tools[t]["installed"]]
        if missing_tools:
            logger.info(f"  ❌ Missing tools: {', '.join(missing_tools)}")
            all_good = False

        if missing_critical:
            logger.info(f"  ❌ Missing critical packages: {', '.join(missing_critical)}")
            all_good = False

        if not api["available"]:
            logger.info("  ⚠️  Backend API not running")

        if all_good:
            logger.info("\n✅ All critical external services are configured!")
        else:
            logger.info("\n⚠️  Some external services need configuration")
            logger.info("\nTo fix:")

            if not aws_creds["configured"]:
                logger.info(
                    "  • Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables"
                )
                logger.info("    or create a .env file with these values")

            if missing_tools:
                logger.info(f"  • Install missing tools: pip install {' '.join(missing_tools)}")

            if missing_critical:
                logger.info(
                    f"  • Install missing packages: pip install {' '.join(missing_critical)}"
                )

        return all_good


async def main():
    verifier = ExternalServiceVerifier()
    success = await verifier.run_verification()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
