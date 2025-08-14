"""Test Agent Registry System"""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.evolution.planner_agent import PlannerAgent
from src.agents.evolution.research_agent import ResearchAgent
from src.agents.minimal.code_analyzer_agent import CodeAnalyzerAgent
from src.agents.minimal.github_search_agent import GitHubSearchAgent
from src.agents.registry import get_global_registry


async def test_registry():
    """Agent Registry 시스템 테스트"""
    print("=" * 60)
    print("🧬 T-Developer Agent Registry Test")
    print("=" * 60)

    # Registry 초기화
    registry = get_global_registry()

    # 1. 최소 단위 에이전트 등록
    print("\n1️⃣ Registering Minimal Agents...")

    github_agent = GitHubSearchAgent()
    code_analyzer = CodeAnalyzerAgent()

    registry.register_agent("github_search", github_agent, "minimal")
    registry.register_agent("code_analyzer", code_analyzer, "minimal")

    print("✅ Registered: github_search")
    print("✅ Registered: code_analyzer")

    # 2. 메타 에이전트 등록 (Research와 Planner)
    print("\n2️⃣ Registering Meta Agents...")

    research_agent = ResearchAgent()
    planner_agent = PlannerAgent()

    registry.register_agent("research_meta", research_agent, "meta")
    registry.register_agent("planner_meta", planner_agent, "meta")

    print("✅ Registered: research_meta")
    print("✅ Registered: planner_meta")

    # 3. Composite Agent 구성
    print("\n3️⃣ Creating Composite Agent...")

    registry.register_composite_agent("code_research_agent", ["github_search", "code_analyzer"])

    print("✅ Created composite: code_research_agent")

    # 4. 에이전트 디스커버리 테스트
    print("\n4️⃣ Testing Agent Discovery...")

    # GitHub 검색 능력을 가진 에이전트 찾기
    github_capable = registry.discover_agents(["github_search"])
    print(f"Agents with 'github_search' capability: {github_capable}")

    # 코드 분석 능력을 가진 에이전트 찾기
    code_capable = registry.discover_agents(["code_analysis"])
    print(f"Agents with 'code_analysis' capability: {code_capable}")

    # 5. 에이전트 실행 테스트
    print("\n5️⃣ Testing Agent Execution...")

    # GitHub 검색 테스트
    github = registry.get_agent("github_search")
    if github:
        result = await github.execute(
            {"query": "self-improving AI", "language": "Python", "limit": 3}
        )
        print(f"\nGitHub Search Results:")
        for project in result.get("projects", []):
            print(f"  - {project['name']}: ⭐ {project['stars']}")

    # 코드 분석 테스트
    analyzer = registry.get_agent("code_analyzer")
    if analyzer:
        test_code = '''
def fibonacci(n):
    """Calculate fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b
'''
        result = await analyzer.execute(
            {"code": test_code, "analysis_type": ["structure", "complexity", "quality"]}
        )

        print(f"\nCode Analysis Results:")
        print(
            f"  Structure: {result['analysis']['structure']['classes']} classes, "
            f"{len(result['analysis']['structure']['functions'])} functions"
        )
        print(f"  Complexity: {result['analysis']['complexity']['rating']}")
        print(f"  Quality Score: {result['analysis']['quality']['quality_score']}/100")

        if result.get("improvements"):
            print(f"  Improvements:")
            for improvement in result["improvements"][:3]:
                print(f"    - {improvement}")

    # 6. Composite Agent 테스트
    print("\n6️⃣ Testing Composite Agent...")

    composite = registry.get_agent("code_research_agent")
    if composite:
        results = await composite.execute({"query": "code analysis", "code": "def test(): pass"})
        print(f"Composite agent executed {len(results)} components")

    # 7. 통계 출력
    print("\n7️⃣ Registry Statistics:")
    stats = registry.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 8. 에이전트 내보내기 테스트
    print("\n8️⃣ Testing Agent Export...")
    export_data = registry.export_agent("github_search")
    print(f"Exported agent: {export_data.get('name')} v{export_data.get('version')}")
    print(f"  Capabilities: {len(export_data.get('capabilities', []))} capabilities")

    print("\n" + "=" * 60)
    print("✅ Agent Registry Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_registry())
