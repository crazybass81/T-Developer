#!/usr/bin/env python3
# scripts/check-agno-installation.py

def check_agno_installation():
    """Agno 프레임워크 설치 확인"""
    try:
        # Phi (Agno) 프레임워크 확인
        from phi.agent import Agent
        from phi.model.openai import OpenAIChat
        from phi.model.anthropic import Claude
        
        print("✅ Agno (Phi) 프레임워크 설치 확인됨")
        print("✅ Agent 클래스 임포트 성공")
        print("✅ OpenAI 모델 지원 확인")
        print("✅ Anthropic 모델 지원 확인")
        
        # 간단한 에이전트 생성 테스트
        agent = Agent(
            name="TestAgent",
            model=OpenAIChat(id="gpt-4"),
            description="Test agent for installation verification"
        )
        
        print("✅ 테스트 에이전트 생성 성공")
        print(f"   - 에이전트 이름: {agent.name}")
        print(f"   - 모델: {agent.model.id}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Agno 프레임워크 임포트 실패: {e}")
        print("📋 설치 방법:")
        print("   pip install phidata")
        return False
    except Exception as e:
        print(f"❌ 에이전트 생성 실패: {e}")
        return False

if __name__ == "__main__":
    success = check_agno_installation()
    if success:
        print("\n🎉 Agno 프레임워크가 정상적으로 설치되어 있습니다!")
    else:
        print("\n⚠️  Agno 프레임워크 설치를 확인해주세요.")
        exit(1)