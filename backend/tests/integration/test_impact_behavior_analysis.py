#!/usr/bin/env python3
"""Test ImpactAnalyzer and BehaviorAnalyzer with T-Developer project."""

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
from backend.packages.agents.impact_analyzer import ImpactAnalyzer
from backend.packages.agents.behavior_analyzer import BehaviorAnalyzer
from backend.packages.agents.static_analyzer import StaticAnalyzer
from backend.packages.agents.base import AgentTask


def format_impact_report(data: dict) -> str:
    """Format impact analysis as a markdown report."""
    
    lines = []
    
    # Title
    lines.append("# Impact Analysis Report - T-Developer v2")
    lines.append(f"\n**Generated:** {datetime.now().isoformat()}")
    lines.append(f"**Project:** T-Developer v2")
    lines.append(f"**Analysis Type:** Dependency and Change Impact Analysis")
    lines.append("")
    
    # Executive Summary
    lines.append("## Executive Summary")
    if 'system_health' in data:
        health = data['system_health']
        lines.append(f"- **Overall Health Score:** {health.get('overall_score', 0):.1f}/100")
        lines.append(f"- **Maintainability Score:** {health.get('maintainability_score', 0):.1f}")
        lines.append(f"- **Technical Debt Score:** {health.get('technical_debt_score', 0):.1f}")
        lines.append(f"- **Modularity Score:** {health.get('modularity_score', 0):.1f}")
    lines.append("")
    
    # Dependency Analysis
    if 'dependencies' in data:
        deps = data['dependencies']
        lines.append("## Dependency Analysis")
        
        if 'total_modules' in deps:
            lines.append(f"- **Total Modules:** {deps['total_modules']}")
            lines.append(f"- **Total Dependencies:** {deps.get('total_dependencies', 0)}")
            lines.append(f"- **Average Dependencies per Module:** {deps.get('avg_dependencies', 0):.1f}")
        
        if 'most_dependent' in deps:
            lines.append("\n### Most Dependent Modules (High Risk)")
            for module in deps['most_dependent'][:5]:
                lines.append(f"- **{module['module']}:** {module['count']} dependencies")
        
        if 'most_depended_upon' in deps:
            lines.append("\n### Most Depended Upon (Core Modules)")
            for module in deps['most_depended_upon'][:5]:
                lines.append(f"- **{module['module']}:** {module['count']} dependents")
        lines.append("")
    
    # Architecture Layers
    if 'architecture' in data:
        arch = data['architecture']
        lines.append("## Architecture Analysis")
        
        if 'layers' in arch:
            lines.append("\n### Detected Layers")
            for layer_name, modules in arch['layers'].items():
                if isinstance(modules, list) and modules:
                    lines.append(f"- **{layer_name}:** {len(modules)} modules")
        
        if 'coupling' in arch:
            lines.append(f"\n### Coupling Metrics")
            lines.append(f"- **Coupling Score:** {arch['coupling']}")
            lines.append(f"- **Cohesion Score:** {arch.get('cohesion', 'N/A')}")
        lines.append("")
    
    # Risk Analysis
    if 'risks' in data:
        risks = data['risks']
        lines.append("## Risk Analysis")
        
        if 'circular_dependencies' in risks:
            lines.append(f"- **Circular Dependencies:** {risks['circular_dependencies']}")
            if risks['circular_dependencies'] > 0:
                lines.append("  ⚠️ Circular dependencies detected - refactoring recommended")
        
        if 'high_risk_components' in risks:
            lines.append("\n### High Risk Components")
            for comp in risks['high_risk_components'][:5]:
                if isinstance(comp, dict):
                    lines.append(f"- **{comp.get('name', 'Unknown')}:** {comp.get('risk', 'N/A')}")
                else:
                    lines.append(f"- {comp}")
        
        if 'single_points_of_failure' in risks:
            lines.append(f"\n### Single Points of Failure: {len(risks['single_points_of_failure'])}")
            for spof in risks['single_points_of_failure'][:3]:
                lines.append(f"- {spof}")
        lines.append("")
    
    # Change Impact Scenarios
    if 'change_impact_scenarios' in data:
        lines.append("## Change Impact Analysis")
        scenarios = data['change_impact_scenarios']
        
        for scenario in scenarios[:3]:
            if isinstance(scenario, dict):
                lines.append(f"\n### Scenario: {scenario.get('component', 'Component')} Change")
                lines.append(f"- **Affected Modules:** {scenario.get('affected_count', 0)}")
                lines.append(f"- **Impact Level:** {scenario.get('impact_level', 'Unknown')}")
                if 'affected_modules' in scenario:
                    lines.append("- **Affected:** " + ", ".join(scenario['affected_modules'][:5]))
        lines.append("")
    
    # Recommendations
    if 'recommendations' in data:
        lines.append("## Recommendations")
        for i, rec in enumerate(data['recommendations'][:10], 1):
            lines.append(f"{i}. {rec}")
    lines.append("")
    
    return '\n'.join(lines)


def format_behavior_report(data: dict) -> str:
    """Format behavior analysis as a markdown report."""
    
    lines = []
    
    # Title
    lines.append("# Behavior Analysis Report - T-Developer v2")
    lines.append(f"\n**Generated:** {datetime.now().isoformat()}")
    lines.append(f"**Project:** T-Developer v2")
    lines.append(f"**Analysis Type:** Log Pattern and Runtime Behavior Analysis")
    lines.append("")
    
    # Executive Summary
    lines.append("## Executive Summary")
    if 'summary' in data:
        summary = data['summary']
        lines.append(f"- **Total Patterns Found:** {summary.get('total_patterns', 0)}")
        lines.append(f"- **Error Rate:** {summary.get('error_rate', 0):.2%}")
        lines.append(f"- **Performance Score:** {summary.get('performance_score', 0):.1f}/100")
    lines.append("")
    
    # Error Patterns
    if 'error_patterns' in data:
        lines.append("## Error Patterns Analysis")
        patterns = data['error_patterns']
        
        if isinstance(patterns, list) and patterns:
            lines.append("\n### Top Error Patterns")
            for pattern in patterns[:5]:
                if isinstance(pattern, dict):
                    lines.append(f"- **{pattern.get('type', 'Error')}:** {pattern.get('count', 0)} occurrences")
                    if 'message' in pattern:
                        lines.append(f"  - Message: {pattern['message'][:100]}...")
                else:
                    lines.append(f"- {pattern}")
        lines.append("")
    
    # Performance Patterns
    if 'performance_patterns' in data:
        lines.append("## Performance Patterns")
        perf = data['performance_patterns']
        
        if 'slow_operations' in perf:
            lines.append("\n### Slow Operations")
            for op in perf['slow_operations'][:5]:
                if isinstance(op, dict):
                    lines.append(f"- **{op.get('operation', 'Operation')}:** {op.get('avg_time', 0):.2f}ms")
                else:
                    lines.append(f"- {op}")
        
        if 'bottlenecks' in perf:
            lines.append("\n### Performance Bottlenecks")
            for bottleneck in perf['bottlenecks'][:5]:
                lines.append(f"- {bottleneck}")
        lines.append("")
    
    # User Behavior
    if 'user_patterns' in data:
        lines.append("## User Behavior Patterns")
        user = data['user_patterns']
        
        if 'common_flows' in user:
            lines.append("\n### Common User Flows")
            for flow in user['common_flows'][:5]:
                if isinstance(flow, dict):
                    lines.append(f"- **{flow.get('name', 'Flow')}:** {flow.get('frequency', 0)} times")
                else:
                    lines.append(f"- {flow}")
        
        if 'peak_usage' in user:
            lines.append(f"\n### Peak Usage Times")
            lines.append(f"- {user['peak_usage']}")
        lines.append("")
    
    # Security Events
    if 'security_events' in data:
        lines.append("## Security Events")
        security = data['security_events']
        
        if isinstance(security, list) and security:
            lines.append("\n### Detected Security Events")
            for event in security[:5]:
                if isinstance(event, dict):
                    lines.append(f"- **{event.get('type', 'Event')}:** {event.get('severity', 'Unknown')} severity")
                else:
                    lines.append(f"- {event}")
        lines.append("")
    
    # System Metrics
    if 'system_metrics' in data:
        lines.append("## System Behavior Metrics")
        metrics = data['system_metrics']
        
        if 'uptime' in metrics:
            lines.append(f"- **Uptime:** {metrics['uptime']}")
        if 'avg_response_time' in metrics:
            lines.append(f"- **Average Response Time:** {metrics['avg_response_time']}ms")
        if 'memory_usage' in metrics:
            lines.append(f"- **Memory Usage:** {metrics['memory_usage']}%")
        lines.append("")
    
    # Anomalies
    if 'anomalies' in data:
        lines.append("## Detected Anomalies")
        anomalies = data['anomalies']
        
        if isinstance(anomalies, list) and anomalies:
            for anomaly in anomalies[:5]:
                if isinstance(anomaly, dict):
                    lines.append(f"- **{anomaly.get('type', 'Anomaly')}:** {anomaly.get('description', '')}")
                else:
                    lines.append(f"- {anomaly}")
        lines.append("")
    
    # Recommendations
    if 'recommendations' in data:
        lines.append("## Recommendations")
        for i, rec in enumerate(data['recommendations'][:10], 1):
            lines.append(f"{i}. {rec}")
    lines.append("")
    
    return '\n'.join(lines)


async def test_impact_analyzer():
    """Test ImpactAnalyzer on T-Developer project."""
    
    print("\n" + "=" * 80)
    print("🎯 Testing ImpactAnalyzer on T-Developer")
    print("=" * 80)
    
    project_path = "/home/ec2-user/T-Developer-v2"
    
    # Initialize with StaticAnalyzer for better analysis
    static_analyzer = StaticAnalyzer()
    impact_analyzer = ImpactAnalyzer(static_analyzer=static_analyzer)
    
    print("\n⏳ Running impact analysis...")
    start_time = datetime.now()
    
    # Create task for T-Developer analysis
    task = AgentTask(
        type="analyze",
        intent="Analyze dependencies and change impact for T-Developer",
        inputs={
            "project_path": project_path,
            "analysis_type": "comprehensive",  # or "dependency", "change_impact", "report"
            "include_architecture": True,
            "include_risks": True,
            "recursive": True
        }
    )
    
    try:
        result = await impact_analyzer.execute(task)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.success:
            print(f"✅ Impact analysis completed in {elapsed:.1f} seconds")
            
            data = result.data
            
            # Quick summary
            print(f"\n📊 Analysis Results:")
            if 'dependencies' in data:
                deps = data['dependencies']
                print(f"  • Total modules: {deps.get('total_modules', 0)}")
                print(f"  • Total dependencies: {deps.get('total_dependencies', 0)}")
            
            if 'risks' in data:
                risks = data['risks']
                print(f"  • Circular dependencies: {risks.get('circular_dependencies', 0)}")
                print(f"  • High risk components: {len(risks.get('high_risk_components', []))}")
            
            if 'system_health' in data:
                health = data['system_health']
                print(f"  • Health score: {health.get('overall_score', 0):.1f}/100")
                print(f"  • Technical debt: {health.get('technical_debt_score', 0):.1f}")
            
            # Save report
            report_dir = Path("reports/ImpactAnalysis")
            report_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save markdown
            markdown_content = format_impact_report(data)
            markdown_file = report_dir / f"impact_analysis_{timestamp}.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"\n📝 Impact report saved: {markdown_file}")
            
            # Save JSON
            json_file = report_dir / f"impact_analysis_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 JSON data saved: {json_file}")
            
            return True
            
        else:
            print(f"❌ Impact analysis failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Error during impact analysis: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_behavior_analyzer():
    """Test BehaviorAnalyzer on T-Developer project."""
    
    print("\n" + "=" * 80)
    print("🎯 Testing BehaviorAnalyzer on T-Developer")
    print("=" * 80)
    
    project_path = "/home/ec2-user/T-Developer-v2"
    
    # Initialize analyzer
    behavior_analyzer = BehaviorAnalyzer()
    
    # Find log files in the project
    log_paths = []
    log_dirs = ["logs", "log", ".logs", "test_outputs", "reports"]
    
    for log_dir in log_dirs:
        dir_path = os.path.join(project_path, log_dir)
        if os.path.exists(dir_path):
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith(('.log', '.txt', '.out')):
                        log_paths.append(os.path.join(root, file))
    
    # Also check for Python files that might contain logging patterns
    if not log_paths:
        print("⚠️ No log files found, analyzing Python files for behavior patterns...")
        for root, _, files in os.walk(project_path):
            if 'venv' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    log_paths.append(os.path.join(root, file))
                    if len(log_paths) >= 10:  # Limit to 10 files
                        break
    
    print(f"📁 Found {len(log_paths)} files to analyze")
    if log_paths:
        print(f"   Sample files: {[Path(p).name for p in log_paths[:3]]}")
    
    print("\n⏳ Running behavior analysis...")
    start_time = datetime.now()
    
    # Create task
    task = AgentTask(
        type="analyze",
        intent="Analyze runtime behavior and patterns in T-Developer",
        inputs={
            "log_paths": log_paths[:20],  # Limit to 20 files
            "project_path": project_path,
            "analysis_types": ["errors", "performance", "security", "patterns"],
            "extract_metrics": True
        }
    )
    
    try:
        result = await behavior_analyzer.execute(task)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.success:
            print(f"✅ Behavior analysis completed in {elapsed:.1f} seconds")
            
            data = result.data
            
            # Quick summary
            print(f"\n📊 Analysis Results:")
            if 'summary' in data:
                summary = data['summary']
                print(f"  • Total patterns: {summary.get('total_patterns', 0)}")
                print(f"  • Error rate: {summary.get('error_rate', 0):.2%}")
            
            if 'error_patterns' in data:
                print(f"  • Error patterns found: {len(data['error_patterns'])}")
            
            if 'performance_patterns' in data:
                perf = data['performance_patterns']
                if 'slow_operations' in perf:
                    print(f"  • Slow operations: {len(perf['slow_operations'])}")
            
            if 'anomalies' in data:
                print(f"  • Anomalies detected: {len(data['anomalies'])}")
            
            # Save report
            report_dir = Path("reports/BehaviorAnalysis")
            report_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save markdown
            markdown_content = format_behavior_report(data)
            markdown_file = report_dir / f"behavior_analysis_{timestamp}.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"\n📝 Behavior report saved: {markdown_file}")
            
            # Save JSON
            json_file = report_dir / f"behavior_analysis_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"💾 JSON data saved: {json_file}")
            
            return True
            
        else:
            print(f"❌ Behavior analysis failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Error during behavior analysis: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run both analyses."""
    print("\n" + "=" * 80)
    print("🔬 T-Developer v2 - Impact & Behavior Analysis")
    print("=" * 80)
    
    # Setup environment
    print("\n📥 Loading API keys from AWS...")
    setup_environment_from_aws()
    
    # Run Impact Analysis
    impact_success = await test_impact_analyzer()
    
    # Run Behavior Analysis
    behavior_success = await test_behavior_analyzer()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"✅ Impact Analysis: {'Success' if impact_success else 'Failed'}")
    print(f"✅ Behavior Analysis: {'Success' if behavior_success else 'Failed'}")
    print("\n📁 Reports saved in:")
    print("  • reports/ImpactAnalysis/")
    print("  • reports/BehaviorAnalysis/")


if __name__ == "__main__":
    asyncio.run(main())