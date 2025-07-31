#!/usr/bin/env python3
# scripts/identify_risks.py

import json
import subprocess
import re
import glob
from typing import List, Dict

class RiskAnalyzer:
    def __init__(self):
        self.risks = []
        
    def analyze_package_compatibility(self):
        """패키지 호환성 위험 분석"""
        # requirements.txt 파일 분석
        with open('requirements.txt', 'r') as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        for pkg_line in packages:
            pkg_name = pkg_line.split('>=')[0].split('==')[0].strip()
            
            # 오래된 패키지 확인
            if self._is_legacy_package(pkg_name):
                self.risks.append({
                    'type': 'compatibility',
                    'severity': 'high',
                    'package': pkg_name,
                    'issue': 'Legacy package may not be compatible with uv',
                    'mitigation': f'Test {pkg_name} installation separately'
                })
            
            # 특수 설치 옵션 사용 패키지
            if self._has_special_install_options(pkg_name):
                self.risks.append({
                    'type': 'installation',
                    'severity': 'medium',
                    'package': pkg_name,
                    'issue': 'Package requires special installation options',
                    'mitigation': 'Document installation process'
                })
    
    def analyze_ci_dependencies(self):
        """CI/CD 파이프라인 의존성 분석"""
        # GitHub Actions 워크플로우 분석
        workflows = glob.glob('.github/workflows/*.yml')
        
        for workflow in workflows:
            try:
                with open(workflow, 'r') as f:
                    content = f.read()
                    if 'pip install' in content:
                        self.risks.append({
                            'type': 'ci/cd',
                            'severity': 'medium',
                            'file': workflow,
                            'issue': 'Workflow uses pip directly',
                            'mitigation': 'Update workflow to use uv'
                        })
            except Exception as e:
                print(f"Error reading {workflow}: {e}")
    
    def _is_legacy_package(self, name: str) -> bool:
        # 알려진 레거시 패키지 목록
        legacy_packages = ['nose', 'distribute', 'PIL']
        return name in legacy_packages
    
    def _has_special_install_options(self, name: str) -> bool:
        # 특수 설치가 필요한 패키지
        special_packages = ['mysqlclient', 'psycopg2', 'Pillow']
        return name in special_packages
    
    def generate_report(self):
        """위험 분석 보고서 생성"""
        report = {
            'total_risks': len(self.risks),
            'by_severity': {
                'high': len([r for r in self.risks if r['severity'] == 'high']),
                'medium': len([r for r in self.risks if r['severity'] == 'medium']),
                'low': len([r for r in self.risks if r['severity'] == 'low'])
            },
            'risks': self.risks
        }
        
        with open('risk_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"⚠️  총 {report['total_risks']}개의 위험 요소 발견")
        print(f"   - 높음: {report['by_severity']['high']}")
        print(f"   - 중간: {report['by_severity']['medium']}")
        print(f"   - 낮음: {report['by_severity']['low']}")

if __name__ == "__main__":
    analyzer = RiskAnalyzer()
    analyzer.analyze_package_compatibility()
    analyzer.analyze_ci_dependencies()
    analyzer.generate_report()