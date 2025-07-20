# T-Developer Workspace

This directory contains target repositories that T-Developer works with.

## Structure

- `target_repos/` - Contains cloned target repositories that T-Developer modifies
  - Each task gets its own subdirectory named with the task ID

## Purpose

T-Developer doesn't modify itself. Instead, it clones and modifies target repositories specified in the task configuration. This workspace directory serves as a container for these target repositories.

When a user requests a new feature or modification, T-Developer:

1. Clones the target repository into a task-specific directory under `target_repos/`
2. Makes the requested changes to the code in that directory
3. Commits and pushes the changes to the target repository
4. Creates a pull request for review

This approach ensures that T-Developer acts as a development assistant that creates new functionality in target repositories rather than duplicating itself.