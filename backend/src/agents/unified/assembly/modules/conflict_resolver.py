"""
Conflict Resolver Module for Assembly Agent
Resolves file conflicts and ensures consistent project structure
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import asyncio
import os
import hashlib
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import difflib
import json


class ConflictType(Enum):
    DUPLICATE_FILES = "duplicate_files"
    CONFLICTING_DEPENDENCIES = "conflicting_dependencies"
    INCOMPATIBLE_CONFIGURATIONS = "incompatible_configurations"
    NAMING_CONFLICTS = "naming_conflicts"
    VERSION_CONFLICTS = "version_conflicts"
    IMPORT_CONFLICTS = "import_conflicts"


class ResolutionStrategy(Enum):
    MERGE = "merge"
    OVERWRITE = "overwrite"
    RENAME = "rename"
    COMBINE = "combine"
    MANUAL = "manual"
    SKIP = "skip"


@dataclass
class FileConflict:
    conflict_type: ConflictType
    files_involved: List[str]
    description: str
    severity: str  # low, medium, high, critical
    resolution_strategy: ResolutionStrategy
    resolution_details: Dict[str, Any]
    auto_resolvable: bool


@dataclass
class ConflictResolutionResult:
    success: bool
    resolved_files: Dict[str, str]
    conflicts_found: List[FileConflict]
    conflicts_resolved: int
    conflicts_remaining: int
    resolution_log: List[str]
    processing_time: float
    error: str = ""


class ConflictResolver:
    """Advanced conflict resolution system"""

    def __init__(self):
        self.version = "1.0.0"

        # Resolution strategies by conflict type
        self.resolution_strategies = {
            ConflictType.DUPLICATE_FILES: [
                ResolutionStrategy.MERGE,
                ResolutionStrategy.OVERWRITE,
                ResolutionStrategy.RENAME,
            ],
            ConflictType.CONFLICTING_DEPENDENCIES: [
                ResolutionStrategy.COMBINE,
                ResolutionStrategy.OVERWRITE,
            ],
            ConflictType.INCOMPATIBLE_CONFIGURATIONS: [
                ResolutionStrategy.MERGE,
                ResolutionStrategy.MANUAL,
            ],
            ConflictType.NAMING_CONFLICTS: [
                ResolutionStrategy.RENAME,
                ResolutionStrategy.OVERWRITE,
            ],
            ConflictType.VERSION_CONFLICTS: [
                ResolutionStrategy.COMBINE,
                ResolutionStrategy.OVERWRITE,
            ],
            ConflictType.IMPORT_CONFLICTS: [
                ResolutionStrategy.MERGE,
                ResolutionStrategy.RENAME,
            ],
        }

        # Auto-resolution rules
        self.auto_resolution_rules = {
            # Package.json files should be merged
            "package.json": {
                "strategy": ResolutionStrategy.MERGE,
                "merge_fields": [
                    "dependencies",
                    "devDependencies",
                    "scripts",
                    "keywords",
                ],
            },
            # Requirements.txt should be combined
            "requirements.txt": {
                "strategy": ResolutionStrategy.COMBINE,
                "combine_method": "unique_lines",
            },
            # Config files should be carefully merged
            ".env": {
                "strategy": ResolutionStrategy.MERGE,
                "conflict_resolution": "prefer_first",
            },
            # README files should be combined
            "README.md": {
                "strategy": ResolutionStrategy.COMBINE,
                "combine_method": "append_sections",
            },
            # Gitignore should be combined
            ".gitignore": {
                "strategy": ResolutionStrategy.COMBINE,
                "combine_method": "unique_lines",
            },
        }

        # File similarity thresholds
        self.similarity_thresholds = {
            "exact_match": 1.0,
            "high_similarity": 0.9,
            "medium_similarity": 0.7,
            "low_similarity": 0.3,
        }

    async def resolve_conflicts(
        self, organized_files: Dict[str, Any], context: Dict[str, Any]
    ) -> ConflictResolutionResult:
        """Resolve all file conflicts in the organized project"""

        start_time = datetime.now()
        resolution_log = []

        try:
            # Detect conflicts
            conflicts = await self._detect_conflicts(organized_files)
            resolution_log.append(f"Detected {len(conflicts)} conflicts")

            resolved_files = {}
            conflicts_resolved = 0

            # Resolve each conflict
            for conflict in conflicts:
                resolution_result = await self._resolve_single_conflict(
                    conflict, organized_files, context
                )

                if resolution_result["resolved"]:
                    conflicts_resolved += 1
                    resolved_files.update(resolution_result["files"])
                    resolution_log.append(
                        f"Resolved {conflict.conflict_type.value}: {resolution_result['description']}"
                    )
                else:
                    resolution_log.append(
                        f"Could not resolve {conflict.conflict_type.value}: {resolution_result['reason']}"
                    )

            # Add non-conflicting files
            for file_path, file_data in organized_files.items():
                if not self._is_file_in_conflicts(file_path, conflicts):
                    if hasattr(file_data, "organized_path"):
                        # File organizer result
                        with open(file_data.organized_path, "r", encoding="utf-8") as f:
                            resolved_files[file_path] = f.read()
                    else:
                        # Direct file content
                        resolved_files[file_path] = file_data

            processing_time = (datetime.now() - start_time).total_seconds()

            return ConflictResolutionResult(
                success=True,
                resolved_files=resolved_files,
                conflicts_found=conflicts,
                conflicts_resolved=conflicts_resolved,
                conflicts_remaining=len(conflicts) - conflicts_resolved,
                resolution_log=resolution_log,
                processing_time=processing_time,
            )

        except Exception as e:
            return ConflictResolutionResult(
                success=False,
                resolved_files={},
                conflicts_found=[],
                conflicts_resolved=0,
                conflicts_remaining=0,
                resolution_log=resolution_log,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error=str(e),
            )

    async def _detect_conflicts(
        self, organized_files: Dict[str, Any]
    ) -> List[FileConflict]:
        """Detect various types of conflicts in organized files"""

        conflicts = []

        # Group files by final path to detect duplicates
        path_groups = {}
        for file_path, file_data in organized_files.items():
            if hasattr(file_data, "organized_path"):
                final_path = os.path.basename(file_data.organized_path)
            else:
                final_path = os.path.basename(file_path)

            if final_path not in path_groups:
                path_groups[final_path] = []
            path_groups[final_path].append(file_path)

        # Detect duplicate files
        for final_path, file_paths in path_groups.items():
            if len(file_paths) > 1:
                # Check if files are actually different
                file_contents = []
                for fp in file_paths:
                    if hasattr(organized_files[fp], "organized_path"):
                        with open(
                            organized_files[fp].organized_path, "r", encoding="utf-8"
                        ) as f:
                            file_contents.append(f.read())
                    else:
                        file_contents.append(organized_files[fp])

                # If contents are different, it's a conflict
                if len(set(file_contents)) > 1:
                    conflict = FileConflict(
                        conflict_type=ConflictType.DUPLICATE_FILES,
                        files_involved=file_paths,
                        description=f"Multiple files want to be named '{final_path}' with different contents",
                        severity="medium",
                        resolution_strategy=self._determine_resolution_strategy(
                            final_path, file_contents
                        ),
                        resolution_details={
                            "final_path": final_path,
                            "contents": file_contents,
                        },
                        auto_resolvable=final_path in self.auto_resolution_rules,
                    )
                    conflicts.append(conflict)

        # Detect dependency conflicts (for package.json, requirements.txt, etc.)
        dependency_conflicts = await self._detect_dependency_conflicts(organized_files)
        conflicts.extend(dependency_conflicts)

        # Detect configuration conflicts
        config_conflicts = await self._detect_configuration_conflicts(organized_files)
        conflicts.extend(config_conflicts)

        # Detect import/export conflicts
        import_conflicts = await self._detect_import_conflicts(organized_files)
        conflicts.extend(import_conflicts)

        return conflicts

    async def _detect_dependency_conflicts(
        self, organized_files: Dict[str, Any]
    ) -> List[FileConflict]:
        """Detect conflicts in dependency files"""

        conflicts = []

        # Check package.json files
        package_json_files = []
        for file_path, file_data in organized_files.items():
            if os.path.basename(file_path) == "package.json":
                package_json_files.append((file_path, file_data))

        if len(package_json_files) > 1:
            # Parse and compare dependencies
            dependency_sets = []
            for file_path, file_data in package_json_files:
                try:
                    if hasattr(file_data, "organized_path"):
                        with open(file_data.organized_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    else:
                        content = file_data

                    package_data = json.loads(content)
                    deps = package_data.get("dependencies", {})
                    dev_deps = package_data.get("devDependencies", {})
                    dependency_sets.append((file_path, deps, dev_deps))
                except:
                    continue

            # Check for conflicting versions
            all_deps = {}
            conflicting_deps = {}

            for file_path, deps, dev_deps in dependency_sets:
                for dep_name, version in {**deps, **dev_deps}.items():
                    if dep_name in all_deps and all_deps[dep_name] != version:
                        if dep_name not in conflicting_deps:
                            conflicting_deps[dep_name] = []
                        conflicting_deps[dep_name].append((file_path, version))
                    else:
                        all_deps[dep_name] = version

            if conflicting_deps:
                conflict = FileConflict(
                    conflict_type=ConflictType.CONFLICTING_DEPENDENCIES,
                    files_involved=[fp for fp, _, _ in dependency_sets],
                    description=f"Conflicting dependency versions: {list(conflicting_deps.keys())}",
                    severity="high",
                    resolution_strategy=ResolutionStrategy.COMBINE,
                    resolution_details={"conflicting_deps": conflicting_deps},
                    auto_resolvable=True,
                )
                conflicts.append(conflict)

        # Similar logic for requirements.txt, Cargo.toml, etc.

        return conflicts

    async def _detect_configuration_conflicts(
        self, organized_files: Dict[str, Any]
    ) -> List[FileConflict]:
        """Detect conflicts in configuration files"""

        conflicts = []

        # Check for conflicting environment variables
        env_files = []
        for file_path, file_data in organized_files.items():
            if ".env" in os.path.basename(file_path):
                env_files.append((file_path, file_data))

        if len(env_files) > 1:
            env_vars = {}
            conflicting_vars = {}

            for file_path, file_data in env_files:
                if hasattr(file_data, "organized_path"):
                    with open(file_data.organized_path, "r", encoding="utf-8") as f:
                        content = f.read()
                else:
                    content = file_data

                # Parse env variables
                for line in content.split("\n"):
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()

                        if key in env_vars and env_vars[key] != value:
                            if key not in conflicting_vars:
                                conflicting_vars[key] = []
                            conflicting_vars[key].append((file_path, value))
                        else:
                            env_vars[key] = value

            if conflicting_vars:
                conflict = FileConflict(
                    conflict_type=ConflictType.INCOMPATIBLE_CONFIGURATIONS,
                    files_involved=[fp for fp, _ in env_files],
                    description=f"Conflicting environment variables: {list(conflicting_vars.keys())}",
                    severity="medium",
                    resolution_strategy=ResolutionStrategy.MERGE,
                    resolution_details={"conflicting_vars": conflicting_vars},
                    auto_resolvable=True,
                )
                conflicts.append(conflict)

        return conflicts

    async def _detect_import_conflicts(
        self, organized_files: Dict[str, Any]
    ) -> List[FileConflict]:
        """Detect import/export conflicts"""

        conflicts = []

        # This would analyze import statements and detect circular dependencies
        # or conflicting exports in a real implementation

        return conflicts

    def _determine_resolution_strategy(
        self, filename: str, file_contents: List[str]
    ) -> ResolutionStrategy:
        """Determine the best resolution strategy for a conflict"""

        if filename in self.auto_resolution_rules:
            return self.auto_resolution_rules[filename]["strategy"]

        # Analyze content similarity
        if len(file_contents) == 2:
            similarity = self._calculate_similarity(file_contents[0], file_contents[1])

            if similarity >= self.similarity_thresholds["high_similarity"]:
                return ResolutionStrategy.MERGE
            elif similarity >= self.similarity_thresholds["medium_similarity"]:
                return ResolutionStrategy.COMBINE
            else:
                return ResolutionStrategy.RENAME

        return ResolutionStrategy.MERGE

    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two file contents"""

        lines1 = content1.splitlines()
        lines2 = content2.splitlines()

        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        return matcher.ratio()

    async def _resolve_single_conflict(
        self,
        conflict: FileConflict,
        organized_files: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve a single conflict"""

        strategy = conflict.resolution_strategy

        if strategy == ResolutionStrategy.MERGE:
            return await self._merge_files(conflict, organized_files)
        elif strategy == ResolutionStrategy.COMBINE:
            return await self._combine_files(conflict, organized_files)
        elif strategy == ResolutionStrategy.OVERWRITE:
            return await self._overwrite_files(conflict, organized_files)
        elif strategy == ResolutionStrategy.RENAME:
            return await self._rename_files(conflict, organized_files)
        else:
            return {
                "resolved": False,
                "reason": f"Strategy {strategy.value} not implemented",
                "files": {},
            }

    async def _merge_files(
        self, conflict: FileConflict, organized_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge conflicting files intelligently"""

        files_involved = conflict.files_involved

        if len(files_involved) == 2:
            file1_path, file2_path = files_involved

            # Get file contents
            if hasattr(organized_files[file1_path], "organized_path"):
                with open(
                    organized_files[file1_path].organized_path, "r", encoding="utf-8"
                ) as f:
                    content1 = f.read()
            else:
                content1 = organized_files[file1_path]

            if hasattr(organized_files[file2_path], "organized_path"):
                with open(
                    organized_files[file2_path].organized_path, "r", encoding="utf-8"
                ) as f:
                    content2 = f.read()
            else:
                content2 = organized_files[file2_path]

            # Merge based on file type
            filename = os.path.basename(file1_path)

            if filename == "package.json":
                merged_content = await self._merge_package_json(content1, content2)
            elif filename.endswith(".md"):
                merged_content = await self._merge_markdown(content1, content2)
            elif filename == ".gitignore":
                merged_content = await self._merge_gitignore(content1, content2)
            else:
                # Generic merge - combine unique lines
                merged_content = await self._merge_text_files(content1, content2)

            return {
                "resolved": True,
                "description": f"Merged {len(files_involved)} files",
                "files": {file1_path: merged_content},  # Use first file path as primary
            }

        return {
            "resolved": False,
            "reason": "Cannot merge more than 2 files",
            "files": {},
        }

    async def _merge_package_json(self, content1: str, content2: str) -> str:
        """Merge two package.json files"""

        try:
            package1 = json.loads(content1)
            package2 = json.loads(content2)

            merged = package1.copy()

            # Merge dependencies
            if "dependencies" in package2:
                if "dependencies" not in merged:
                    merged["dependencies"] = {}
                merged["dependencies"].update(package2["dependencies"])

            # Merge devDependencies
            if "devDependencies" in package2:
                if "devDependencies" not in merged:
                    merged["devDependencies"] = {}
                merged["devDependencies"].update(package2["devDependencies"])

            # Merge scripts
            if "scripts" in package2:
                if "scripts" not in merged:
                    merged["scripts"] = {}
                merged["scripts"].update(package2["scripts"])

            # Merge keywords
            if "keywords" in package2:
                if "keywords" not in merged:
                    merged["keywords"] = []
                for keyword in package2["keywords"]:
                    if keyword not in merged["keywords"]:
                        merged["keywords"].append(keyword)

            return json.dumps(merged, indent=2)

        except json.JSONDecodeError:
            # Fallback to text merge
            return await self._merge_text_files(content1, content2)

    async def _merge_markdown(self, content1: str, content2: str) -> str:
        """Merge two markdown files"""

        # Simple merge - combine with separator
        separator = "\n\n---\n\n"
        return content1 + separator + content2

    async def _merge_gitignore(self, content1: str, content2: str) -> str:
        """Merge two .gitignore files"""

        lines1 = set(line.strip() for line in content1.split("\n") if line.strip())
        lines2 = set(line.strip() for line in content2.split("\n") if line.strip())

        # Combine unique lines
        all_lines = sorted(lines1.union(lines2))
        return "\n".join(all_lines)

    async def _merge_text_files(self, content1: str, content2: str) -> str:
        """Generic text file merge"""

        lines1 = content1.split("\n")
        lines2 = content2.split("\n")

        # Use difflib to create a merged version
        differ = difflib.unified_diff(lines1, lines2, lineterm="")

        # Simple merge - just combine unique lines
        all_lines = []
        seen_lines = set()

        for line in lines1 + lines2:
            if line not in seen_lines:
                all_lines.append(line)
                seen_lines.add(line)

        return "\n".join(all_lines)

    async def _combine_files(
        self, conflict: FileConflict, organized_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine files by appending content"""

        files_involved = conflict.files_involved
        combined_content = ""

        for i, file_path in enumerate(files_involved):
            if hasattr(organized_files[file_path], "organized_path"):
                with open(
                    organized_files[file_path].organized_path, "r", encoding="utf-8"
                ) as f:
                    content = f.read()
            else:
                content = organized_files[file_path]

            if i > 0:
                combined_content += (
                    "\n\n# --- Content from " + os.path.basename(file_path) + " ---\n\n"
                )

            combined_content += content

        return {
            "resolved": True,
            "description": f"Combined {len(files_involved)} files",
            "files": {files_involved[0]: combined_content},  # Use first file path
        }

    async def _overwrite_files(
        self, conflict: FileConflict, organized_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by overwriting with the first file"""

        files_involved = conflict.files_involved
        primary_file = files_involved[0]

        if hasattr(organized_files[primary_file], "organized_path"):
            with open(
                organized_files[primary_file].organized_path, "r", encoding="utf-8"
            ) as f:
                content = f.read()
        else:
            content = organized_files[primary_file]

        return {
            "resolved": True,
            "description": f"Overwrote with {os.path.basename(primary_file)}",
            "files": {primary_file: content},
        }

    async def _rename_files(
        self, conflict: FileConflict, organized_files: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict by renaming files"""

        files_involved = conflict.files_involved
        resolved_files = {}

        for i, file_path in enumerate(files_involved):
            if hasattr(organized_files[file_path], "organized_path"):
                with open(
                    organized_files[file_path].organized_path, "r", encoding="utf-8"
                ) as f:
                    content = f.read()
            else:
                content = organized_files[file_path]

            if i == 0:
                # Keep first file as is
                resolved_files[file_path] = content
            else:
                # Rename subsequent files
                base_name, ext = os.path.splitext(os.path.basename(file_path))
                new_name = f"{base_name}_{i}{ext}"
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                resolved_files[new_path] = content

        return {
            "resolved": True,
            "description": f"Renamed {len(files_involved) - 1} conflicting files",
            "files": resolved_files,
        }

    def _is_file_in_conflicts(
        self, file_path: str, conflicts: List[FileConflict]
    ) -> bool:
        """Check if a file is involved in any conflicts"""

        for conflict in conflicts:
            if file_path in conflict.files_involved:
                return True
        return False
