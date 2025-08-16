"""GitHub integration agent for repository operations.

Phase 4: A2A External Integration
P4-T3: External Agent Implementations
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

from ..protocols import A2AMessage, AgentInfo, CapabilityInfo, ResponseStatus


@dataclass
class GitHubConfig:
    """GitHub agent configuration.

    Attributes:
        api_token: GitHub API token
        base_url: GitHub API base URL
        timeout_seconds: Request timeout
        max_retries: Maximum retry attempts
        rate_limit_per_hour: Rate limit per hour
        default_org: Default organization
    """

    api_token: str
    base_url: str = "https://api.github.com"
    timeout_seconds: int = 30
    max_retries: int = 3
    rate_limit_per_hour: int = 5000
    default_org: Optional[str] = None


class GitHubAgent:
    """GitHub integration agent for repository operations."""

    AGENT_ID = "github-agent"
    AGENT_NAME = "GitHub Integration Agent"
    VERSION = "1.0.0"

    def __init__(self, config: GitHubConfig):
        """Initialize GitHub agent.

        Args:
            config: GitHub configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.session: Optional[aiohttp.ClientSession] = None

        # Load agent card
        self.agent_info = self._load_agent_info()

    def _load_agent_info(self) -> AgentInfo:
        """Load agent information from agent card."""
        # In practice, this would load from the YAML file
        capabilities = [
            CapabilityInfo(
                name="create_repository",
                version="1.0.0",
                description="Create a new GitHub repository",
                tags=["repository", "create", "github"],
            ),
            CapabilityInfo(
                name="create_pull_request",
                version="1.0.0",
                description="Create a pull request",
                tags=["pull-request", "create", "github"],
            ),
            CapabilityInfo(
                name="merge_pull_request",
                version="1.0.0",
                description="Merge a pull request",
                tags=["pull-request", "merge", "github"],
            ),
            CapabilityInfo(
                name="create_issue",
                version="1.0.0",
                description="Create a GitHub issue",
                tags=["issue", "create", "github"],
            ),
            CapabilityInfo(
                name="get_repository_info",
                version="1.0.0",
                description="Get repository information",
                tags=["repository", "info", "github"],
            ),
            CapabilityInfo(
                name="list_branches",
                version="1.0.0",
                description="List repository branches",
                tags=["repository", "branches", "github"],
            ),
        ]

        return AgentInfo(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            agent_type="external",
            version=self.VERSION,
            description="Agent for GitHub repository operations and integration",
            capabilities=capabilities,
        )

    async def start(self) -> None:
        """Start the GitHub agent."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            headers = {
                "Authorization": f"Bearer {self.config.api_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": f"T-Developer-{self.AGENT_NAME}/{self.VERSION}",
            }

            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)

        self.logger.info("GitHub agent started")

    async def stop(self) -> None:
        """Stop the GitHub agent."""
        if self.session:
            await self.session.close()
            self.session = None

        self.logger.info("GitHub agent stopped")

    async def handle_request(self, message: A2AMessage) -> A2AMessage:
        """Handle incoming A2A request.

        Args:
            message: Incoming request message

        Returns:
            Response message
        """
        try:
            capability = message.payload.capability
            action = message.payload.action or capability
            parameters = message.payload.parameters

            # Route to appropriate handler
            if action == "create_repository":
                result = await self.create_repository(parameters)
            elif action == "create_pull_request":
                result = await self.create_pull_request(parameters)
            elif action == "merge_pull_request":
                result = await self.merge_pull_request(parameters)
            elif action == "create_issue":
                result = await self.create_issue(parameters)
            elif action == "get_repository_info":
                result = await self.get_repository_info(parameters)
            elif action == "list_branches":
                result = await self.list_branches(parameters)
            else:
                return message.create_response(
                    status=ResponseStatus.NOT_FOUND, error=f"Unknown action: {action}"
                )

            return message.create_response(status=ResponseStatus.SUCCESS, data=result)

        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return message.create_response(status=ResponseStatus.ERROR, error=str(e))

    async def create_repository(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new GitHub repository.

        Args:
            params: Repository parameters

        Returns:
            Repository information
        """
        required_fields = ["name"]
        self._validate_parameters(params, required_fields)

        repo_data = {
            "name": params["name"],
            "description": params.get("description"),
            "private": params.get("private", False),
            "auto_init": params.get("auto_init", True),
        }

        if params.get("gitignore_template"):
            repo_data["gitignore_template"] = params["gitignore_template"]

        # Remove None values
        repo_data = {k: v for k, v in repo_data.items() if v is not None}

        # Determine endpoint
        if self.config.default_org:
            url = f"{self.config.base_url}/orgs/{self.config.default_org}/repos"
        else:
            url = f"{self.config.base_url}/user/repos"

        async with self.session.post(url, json=repo_data) as response:
            if response.status == 201:
                repo_info = await response.json()
                return {
                    "id": repo_info["id"],
                    "name": repo_info["name"],
                    "full_name": repo_info["full_name"],
                    "html_url": repo_info["html_url"],
                    "clone_url": repo_info["clone_url"],
                }
            else:
                error_data = await response.json()
                raise Exception(f"GitHub API error: {error_data.get('message', 'Unknown error')}")

    async def create_pull_request(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a pull request.

        Args:
            params: Pull request parameters

        Returns:
            Pull request information
        """
        required_fields = ["owner", "repo", "title", "head", "base"]
        self._validate_parameters(params, required_fields)

        pr_data = {
            "title": params["title"],
            "head": params["head"],
            "base": params["base"],
            "body": params.get("body"),
            "draft": params.get("draft", False),
        }

        # Remove None values
        pr_data = {k: v for k, v in pr_data.items() if v is not None}

        url = f"{self.config.base_url}/repos/{params['owner']}/{params['repo']}/pulls"

        async with self.session.post(url, json=pr_data) as response:
            if response.status == 201:
                pr_info = await response.json()
                return {
                    "id": pr_info["id"],
                    "number": pr_info["number"],
                    "title": pr_info["title"],
                    "html_url": pr_info["html_url"],
                    "state": pr_info["state"],
                }
            else:
                error_data = await response.json()
                raise Exception(f"GitHub API error: {error_data.get('message', 'Unknown error')}")

    async def merge_pull_request(self, params: dict[str, Any]) -> dict[str, Any]:
        """Merge a pull request.

        Args:
            params: Merge parameters

        Returns:
            Merge result
        """
        required_fields = ["owner", "repo", "pull_number"]
        self._validate_parameters(params, required_fields)

        merge_data = {
            "commit_title": params.get("commit_title"),
            "commit_message": params.get("commit_message"),
            "merge_method": params.get("merge_method", "merge"),
        }

        # Remove None values
        merge_data = {k: v for k, v in merge_data.items() if v is not None}

        url = f"{self.config.base_url}/repos/{params['owner']}/{params['repo']}/pulls/{params['pull_number']}/merge"

        async with self.session.put(url, json=merge_data) as response:
            if response.status == 200:
                merge_info = await response.json()
                return {
                    "sha": merge_info["sha"],
                    "merged": merge_info["merged"],
                    "message": merge_info["message"],
                }
            else:
                error_data = await response.json()
                raise Exception(f"GitHub API error: {error_data.get('message', 'Unknown error')}")

    async def create_issue(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a GitHub issue.

        Args:
            params: Issue parameters

        Returns:
            Issue information
        """
        required_fields = ["owner", "repo", "title"]
        self._validate_parameters(params, required_fields)

        issue_data = {
            "title": params["title"],
            "body": params.get("body"),
            "labels": params.get("labels", []),
            "assignees": params.get("assignees", []),
        }

        # Remove empty lists and None values
        issue_data = {
            k: v for k, v in issue_data.items() if v is not None and (not isinstance(v, list) or v)
        }

        url = f"{self.config.base_url}/repos/{params['owner']}/{params['repo']}/issues"

        async with self.session.post(url, json=issue_data) as response:
            if response.status == 201:
                issue_info = await response.json()
                return {
                    "id": issue_info["id"],
                    "number": issue_info["number"],
                    "title": issue_info["title"],
                    "html_url": issue_info["html_url"],
                    "state": issue_info["state"],
                }
            else:
                error_data = await response.json()
                raise Exception(f"GitHub API error: {error_data.get('message', 'Unknown error')}")

    async def get_repository_info(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get repository information.

        Args:
            params: Repository parameters

        Returns:
            Repository information
        """
        required_fields = ["owner", "repo"]
        self._validate_parameters(params, required_fields)

        url = f"{self.config.base_url}/repos/{params['owner']}/{params['repo']}"

        async with self.session.get(url) as response:
            if response.status == 200:
                repo_info = await response.json()
                return {
                    "id": repo_info["id"],
                    "name": repo_info["name"],
                    "full_name": repo_info["full_name"],
                    "description": repo_info["description"],
                    "private": repo_info["private"],
                    "html_url": repo_info["html_url"],
                    "clone_url": repo_info["clone_url"],
                    "default_branch": repo_info["default_branch"],
                    "language": repo_info["language"],
                    "stargazers_count": repo_info["stargazers_count"],
                    "forks_count": repo_info["forks_count"],
                }
            else:
                error_data = await response.json()
                raise Exception(f"GitHub API error: {error_data.get('message', 'Unknown error')}")

    async def list_branches(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """List repository branches.

        Args:
            params: Repository parameters

        Returns:
            List of branches
        """
        required_fields = ["owner", "repo"]
        self._validate_parameters(params, required_fields)

        url = f"{self.config.base_url}/repos/{params['owner']}/{params['repo']}/branches"

        # Add protected filter if specified
        if params.get("protected") is not None:
            url += f"?protected={str(params['protected']).lower()}"

        async with self.session.get(url) as response:
            if response.status == 200:
                branches = await response.json()
                return [
                    {
                        "name": branch["name"],
                        "commit": {"sha": branch["commit"]["sha"], "url": branch["commit"]["url"]},
                        "protected": branch["protected"],
                    }
                    for branch in branches
                ]
            else:
                error_data = await response.json()
                raise Exception(f"GitHub API error: {error_data.get('message', 'Unknown error')}")

    async def health_check(self) -> bool:
        """Check GitHub API health.

        Returns:
            True if healthy
        """
        try:
            url = f"{self.config.base_url}/rate_limit"
            async with self.session.get(url) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def _validate_parameters(self, params: dict[str, Any], required_fields: list[str]) -> None:
        """Validate request parameters.

        Args:
            params: Parameters to validate
            required_fields: Required field names

        Raises:
            ValueError: If required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in params]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

    def get_agent_info(self) -> AgentInfo:
        """Get agent information."""
        return self.agent_info
