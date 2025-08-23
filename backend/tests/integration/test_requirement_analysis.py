#!/usr/bin/env python3
"""Complex Requirements Analysis Test with Report Generation."""

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
from backend.packages.agents.requirement_analyzer import RequirementAnalyzer
from backend.packages.agents.base import AgentTask


def format_requirement_report(data: dict) -> str:
    """Format requirement analysis as a markdown report."""
    
    lines = []
    
    # Title
    lines.append("# Requirements Analysis Report")
    lines.append(f"\n**Generated:** {data.get('timestamp', datetime.now().isoformat())}")
    lines.append("")
    
    # Original Requirements
    if 'original_requirements' in data:
        lines.append("## Original Requirements")
        lines.append("```")
        lines.append(data['original_requirements'])
        lines.append("```")
        lines.append("")
    
    # Executive Summary
    spec = data.get('specification', {})
    feasibility = data.get('feasibility', {})
    
    lines.append("## Executive Summary")
    lines.append(f"- **Complexity:** {spec.get('complexity', 'Unknown')}")
    lines.append(f"- **Priority:** {spec.get('priority', 'Unknown')}")
    lines.append(f"- **Estimated Effort:** {spec.get('estimated_effort', 'Not estimated')}")
    lines.append(f"- **Feasibility Score:** {feasibility.get('overall_score', 0):.1%}")
    lines.append(f"- **Risk Level:** {feasibility.get('risk_level', 'Unknown')}")
    lines.append("")
    
    # Functional Requirements
    if spec.get('functional_requirements'):
        lines.append("## Functional Requirements")
        for i, req in enumerate(spec['functional_requirements'], 1):
            lines.append(f"{i}. {req}")
        lines.append("")
    
    # Non-Functional Requirements
    if spec.get('non_functional_requirements'):
        lines.append("## Non-Functional Requirements")
        for i, req in enumerate(spec['non_functional_requirements'], 1):
            lines.append(f"{i}. {req}")
        lines.append("")
    
    # System Components
    if spec.get('components'):
        lines.append("## System Components")
        for component in spec['components']:
            if isinstance(component, dict):
                lines.append(f"\n### {component.get('name', 'Unknown Component')}")
                lines.append(f"- **Type:** {component.get('type', 'Unknown')}")
                lines.append(f"- **Responsibility:** {component.get('responsibility', 'Not specified')}")
            else:
                lines.append(f"- {component}")
        lines.append("")
    
    # Dependencies
    if spec.get('dependencies'):
        lines.append("## External Dependencies")
        for dep in spec['dependencies']:
            lines.append(f"- {dep}")
        lines.append("")
    
    # Constraints
    if spec.get('constraints'):
        lines.append("## Constraints")
        for constraint in spec['constraints']:
            lines.append(f"- {constraint}")
        lines.append("")
    
    # Assumptions
    if spec.get('assumptions'):
        lines.append("## Assumptions")
        for assumption in spec['assumptions']:
            lines.append(f"- {assumption}")
        lines.append("")
    
    # Risks
    if spec.get('risks'):
        lines.append("## Identified Risks")
        for i, risk in enumerate(spec['risks'], 1):
            lines.append(f"{i}. {risk}")
        lines.append("")
    
    # Success Criteria
    if spec.get('success_criteria'):
        lines.append("## Success Criteria")
        for i, criteria in enumerate(spec['success_criteria'], 1):
            lines.append(f"{i}. {criteria}")
        lines.append("")
    
    # Feasibility Analysis
    lines.append("## Feasibility Analysis")
    lines.append(f"\n### Overall Assessment")
    lines.append(f"- **Score:** {feasibility.get('overall_score', 0):.1%}")
    lines.append(f"- **Technical Feasibility:** {'✅' if feasibility.get('technical_feasibility') else '❌'}")
    lines.append(f"- **Resource Availability:** {'✅' if feasibility.get('resource_availability') else '❌'}")
    lines.append(f"- **Time Feasibility:** {'✅' if feasibility.get('time_feasibility') else '❌'}")
    
    if feasibility.get('recommendations'):
        lines.append(f"\n### Recommendations")
        for rec in feasibility['recommendations']:
            lines.append(f"- {rec}")
    
    if feasibility.get('warnings'):
        lines.append(f"\n### Warnings")
        for warning in feasibility['warnings']:
            lines.append(f"- ⚠️ {warning}")
    
    if feasibility.get('blockers'):
        lines.append(f"\n### Blockers")
        for blocker in feasibility['blockers']:
            lines.append(f"- 🚫 {blocker}")
    
    lines.append("")
    
    # Implementation Roadmap
    lines.append("## Implementation Roadmap")
    
    # Phase 1
    lines.append("\n### Phase 1: Foundation (Week 1-2)")
    lines.append("- Set up development environment")
    lines.append("- Initialize project structure")
    lines.append("- Implement core authentication and authorization")
    
    # Phase 2
    lines.append("\n### Phase 2: Core Features (Week 3-6)")
    lines.append("- Develop main business logic")
    lines.append("- Implement data models and persistence")
    lines.append("- Create APIs and service integrations")
    
    # Phase 3
    lines.append("\n### Phase 3: Advanced Features (Week 7-10)")
    lines.append("- Add AI/ML capabilities")
    lines.append("- Implement advanced analytics")
    lines.append("- Performance optimization")
    
    # Phase 4
    lines.append("\n### Phase 4: Production Readiness (Week 11-12)")
    lines.append("- Security hardening")
    lines.append("- Load testing and optimization")
    lines.append("- Documentation and deployment")
    
    lines.append("")
    
    # Metadata
    lines.append("## Metadata")
    lines.append(f"- Analysis completed at: {data.get('timestamp', 'N/A')}")
    lines.append(f"- Analyzer version: {spec.get('metadata', {}).get('analyzer_version', 'Unknown')}")
    lines.append(f"- Total components: {len(spec.get('components', []))}")
    lines.append(f"- Total dependencies: {len(spec.get('dependencies', []))}")
    lines.append(f"- Total risks identified: {len(spec.get('risks', []))}")
    
    return '\n'.join(lines)


async def test_complex_requirements():
    """Test RequirementAnalyzer with complex, multi-faceted requirements."""
    
    print("=" * 80)
    print("🎯 Complex Requirements Analysis Test")
    print("=" * 80)
    
    # Setup environment
    print("\n📥 Loading API keys from AWS...")
    setup_environment_from_aws()
    
    # Complex requirement scenario
    complex_requirements = """
    Build a comprehensive e-commerce platform with the following capabilities:

    1. Multi-tenant SaaS Architecture:
       - Support for 10,000+ concurrent merchants
       - White-label customization per tenant
       - Isolated data storage with shared infrastructure
       - Real-time tenant provisioning under 30 seconds
       - Custom domain mapping for each tenant

    2. Advanced Product Management:
       - Support for 1M+ products per tenant
       - Complex product variants (size, color, material, etc.)
       - Dynamic pricing rules based on customer segments
       - AI-powered product recommendations using collaborative filtering
       - Real-time inventory tracking across multiple warehouses
       - Bulk import/export via CSV, JSON, and API
       - Product bundling and kit management

    3. Order Processing Pipeline:
       - Support 100K orders/day throughput
       - Distributed order processing with Apache Kafka
       - Multi-step approval workflows for B2B orders
       - Split shipments and partial fulfillments
       - Automatic fraud detection using ML models
       - Integration with 15+ payment gateways
       - Support for cryptocurrencies and BNPL options

    4. Customer Experience:
       - Sub-100ms page load times globally
       - Progressive Web App with offline capabilities
       - AR/VR product visualization for furniture/fashion
       - AI chatbot for customer support (95% resolution rate)
       - Personalized shopping experience using behavior analysis
       - Social commerce integration (Instagram, TikTok, Facebook shops)
       - Voice commerce via Alexa/Google Assistant

    5. Analytics and Intelligence:
       - Real-time dashboards with WebSocket updates
       - Predictive analytics for demand forecasting
       - Customer lifetime value prediction
       - Churn prediction and prevention automation
       - A/B testing framework for all features
       - Custom report builder with SQL access
       - Data lake integration for historical analysis

    6. Technical Requirements:
       - Microservices architecture with service mesh (Istio)
       - Kubernetes orchestration with auto-scaling
       - GraphQL federation for API gateway
       - Event-driven architecture with CQRS pattern
       - Multi-region deployment with <50ms latency
       - 99.99% uptime SLA with zero-downtime deployments
       - GDPR, CCPA, PCI-DSS compliance
       - End-to-end encryption for sensitive data

    7. Integration Requirements:
       - ERP systems (SAP, Oracle, Microsoft Dynamics)
       - Shipping carriers (FedEx, UPS, DHL, 50+ regional)
       - Tax calculation services (Avalara, TaxJar)
       - Marketing automation (HubSpot, Mailchimp, Klaviyo)
       - Accounting software (QuickBooks, Xero)
       - CDN and DDoS protection (Cloudflare)
       - Observability stack (Datadog, New Relic)

    8. Performance Constraints:
       - API response time < 200ms p99
       - Database queries < 50ms p95
       - Search results < 100ms with faceting
       - Image optimization and lazy loading
       - Redis caching with 98% cache hit ratio
       - Elasticsearch for full-text search
       - GraphQL query complexity limits

    9. Security Requirements:
       - OAuth 2.0 / OIDC authentication
       - Role-based access control with attribute-based policies
       - API rate limiting per tenant
       - Web Application Firewall (WAF)
       - Regular security audits and penetration testing
       - Secrets management with HashiCorp Vault
       - Container image scanning in CI/CD

    10. Scalability Goals:
        - Handle Black Friday traffic (50x normal load)
        - Auto-scale based on CPU, memory, and custom metrics
        - Database sharding strategy for horizontal scaling
        - Read replicas for reporting workloads
        - Message queue for async processing
        - Circuit breakers for service resilience

    The platform should be production-ready within 6 months with a phased rollout plan.
    Initial MVP should support 100 tenants with core e-commerce features.
    Budget constraint: $2M for development and first-year infrastructure.
    Team size: 15-20 engineers with mixed experience levels.
    """
    
    print(f"\n🔍 Analyzing complex e-commerce platform requirements...")
    print(f"📋 Requirement length: {len(complex_requirements)} characters")
    
    # Initialize analyzer
    analyzer = RequirementAnalyzer()
    
    # Run analysis
    print("\n⏳ Running comprehensive requirement analysis...")
    start_time = datetime.now()
    
    task = AgentTask(
        type="analyze",
        intent="Analyze complex e-commerce platform requirements",
        inputs={
            "requirements": complex_requirements,
            "focus_area": "Technical architecture and feasibility",
            "project_context": {
                "type": "SaaS Platform",
                "industry": "E-commerce",
                "scale": "Enterprise",
                "timeline": "6 months",
                "budget": "$2M",
                "team_size": "15-20 engineers"
            }
        }
    )
    
    try:
        result = await analyzer.execute(task)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.success:
            print(f"✅ Analysis completed in {elapsed:.1f} seconds")
            
            data = result.data
            data['original_requirements'] = complex_requirements[:500] + "..."  # First 500 chars
            
            # Quick summary
            spec = data.get('specification', {})
            feasibility = data.get('feasibility', {})
            
            print(f"\n📊 Analysis Results:")
            print(f"  • Complexity: {spec.get('complexity', 'unknown')}")
            print(f"  • Priority: {spec.get('priority', 'unknown')}")
            print(f"  • Components: {len(spec.get('components', []))}")
            print(f"  • Dependencies: {len(spec.get('dependencies', []))}")
            print(f"  • Risks: {len(spec.get('risks', []))}")
            print(f"  • Feasibility Score: {feasibility.get('overall_score', 0):.1%}")
            
            # Save reports
            report_dir = Path("reports/RequirementAnalysis")
            report_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save formatted markdown
            markdown_content = format_requirement_report(data)
            markdown_file = report_dir / f"requirement_analysis_{timestamp}.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"\n📝 Markdown report saved: {markdown_file}")
            
            # Show preview
            lines = markdown_content.split('\n')
            print(f"\n📄 Report Preview (first 40 lines):")
            print("-" * 60)
            for line in lines[:40]:
                print(line)
            print("-" * 60)
            print(f"... (Total {len(lines)} lines)")
            
            # Save JSON data
            json_file = report_dir / f"requirement_data_{timestamp}.json"
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            print(f"\n💾 JSON data saved: {json_file}")
            
            print(f"\n✅ SUCCESS! Check the reports in: {report_dir}")
            
        else:
            print(f"❌ Analysis failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 Complex Requirements Analysis Test")
    print("This will analyze a comprehensive e-commerce platform requirement")
    print("")
    
    asyncio.run(test_complex_requirements())