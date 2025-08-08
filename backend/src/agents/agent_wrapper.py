#!/usr/bin/env python3
"""
Python Agent Wrapper
TypeScript에서 호출 가능한 Python Agent 래퍼
"""

import sys
import json
import argparse
import importlib
from pathlib import Path
from typing import Dict, Any

# 프로젝트 루트 경로 설정
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def load_agent(agent_name: str):
    """동적으로 에이전트 모듈 로드"""
    try:
        module_path = f"backend.src.agents.implementations.{agent_name}.{agent_name}"
        return importlib.import_module(module_path)
    except ImportError as e:
        # 대체 경로 시도
        try:
            module_path = f"backend.src.agents.{agent_name}"
            return importlib.import_module(module_path)
        except ImportError:
            raise ImportError(f"Cannot load agent: {agent_name}. Error: {e}")

def execute_agent_method(agent_module, method_name: str, input_data: Dict[str, Any]):
    """에이전트 메소드 실행"""
    # 에이전트 클래스 찾기
    agent_class = None
    for attr_name in dir(agent_module):
        attr = getattr(agent_module, attr_name)
        if isinstance(attr, type) and 'Agent' in attr_name:
            agent_class = attr
            break
    
    if not agent_class:
        raise ValueError(f"No Agent class found in module")
    
    # 에이전트 인스턴스 생성 및 메소드 실행
    agent_instance = agent_class()
    
    if hasattr(agent_instance, method_name):
        method = getattr(agent_instance, method_name)
        return method(**input_data)
    else:
        raise ValueError(f"Method {method_name} not found in agent")

def main():
    parser = argparse.ArgumentParser(description='Python Agent Wrapper')
    parser.add_argument('agent_name', help='Name of the agent to execute')
    parser.add_argument('--method', required=True, help='Method to call on the agent')
    parser.add_argument('--input', required=True, help='JSON input for the agent')
    
    args = parser.parse_args()
    
    try:
        # JSON 입력 파싱
        input_data = json.loads(args.input)
        
        # 에이전트 로드 및 실행
        agent_module = load_agent(args.agent_name)
        result = execute_agent_method(agent_module, args.method, input_data)
        
        # 결과 출력 (JSON 형식)
        output = {
            'success': True,
            'result': result
        }
        print(json.dumps(output))
        
    except Exception as e:
        # 에러 출력
        error_output = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_output), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()