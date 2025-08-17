"""Code Improver - Directly modifies code to add docstrings and type hints."""

import ast
from pathlib import Path
from typing import Any


class CodeImprover:
    """Improve Python code by adding docstrings and type hints."""

    def __init__(self):
        """Initialize code improver."""
        self.improvements_made = []

    def add_docstring_to_function(self, func_def: ast.FunctionDef) -> str:
        """Generate docstring for a function."""
        # Extract parameter names
        args = []
        for arg in func_def.args.args:
            if arg.arg != "self":
                args.append(arg.arg)

        # Build docstring
        docstring_lines = ['"""']

        # Add function name as brief description
        func_name = func_def.name.replace("_", " ").title()
        docstring_lines.append(f"{func_name}.")

        # Add parameters section if there are args
        if args:
            docstring_lines.append("")
            docstring_lines.append("Args:")
            for arg in args:
                docstring_lines.append(f"    {arg}: TODO: Add description")

        # Add returns section if function has return statement
        has_return = any(isinstance(node, ast.Return) for node in ast.walk(func_def))
        if has_return and func_def.name != "__init__":
            docstring_lines.append("")
            docstring_lines.append("Returns:")
            docstring_lines.append("    TODO: Add return description")

        docstring_lines.append('"""')

        return "\n    ".join(docstring_lines)

    def add_type_hints(self, func_def: ast.FunctionDef) -> tuple[str, str]:
        """Generate type hints for function parameters and return type."""
        # Simple heuristics for type hints
        param_hints = {}

        for arg in func_def.args.args:
            if arg.arg == "self":
                continue

            # Try to guess type from argument name
            if "path" in arg.arg or "file" in arg.arg:
                param_hints[arg.arg] = "str"
            elif "id" in arg.arg or "name" in arg.arg:
                param_hints[arg.arg] = "str"
            elif "count" in arg.arg or "num" in arg.arg or "size" in arg.arg:
                param_hints[arg.arg] = "int"
            elif "flag" in arg.arg or "is_" in arg.arg or "enable" in arg.arg:
                param_hints[arg.arg] = "bool"
            elif "data" in arg.arg or "config" in arg.arg:
                param_hints[arg.arg] = "Dict[str, Any]"
            elif "list" in arg.arg or "items" in arg.arg:
                param_hints[arg.arg] = "List[Any]"
            else:
                param_hints[arg.arg] = "Any"

        # Guess return type
        return_hint = "None"
        if func_def.name.startswith("get_") or func_def.name.startswith("find_"):
            return_hint = "Optional[Any]"
        elif func_def.name.startswith("is_") or func_def.name.startswith("has_"):
            return_hint = "bool"
        elif func_def.name.startswith("count_") or func_def.name.startswith("calculate_"):
            return_hint = "int"
        elif func_def.name == "__init__":
            return_hint = "None"

        return param_hints, return_hint

    def improve_file(self, file_path: str) -> tuple[bool, str, list[str]]:
        """Improve a Python file by adding docstrings and type hints.

        Args:
            file_path: Path to the Python file

        Returns:
            Tuple of (success, modified_content, improvements_list)
        """
        improvements = []

        try:
            # Read file
            with open(file_path) as f:
                original_content = f.read()

            # Parse AST
            tree = ast.parse(original_content)

            # Track lines to insert
            insertions = []  # List of (line_number, content)

            # Find functions without docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has docstring
                    has_docstring = (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    )

                    if not has_docstring:
                        # Generate docstring
                        docstring = self.add_docstring_to_function(node)
                        # Calculate indentation
                        indent = "    "  # Default 4 spaces
                        # Insert after function definition line
                        insertions.append((node.lineno, indent + docstring))
                        improvements.append(f"Added docstring to {node.name}")

                    # Check for type hints
                    if not node.returns and node.name != "__init__":
                        improvements.append(f"Could add return type hint to {node.name}")

            # Apply insertions to content
            if insertions:
                lines = original_content.split("\n")

                # Sort insertions by line number (reverse order to maintain line numbers)
                insertions.sort(key=lambda x: x[0], reverse=True)

                for line_num, content in insertions:
                    # Insert docstring after function definition
                    if line_num <= len(lines):
                        # Find the line with function definition
                        func_line = lines[line_num - 1]
                        # Insert docstring on next line
                        lines.insert(line_num, content)

                modified_content = "\n".join(lines)

                # Verify syntax
                try:
                    ast.parse(modified_content)
                    return True, modified_content, improvements
                except SyntaxError:
                    return False, original_content, ["Syntax error in modified code"]
            else:
                return False, original_content, ["No improvements needed"]

        except Exception as e:
            return False, "", [f"Error processing file: {e!s}"]

    def improve_directory(self, directory: str, pattern: str = "*.py") -> dict[str, list[str]]:
        """Improve all Python files in a directory.

        Args:
            directory: Directory path
            pattern: File pattern to match

        Returns:
            Dictionary mapping file paths to improvements made
        """
        results = {}
        dir_path = Path(directory)

        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                success, modified_content, improvements = self.improve_file(str(file_path))

                if success and improvements:
                    # Write improved content back
                    with open(file_path, "w") as f:
                        f.write(modified_content)
                    results[str(file_path)] = improvements
                    self.improvements_made.extend(improvements)

        return results


class SimpleRefactor:
    """Simple refactoring operations without external dependencies."""

    def __init__(self):
        """Initialize simple refactor."""
        self.improver = CodeImprover()

    async def execute_improvements(
        self, target_path: str, focus_areas: list[str]
    ) -> dict[str, Any]:
        """Execute code improvements on target.

        Args:
            target_path: File or directory to improve
            focus_areas: Areas to focus on (documentation, type_hints, etc.)

        Returns:
            Results dictionary
        """
        path = Path(target_path)
        results = {"files_modified": 0, "improvements": [], "errors": []}

        try:
            if path.is_file() and path.suffix == ".py":
                # Improve single file
                success, content, improvements = self.improver.improve_file(str(path))

                if success and improvements:
                    # Write back to file
                    with open(path, "w") as f:
                        f.write(content)

                    results["files_modified"] = 1
                    results["improvements"] = improvements

            elif path.is_dir():
                # Improve directory
                improvements_by_file = self.improver.improve_directory(str(path))

                results["files_modified"] = len(improvements_by_file)
                for file, improvements in improvements_by_file.items():
                    results["improvements"].extend([f"{file}: {imp}" for imp in improvements])

        except Exception as e:
            results["errors"].append(str(e))

        return results
