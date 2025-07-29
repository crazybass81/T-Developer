#!/usr/bin/env python3
# scripts/check-multi-agent-frameworks.py

def check_multi_agent_frameworks():
    """멀티에이전트 프레임워크 설치 상태 확인"""
    print("🔍 멀티에이전트 프레임워크 설치 확인 중...\n")
    
    frameworks = []
    
    # 1. Phi (Agno) 확인
    try:
        from phi.agent import Agent
        from phi.model.openai import OpenAIChat
        frameworks.append("✅ Phi (Agno) - 정상 설치됨")
    except ImportError:
        frameworks.append("❌ Phi (Agno) - 설치되지 않음")
    
    # 2. CrewAI 확인 (Python 3.10+ 필요)
    try:
        import sys
        if sys.version_info >= (3, 10):
            from crewai import Agent, Task, Crew
            frameworks.append("✅ CrewAI - 정상 설치됨")
        else:
            frameworks.append("⚠️  CrewAI - Python 3.10+ 필요 (현재: Python 3.9)")
    except ImportError:
        frameworks.append("❌ CrewAI - 설치되지 않음")
    except Exception as e:
        frameworks.append(f"⚠️  CrewAI - 호환성 문제: {str(e)[:50]}...")
    
    # 3. Agent Squad (Node.js) 확인
    import subprocess
    try:
        result = subprocess.run(['npm', 'list', 'agent-squad'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            frameworks.append("✅ Agent Squad (Node.js) - 정상 설치됨")
        else:
            frameworks.append("❌ Agent Squad (Node.js) - 설치되지 않음")
    except:
        frameworks.append("❌ Agent Squad (Node.js) - 확인 불가")
    
    # 결과 출력
    for framework in frameworks:
        print(framework)
    
    # 권장사항
    print("\n📋 T-Developer 프로젝트 권장사항:")
    print("1. 🎯 주력 프레임워크: Phi (Agno) - 이미 설치됨")
    print("2. 🔄 대안: 직접 구현한 멀티에이전트 시스템")
    print("3. 🐳 Docker: Agent Squad를 Docker 환경에서 실행")
    
    return True

def create_simple_multi_agent_example():
    """간단한 멀티에이전트 예제 생성"""
    example_code = '''
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
'''
    
    with open('/home/ec2-user/T-DeveloperMVP/examples/multi-agent-example.py', 'w') as f:
        f.write(example_code)
    
    print("\n📁 예제 파일 생성: examples/multi-agent-example.py")

if __name__ == "__main__":
    import os
    os.makedirs('/home/ec2-user/T-DeveloperMVP/examples', exist_ok=True)
    
    check_multi_agent_frameworks()
    create_simple_multi_agent_example()