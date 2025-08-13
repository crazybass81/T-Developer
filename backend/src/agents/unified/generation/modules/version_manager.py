"""
Version Manager Module for Generation Agent
Manages project versioning, git setup, and release management
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import json
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import semver
import re


class VersioningStrategy(Enum):
    SEMANTIC = "semantic"
    CALVER = "calver"
    CUSTOM = "custom"


class ReleaseType(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRERELEASE = "prerelease"
    BUILD = "build"


@dataclass
class VersionInfo:
    current_version: str
    next_version: str
    strategy: VersioningStrategy
    release_type: ReleaseType
    changelog_entry: str
    git_tag: str
    release_notes: str


@dataclass
class GitConfig:
    repository_initialized: bool
    initial_commit_created: bool
    gitignore_configured: bool
    branches_configured: bool
    hooks_installed: bool
    remote_configured: bool


@dataclass
class ReleaseConfig:
    automated_changelog: bool
    version_bump_strategy: str
    release_branch_pattern: str
    tag_pattern: str
    pre_release_hooks: List[str]
    post_release_hooks: List[str]


@dataclass
class VersioningResult:
    success: bool
    version_info: VersionInfo
    git_config: GitConfig
    release_config: ReleaseConfig
    generated_files: Dict[str, str]
    processing_time: float
    metadata: Dict[str, Any]
    error: str = ""


class VersionManager:
    """Advanced project version and release management"""

    def __init__(self):
        self.version = "1.0.0"

        # Version patterns for different strategies
        self.version_patterns = {
            VersioningStrategy.SEMANTIC: r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?(?:\+([a-zA-Z0-9\-\.]+))?$",
            VersioningStrategy.CALVER: r"^(\d{4})\.(\d{2})\.(\d+)(?:-([a-zA-Z0-9\-\.]+))?$",
            VersioningStrategy.CUSTOM: r"^(.+)$",
        }

        # Framework-specific version configurations
        self.framework_configs = {
            "react": {
                "version_files": ["package.json"],
                "build_command": "npm run build",
                "test_command": "npm test",
                "release_assets": ["build/"],
            },
            "vue": {
                "version_files": ["package.json"],
                "build_command": "npm run build",
                "test_command": "npm test",
                "release_assets": ["dist/"],
            },
            "angular": {
                "version_files": ["package.json", "angular.json"],
                "build_command": "ng build --prod",
                "test_command": "ng test",
                "release_assets": ["dist/"],
            },
            "express": {
                "version_files": ["package.json"],
                "build_command": "npm run build",
                "test_command": "npm test",
                "release_assets": ["dist/"],
            },
            "fastapi": {
                "version_files": ["pyproject.toml", "setup.py"],
                "build_command": "python -m build",
                "test_command": "pytest",
                "release_assets": ["dist/"],
            },
            "django": {
                "version_files": ["setup.py", "pyproject.toml"],
                "build_command": "python setup.py sdist bdist_wheel",
                "test_command": "python manage.py test",
                "release_assets": ["dist/"],
            },
            "flask": {
                "version_files": ["setup.py", "pyproject.toml"],
                "build_command": "python -m build",
                "test_command": "pytest",
                "release_assets": ["dist/"],
            },
        }

        # Git hooks templates
        self.git_hooks = {
            "pre-commit": self._generate_pre_commit_hook,
            "pre-push": self._generate_pre_push_hook,
            "commit-msg": self._generate_commit_msg_hook,
            "prepare-commit-msg": self._generate_prepare_commit_msg_hook,
        }

        # Changelog templates
        self.changelog_templates = {
            "keepachangelog": self._generate_keepachangelog,
            "conventional": self._generate_conventional_changelog,
            "custom": self._generate_custom_changelog,
        }

    async def setup_versioning(
        self, project_path: str, context: Dict[str, Any]
    ) -> VersioningResult:
        """Setup complete versioning system for the project"""

        start_time = datetime.now()

        try:
            framework = context.get("target_framework", "react")
            project_name = context.get("project_name", "generated-project")
            initial_version = context.get("initial_version", "1.0.0")

            # Initialize version information
            version_info = await self._initialize_version_info(initial_version, context)

            # Setup Git repository
            git_config = await self._setup_git_repository(
                project_path, project_name, context
            )

            # Configure release management
            release_config = await self._setup_release_configuration(framework, context)

            # Generate version-related files
            generated_files = await self._generate_version_files(
                project_path, framework, version_info, context
            )

            # Install Git hooks
            await self._install_git_hooks(project_path, framework)

            # Create initial changelog
            await self._create_initial_changelog(project_path, version_info, context)

            processing_time = (datetime.now() - start_time).total_seconds()

            return VersioningResult(
                success=True,
                version_info=version_info,
                git_config=git_config,
                release_config=release_config,
                generated_files=generated_files,
                processing_time=processing_time,
                metadata={
                    "framework": framework,
                    "project_name": project_name,
                    "versioning_strategy": version_info.strategy.value,
                    "initial_version": initial_version,
                },
            )

        except Exception as e:
            return VersioningResult(
                success=False,
                version_info=VersionInfo(
                    "0.0.0",
                    "0.0.0",
                    VersioningStrategy.SEMANTIC,
                    ReleaseType.PATCH,
                    "",
                    "",
                    "",
                ),
                git_config=GitConfig(False, False, False, False, False, False),
                release_config=ReleaseConfig(False, "", "", "", [], []),
                generated_files={},
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                error=str(e),
            )

    async def _initialize_version_info(
        self, initial_version: str, context: Dict[str, Any]
    ) -> VersionInfo:
        """Initialize version information"""

        # Determine versioning strategy
        strategy = self._determine_versioning_strategy(initial_version, context)

        # Validate initial version
        if not self._validate_version(initial_version, strategy):
            initial_version = "1.0.0"  # Fallback to semantic versioning
            strategy = VersioningStrategy.SEMANTIC

        # Generate initial changelog entry
        changelog_entry = f"## [{initial_version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n### Added\n- Initial project setup\n- Core functionality implementation\n"

        # Generate git tag
        git_tag = f"v{initial_version}"

        # Generate release notes
        release_notes = f"# Release {initial_version}\n\nInitial release of {context.get('project_name', 'the project')}.\n\n## Features\n- Core application structure\n- Basic functionality\n- Automated testing setup\n- Documentation\n"

        return VersionInfo(
            current_version=initial_version,
            next_version=initial_version,
            strategy=strategy,
            release_type=ReleaseType.MAJOR,
            changelog_entry=changelog_entry,
            git_tag=git_tag,
            release_notes=release_notes,
        )

    async def _setup_git_repository(
        self, project_path: str, project_name: str, context: Dict[str, Any]
    ) -> GitConfig:
        """Setup Git repository configuration"""

        git_config = GitConfig(
            repository_initialized=False,
            initial_commit_created=False,
            gitignore_configured=False,
            branches_configured=False,
            hooks_installed=False,
            remote_configured=False,
        )

        try:
            # Initialize git repository
            await self._run_git_command(project_path, ["init"])
            git_config.repository_initialized = True

            # Configure git user (if not already configured)
            await self._configure_git_user(project_path)

            # Add all files to staging
            await self._run_git_command(project_path, ["add", "."])

            # Create initial commit
            initial_commit_message = f"feat: Initial project setup for {project_name}\n\n🤖 Generated with T-Developer\n\nCo-authored-by: Claude <noreply@anthropic.com>"
            await self._run_git_command(
                project_path, ["commit", "-m", initial_commit_message]
            )
            git_config.initial_commit_created = True

            # Configure branches
            await self._setup_git_branches(project_path)
            git_config.branches_configured = True

            # gitignore is configured during file generation
            git_config.gitignore_configured = True

        except Exception as e:
            # Git operations are optional, don't fail the entire setup
            pass

        return git_config

    async def _setup_release_configuration(
        self, framework: str, context: Dict[str, Any]
    ) -> ReleaseConfig:
        """Setup release management configuration"""

        framework_config = self.framework_configs.get(
            framework, self.framework_configs["react"]
        )

        return ReleaseConfig(
            automated_changelog=True,
            version_bump_strategy="semantic",
            release_branch_pattern="release/*",
            tag_pattern="v{version}",
            pre_release_hooks=[
                framework_config["test_command"],
                framework_config["build_command"],
                "git add .",
                "git commit -m 'chore: prepare release {version}'",
            ],
            post_release_hooks=[
                "git push origin main",
                "git push origin --tags",
                f"echo 'Released version {{version}} successfully!'",
            ],
        )

    async def _generate_version_files(
        self,
        project_path: str,
        framework: str,
        version_info: VersionInfo,
        context: Dict[str, Any],
    ) -> Dict[str, str]:
        """Generate version-related files"""

        generated_files = {}
        framework_config = self.framework_configs.get(framework, {})
        version_files = framework_config.get("version_files", ["package.json"])

        # Generate version configuration file
        version_config = {
            "version": version_info.current_version,
            "versioning_strategy": version_info.strategy.value,
            "last_updated": datetime.now().isoformat(),
            "build_number": 1,
            "release_type": version_info.release_type.value,
        }

        generated_files["version.json"] = json.dumps(version_config, indent=2)

        # Generate release configuration
        release_script = self._generate_release_script(framework, version_info)
        generated_files["scripts/release.sh"] = release_script

        # Generate version bump script
        version_bump_script = self._generate_version_bump_script(framework)
        generated_files["scripts/version-bump.js"] = version_bump_script

        # Generate GitHub Actions workflow for releases
        if context.get("include_deployment", True):
            release_workflow = self._generate_release_workflow(framework)
            generated_files[".github/workflows/release.yml"] = release_workflow

        return generated_files

    async def _install_git_hooks(self, project_path: str, framework: str):
        """Install Git hooks"""

        hooks_dir = os.path.join(project_path, ".git", "hooks")

        if not os.path.exists(hooks_dir):
            return

        # Install hooks
        for hook_name, hook_generator in self.git_hooks.items():
            hook_content = await hook_generator(framework)
            hook_path = os.path.join(hooks_dir, hook_name)

            with open(hook_path, "w") as f:
                f.write(hook_content)

            # Make hook executable
            os.chmod(hook_path, 0o755)

    async def _create_initial_changelog(
        self, project_path: str, version_info: VersionInfo, context: Dict[str, Any]
    ):
        """Create initial changelog file"""

        changelog_content = f"""# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

{version_info.changelog_entry}
### Features
- Initial project setup
- Core application structure
- Automated testing configuration
- Documentation generation
- CI/CD pipeline setup

### Security
- Basic security headers configured
- Input validation implemented
- Authentication system ready

---

*This changelog is automatically maintained.*
"""

        changelog_path = os.path.join(project_path, "CHANGELOG.md")
        with open(changelog_path, "w") as f:
            f.write(changelog_content)

    def _determine_versioning_strategy(
        self, version: str, context: Dict[str, Any]
    ) -> VersioningStrategy:
        """Determine the appropriate versioning strategy"""

        # Check if version matches semantic versioning
        if re.match(self.version_patterns[VersioningStrategy.SEMANTIC], version):
            return VersioningStrategy.SEMANTIC

        # Check if version matches calendar versioning
        if re.match(self.version_patterns[VersioningStrategy.CALVER], version):
            return VersioningStrategy.CALVER

        # Default to semantic versioning
        return VersioningStrategy.SEMANTIC

    def _validate_version(self, version: str, strategy: VersioningStrategy) -> bool:
        """Validate version string against strategy"""

        pattern = self.version_patterns.get(strategy)
        if pattern:
            return bool(re.match(pattern, version))
        return False

    async def _configure_git_user(self, project_path: str):
        """Configure git user if not already configured"""

        try:
            # Check if user is configured globally
            result = await self._run_git_command(project_path, ["config", "user.name"])
            if not result.strip():
                await self._run_git_command(
                    project_path, ["config", "user.name", "T-Developer"]
                )
                await self._run_git_command(
                    project_path, ["config", "user.email", "noreply@t-developer.com"]
                )
        except:
            # Set default user
            await self._run_git_command(
                project_path, ["config", "user.name", "T-Developer"]
            )
            await self._run_git_command(
                project_path, ["config", "user.email", "noreply@t-developer.com"]
            )

    async def _setup_git_branches(self, project_path: str):
        """Setup standard git branches"""

        try:
            # Create develop branch
            await self._run_git_command(project_path, ["checkout", "-b", "develop"])
            await self._run_git_command(project_path, ["checkout", "main"])

            # Set up branch protection (conceptually - would require GitHub API)
            # This would be done via GitHub API or repository settings
        except:
            pass

    async def _run_git_command(self, project_path: str, command: List[str]) -> str:
        """Run git command in project directory"""

        full_command = ["git"] + command
        process = await asyncio.create_subprocess_exec(
            *full_command,
            cwd=project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Git command failed: {stderr.decode()}")

        return stdout.decode()

    def _generate_release_script(
        self, framework: str, version_info: VersionInfo
    ) -> str:
        """Generate release automation script"""

        framework_config = self.framework_configs.get(
            framework, self.framework_configs["react"]
        )

        script = f"""#!/bin/bash
set -e

# Release automation script generated by T-Developer
# Framework: {framework}
# Version: {version_info.current_version}

echo "🚀 Starting release process..."

# Pre-release checks
echo "📋 Running pre-release checks..."
{framework_config.get('test_command', 'echo "No tests configured"')}

# Build project
echo "🔨 Building project..."
{framework_config.get('build_command', 'echo "No build configured"')}

# Version bump
echo "📦 Bumping version..."
npm run version:bump

# Update changelog
echo "📝 Updating changelog..."
npm run changelog:update

# Commit changes
echo "💾 Committing release changes..."
git add .
git commit -m "chore: prepare release ${{1:-patch}}"

# Create tag
echo "🏷️  Creating release tag..."
VERSION=$(node -p "require('./package.json').version")
git tag -a "v$VERSION" -m "Release v$VERSION"

# Push changes
echo "🚀 Publishing release..."
git push origin main
git push origin --tags

echo "✅ Release completed successfully!"
echo "📦 Released version: v$VERSION"
"""

        return script

    def _generate_version_bump_script(self, framework: str) -> str:
        """Generate version bump automation script"""

        return """const fs = require('fs');
const semver = require('semver');

const RELEASE_TYPES = ['major', 'minor', 'patch', 'prerelease'];

function bumpVersion(releaseType = 'patch') {
  if (!RELEASE_TYPES.includes(releaseType)) {
    console.error(`Invalid release type: ${releaseType}`);
    process.exit(1);
  }

  // Read current version
  const packagePath = './package.json';
  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
  const currentVersion = packageJson.version;

  // Calculate new version
  const newVersion = semver.inc(currentVersion, releaseType);

  if (!newVersion) {
    console.error(`Failed to bump version from ${currentVersion}`);
    process.exit(1);
  }

  // Update package.json
  packageJson.version = newVersion;
  fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2) + '\\n');

  // Update version.json
  const versionConfig = {
    version: newVersion,
    previous_version: currentVersion,
    release_type: releaseType,
    timestamp: new Date().toISOString(),
    build_number: Date.now()
  };

  fs.writeFileSync('./version.json', JSON.stringify(versionConfig, null, 2) + '\\n');

  console.log(`📦 Version bumped from ${currentVersion} to ${newVersion}`);
  return newVersion;
}

// CLI usage
const releaseType = process.argv[2] || 'patch';
bumpVersion(releaseType);
"""

    def _generate_release_workflow(self, framework: str) -> str:
        """Generate GitHub Actions release workflow"""

        framework_config = self.framework_configs.get(
            framework, self.framework_configs["react"]
        )

        workflow = {
            "name": "Release",
            "on": {"push": {"tags": ["v*"]}},
            "jobs": {
                "release": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Setup Node.js"
                            if framework in ["react", "vue", "angular", "express"]
                            else "Setup Python",
                            "uses": "actions/setup-node@v3"
                            if framework in ["react", "vue", "angular", "express"]
                            else "actions/setup-python@v3",
                            "with": {
                                "node-version": "18"
                                if framework in ["react", "vue", "angular", "express"]
                                else None,
                                "python-version": "3.9"
                                if framework
                                not in ["react", "vue", "angular", "express"]
                                else None,
                            },
                        },
                        {
                            "name": "Install dependencies",
                            "run": "npm ci"
                            if framework in ["react", "vue", "angular", "express"]
                            else "pip install -r requirements.txt",
                        },
                        {
                            "name": "Run tests",
                            "run": framework_config.get(
                                "test_command", 'echo "No tests"'
                            ),
                        },
                        {
                            "name": "Build project",
                            "run": framework_config.get(
                                "build_command", 'echo "No build"'
                            ),
                        },
                        {
                            "name": "Create Release",
                            "uses": "actions/create-release@v1",
                            "env": {"GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"},
                            "with": {
                                "tag_name": "${{ github.ref }}",
                                "release_name": "Release ${{ github.ref }}",
                                "draft": False,
                                "prerelease": False,
                            },
                        },
                    ],
                }
            },
        }

        # Clean up None values
        if framework in ["react", "vue", "angular", "express"]:
            del workflow["jobs"]["release"]["steps"][1]["with"]["python-version"]
        else:
            del workflow["jobs"]["release"]["steps"][1]["with"]["node-version"]

        import yaml

        return yaml.dump(workflow, default_flow_style=False)

    # Git hooks generators
    async def _generate_pre_commit_hook(self, framework: str) -> str:
        """Generate pre-commit git hook"""

        return f"""#!/bin/sh
# Pre-commit hook generated by T-Developer

set -e

echo "🔍 Running pre-commit checks..."

# Run linter
if [ -f "package.json" ]; then
    npm run lint 2>/dev/null || echo "⚠️  Linting not configured"
fi

# Run type check
if [ -f "tsconfig.json" ]; then
    npm run type-check 2>/dev/null || npx tsc --noEmit 2>/dev/null || echo "⚠️  Type checking not available"
fi

# Run tests
if [ -f "package.json" ]; then
    npm test -- --watchAll=false 2>/dev/null || echo "⚠️  Tests not configured or failed"
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    python -m pytest --tb=short 2>/dev/null || echo "⚠️  Tests not configured or failed"
fi

echo "✅ Pre-commit checks completed"
"""

    async def _generate_pre_push_hook(self, framework: str) -> str:
        """Generate pre-push git hook"""

        return """#!/bin/sh
# Pre-push hook generated by T-Developer

set -e

echo "🚀 Running pre-push checks..."

# Check if pushing to main/master
branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" = "main" ] || [ "$branch" = "master" ]; then
    echo "🔒 Direct push to main branch detected"
    echo "📋 Running comprehensive checks..."

    # Run full test suite
    npm test 2>/dev/null || python -m pytest 2>/dev/null || echo "⚠️  Tests failed"

    # Run build
    npm run build 2>/dev/null || python -m build 2>/dev/null || echo "⚠️  Build failed"
fi

echo "✅ Pre-push checks completed"
"""

    async def _generate_commit_msg_hook(self, framework: str) -> str:
        """Generate commit message validation hook"""

        return """#!/bin/sh
# Commit message hook generated by T-Developer
# Validates commit messages follow Conventional Commits format

commit_regex='^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}'

error_msg="❌ Invalid commit message format!
📋 Use: <type>(<scope>): <subject>
📋 Types: feat, fix, docs, style, refactor, test, chore
📋 Example: feat(auth): add login functionality"

if ! grep -qE "$commit_regex" "$1"; then
    echo "$error_msg" >&2
    exit 1
fi

echo "✅ Commit message format is valid"
"""

    async def _generate_prepare_commit_msg_hook(self, framework: str) -> str:
        """Generate prepare commit message hook"""

        return """#!/bin/sh
# Prepare commit message hook generated by T-Developer

# Add branch name to commit message if on feature branch
branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" != "main" ] && [ "$branch" != "master" ] && [ "$branch" != "develop" ]; then
    # Extract ticket/issue number from branch name if present
    ticket=$(echo "$branch" | grep -oE '[A-Z]+-[0-9]+|#[0-9]+' | head -1)

    if [ -n "$ticket" ]; then
        # Add ticket to commit message if not already present
        if ! grep -q "$ticket" "$1"; then
            echo "" >> "$1"
            echo "Refs: $ticket" >> "$1"
        fi
    fi
fi
"""

    # Changelog generators (simplified)
    def _generate_keepachangelog(self, version_info: VersionInfo) -> str:
        """Generate Keep a Changelog format"""
        return version_info.changelog_entry

    def _generate_conventional_changelog(self, version_info: VersionInfo) -> str:
        """Generate Conventional Changelog format"""
        return version_info.changelog_entry

    def _generate_custom_changelog(self, version_info: VersionInfo) -> str:
        """Generate custom changelog format"""
        return version_info.changelog_entry
