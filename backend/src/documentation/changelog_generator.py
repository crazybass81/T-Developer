"""ChangelogGenerator - Day 35
Changelog auto-generation - Size: ~6.5KB"""
import re
from datetime import datetime
from typing import Any, Dict, List


class ChangelogGenerator:
    """Generate changelogs automatically - Size optimized to 6.5KB"""

    def __init__(self):
        self.categories = ["added", "changed", "fixed", "deprecated", "removed", "security"]
        self.version_pattern = r"^\d+\.\d+\.\d+$"

    def generate_from_commits(self, commits: List[Dict[str, Any]]) -> str:
        """Generate changelog from git commits"""
        versions = self._group_by_version(commits)
        changelog = "# Changelog\n\n"
        changelog += "All notable changes to this project will be documented in this file.\n\n"

        for version, changes in versions.items():
            changelog += f"## [{version}] - {changes['date']}\n\n"

            for category in self.categories:
                if category in changes:
                    changelog += f"### {category.capitalize()}\n"
                    for item in changes[category]:
                        changelog += f"- {item}\n"
                    changelog += "\n"

        return changelog

    def parse_commit_message(self, message: str) -> Dict[str, str]:
        """Parse conventional commit message"""
        patterns = {
            "feat": "added",
            "fix": "fixed",
            "docs": "changed",
            "style": "changed",
            "refactor": "changed",
            "perf": "changed",
            "test": "changed",
            "chore": "changed",
            "security": "security",
            "deprecate": "deprecated",
            "remove": "removed",
        }

        # Parse conventional commit
        match = re.match(r"^(\w+)(?:\(([^)]+)\))?: (.+)$", message)
        if match:
            type_str, scope, desc = match.groups()
            category = patterns.get(type_str, "changed")

            if scope:
                return {"category": category, "message": f"**{scope}**: {desc}"}
            else:
                return {"category": category, "message": desc}

        # Fallback for non-conventional commits
        if "fix" in message.lower():
            return {"category": "fixed", "message": message}
        elif "add" in message.lower() or "feat" in message.lower():
            return {"category": "added", "message": message}
        else:
            return {"category": "changed", "message": message}

    def generate_release_notes(self, version: str, changes: Dict[str, List[str]]) -> str:
        """Generate release notes for a version"""
        notes = f"# Release Notes - v{version}\n\n"
        notes += f"Release Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"

        # Summary
        total_changes = sum(len(items) for items in changes.values())
        notes += f"## Summary\n\n"
        notes += f"This release includes {total_changes} changes:\n"

        for category, items in changes.items():
            if items:
                notes += f"- {len(items)} {category}\n"
        notes += "\n"

        # Details
        notes += "## Changes\n\n"

        for category in self.categories:
            if category in changes and changes[category]:
                notes += f"### {category.capitalize()}\n"
                for item in changes[category]:
                    notes += f"- {item}\n"
                notes += "\n"

        # Migration guide if needed
        if "deprecated" in changes or "removed" in changes:
            notes += "## Migration Guide\n\n"
            if "deprecated" in changes:
                notes += "### Deprecated Features\n"
                for item in changes["deprecated"]:
                    notes += f"- {item}\n"
                notes += "\n"
            if "removed" in changes:
                notes += "### Removed Features\n"
                for item in changes["removed"]:
                    notes += f"- {item}\n"
                notes += "\n"

        return notes

    def update_changelog(
        self, existing: str, new_version: str, changes: Dict[str, List[str]]
    ) -> str:
        """Update existing changelog with new version"""
        if not existing:
            existing = "# Changelog\n\n"

        # Find insertion point (after header)
        lines = existing.split("\n")
        insert_idx = 0

        for i, line in enumerate(lines):
            if line.startswith("## "):
                insert_idx = i
                break
            elif i > 5:  # Don't go too far
                insert_idx = i
                break

        # Create new version section
        new_section = f"## [{new_version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"

        for category in self.categories:
            if category in changes and changes[category]:
                new_section += f"### {category.capitalize()}\n"
                for item in changes[category]:
                    new_section += f"- {item}\n"
                new_section += "\n"

        # Insert new section
        lines.insert(insert_idx, new_section)

        return "\n".join(lines)

    def _group_by_version(self, commits: List[Dict[str, Any]]) -> Dict[str, Dict]:
        """Group commits by version"""
        versions = {}
        current_version = "Unreleased"

        for commit in commits:
            # Check for version tag
            if "tag" in commit and re.match(self.version_pattern, commit["tag"]):
                current_version = commit["tag"]
                if current_version not in versions:
                    versions[current_version] = {
                        "date": commit.get("date", datetime.now().strftime("%Y-%m-%d"))
                    }

            # Parse commit message
            parsed = self.parse_commit_message(commit.get("message", ""))
            category = parsed["category"]

            if current_version not in versions:
                versions[current_version] = {"date": datetime.now().strftime("%Y-%m-%d")}

            if category not in versions[current_version]:
                versions[current_version][category] = []

            versions[current_version][category].append(parsed["message"])

        return versions
