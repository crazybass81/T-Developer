#!/usr/bin/env python3
"""모든 에이전트에 페르소나 적용"""

import os
import re
from pathlib import Path

agents_dir = Path("/home/ec2-user/T-Developer/backend/packages/agents")

# 업데이트할 에이전트 파일들과 페르소나 이름 매핑
agent_persona_map = {
    "external_researcher.py": "ExternalResearcher",
    "gap_analyzer.py": "GapAnalyzer",
    "system_architect.py": "SystemArchitect",
    "orchestrator_designer.py": "OrchestratorDesigner",
    "planner_agent.py": "PlannerAgent",
    "task_creator_agent.py": "TaskCreatorAgent",
    "code_generator.py": "CodeGenerator",
    "quality_gate.py": "QualityGate",
    "static_analyzer.py": "StaticAnalyzer",
    "behavior_analyzer.py": "BehaviorAnalyzer",
    "impact_analyzer.py": "ImpactAnalyzer"
}

def add_persona_to_init(file_path, persona_name):
    """__init__ 메서드에 페르소나 적용 코드 추가"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 이미 페르소나가 있는지 확인
    if 'self.persona = get_persona' in content:
        print(f"  ⏭️ {file_path.name} already has persona")
        return False
    
    # self.capabilities 또는 self.config 뒤에 페르소나 코드 추가
    pattern = r'(self\.capabilities = \[.*?\]|self\.config = .*?)(\n)'
    
    persona_code = f'''\\1\\2
        
        # 페르소나 적용 - {persona_name}
        from .personas import get_persona
        self.persona = get_persona("{persona_name}")
        if self.persona:
            logger.info(f"🎭 {{self.persona.name}}: {{self.persona.catchphrase}}")\\2'''
    
    new_content = re.sub(pattern, persona_code, content, count=1)
    
    if new_content == content:
        # 패턴을 찾지 못한 경우, __init__ 끝 부분에 추가
        init_pattern = r'(def __init__\([^)]*\):[^}]*?)(\n\s+def |\n\s+async def |\nclass |\Z)'
        
        persona_code = f'''\\1
        
        # 페르소나 적용 - {persona_name}
        from .personas import get_persona
        self.persona = get_persona("{persona_name}")
        if self.persona:
            logger.info(f"🎭 {{self.persona.name}}: {{self.persona.catchphrase}}")
\\2'''
        
        new_content = re.sub(init_pattern, persona_code, content, count=1, flags=re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def add_persona_to_prompts(file_path):
    """AI 프롬프트에 페르소나 추가"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 이미 페르소나 프롬프트가 있는지 확인
    if 'persona_prompt' in content or 'self.persona.to_prompt()' in content:
        return False
    
    # system_prompt 패턴 찾기
    pattern = r'(system_prompt\s*=\s*)("""[^"]*"""|\'\'\'[^\']*\'\'\'|f"""[^"]*""")'
    
    def replace_system_prompt(match):
        indent = "        "  # 기본 들여쓰기
        return f'''{indent}# 페르소나 적용
{indent}persona_prompt = self.persona.to_prompt() if self.persona else ""
{indent}
{indent}system_prompt = f"""{{persona_prompt}}

{match.group(2)[3:-3]}"""'''
    
    new_content = re.sub(pattern, replace_system_prompt, content, count=1)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def main():
    print("=" * 60)
    print("모든 에이전트에 페르소나 적용")
    print("=" * 60)
    
    init_updated = 0
    prompt_updated = 0
    
    for agent_file, persona_name in agent_persona_map.items():
        file_path = agents_dir / agent_file
        
        if not file_path.exists():
            print(f"❌ {agent_file} not found")
            continue
        
        print(f"\n처리 중: {agent_file}")
        
        # 1. __init__에 페르소나 추가
        if add_persona_to_init(file_path, persona_name):
            print(f"  ✅ 페르소나 초기화 추가됨")
            init_updated += 1
        
        # 2. AI 프롬프트에 페르소나 추가
        if add_persona_to_prompts(file_path):
            print(f"  ✅ AI 프롬프트에 페르소나 추가됨")
            prompt_updated += 1
    
    print("\n" + "=" * 60)
    print(f"완료:")
    print(f"  - __init__ 업데이트: {init_updated}개")
    print(f"  - AI 프롬프트 업데이트: {prompt_updated}개")
    print("=" * 60)

if __name__ == "__main__":
    main()