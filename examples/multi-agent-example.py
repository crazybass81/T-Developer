
# T-Developer Multi-Agent System Example
from phi.agent import Agent
from phi.model.openai import OpenAIChat

# 요구사항 분석 에이전트
requirements_agent = Agent(
    name="RequirementsAnalyzer",
    model=OpenAIChat(id="gpt-4"),
    description="Analyzes user requirements and creates technical specifications"
)

# 코드 생성 에이전트  
code_agent = Agent(
    name="CodeGenerator",
    model=OpenAIChat(id="gpt-4"),
    description="Generates code based on technical specifications"
)

# 테스트 에이전트
test_agent = Agent(
    name="TestGenerator", 
    model=OpenAIChat(id="gpt-4"),
    description="Creates comprehensive tests for generated code"
)

print("✅ T-Developer 멀티에이전트 시스템 예제 준비 완료!")
