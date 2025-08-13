"""🧬 Migration Scheduler <6.5KB"""
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List

from .compatibility_checker_compact import CompatibilityChecker
from .code_converter_compact import CodeConverter
from .legacy_analyzer_compact import LegacyAnalyzer


class MigrationScheduler:
    """Orchestrates migration - ultra compact"""
    
    def __init__(self, src: str, tgt: str):
        self.src = Path(src)
        self.tgt = Path(tgt)
        self.analyzer = LegacyAnalyzer()
        self.converter = CodeConverter()
        self.checker = CompatibilityChecker()
        self.tasks = {}
        self.done = set()
        self.failed = set()
    
    def plan(self) -> Dict:
        """Create migration plan"""
        results = self.analyzer.batch(str(self.src))
        
        tasks = []
        for r in results:
            if "error" not in r:
                name = r["name"]
                tasks.append({
                    "name": name,
                    "src": str(self.src / f"{name}.py"),
                    "tgt": str(self.tgt / f"{name}_v2.py"),
                    "deps": [d for d in r.get("deps", []) if "agent" in d.lower()],
                    "complexity": r.get("complexity", "low")
                })
                self.tasks[name] = tasks[-1]
        
        # Group by dependencies
        groups = self._group(tasks)
        
        # Estimate time
        pts = sum(1 if t["complexity"] == "low" else 3 if t["complexity"] == "medium" else 5 for t in tasks)
        
        return {
            "tasks": len(tasks),
            "groups": groups,
            "est_sec": pts * 2,
            "complexity": pts
        }
    
    def _group(self, tasks: List[Dict]) -> List[List[str]]:
        """Create parallel groups"""
        groups = []
        remaining = {t["name"] for t in tasks}
        done = set()
        
        while remaining:
            group = []
            for name in remaining:
                t = self.tasks.get(name, {})
                if all(d in done for d in t.get("deps", [])):
                    group.append(name)
            
            if not group:
                group = list(remaining)
            
            groups.append(group)
            done.update(group)
            remaining -= set(group)
        
        return groups
    
    async def execute(self, plan: Dict) -> Dict:
        """Execute migration"""
        start = time.time()
        results = {"total": plan["tasks"], "done": 0, "failed": 0}
        
        self.tgt.mkdir(parents=True, exist_ok=True)
        backup = self.tgt / ".backup"
        backup.mkdir(exist_ok=True)
        
        for group in plan["groups"]:
            # Run group in parallel (max 5)
            tasks = []
            for name in group[:5]:
                if name in self.tasks:
                    tasks.append(self._migrate(name, backup))
            
            if tasks:
                group_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for name, res in zip(group, group_results):
                    if isinstance(res, Exception):
                        self.failed.add(name)
                        results["failed"] += 1
                    else:
                        self.done.add(name)
                        results["done"] += 1
        
        results["duration"] = time.time() - start
        return results
    
    async def _migrate(self, name: str, backup: Path) -> bool:
        """Migrate single agent"""
        task = self.tasks[name]
        
        try:
            # Backup if exists
            tgt_path = Path(task["tgt"])
            if tgt_path.exists():
                tgt_path.rename(backup / tgt_path.name)
            
            # Convert
            ok, msg = self.converter.convert(task["src"], task["tgt"])
            if not ok:
                raise Exception(f"Convert failed: {msg}")
            
            # Check
            result = self.checker.check(task["tgt"])
            if not result["compatible"]:
                raise Exception(f"Check failed: {result['issues']}")
            
            # Simulate deploy
            await asyncio.sleep(0.1)
            
            return True
            
        except Exception as e:
            # Rollback
            if tgt_path.exists():
                tgt_path.unlink()
            bak = backup / tgt_path.name
            if bak.exists():
                bak.rename(tgt_path)
            raise e
    
    def status(self) -> Dict:
        """Get status"""
        return {
            "total": len(self.tasks),
            "done": len(self.done),
            "failed": len(self.failed),
            "pending": len(self.tasks) - len(self.done) - len(self.failed)
        }
    
    def report(self) -> str:
        """Generate report"""
        lines = ["=" * 40, "MIGRATION REPORT", "=" * 40]
        
        st = self.status()
        lines.extend([
            f"Total: {st['total']}",
            f"Done: {st['done']}",
            f"Failed: {st['failed']}"
        ])
        
        if self.failed:
            lines.append("\nFailed:")
            for name in sorted(self.failed):
                lines.append(f"  - {name}")
        
        if self.done:
            lines.append("\nCompleted:")
            for name in sorted(self.done):
                lines.append(f"  - {name}")
        
        return "\n".join(lines)


# Example
if __name__ == "__main__":
    async def run():
        sched = MigrationScheduler("backend/src/agents/legacy", "backend/src/agents/migrated")
        plan = sched.plan()
        print(f"Plan: {json.dumps(plan, indent=2)}")
        
        results = await sched.execute(plan)
        print(f"Results: {results}")
        print(sched.report())
    
    asyncio.run(run())