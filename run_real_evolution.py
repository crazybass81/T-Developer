#!/usr/bin/env python3
"""Run REAL T-Developer evolution with actual AI and code modification."""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import git

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv

from packages.agents.ai_integration import get_ai_provider

load_dotenv()


class RealEvolutionSystem:
    """Real self-evolution system that actually modifies code."""

    def __init__(self, target_path: str = "./packages"):
        """Initialize the evolution system."""
        self.target_path = Path(target_path)
        self.ai = get_ai_provider()
        self.repo = git.Repo(".")
        self.results = []

        # Check if we have API keys
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            print("⚠️ No API keys found. Using mock mode.")
            self.mock_mode = True
        else:
            print("✅ API keys found. Using REAL AI!")
            self.mock_mode = False

    def analyze_codebase(self) -> dict:
        """Step 1: Analyze the codebase using real AI."""
        print("\n📚 PHASE 1: ANALYZING CODEBASE WITH AI...")

        # Find Python files
        py_files = list(self.target_path.rglob("*.py"))[:5]  # Limit for demo

        all_findings = []
        all_metrics = {}

        for py_file in py_files:
            print(f"  Analyzing: {py_file}")

            try:
                with open(py_file) as f:
                    code = f.read()

                # Use real AI to analyze
                analysis = self.ai.analyze_code(
                    code=code, problem="improve code quality, add documentation, fix issues"
                )

                all_findings.extend(analysis.get("findings", []))
                all_metrics[str(py_file)] = analysis.get("metrics", {})

            except Exception as e:
                print(f"    Error analyzing {py_file}: {e}")

        print(f"\n  Found {len(all_findings)} total issues across {len(py_files)} files")

        return {
            "findings": all_findings[:10],  # Top 10 issues
            "metrics": all_metrics,
            "files_analyzed": len(py_files),
        }

    def create_plan(self, analysis: dict) -> dict:
        """Step 2: Create improvement plan using AI."""
        print("\n📋 PHASE 2: CREATING IMPROVEMENT PLAN WITH AI...")

        # Use AI to create plan
        plan = self.ai.create_improvement_plan(
            findings=analysis["findings"], metrics=analysis["metrics"]
        )

        print(f"  Generated {len(plan.get('tasks', []))} improvement tasks")
        for task in plan.get("tasks", [])[:3]:
            print(f"    - {task['action']} ({task['priority']})")

        return plan

    def execute_improvements(self, plan: dict) -> dict:
        """Step 3: Execute improvements - actually modify code!"""
        print("\n🔧 PHASE 3: EXECUTING IMPROVEMENTS...")

        if os.getenv("ENABLE_CODE_MODIFICATION") != "true":
            print("  ⚠️ Code modification disabled. Set ENABLE_CODE_MODIFICATION=true to enable.")
            return {"status": "simulated", "changes": []}

        changes = []

        for task in plan.get("tasks", [])[:2]:  # Limit to 2 tasks for safety
            print(f"\n  Executing: {task['action']}")

            # Find target file
            target = task.get("target", "base.py")
            target_file = self.target_path / target if "/" in target else None

            if not target_file:
                # Find first Python file as target
                py_files = list(self.target_path.rglob("*.py"))
                if py_files:
                    target_file = py_files[0]

            if target_file and target_file.exists():
                try:
                    # Read original code
                    with open(target_file) as f:
                        original_code = f.read()

                    # Generate improved code using AI
                    improved_code = self.ai.generate_improved_code(
                        original_code=original_code, task=task
                    )

                    # Save backup
                    backup_file = target_file.with_suffix(".backup")
                    with open(backup_file, "w") as f:
                        f.write(original_code)

                    # Write improved code
                    with open(target_file, "w") as f:
                        f.write(improved_code)

                    changes.append(
                        {
                            "file": str(target_file),
                            "task": task["action"],
                            "backup": str(backup_file),
                        }
                    )

                    print(f"    ✅ Modified: {target_file}")

                except Exception as e:
                    print(f"    ❌ Error: {e}")

        return {"status": "executed", "changes": changes}

    def evaluate_improvements(self, changes: dict) -> dict:
        """Step 4: Evaluate the improvements using AI."""
        print("\n📊 PHASE 4: EVALUATING IMPROVEMENTS...")

        evaluations = []

        for change in changes.get("changes", []):
            try:
                # Read before and after
                with open(change["backup"]) as f:
                    before = f.read()

                with open(change["file"]) as f:
                    after = f.read()

                # Use AI to evaluate
                evaluation = self.ai.evaluate_changes(before, after)
                evaluations.append(evaluation)

                print(
                    f"  {change['file']}: Quality score = {evaluation.get('quality_score', 'N/A')}"
                )

            except Exception as e:
                print(f"  Error evaluating {change['file']}: {e}")

        return {"evaluations": evaluations}

    def commit_changes(self, changes: dict, evaluation: dict) -> bool:
        """Step 5: Commit changes to git if approved."""
        print("\n💾 PHASE 5: COMMITTING CHANGES...")

        if os.getenv("ENABLE_GIT_COMMITS") != "true":
            print("  ⚠️ Git commits disabled. Set ENABLE_GIT_COMMITS=true to enable.")
            return False

        try:
            # Check if there are changes to commit
            if not changes.get("changes"):
                print("  No changes to commit")
                return False

            # Add changed files
            for change in changes["changes"]:
                self.repo.index.add([change["file"]])

            # Create commit message
            commit_msg = f"""AI: Self-evolution cycle {datetime.now().strftime('%Y%m%d-%H%M%S')}

Improvements made:
{json.dumps([c['task'] for c in changes['changes']], indent=2)}

Quality scores:
{json.dumps([e.get('quality_score', 'N/A') for e in evaluation.get('evaluations', [])], indent=2)}

Generated by T-Developer v2.0 🤖
"""

            # Commit
            self.repo.index.commit(commit_msg)

            print(f"  ✅ Committed changes: {len(changes['changes'])} files modified")
            return True

        except Exception as e:
            print(f"  ❌ Commit failed: {e}")
            return False

    def run_evolution_cycle(self):
        """Run a complete evolution cycle."""
        print("=" * 60)
        print("🧬 T-DEVELOPER REAL EVOLUTION CYCLE")
        print("=" * 60)
        print(f"Target: {self.target_path}")
        print(f"AI Mode: {'REAL' if not self.mock_mode else 'MOCK'}")
        print(f"Modification: {os.getenv('ENABLE_CODE_MODIFICATION', 'false')}")
        print(f"Git Commits: {os.getenv('ENABLE_GIT_COMMITS', 'false')}")
        print("=" * 60)

        # Run the cycle
        analysis = self.analyze_codebase()
        plan = self.create_plan(analysis)
        changes = self.execute_improvements(plan)
        evaluation = self.evaluate_improvements(changes)

        if changes.get("changes"):
            self.commit_changes(changes, evaluation)

        print("\n" + "=" * 60)
        print("✅ EVOLUTION CYCLE COMPLETE!")
        print("=" * 60)

        # Summary
        print("\n📊 SUMMARY:")
        print(f"  Files Analyzed: {analysis.get('files_analyzed', 0)}")
        print(f"  Issues Found: {len(analysis.get('findings', []))}")
        print(f"  Tasks Created: {len(plan.get('tasks', []))}")
        print(f"  Files Modified: {len(changes.get('changes', []))}")

        avg_score = 0
        if evaluation.get("evaluations"):
            scores = [e.get("quality_score", 0) for e in evaluation["evaluations"]]
            avg_score = sum(scores) / len(scores) if scores else 0
            print(f"  Avg Quality Score: {avg_score:.1f}/100")

        return {
            "analysis": analysis,
            "plan": plan,
            "changes": changes,
            "evaluation": evaluation,
            "success": avg_score > 70,
        }


def main():
    """Main entry point."""
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️ WARNING: No API keys found in .env file!")
        print("Add OPENAI_API_KEY or ANTHROPIC_API_KEY to .env file for real AI.")
        print("Continuing in mock mode...\n")
        time.sleep(2)

    # Set safety flags
    if input("\nEnable actual code modification? (yes/no): ").lower() == "yes":
        os.environ["ENABLE_CODE_MODIFICATION"] = "true"

    if input("Enable git commits? (yes/no): ").lower() == "yes":
        os.environ["ENABLE_GIT_COMMITS"] = "true"

    # Run evolution
    evolution = RealEvolutionSystem(
        target_path=input("Target path (default: ./packages): ") or "./packages"
    )

    result = evolution.run_evolution_cycle()

    if result["success"]:
        print("\n🎉 Evolution successful! T-Developer has improved itself!")
    else:
        print("\n⚠️ Evolution completed with warnings. Review changes carefully.")


if __name__ == "__main__":
    main()
