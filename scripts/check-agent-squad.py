#!/usr/bin/env python3
# scripts/check-agent-squad.py

def check_agent_squad_installation():
    """Agent Squad 설치 확인"""
    print("🔍 Agent Squad 설치 확인 중...")
    
    # Node.js 패키지 확인
    import subprocess
    import json
    
    try:
        # npm list로 agent-squad 확인
        result = subprocess.run(['npm', 'list', 'agent-squad', '--json'], 
                              capture_output=True, text=True, cwd='/home/ec2-user/T-DeveloperMVP')
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'dependencies' in data and 'agent-squad' in data['dependencies']:
                version = data['dependencies']['agent-squad']['version']
                print(f"✅ Agent Squad 설치 확인됨 (버전: {version})")
                return True
        
        print("❌ Agent Squad가 설치되지 않음")
        print("📋 설치 방법:")
        print("   npm install agent-squad")
        print("\n⚠️  참고: Agent Squad는 SQLite 의존성으로 인해 Node.js v18-20 권장")
        print("   현재 Node.js v22에서는 컴파일 오류 발생 가능")
        
        # 대안 제안
        print("\n🔄 대안:")
        print("1. Node.js v18 또는 v20 사용")
        print("2. Docker 환경에서 Agent Squad 실행")
        print("3. Python 기반 멀티에이전트 프레임워크 사용")
        
        return False
        
    except Exception as e:
        print(f"❌ 확인 중 오류 발생: {e}")
        return False

def suggest_alternatives():
    """Agent Squad 대안 제안"""
    print("\n🔧 Agent Squad 대안 프레임워크:")
    print("1. CrewAI (Python) - pip install crewai")
    print("2. AutoGen (Python) - pip install pyautogen")
    print("3. LangGraph (Python) - pip install langgraph")
    print("4. Phi (Agno) 직접 사용 - 이미 설치됨")

if __name__ == "__main__":
    success = check_agent_squad_installation()
    if not success:
        suggest_alternatives()
        print("\n💡 현재 환경에서는 Phi (Agno) 프레임워크를 직접 사용하는 것을 권장합니다.")