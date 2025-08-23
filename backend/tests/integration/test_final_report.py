#!/usr/bin/env python3
"""Final test for Unified External Researcher with proper report formatting."""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup environment from AWS Secrets
from scripts.setup_aws_secrets import setup_environment_from_aws
from backend.packages.agents.external_researcher import ExternalResearcher, ResearchMode, ResearchConfig
from backend.packages.agents.base import AgentTask


def format_report_as_markdown(data: dict) -> str:
    """Format research data as a proper markdown report."""
    
    lines = []
    
    # Title
    lines.append(f"# External Research Report")
    lines.append(f"\n**Generated:** {data.get('timestamp', datetime.now().isoformat())}")
    lines.append(f"**Topic:** {data.get('topic', 'N/A')}")
    lines.append(f"**Mode:** {data.get('research_mode', 'comprehensive')}")
    lines.append(f"**Confidence:** {data.get('confidence_level', 'medium')}")
    lines.append("")
    
    # Executive Summary
    if 'executive_summary' in data:
        lines.append("## Executive Summary")
        lines.append(data['executive_summary'])
        lines.append("")
    
    # Key Insights
    if 'key_insights' in data and data['key_insights']:
        lines.append("## Key Insights")
        for i, insight in enumerate(data['key_insights'][:10], 1):
            if isinstance(insight, dict):
                content = insight.get('content', str(insight))
                source = insight.get('source', 'Unknown')
                confidence = insight.get('confidence', 'medium')
                lines.append(f"\n### {i}. {content[:150]}...")
                lines.append(f"- **Source:** {source}")
                lines.append(f"- **Confidence:** {confidence}")
                if insight.get('url'):
                    lines.append(f"- **URL:** [{insight['url']}]({insight['url']})")
        lines.append("")
    
    # Best Practices
    if 'best_practices' in data and data['best_practices']:
        lines.append("## Best Practices")
        for i, practice in enumerate(data['best_practices'][:5], 1):
            if isinstance(practice, dict):
                content = practice.get('practice', practice.get('content', str(practice)))
            else:
                content = str(practice)
            lines.append(f"{i}. {content}")
        lines.append("")
    
    # Recommendations
    if 'recommendations' in data and data['recommendations']:
        lines.append("## Recommendations")
        for i, rec in enumerate(data['recommendations'][:8], 1):
            if isinstance(rec, dict):
                action = rec.get('action', rec.get('content', str(rec)))
                priority = rec.get('priority', 'medium')
                lines.append(f"\n### {i}. {action}")
                lines.append(f"**Priority:** {priority}")
            else:
                lines.append(f"{i}. {rec}")
        lines.append("")
    
    # Implementation Roadmap
    if 'implementation_roadmap' in data:
        lines.append("## Implementation Roadmap")
        roadmap = data['implementation_roadmap']
        
        if roadmap.get('immediate'):
            lines.append("\n### Phase 1: Immediate Actions")
            for action in roadmap['immediate'][:3]:
                if isinstance(action, dict):
                    content = action.get('action', action.get('content', str(action)))
                else:
                    content = str(action)
                lines.append(f"- {content}")
        
        if roadmap.get('short_term'):
            lines.append("\n### Phase 2: Short-term Goals")
            for action in roadmap['short_term'][:3]:
                if isinstance(action, dict):
                    content = action.get('action', action.get('content', str(action)))
                else:
                    content = str(action)
                lines.append(f"- {content}")
        
        if roadmap.get('long_term'):
            lines.append("\n### Phase 3: Long-term Vision")
            for action in roadmap['long_term'][:3]:
                if isinstance(action, dict):
                    content = action.get('action', action.get('content', str(action)))
                else:
                    content = str(action)
                lines.append(f"- {content}")
        lines.append("")
    
    # Sources
    if 'source_summary' in data:
        lines.append("## Sources")
        summary = data['source_summary']
        lines.append(f"**Total Sources:** {summary.get('total_sources', 0)}")
        
        if summary.get('by_type'):
            lines.append("\n**By Type:**")
            for source_type, count in summary['by_type'].items():
                lines.append(f"- {source_type}: {count}")
        
        if summary.get('top_sources'):
            lines.append("\n**Top Sources:**")
            for source in summary['top_sources'][:10]:
                lines.append(f"- [{source['type']}] {source['title']}")
                if source.get('url'):
                    lines.append(f"  - URL: {source['url']}")
        lines.append("")
    
    # Metadata
    lines.append("## Metadata")
    lines.append(f"- Research completed at: {data.get('timestamp', 'N/A')}")
    lines.append(f"- Focus Areas: {', '.join(data.get('focus_areas', []))}")
    if 'all_sources' in data:
        lines.append(f"- Total sources analyzed: {len(data['all_sources'])}")
    if 'key_insights' in data:
        lines.append(f"- Insights generated: {len(data['key_insights'])}")
    
    return '\n'.join(lines)


async def test_with_proper_report():
    """Test and generate a properly formatted report."""
    
    print("=" * 80)
    print("🎯 Final Test: External Researcher with Proper Report")
    print("=" * 80)
    
    # Setup environment
    print("\n📥 Loading API keys from AWS...")
    setup_environment_from_aws()
    
    # Research topic
    topic = "Circuit breaker pattern for microservices resilience"
    focus_areas = [
        "Hystrix vs Resilience4j comparison",
        "Implementation best practices",
        "Common anti-patterns to avoid"
    ]
    
    print(f"\n🔍 Topic: {topic}")
    print(f"📋 Focus Areas:")
    for area in focus_areas:
        print(f"  • {area}")
    
    # Initialize researcher
    researcher = ExternalResearcher()
    
    # Run comprehensive research
    print("\n⏳ Running comprehensive research...")
    start_time = datetime.now()
    
    task = AgentTask(
        type="research",
        intent="Comprehensive research with all methods",
        inputs={
            "topic": topic,
            "focus_areas": focus_areas
        }
    )
    
    result = await researcher.execute(task)
    elapsed = (datetime.now() - start_time).total_seconds()
    
    if result.success:
        print(f"✅ Research completed in {elapsed:.1f} seconds")
        
        data = result.data
        
        # Quick summary
        print(f"\n📊 Results:")
        print(f"  • Confidence: {data.get('confidence_level', 'unknown')}")
        print(f"  • Sources: {len(data.get('all_sources', []))}")
        print(f"  • Insights: {len(data.get('key_insights', []))}")
        print(f"  • Recommendations: {len(data.get('recommendations', []))}")
        
        # Save reports
        report_dir = Path("reports/FinalExternalResearcher")
        report_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save formatted markdown
        markdown_content = format_report_as_markdown(data)
        markdown_file = report_dir / f"research_report_{timestamp}.md"
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"\n📝 Markdown report saved: {markdown_file}")
        
        # Show preview
        lines = markdown_content.split('\n')
        print(f"\n📄 Report Preview (first 30 lines):")
        print("-" * 60)
        for line in lines[:30]:
            print(line)
        print("-" * 60)
        print(f"... (Total {len(lines)} lines)")
        
        # Save JSON data
        json_file = report_dir / f"research_data_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\n💾 JSON data saved: {json_file}")
        
        print(f"\n✅ SUCCESS! Check the reports in: {report_dir}")
        
    else:
        print(f"❌ Research failed: {result.error}")


if __name__ == "__main__":
    print("\n🚀 Final External Researcher Test")
    print("This will generate a complete, properly formatted report.")
    print("")
    
    asyncio.run(test_with_proper_report())