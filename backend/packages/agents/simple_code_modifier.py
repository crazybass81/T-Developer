"""Simple code modifier using external tools and AST."""

import ast
import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class SimpleCodeModifier:
    """Simple and stable code modification using AST."""

    @staticmethod
    def add_docstring_after_def(file_path: str) -> bool:
        """Add simple docstrings using sed command."""
        try:
            # Read file
            with open(file_path) as f:
                lines = f.readlines()

            modified = False
            new_lines = []

            for i, line in enumerate(lines):
                new_lines.append(line)

                # Check if this is a function definition
                if line.strip().startswith("def ") and i + 1 < len(lines):
                    # Check if next line already has docstring
                    next_line = lines[i + 1].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        # Add simple docstring
                        indent = len(line) - len(line.lstrip())
                        func_name = line.strip().split("(")[0].replace("def ", "")
                        docstring = (
                            f'{" " * (indent + 4)}"""TODO: Add description for {func_name}."""\n'
                        )
                        new_lines.append(docstring)
                        modified = True

            if modified:
                # Write back
                with open(file_path, "w") as f:
                    f.writelines(new_lines)
                logger.info(f"Added docstrings to {file_path}")
                return True

        except Exception as e:
            logger.error(f"Failed to modify {file_path}: {e}")

        return False

    @staticmethod
    def add_type_hints_simple(file_path: str) -> bool:
        """Add simple type hints using regex."""
        try:
            import re

            with open(file_path) as f:
                content = f.read()

            # Simple pattern to add -> None to functions without return type
            pattern = r"(def \w+\([^)]*\)):"
            replacement = r"\1 -> None:"

            # Check if modifications needed
            if "-> None" not in content and "def " in content:
                modified_content = re.sub(pattern, replacement, content)

                # Only write if syntax is valid
                try:
                    ast.parse(modified_content)
                    with open(file_path, "w") as f:
                        f.write(modified_content)
                    logger.info(f"Added type hints to {file_path}")
                    return True
                except SyntaxError:
                    logger.warning("Type hint modification would cause syntax error")

        except Exception as e:
            logger.error(f"Failed to add type hints: {e}")

        return False


class ExternalToolModifier:
    """Use external tools for code modification."""

    @staticmethod
    async def use_black_formatter(file_path: str) -> bool:
        """Format code using Black."""
        try:
            result = subprocess.run(["black", "--quiet", file_path], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            logger.warning("Black formatter not installed")
            return False

    @staticmethod
    async def use_isort(file_path: str) -> bool:
        """Sort imports using isort."""
        try:
            result = subprocess.run(["isort", "--quiet", file_path], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            logger.warning("isort not installed")
            return False

    @staticmethod
    async def use_autopep8(file_path: str) -> bool:
        """Fix PEP8 issues using autopep8."""
        try:
            result = subprocess.run(
                ["autopep8", "--in-place", file_path], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            # Try with sed as fallback
            return SimpleCodeModifier.add_docstring_after_def(file_path)


async def modify_code_safely(file_path: str, modifications: list[str]) -> dict[str, Any]:
    """Safely modify code using multiple methods."""

    results = {"success": False, "modifications_applied": [], "errors": []}

    modifier = SimpleCodeModifier()
    external = ExternalToolModifier()

    for mod_type in modifications:
        try:
            if mod_type == "docstrings":
                if modifier.add_docstring_after_def(file_path):
                    results["modifications_applied"].append("Added docstrings")
                    results["success"] = True

            elif mod_type == "type_hints":
                if modifier.add_type_hints_simple(file_path):
                    results["modifications_applied"].append("Added type hints")
                    results["success"] = True

            elif mod_type == "format":
                if await external.use_black_formatter(file_path):
                    results["modifications_applied"].append("Formatted with Black")
                    results["success"] = True
                elif await external.use_autopep8(file_path):
                    results["modifications_applied"].append("Formatted with autopep8")
                    results["success"] = True

        except Exception as e:
            results["errors"].append(str(e))

    return results
