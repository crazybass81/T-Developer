"""
OpenAI-based code generator for T-Developer

Uses OpenAI API to generate code when Amazon Q Developer CLI is not available
"""
import logging
import os
import json
import re
import openai
from typing import Dict, List, Any, Optional, Tuple

from config import settings

# Set up logging
logger = logging.getLogger(__name__)

class OpenAICodeGenerator:
    """
    OpenAI-based code generator
    
    Uses OpenAI API to generate code when Amazon Q Developer CLI is not available
    """
    
    def __init__(self):
        """Initialize the OpenAI code generator"""
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        self.model = "gpt-4"  # Use GPT-4 for better code generation
        logger.info("OpenAI code generator initialized")
    
    def is_available(self) -> bool:
        """
        Check if OpenAI API is available
        
        Returns:
            True if OpenAI API is available, False otherwise
        """
        return bool(self.api_key)
    
    def generate_code(self, instruction: Dict[str, Any], workspace_dir: str) -> Dict[str, Any]:
        """
        Generate code based on instruction
        
        Args:
            instruction: Instruction dictionary
            workspace_dir: Workspace directory
            
        Returns:
            Dictionary with generated code information
        """
        logger.info("Generating code with OpenAI")
        
        try:
            # Extract relevant information from instruction
            task_id = instruction.get("task_id", "unknown")
            feature_name = instruction.get("feature_name", "")
            description = instruction.get("description", "")
            plan = instruction.get("plan", {})
            context = instruction.get("context", {})
            
            # Create a prompt for OpenAI
            prompt = self._create_code_prompt(feature_name, description, plan, context, workspace_dir)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer. Your task is to implement code changes based on the provided instructions and context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more deterministic output
                max_tokens=4000
            )
            
            # Extract code changes from response
            code_changes = self._extract_code_changes(response.choices[0].message.content)
            
            # Apply code changes to workspace
            modified_files, created_files, diff = self._apply_code_changes(code_changes, workspace_dir)
            
            return {
                "success": True,
                "modified_files": modified_files,
                "created_files": created_files,
                "diff": diff
            }
        except Exception as e:
            logger.error(f"Error generating code with OpenAI: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "modified_files": [],
                "created_files": [],
                "diff": ""
            }
    
    def fix_test_failures(self, failures: List[Dict[str, Any]], workspace_dir: str) -> Dict[str, Any]:
        """
        Fix test failures
        
        Args:
            failures: List of test failures
            workspace_dir: Workspace directory
            
        Returns:
            Dictionary with fix information
        """
        logger.info(f"Fixing {len(failures)} test failures with OpenAI")
        
        try:
            # Create a prompt for OpenAI
            prompt = self._create_test_fix_prompt(failures, workspace_dir)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software developer. Your task is to fix failing tests based on the provided information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            # Extract code changes from response
            code_changes = self._extract_code_changes(response.choices[0].message.content)
            
            # Apply code changes to workspace
            modified_files, created_files, diff = self._apply_code_changes(code_changes, workspace_dir)
            
            return {
                "success": True,
                "fixed": len(failures),
                "changes": modified_files + created_files
            }
        except Exception as e:
            logger.error(f"Error fixing tests with OpenAI: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "fixed": 0,
                "changes": []
            }
    
    def _create_code_prompt(self, feature_name: str, description: str, plan: Dict[str, Any], context: Dict[str, Any], workspace_dir: str) -> str:
        """
        Create a prompt for code generation
        
        Args:
            feature_name: Feature name
            description: Feature description
            plan: Plan dictionary
            context: Context dictionary
            workspace_dir: Workspace directory
            
        Returns:
            Prompt string
        """
        # Get relevant files from workspace
        file_contents = self._get_relevant_files(workspace_dir, context.get("related_files", []))
        
        # Create prompt
        prompt = f"""
# Task: Implement {feature_name}

## Description
{description}

## Plan
{json.dumps(plan, indent=2)}

## Current Files
{file_contents}

## Instructions
1. Implement the necessary changes to fulfill the requirements
2. You can modify existing files or create new ones
3. Provide your changes in the following format:

```file:path/to/file.py
// Full content of the file after changes
```

For each file you want to modify or create, use the above format.
"""
        return prompt
    
    def _create_test_fix_prompt(self, failures: List[Dict[str, Any]], workspace_dir: str) -> str:
        """
        Create a prompt for test fix
        
        Args:
            failures: List of test failures
            workspace_dir: Workspace directory
            
        Returns:
            Prompt string
        """
        # Get failing test files
        test_files = []
        implementation_files = []
        
        for failure in failures:
            file_path = failure.get("file", "")
            if file_path and file_path not in test_files:
                test_files.append(file_path)
                
                # Try to find the implementation file being tested
                if file_path.startswith("tests/") and file_path.endswith(".py"):
                    impl_file = file_path.replace("tests/", "").replace("test_", "")
                    if os.path.exists(os.path.join(workspace_dir, impl_file)):
                        implementation_files.append(impl_file)
        
        # Get file contents
        file_contents = self._get_file_contents(workspace_dir, test_files + implementation_files)
        
        # Format failures
        failures_text = ""
        for i, failure in enumerate(failures):
            failures_text += f"{i+1}. File: {failure.get('file', 'unknown')}, Test: {failure.get('test', 'unknown')}\n"
            if failure.get('message'):
                failures_text += f"   Message: {failure.get('message')}\n"
        
        # Create prompt
        prompt = f"""
# Task: Fix Failing Tests

## Failing Tests
{failures_text}

## Relevant Files
{file_contents}

## Instructions
1. Analyze the failing tests and identify the issues
2. Fix the implementation code or tests as needed
3. Provide your changes in the following format:

```file:path/to/file.py
// Full content of the file after changes
```

For each file you want to modify, use the above format.
"""
        return prompt
    
    def _extract_code_changes(self, response_text: str) -> Dict[str, str]:
        """
        Extract code changes from response text
        
        Args:
            response_text: Response text from OpenAI
            
        Returns:
            Dictionary with file paths and contents
        """
        # Extract code blocks with file paths
        pattern = r"```file:(.*?)\n(.*?)```"
        matches = re.finditer(pattern, response_text, re.DOTALL)
        
        code_changes = {}
        for match in matches:
            file_path = match.group(1).strip()
            file_content = match.group(2).strip()
            code_changes[file_path] = file_content
        
        return code_changes
    
    def _apply_code_changes(self, code_changes: Dict[str, str], workspace_dir: str) -> Tuple[List[str], List[str], str]:
        """
        Apply code changes to workspace
        
        Args:
            code_changes: Dictionary with file paths and contents
            workspace_dir: Workspace directory
            
        Returns:
            Tuple of modified files, created files, and diff
        """
        modified_files = []
        created_files = []
        diff = ""
        
        for file_path, content in code_changes.items():
            full_path = os.path.join(workspace_dir, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Check if file exists
            if os.path.exists(full_path):
                # Read existing content
                with open(full_path, 'r') as f:
                    old_content = f.read()
                
                # Generate diff
                file_diff = self._generate_diff(file_path, old_content, content)
                diff += file_diff
                
                # Write new content
                with open(full_path, 'w') as f:
                    f.write(content)
                
                modified_files.append(file_path)
            else:
                # Generate diff for new file
                file_diff = self._generate_diff(file_path, "", content)
                diff += file_diff
                
                # Write new content
                with open(full_path, 'w') as f:
                    f.write(content)
                
                created_files.append(file_path)
        
        return modified_files, created_files, diff
    
    def _generate_diff(self, file_path: str, old_content: str, new_content: str) -> str:
        """
        Generate diff between old and new content
        
        Args:
            file_path: File path
            old_content: Old content
            new_content: New content
            
        Returns:
            Diff string
        """
        import difflib
        
        # Split content into lines
        old_lines = old_content.splitlines()
        new_lines = new_content.splitlines()
        
        # Generate unified diff
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=""
        )
        
        return "\n".join(diff) + "\n"
    
    def _get_relevant_files(self, workspace_dir: str, related_files: List[Dict[str, str]]) -> str:
        """
        Get relevant files from workspace
        
        Args:
            workspace_dir: Workspace directory
            related_files: List of related files
            
        Returns:
            String with file contents
        """
        file_paths = [file_info.get("path") for file_info in related_files]
        
        # Add common files
        common_files = ["main.py", "config.py", "requirements.txt"]
        for file in common_files:
            if os.path.exists(os.path.join(workspace_dir, file)) and file not in file_paths:
                file_paths.append(file)
        
        return self._get_file_contents(workspace_dir, file_paths)
    
    def _get_file_contents(self, workspace_dir: str, file_paths: List[str]) -> str:
        """
        Get file contents
        
        Args:
            workspace_dir: Workspace directory
            file_paths: List of file paths
            
        Returns:
            String with file contents
        """
        result = ""
        
        for file_path in file_paths:
            full_path = os.path.join(workspace_dir, file_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                    
                    result += f"\n### File: {file_path}\n```python\n{content}\n```\n"
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {e}")
        
        return result