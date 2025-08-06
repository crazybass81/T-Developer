#!/usr/bin/env python3
"""
CloudWatch 대시보드 생성 스크립트
"""
import boto3
import json
import os
from pathlib import Path

def create_dashboard():
    """CloudWatch 대시보드 생성"""
    cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
    
    # 템플릿 파일 로드
    template_path = Path(__file__).parent.parent / 'cloudwatch' / 'dashboard-template.json'
    
    with open(template_path, 'r') as f:
        dashboard_body = f.read()
    
    try:
        # 대시보드 생성
        response = cloudwatch.put_dashboard(
            DashboardName='T-Developer-Monitoring',
            DashboardBody=dashboard_body
        )
        
        print("✅ CloudWatch 대시보드 생성 완료")
        print(f"📊 대시보드 URL: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=T-Developer-Monitoring")
        
        return True
        
    except Exception as e:
        print(f"❌ 대시보드 생성 실패: {e}")
        return False

def create_alarms():
    """기본 알람 생성"""
    cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
    
    alarms = [
        {
            'AlarmName': 'T-Developer-High-Error-Rate',
            'ComparisonOperator': 'GreaterThanThreshold',
            'EvaluationPeriods': 2,
            'MetricName': 'Errors',
            'Namespace': 'AWS/Lambda',
            'Period': 300,
            'Statistic': 'Sum',
            'Threshold': 10.0,
            'ActionsEnabled': True,
            'AlarmDescription': 'T-Developer Lambda 에러율 높음',
            'Unit': 'Count'
        },
        {
            'AlarmName': 'T-Developer-Agent-Execution-Time',
            'ComparisonOperator': 'GreaterThanThreshold',
            'EvaluationPeriods': 3,
            'MetricName': 'AgentExecutionTime',
            'Namespace': 'T-Developer',
            'Period': 300,
            'Statistic': 'Average',
            'Threshold': 30000.0,
            'ActionsEnabled': True,
            'AlarmDescription': 'T-Developer 에이전트 실행 시간 초과',
            'Unit': 'Milliseconds'
        }
    ]
    
    for alarm in alarms:
        try:
            cloudwatch.put_metric_alarm(**alarm)
            print(f"✅ 알람 생성 완료: {alarm['AlarmName']}")
        except Exception as e:
            print(f"❌ 알람 생성 실패 {alarm['AlarmName']}: {e}")

if __name__ == "__main__":
    print("🔧 CloudWatch 대시보드 및 알람 설정 중...")
    
    if create_dashboard():
        create_alarms()
        print("\n✅ CloudWatch 설정 완료!")
    else:
        print("\n❌ CloudWatch 설정 실패")