"""External agent integrations for A2A communication.

Phase 4: A2A External Integration - External Agents Package
"""

from .github_agent import GitHubAgent, GitHubConfig
from .jira_agent import JiraAgent, JiraConfig
from .slack_agent import SlackAgent, SlackConfig

# Note: Datadog and PagerDuty agents would be imported here when implemented
# from .datadog_agent import DatadogAgent, DatadogConfig
# from .pagerduty_agent import PagerDutyAgent, PagerDutyConfig

__all__ = [
    "GitHubAgent",
    "GitHubConfig",
    "JiraAgent",
    "JiraConfig",
    "SlackAgent",
    "SlackConfig",
    # "DatadogAgent",
    # "DatadogConfig",
    # "PagerDutyAgent",
    # "PagerDutyConfig"
]

__version__ = "1.0.0"
__author__ = "T-Developer System"
__description__ = "External agent integrations for third-party services"
