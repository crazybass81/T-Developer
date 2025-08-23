#!/usr/bin/env python3
"""Extract all reports from MemoryHub and save to /docs/reports/."""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.packages.memory.hub import MemoryHub
from backend.packages.memory.contexts import ContextType


def format_as_markdown(data: Any, title: str = "") -> str:
    """Convert data to markdown format."""
    lines = []
    
    if title:
        lines.append(f"# {title}")
        lines.append("")
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"## {key.replace('_', ' ').title()}")
                lines.append("")
                if isinstance(value, dict):
                    for k, v in value.items():
                        lines.append(f"- **{k}**: {v}")
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            lines.append(f"- {json.dumps(item, indent=2)}")
                        else:
                            lines.append(f"- {item}")
                lines.append("")
            else:
                lines.append(f"**{key.replace('_', ' ').title()}**: {value}")
                lines.append("")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                lines.append("---")
                lines.append(format_as_markdown(item))
            else:
                lines.append(f"- {item}")
    else:
        lines.append(str(data))
    
    return "\n".join(lines)


async def extract_all_reports():
    """Extract all reports from memory and save to files."""
    
    print("=" * 80)
    print("  EXTRACTING MEMORY REPORTS TO /docs/reports/")
    print("=" * 80)
    print()
    
    # Initialize memory hub
    memory_hub = MemoryHub()
    await memory_hub.initialize()
    
    # Create output directory structure
    base_dir = Path("/home/ec2-user/T-Developer-v2/docs/reports")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    subdirs = [
        "orchestrator",
        "agents/requirement_analyzer",
        "agents/code_analysis",
        "agents/static_analyzer",
        "agents/gap_analyzer",
        "agents/behavior_analyzer",
        "agents/impact_analyzer",
        "agents/planner_agent",
        "agents/task_creator",
        "agents/quality_gate",
        "agents/external_researcher",
        "agents/code_generator",
        "summary",
        "memory_snapshots"
    ]
    
    for subdir in subdirs:
        (base_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    extracted_count = 0
    reports_by_context = {}
    
    try:
        # Extract from each context
        for context_type in ContextType:
            print(f"\n📂 Scanning {context_type.value} context...")
            
            context = memory_hub.contexts.get(context_type)
            if not context:
                print(f"   ⚠️  No context found for {context_type.value}")
                continue
            
            reports_by_context[context_type.value] = []
            
            # Iterate through all entries
            for key, entry in context.entries.items():
                if entry and entry.value:
                    print(f"   • Found: {key}")
                    
                    # Determine output path based on key
                    output_path = None
                    
                    # Orchestrator reports
                    if "evolution" in key or "upgrade" in key:
                        output_path = base_dir / "orchestrator"
                    # Agent-specific reports
                    elif "requirement" in key.lower():
                        output_path = base_dir / "agents/requirement_analyzer"
                    elif "code_analysis" in key.lower() or "codeanalysis" in key.lower():
                        output_path = base_dir / "agents/code_analysis"
                    elif "static" in key.lower():
                        output_path = base_dir / "agents/static_analyzer"
                    elif "gap" in key.lower():
                        output_path = base_dir / "agents/gap_analyzer"
                    elif "behavior" in key.lower():
                        output_path = base_dir / "agents/behavior_analyzer"
                    elif "impact" in key.lower():
                        output_path = base_dir / "agents/impact_analyzer"
                    elif "planner" in key.lower() or "plan" in key.lower():
                        output_path = base_dir / "agents/planner_agent"
                    elif "task" in key.lower():
                        output_path = base_dir / "agents/task_creator"
                    elif "quality" in key.lower():
                        output_path = base_dir / "agents/quality_gate"
                    elif "research" in key.lower() or "external" in key.lower():
                        output_path = base_dir / "agents/external_researcher"
                    elif "generat" in key.lower():
                        output_path = base_dir / "agents/code_generator"
                    else:
                        output_path = base_dir / "memory_snapshots"
                    
                    # Generate filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_key = key.replace("/", "_").replace(":", "_")
                    
                    # Save as JSON
                    json_file = output_path / f"{safe_key}_{timestamp}.json"
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "key": key,
                            "context": context_type.value,
                            "timestamp": timestamp,
                            "data": entry.value,
                            "tags": entry.tags if hasattr(entry, 'tags') else [],
                            "created_at": entry.created_at.isoformat() if hasattr(entry, 'created_at') else None
                        }, f, indent=2, default=str)
                    
                    # Save as Markdown
                    md_file = output_path / f"{safe_key}_{timestamp}.md"
                    md_content = format_as_markdown(
                        entry.value,
                        title=f"{key} Report"
                    )
                    
                    # Add metadata
                    metadata = f"""---
key: {key}
context: {context_type.value}
extracted: {timestamp}
tags: {entry.tags if hasattr(entry, 'tags') else []}
---

"""
                    
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(metadata + md_content)
                    
                    extracted_count += 1
                    reports_by_context[context_type.value].append({
                        "key": key,
                        "json_path": str(json_file),
                        "md_path": str(md_file)
                    })
        
        # Generate summary report
        print("\n📝 Generating summary report...")
        
        summary = {
            "extraction_timestamp": datetime.now().isoformat(),
            "total_reports_extracted": extracted_count,
            "reports_by_context": reports_by_context,
            "output_directory": str(base_dir)
        }
        
        # Save summary as JSON
        summary_json = base_dir / "summary" / "extraction_summary.json"
        with open(summary_json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        # Save summary as Markdown
        summary_md = base_dir / "summary" / "extraction_summary.md"
        summary_content = f"""# Memory Report Extraction Summary

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistics

- **Total Reports Extracted**: {extracted_count}
- **Output Directory**: `{base_dir}`

## Reports by Context

"""
        
        for ctx, reports in reports_by_context.items():
            summary_content += f"### {ctx.upper()} Context ({len(reports)} reports)\n\n"
            for report in reports:
                summary_content += f"- `{report['key']}`\n"
            summary_content += "\n"
        
        with open(summary_md, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print("\n" + "=" * 80)
        print("  EXTRACTION COMPLETE")
        print("=" * 80)
        
        print(f"\n📊 Summary:")
        print(f"  • Total reports extracted: {extracted_count}")
        print(f"  • Output directory: {base_dir}")
        
        for ctx, reports in reports_by_context.items():
            if reports:
                print(f"  • {ctx}: {len(reports)} reports")
        
        print(f"\n✅ All reports have been extracted to /docs/reports/")
        print(f"   View summary at: {summary_md}")
        
    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await memory_hub.shutdown()
        print("\n✨ Memory hub shutdown complete")


if __name__ == "__main__":
    print("\n🚀 Starting Memory Report Extraction...")
    print("   This will extract all reports from memory to /docs/reports/\n")
    
    asyncio.run(extract_all_reports())