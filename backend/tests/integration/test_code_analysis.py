#!/usr/bin/env python3
"""Code Analysis Agent Test with Report Generation."""

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
from backend.packages.agents.code_analysis import CodeAnalysisAgent
from backend.packages.agents.base import AgentTask


def format_code_analysis_report(data: dict) -> str:
    """Format code analysis results as a markdown report."""
    
    lines = []
    
    # Title
    lines.append("# Code Analysis Report")
    lines.append(f"\n**Generated:** {datetime.now().isoformat()}")
    lines.append(f"**File:** {data.get('file_path', 'Direct code input')}")
    lines.append(f"**Language:** {data.get('language', 'python')}")
    lines.append(f"**Analysis Type:** {data.get('analysis_type', 'comprehensive')}")
    lines.append("")
    
    # Executive Summary
    lines.append("## Executive Summary")
    if 'summary' in data:
        lines.append(data['summary'])
    else:
        lines.append("Comprehensive code analysis completed successfully.")
    lines.append("")
    
    # Code Quality Metrics
    if 'metrics' in data:
        lines.append("## Code Quality Metrics")
        metrics = data['metrics']
        lines.append(f"- **Lines of Code:** {metrics.get('loc', 'N/A')}")
        lines.append(f"- **Cyclomatic Complexity:** {metrics.get('complexity', 'N/A')}")
        lines.append(f"- **Maintainability Index:** {metrics.get('maintainability', 'N/A')}")
        lines.append(f"- **Test Coverage:** {metrics.get('coverage', 'N/A')}")
        lines.append("")
    
    # AI Analysis Results
    if 'ai_analysis' in data:
        ai = data['ai_analysis']
        
        # Issues Found
        if 'issues' in ai:
            lines.append("## Issues Identified")
            for i, issue in enumerate(ai['issues'], 1):
                if isinstance(issue, dict):
                    lines.append(f"\n### {i}. {issue.get('title', 'Issue')}")
                    lines.append(f"- **Severity:** {issue.get('severity', 'Medium')}")
                    lines.append(f"- **Category:** {issue.get('category', 'General')}")
                    lines.append(f"- **Description:** {issue.get('description', '')}")
                    if issue.get('suggestion'):
                        lines.append(f"- **Suggestion:** {issue.get('suggestion')}")
                else:
                    lines.append(f"{i}. {issue}")
            lines.append("")
        
        # Suggestions
        if 'suggestions' in ai:
            lines.append("## Improvement Suggestions")
            for i, suggestion in enumerate(ai['suggestions'], 1):
                if isinstance(suggestion, dict):
                    lines.append(f"{i}. **{suggestion.get('type', 'General')}:** {suggestion.get('description', suggestion)}")
                else:
                    lines.append(f"{i}. {suggestion}")
            lines.append("")
        
        # Security Analysis
        if 'security' in ai:
            lines.append("## Security Analysis")
            security = ai['security']
            if isinstance(security, dict):
                if security.get('vulnerabilities'):
                    lines.append("\n### Vulnerabilities Found")
                    for vuln in security['vulnerabilities']:
                        lines.append(f"- **{vuln.get('type', 'Unknown')}:** {vuln.get('description', '')}")
                if security.get('recommendations'):
                    lines.append("\n### Security Recommendations")
                    for rec in security['recommendations']:
                        lines.append(f"- {rec}")
            else:
                lines.append(str(security))
            lines.append("")
        
        # Performance Analysis
        if 'performance' in ai:
            lines.append("## Performance Analysis")
            perf = ai['performance']
            if isinstance(perf, dict):
                if perf.get('bottlenecks'):
                    lines.append("\n### Potential Bottlenecks")
                    for bottleneck in perf['bottlenecks']:
                        lines.append(f"- {bottleneck}")
                if perf.get('optimizations'):
                    lines.append("\n### Optimization Opportunities")
                    for opt in perf['optimizations']:
                        lines.append(f"- {opt}")
            else:
                lines.append(str(perf))
            lines.append("")
    
    # Dynamic Analysis Results
    if 'dynamic_analysis' in data:
        lines.append("## Dynamic Analysis Results")
        dynamic = data['dynamic_analysis']
        
        if 'profile' in dynamic:
            lines.append("\n### Performance Profile")
            lines.append("```")
            lines.append(dynamic['profile'][:500])  # First 500 chars
            lines.append("```")
        
        if 'memory' in dynamic:
            lines.append(f"\n### Memory Usage")
            lines.append(f"- Peak Memory: {dynamic['memory'].get('peak', 'N/A')}")
            lines.append(f"- Average Memory: {dynamic['memory'].get('average', 'N/A')}")
        
        if 'execution_time' in dynamic:
            lines.append(f"\n### Execution Time")
            lines.append(f"- Total Time: {dynamic['execution_time']} seconds")
        lines.append("")
    
    # Best Practices
    if 'best_practices' in data:
        lines.append("## Best Practices Assessment")
        for i, practice in enumerate(data['best_practices'], 1):
            if isinstance(practice, dict):
                status = "✅" if practice.get('followed', False) else "❌"
                lines.append(f"{i}. {status} {practice.get('name', practice)}")
            else:
                lines.append(f"{i}. {practice}")
        lines.append("")
    
    # Recommendations
    if 'recommendations' in data:
        lines.append("## Recommendations")
        lines.append("\n### Priority Actions")
        for i, rec in enumerate(data['recommendations'][:5], 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
    
    # Test Coverage
    if 'test_analysis' in data:
        lines.append("## Test Coverage Analysis")
        test = data['test_analysis']
        lines.append(f"- **Current Coverage:** {test.get('coverage', 'Unknown')}")
        lines.append(f"- **Missing Tests:** {test.get('missing_tests', 'N/A')}")
        if test.get('test_suggestions'):
            lines.append("\n### Suggested Tests")
            for suggestion in test['test_suggestions']:
                lines.append(f"- {suggestion}")
        lines.append("")
    
    # Metadata
    lines.append("## Metadata")
    lines.append(f"- Analysis completed at: {datetime.now().isoformat()}")
    lines.append(f"- Analysis type: {data.get('analysis_type', 'comprehensive')}")
    lines.append(f"- Execution time: {data.get('execution_time', 'N/A')} seconds")
    
    return '\n'.join(lines)


# Sample complex code for analysis
SAMPLE_CODE = '''
import asyncio
import aiohttp
from typing import List, Dict, Optional
import json
import logging
from datetime import datetime
import time

class AsyncWebScraper:
    """An async web scraper with rate limiting and error handling."""
    
    def __init__(self, max_concurrent: int = 10, delay: float = 0.1):
        self.max_concurrent = max_concurrent
        self.delay = delay
        self.session = None
        self.results = []
        self.errors = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
        
    async def fetch(self, url: str) -> Optional[str]:
        """Fetch a single URL with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:  # Rate limited
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        logging.error(f"Error {response.status} for {url}")
                        return None
            except asyncio.TimeoutError:
                logging.warning(f"Timeout for {url}, attempt {attempt + 1}")
                if attempt == max_retries - 1:
                    self.errors.append({"url": url, "error": "timeout"})
            except Exception as e:
                logging.error(f"Error fetching {url}: {e}")
                self.errors.append({"url": url, "error": str(e)})
                return None
        return None
    
    async def scrape_batch(self, urls: List[str]) -> List[Dict]:
        """Scrape a batch of URLs with rate limiting."""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def limited_fetch(url):
            async with semaphore:
                await asyncio.sleep(self.delay)  # Rate limiting
                content = await self.fetch(url)
                return {"url": url, "content": content, "timestamp": datetime.now().isoformat()}
        
        tasks = [limited_fetch(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logging.error(f"Task failed: {result}")
            elif result and result.get("content"):
                valid_results.append(result)
                
        self.results.extend(valid_results)
        return valid_results
    
    def get_statistics(self) -> Dict:
        """Get scraping statistics."""
        return {
            "total_scraped": len(self.results),
            "total_errors": len(self.errors),
            "success_rate": len(self.results) / (len(self.results) + len(self.errors)) if self.results or self.errors else 0,
            "error_types": self._categorize_errors()
        }
    
    def _categorize_errors(self) -> Dict[str, int]:
        """Categorize errors by type."""
        categories = {}
        for error in self.errors:
            error_type = error.get("error", "unknown")
            categories[error_type] = categories.get(error_type, 0) + 1
        return categories
    
    def save_results(self, filename: str):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                "results": self.results,
                "errors": self.errors,
                "statistics": self.get_statistics()
            }, f, indent=2)

# Example usage
async def main():
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ]
    
    async with AsyncWebScraper(max_concurrent=5) as scraper:
        await scraper.scrape_batch(urls)
        stats = scraper.get_statistics()
        print(f"Scraping completed: {stats}")
        scraper.save_results("scraping_results.json")

if __name__ == "__main__":
    asyncio.run(main())
'''


async def test_code_analysis():
    """Test CodeAnalysisAgent with complex code and generate report."""
    
    print("=" * 80)
    print("🎯 Code Analysis Agent Test")
    print("=" * 80)
    
    # Setup environment
    print("\n📥 Loading API keys from AWS...")
    setup_environment_from_aws()
    
    print(f"\n🔍 Analyzing AsyncWebScraper code...")
    print(f"📋 Code length: {len(SAMPLE_CODE)} characters")
    print(f"📋 Lines of code: {len(SAMPLE_CODE.splitlines())}")
    
    # Initialize analyzer
    analyzer = CodeAnalysisAgent()
    
    try:
        # Run comprehensive analysis
        print("\n⏳ Running comprehensive code analysis...")
        start_time = datetime.now()
        
        task = AgentTask(
            type="analyze",
            intent="Perform comprehensive code analysis",
            inputs={
                "code": SAMPLE_CODE,
                "analysis_type": "comprehensive",
                "language": "python",
                "use_history": False
            }
        )
        
        result = await analyzer.execute(task)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if result.success:
            print(f"✅ Analysis completed in {elapsed:.1f} seconds")
            
            data = result.data
            data['execution_time'] = elapsed
            
            # Quick summary
            print(f"\n📊 Analysis Results:")
            if 'metrics' in data:
                print(f"  • Metrics calculated: {len(data['metrics'])} items")
            if 'ai_analysis' in data:
                ai = data['ai_analysis']
                print(f"  • Issues found: {len(ai.get('issues', []))}")
                print(f"  • Suggestions: {len(ai.get('suggestions', []))}")
            if 'dynamic_analysis' in data:
                print(f"  • Dynamic analysis: Completed")
            
            # Save reports
            report_dir = Path("reports/CodeAnalysis")
            report_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save formatted markdown
            markdown_content = format_code_analysis_report(data)
            markdown_file = report_dir / f"code_analysis_{timestamp}.md"
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
            json_file = report_dir / f"code_analysis_data_{timestamp}.json"
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
    
    finally:
        pass  # No file to clean up since we're using direct code input


if __name__ == "__main__":
    print("\n🚀 Code Analysis Agent Test")
    print("This will analyze a complex AsyncWebScraper implementation")
    print("")
    
    asyncio.run(test_code_analysis())