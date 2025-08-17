"""Connect to external code modification services."""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class ExternalCodeServices:
    """Connect to various code modification services."""

    @staticmethod
    async def use_openai_codex(code: str, instruction: str) -> Optional[str]:
        """Use OpenAI API to modify code."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key not found")
            return None

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

                payload = {
                    "model": "gpt-4",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a code improvement assistant. Return only the modified code.",
                        },
                        {"role": "user", "content": f"{instruction}\n\nCode:\n{code}"},
                    ],
                    "temperature": 0.2,
                }

                async with session.post(
                    "https://api.openai.com/v1/chat/completions", json=payload, headers=headers
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")

        return None

    @staticmethod
    def use_black_formatter(file_path: str) -> bool:
        """Use Black formatter (most popular Python formatter)."""
        try:
            # First check if black is installed
            result = subprocess.run(["black", "--version"], capture_output=True, text=True)

            if result.returncode == 0:
                # Format the file
                result = subprocess.run(
                    ["black", "--quiet", file_path], capture_output=True, text=True
                )

                if result.returncode == 0:
                    logger.info(f"Black formatted {file_path}")
                    return True
            else:
                # Try to install black
                logger.info("Installing black formatter...")
                subprocess.run(["pip", "install", "black"], capture_output=True)

                # Try again
                result = subprocess.run(
                    ["black", "--quiet", file_path], capture_output=True, text=True
                )
                return result.returncode == 0

        except Exception as e:
            logger.warning(f"Black formatter failed: {e}")

        return False

    @staticmethod
    def use_autopep8(file_path: str) -> bool:
        """Use autopep8 for PEP8 compliance."""
        try:
            # Check if autopep8 is installed
            result = subprocess.run(["autopep8", "--version"], capture_output=True, text=True)

            if result.returncode != 0:
                # Install autopep8
                logger.info("Installing autopep8...")
                subprocess.run(["pip", "install", "autopep8"], capture_output=True)

            # Run autopep8
            result = subprocess.run(
                ["autopep8", "--in-place", "--aggressive", file_path],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info(f"autopep8 formatted {file_path}")
                return True

        except Exception as e:
            logger.warning(f"autopep8 failed: {e}")

        return False

    @staticmethod
    def use_docstring_generator(file_path: str) -> bool:
        """Use doq tool to generate docstrings."""
        try:
            # Try using doq (docstring generator)
            result = subprocess.run(["doq", "--version"], capture_output=True, text=True)

            if result.returncode != 0:
                # Install doq
                logger.info("Installing doq...")
                subprocess.run(["pip", "install", "doq"], capture_output=True)

            # Generate docstrings
            result = subprocess.run(
                ["doq", file_path, "--formatter", "google"], capture_output=True, text=True
            )

            if result.returncode == 0:
                # Write the output back to file
                with open(file_path, "w") as f:
                    f.write(result.stdout)
                logger.info(f"doq added docstrings to {file_path}")
                return True

        except Exception as e:
            logger.warning(f"doq failed: {e}")

        return False

    @staticmethod
    def use_pyupgrade(file_path: str) -> bool:
        """Use pyupgrade to modernize Python code."""
        try:
            # Check if pyupgrade is installed
            result = subprocess.run(["pyupgrade", "--version"], capture_output=True, text=True)

            if result.returncode != 0:
                # Install pyupgrade
                logger.info("Installing pyupgrade...")
                subprocess.run(["pip", "install", "pyupgrade"], capture_output=True)

            # Run pyupgrade
            result = subprocess.run(
                ["pyupgrade", "--py39-plus", file_path], capture_output=True, text=True
            )

            if result.returncode == 0:
                logger.info(f"pyupgrade modernized {file_path}")
                return True

        except Exception as e:
            logger.warning(f"pyupgrade failed: {e}")

        return False


async def apply_external_services(file_path: str) -> dict[str, Any]:
    """Apply multiple external services to improve code."""

    results = {"success": False, "services_applied": [], "improvements": []}

    services = ExternalCodeServices()

    # Read original content
    original_content = Path(file_path).read_text()

    # 1. Try formatting with Black (most reliable)
    if services.use_black_formatter(file_path):
        results["services_applied"].append("Black formatter")
        results["improvements"].append("Code formatted to Black standards")
        results["success"] = True

    # 2. Try PEP8 compliance with autopep8
    elif services.use_autopep8(file_path):
        results["services_applied"].append("autopep8")
        results["improvements"].append("Code formatted to PEP8 standards")
        results["success"] = True

    # 3. Try adding docstrings with doq
    if services.use_docstring_generator(file_path):
        results["services_applied"].append("doq docstring generator")
        results["improvements"].append("Docstrings added")
        results["success"] = True

    # 4. Try modernizing with pyupgrade
    if services.use_pyupgrade(file_path):
        results["services_applied"].append("pyupgrade")
        results["improvements"].append("Code modernized")
        results["success"] = True

    # 5. If we have OpenAI API key, try that for more intelligent modifications
    if os.getenv("OPENAI_API_KEY"):
        modified_code = await services.use_openai_codex(
            original_content, "Add comprehensive docstrings and type hints to this Python code"
        )

        if modified_code:
            # Save the modified code
            Path(file_path).write_text(modified_code)
            results["services_applied"].append("OpenAI Codex")
            results["improvements"].append("AI-powered improvements")
            results["success"] = True

    # Check if file was actually modified
    new_content = Path(file_path).read_text()
    if new_content != original_content:
        results["success"] = True
        logger.info(f"File {file_path} was successfully improved by external services")
    else:
        logger.warning(f"No external services could modify {file_path}")

    return results
