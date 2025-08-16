"""Jira integration agent for project management and issue tracking.

Phase 4: A2A External Integration
P4-T3: External Agent Implementations
"""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from typing import Any, Optional

import aiohttp

from ..protocols import A2AMessage, AgentInfo, CapabilityInfo, ResponseStatus


@dataclass
class JiraConfig:
    """Jira agent configuration.

    Attributes:
        domain: Jira domain (e.g., "company.atlassian.net")
        username: Jira username
        api_token: Jira API token
        timeout_seconds: Request timeout
        max_retries: Maximum retry attempts
        rate_limit_per_second: Rate limit per second
    """

    domain: str
    username: str
    api_token: str
    timeout_seconds: int = 30
    max_retries: int = 3
    rate_limit_per_second: int = 10


class JiraAgent:
    """Jira integration agent for project management and issue tracking."""

    AGENT_ID = "jira-agent"
    AGENT_NAME = "Jira Integration Agent"
    VERSION = "1.0.0"

    def __init__(self, config: JiraConfig):
        """Initialize Jira agent.

        Args:
            config: Jira configuration
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = f"https://{config.domain}/rest/api/3"

        # Load agent card
        self.agent_info = self._load_agent_info()

    def _load_agent_info(self) -> AgentInfo:
        """Load agent information from agent card."""
        capabilities = [
            CapabilityInfo(
                name="create_issue",
                version="1.0.0",
                description="Create a new Jira issue",
                tags=["issue", "create", "jira"],
            ),
            CapabilityInfo(
                name="update_issue",
                version="1.0.0",
                description="Update an existing Jira issue",
                tags=["issue", "update", "jira"],
            ),
            CapabilityInfo(
                name="transition_issue",
                version="1.0.0",
                description="Transition issue to new status",
                tags=["issue", "transition", "jira"],
            ),
            CapabilityInfo(
                name="get_issue",
                version="1.0.0",
                description="Get issue details",
                tags=["issue", "get", "jira"],
            ),
            CapabilityInfo(
                name="search_issues",
                version="1.0.0",
                description="Search for issues using JQL",
                tags=["issue", "search", "jira"],
            ),
            CapabilityInfo(
                name="add_comment",
                version="1.0.0",
                description="Add comment to issue",
                tags=["comment", "create", "jira"],
            ),
            CapabilityInfo(
                name="create_project",
                version="1.0.0",
                description="Create a new Jira project",
                tags=["project", "create", "jira"],
            ),
            CapabilityInfo(
                name="get_project",
                version="1.0.0",
                description="Get project information",
                tags=["project", "get", "jira"],
            ),
        ]

        return AgentInfo(
            agent_id=self.AGENT_ID,
            agent_name=self.AGENT_NAME,
            agent_type="external",
            version=self.VERSION,
            description="Agent for Jira project management and issue tracking",
            capabilities=capabilities,
        )

    async def start(self) -> None:
        """Start the Jira agent."""
        if self.session is None:
            # Create basic auth header
            auth_string = f"{self.config.username}:{self.config.api_token}"
            auth_bytes = auth_string.encode("ascii")
            auth_header = base64.b64encode(auth_bytes).decode("ascii")

            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            headers = {
                "Authorization": f"Basic {auth_header}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": f"T-Developer-{self.AGENT_NAME}/{self.VERSION}",
            }

            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)

        self.logger.info("Jira agent started")

    async def stop(self) -> None:
        """Stop the Jira agent."""
        if self.session:
            await self.session.close()
            self.session = None

        self.logger.info("Jira agent stopped")

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
            if action == "create_issue":
                result = await self.create_issue(parameters)
            elif action == "update_issue":
                result = await self.update_issue(parameters)
            elif action == "transition_issue":
                result = await self.transition_issue(parameters)
            elif action == "get_issue":
                result = await self.get_issue(parameters)
            elif action == "search_issues":
                result = await self.search_issues(parameters)
            elif action == "add_comment":
                result = await self.add_comment(parameters)
            elif action == "create_project":
                result = await self.create_project(parameters)
            elif action == "get_project":
                result = await self.get_project(parameters)
            else:
                return message.create_response(
                    status=ResponseStatus.NOT_FOUND, error=f"Unknown action: {action}"
                )

            return message.create_response(status=ResponseStatus.SUCCESS, data=result)

        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return message.create_response(status=ResponseStatus.ERROR, error=str(e))

    async def create_issue(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new Jira issue.

        Args:
            params: Issue parameters

        Returns:
            Issue information
        """
        required_fields = ["project_key", "summary", "issue_type"]
        self._validate_parameters(params, required_fields)

        # Build issue data
        issue_data = {
            "fields": {
                "project": {"key": params["project_key"]},
                "summary": params["summary"],
                "issuetype": {"name": params["issue_type"]},
            }
        }

        # Add optional fields
        if params.get("description"):
            issue_data["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": params["description"]}],
                    }
                ],
            }

        if params.get("priority"):
            issue_data["fields"]["priority"] = {"name": params["priority"]}

        if params.get("assignee"):
            issue_data["fields"]["assignee"] = {"name": params["assignee"]}

        if params.get("labels"):
            issue_data["fields"]["labels"] = params["labels"]

        if params.get("components"):
            issue_data["fields"]["components"] = [{"name": comp} for comp in params["components"]]

        # Add custom fields
        if params.get("custom_fields"):
            issue_data["fields"].update(params["custom_fields"])

        url = f"{self.base_url}/issue"

        async with self.session.post(url, json=issue_data) as response:
            if response.status == 201:
                issue_info = await response.json()
                return {
                    "id": issue_info["id"],
                    "key": issue_info["key"],
                    "self": issue_info["self"],
                    "url": f"https://{self.config.domain}/browse/{issue_info['key']}",
                }
            else:
                error_data = await response.json()
                raise Exception(
                    f"Jira API error: {error_data.get('errorMessages', ['Unknown error'])[0]}"
                )

    async def update_issue(self, params: dict[str, Any]) -> dict[str, Any]:
        """Update an existing Jira issue.

        Args:
            params: Update parameters

        Returns:
            Update result
        """
        required_fields = ["issue_key"]
        self._validate_parameters(params, required_fields)

        issue_key = params["issue_key"]
        update_data = {"fields": {}}
        updated_fields = []

        # Build update data
        if params.get("summary"):
            update_data["fields"]["summary"] = params["summary"]
            updated_fields.append("summary")

        if params.get("description"):
            update_data["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": params["description"]}],
                    }
                ],
            }
            updated_fields.append("description")

        if params.get("priority"):
            update_data["fields"]["priority"] = {"name": params["priority"]}
            updated_fields.append("priority")

        if params.get("assignee"):
            update_data["fields"]["assignee"] = {"name": params["assignee"]}
            updated_fields.append("assignee")

        if params.get("labels"):
            update_data["fields"]["labels"] = params["labels"]
            updated_fields.append("labels")

        # Add custom fields
        if params.get("custom_fields"):
            update_data["fields"].update(params["custom_fields"])
            updated_fields.extend(params["custom_fields"].keys())

        url = f"{self.base_url}/issue/{issue_key}"

        async with self.session.put(url, json=update_data) as response:
            if response.status == 204:
                return {"success": True, "updated_fields": updated_fields}
            else:
                error_data = await response.json()
                raise Exception(
                    f"Jira API error: {error_data.get('errorMessages', ['Unknown error'])[0]}"
                )

    async def transition_issue(self, params: dict[str, Any]) -> dict[str, Any]:
        """Transition issue to new status.

        Args:
            params: Transition parameters

        Returns:
            Transition result
        """
        required_fields = ["issue_key", "transition_id"]
        self._validate_parameters(params, required_fields)

        issue_key = params["issue_key"]
        transition_data = {"transition": {"id": params["transition_id"]}}

        # Add comment if provided
        if params.get("comment"):
            transition_data["update"] = {
                "comment": [
                    {
                        "add": {
                            "body": {
                                "type": "doc",
                                "version": 1,
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [{"type": "text", "text": params["comment"]}],
                                    }
                                ],
                            }
                        }
                    }
                ]
            }

        # Add additional fields
        if params.get("fields"):
            if "fields" not in transition_data:
                transition_data["fields"] = {}
            transition_data["fields"].update(params["fields"])

        url = f"{self.base_url}/issue/{issue_key}/transitions"

        async with self.session.post(url, json=transition_data) as response:
            if response.status == 204:
                # Get updated issue to return new status
                issue_info = await self.get_issue({"issue_key": issue_key})
                return {"success": True, "new_status": issue_info["fields"]["status"]["name"]}
            else:
                error_data = await response.json()
                raise Exception(
                    f"Jira API error: {error_data.get('errorMessages', ['Unknown error'])[0]}"
                )

    async def get_issue(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get issue details.

        Args:
            params: Issue parameters

        Returns:
            Issue details
        """
        required_fields = ["issue_key"]
        self._validate_parameters(params, required_fields)

        issue_key = params["issue_key"]
        url = f"{self.base_url}/issue/{issue_key}"

        # Add expand parameters if provided
        if params.get("expand"):
            expand_params = ",".join(params["expand"])
            url += f"?expand={expand_params}"

        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise Exception(
                    f"Jira API error: {error_data.get('errorMessages', ['Unknown error'])[0]}"
                )

    async def search_issues(self, params: dict[str, Any]) -> dict[str, Any]:
        """Search for issues using JQL.

        Args:
            params: Search parameters

        Returns:
            Search results
        """
        required_fields = ["jql"]
        self._validate_parameters(params, required_fields)

        search_data = {
            "jql": params["jql"],
            "startAt": params.get("start_at", 0),
            "maxResults": params.get("max_results", 50),
        }

        if params.get("fields"):
            search_data["fields"] = params["fields"]

        if params.get("expand"):
            search_data["expand"] = params["expand"]

        url = f"{self.base_url}/search"

        async with self.session.post(url, json=search_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise Exception(
                    f"Jira API error: {error_data.get('errorMessages', ['Unknown error'])[0]}"
                )

    async def add_comment(self, params: dict[str, Any]) -> dict[str, Any]:
        """Add comment to issue.

        Args:
            params: Comment parameters

        Returns:
            Comment information
        """
        required_fields = ["issue_key", "body"]
        self._validate_parameters(params, required_fields)

        issue_key = params["issue_key"]
        comment_data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": params["body"]}]}
                ],
            }
        }

        # Add visibility if provided
        if params.get("visibility"):
            comment_data["visibility"] = params["visibility"]

        url = f"{self.base_url}/issue/{issue_key}/comment"

        async with self.session.post(url, json=comment_data) as response:
            if response.status == 201:
                return await response.json()
            else:
                error_data = await response.json()
                raise Exception(
                    f"Jira API error: {error_data.get('errorMessages', ['Unknown error'])[0]}"
                )

    async def create_project(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a new Jira project.

        Args:
            params: Project parameters

        Returns:
            Project information
        """
        required_fields = ["key", "name", "project_type_key", "lead"]
        self._validate_parameters(params, required_fields)

        project_data = {
            "key": params["key"],
            "name": params["name"],
            "projectTypeKey": params["project_type_key"],
            "lead": params["lead"],
        }

        if params.get("description"):
            project_data["description"] = params["description"]

        if params.get("template_key"):
            project_data["projectTemplateKey"] = params["template_key"]

        url = f"{self.base_url}/project"

        async with self.session.post(url, json=project_data) as response:
            if response.status == 201:
                return await response.json()
            else:
                error_data = await response.json()
                raise Exception(
                    f"Jira API error: {error_data.get('errorMessages', ['Unknown error'])[0]}"
                )

    async def get_project(self, params: dict[str, Any]) -> dict[str, Any]:
        """Get project information.

        Args:
            params: Project parameters

        Returns:
            Project information
        """
        required_fields = ["project_key"]
        self._validate_parameters(params, required_fields)

        project_key = params["project_key"]
        url = f"{self.base_url}/project/{project_key}"

        # Add expand parameters if provided
        if params.get("expand"):
            expand_params = ",".join(params["expand"])
            url += f"?expand={expand_params}"

        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_data = await response.json()
                raise Exception(
                    f"Jira API error: {error_data.get('errorMessages', ['Unknown error'])[0]}"
                )

    async def health_check(self) -> bool:
        """Check Jira API health.

        Returns:
            True if healthy
        """
        try:
            url = f"{self.base_url}/serverInfo"
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
