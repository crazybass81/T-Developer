#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T-Developer Secret Scanner Lambda Function
비밀번호, API 키 등 민감한 정보를 자동으로 탐지하고 보고하는 Lambda 함수

Environment Variables:
- PROJECT_NAME: 프로젝트 이름
- ENVIRONMENT: 환경 (development/staging/production)
- EMERGENCY_SNS_TOPIC: 긴급 알림 SNS 토픽
- SAFETY_SNS_TOPIC: 안전 알림 SNS 토픽
- SECRETS_KMS_KEY: Secrets Manager KMS 키
- DISCOVERY_PREFIX: 발견된 비밀 저장 프리픽스
"""

import json
import re
import os
import boto3
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from urllib.parse import unquote_plus
import base64
import hashlib

# 로깅 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS 클라이언트 초기화
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
ssm_client = boto3.client('ssm')
secrets_client = boto3.client('secretsmanager')

# 환경 변수 로드
PROJECT_NAME = os.environ.get('PROJECT_NAME', 't-developer')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
EMERGENCY_SNS_TOPIC = os.environ['EMERGENCY_SNS_TOPIC']
SAFETY_SNS_TOPIC = os.environ['SAFETY_SNS_TOPIC']
SECRETS_KMS_KEY = os.environ['SECRETS_KMS_KEY']
DISCOVERY_PREFIX = os.environ['DISCOVERY_PREFIX']

class SecretPattern:
    """비밀 탐지 패턴 클래스"""
    
    def __init__(self, name: str, pattern: str, severity: str, description: str):
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.severity = severity
        self.description = description
    
    def search(self, content: str) -> List[Dict[str, Any]]:
        """컨텐츠에서 패턴 검색"""
        matches = []
        for match in self.pattern.finditer(content):
            start, end = match.span()
            # 컨텍스트 추출 (전후 50자)
            context_start = max(0, start - 50)
            context_end = min(len(content), end + 50)
            context = content[context_start:context_end]
            
            matches.append({
                'pattern_name': self.name,
                'severity': self.severity,
                'description': self.description,
                'match': match.group(),
                'position': {'start': start, 'end': end},
                'context': context,
                'line_number': content[:start].count('\n') + 1
            })
        
        return matches

class SecretScanner:
    """메인 비밀 스캐너 클래스"""
    
    def __init__(self):
        self.patterns = self._load_detection_patterns()
        self.excluded_patterns = []
        self.supported_extensions = {
            '.py', '.js', '.ts', '.java', '.go', '.rb', '.php',
            '.json', '.yaml', '.yml', '.xml', '.conf', '.cfg',
            '.env', '.properties', '.ini', '.toml', '.sh', '.bash'
        }
    
    def _load_detection_patterns(self) -> List[SecretPattern]:
        """Parameter Store에서 탐지 패턴 로드"""
        try:
            param_name = f"/{PROJECT_NAME}/{ENVIRONMENT}/security/secret-detection-rules"
            response = ssm_client.get_parameter(Name=param_name, WithDecryption=True)
            rules = json.loads(response['Parameter']['Value'])
            
            patterns = []
            for pattern_name in rules.get('enabled_patterns', []):
                if pattern_name in rules['regex_patterns']:
                    regex = rules['regex_patterns'][pattern_name]
                    severity = rules['severity_levels'].get(pattern_name, 'MEDIUM')
                    
                    patterns.append(SecretPattern(
                        name=pattern_name,
                        pattern=regex,
                        severity=severity,
                        description=f"Detected {pattern_name.replace('_', ' ').title()}"
                    ))
            
            # 제외 패턴 설정
            self.excluded_patterns = [
                re.compile(pattern, re.IGNORECASE) 
                for pattern in rules.get('excluded_patterns', [])
            ]
            
            logger.info(f"Loaded {len(patterns)} detection patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to load detection patterns: {str(e)}")
            # 기본 패턴으로 폴백
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> List[SecretPattern]:
        """기본 탐지 패턴"""
        return [
            SecretPattern(
                'aws_access_key',
                r'AKIA[0-9A-Z]{16}',
                'CRITICAL',
                'AWS Access Key ID detected'
            ),
            SecretPattern(
                'aws_secret_key', 
                r'aws.{0,20}[\'"][0-9a-zA-Z/+]{40}[\'"]',
                'CRITICAL',
                'AWS Secret Access Key detected'
            ),
            SecretPattern(
                'private_key',
                r'-----BEGIN [A-Z]+ PRIVATE KEY-----',
                'CRITICAL',
                'Private key detected'
            ),
            SecretPattern(
                'api_key',
                r'(api[_-]?key|apikey).{0,20}[\'"][0-9a-zA-Z]{20,}[\'"]',
                'HIGH',
                'API key detected'
            ),
            SecretPattern(
                'password',
                r'(password|pass|pwd).{0,20}[\'"][^\'"\\s]{6,}[\'"]',
                'MEDIUM',
                'Password detected'
            )
        ]
    
    def _is_excluded(self, content: str, match: Dict[str, Any]) -> bool:
        """제외 패턴 확인"""
        for excluded_pattern in self.excluded_patterns:
            if excluded_pattern.search(match['context']):
                return True
        return False
    
    def _should_scan_file(self, key: str) -> bool:
        """파일 스캔 여부 결정"""
        # 확장자 확인
        if any(key.lower().endswith(ext) for ext in self.supported_extensions):
            return True
        
        # 확장자가 없는 설정 파일들
        filename = os.path.basename(key).lower()
        if filename in {'dockerfile', 'makefile', 'jenkinsfile', 'readme'}:
            return True
            
        return False
    
    def scan_content(self, content: str, source_info: Dict[str, str]) -> Dict[str, Any]:
        """컨텐츠 스캔"""
        scan_result = {
            'source': source_info,
            'timestamp': datetime.utcnow().isoformat(),
            'findings': [],
            'summary': {
                'total_findings': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
        
        # 각 패턴으로 스캔
        for pattern in self.patterns:
            matches = pattern.search(content)
            
            for match in matches:
                if not self._is_excluded(content, match):
                    # 매치된 비밀 정보 해시화 (보안상)
                    secret_hash = hashlib.sha256(match['match'].encode()).hexdigest()[:16]
                    
                    finding = {
                        'id': f"{pattern.name}_{secret_hash}",
                        'pattern': pattern.name,
                        'severity': pattern.severity,
                        'description': pattern.description,
                        'line_number': match['line_number'],
                        'context': match['context'][:200],  # 컨텍스트 길이 제한
                        'hash': secret_hash,
                        'position': match['position']
                    }
                    
                    scan_result['findings'].append(finding)
                    scan_result['summary']['total_findings'] += 1
                    scan_result['summary'][pattern.severity.lower()] += 1
        
        return scan_result
    
    def scan_s3_object(self, bucket: str, key: str) -> Dict[str, Any]:
        """S3 객체 스캔"""
        source_info = {
            'type': 's3',
            'bucket': bucket,
            'key': key,
            'size': 0
        }
        
        try:
            # 파일 스캔 필요성 확인
            if not self._should_scan_file(key):
                logger.info(f"Skipping unsupported file: {key}")
                return {'source': source_info, 'findings': [], 'skipped': True}
            
            # 객체 메타데이터 확인
            head_response = s3_client.head_object(Bucket=bucket, Key=key)
            file_size = head_response['ContentLength']
            source_info['size'] = file_size
            
            # 큰 파일 제한 (10MB)
            if file_size > 10 * 1024 * 1024:
                logger.warning(f"File too large to scan: {key} ({file_size} bytes)")
                return {'source': source_info, 'findings': [], 'too_large': True}
            
            # 객체 다운로드
            response = s3_client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read()
            
            # 바이너리 파일 감지
            if b'\x00' in content:
                logger.info(f"Binary file detected, skipping: {key}")
                return {'source': source_info, 'findings': [], 'binary_file': True}
            
            # 텍스트로 디코드
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_content = content.decode('latin-1')
                except UnicodeDecodeError:
                    logger.warning(f"Cannot decode file: {key}")
                    return {'source': source_info, 'findings': [], 'decode_error': True}
            
            # 스캔 수행
            return self.scan_content(text_content, source_info)
            
        except Exception as e:
            logger.error(f"Error scanning {bucket}/{key}: {str(e)}")
            return {
                'source': source_info,
                'findings': [],
                'error': str(e)
            }

def quarantine_secret(bucket: str, key: str, finding: Dict[str, Any]) -> bool:
    """발견된 비밀을 격리"""
    try:
        quarantine_bucket = f"{PROJECT_NAME}-discovered-secrets-{ENVIRONMENT}"
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        quarantine_key = f"quarantine/{timestamp}/{finding['severity']}/{finding['id']}/{key}"
        
        # 원본 파일을 격리 버킷으로 복사
        copy_source = {'Bucket': bucket, 'Key': key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=quarantine_bucket,
            Key=quarantine_key,
            ServerSideEncryption='aws:kms',
            SSEKMSKeyId=SECRETS_KMS_KEY,
            Metadata={
                'original-bucket': bucket,
                'original-key': key,
                'severity': finding['severity'],
                'pattern': finding['pattern'],
                'quarantine-timestamp': timestamp,
                'finding-id': finding['id']
            },
            MetadataDirective='REPLACE'
        )
        
        logger.info(f"Secret quarantined: {quarantine_key}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to quarantine secret: {str(e)}")
        return False

def send_alert(scan_result: Dict[str, Any]) -> None:
    """스캔 결과에 따른 알림 발송"""
    summary = scan_result['summary']
    source = scan_result['source']
    
    if summary['critical'] > 0:
        # 중요 비밀 발견 - 긴급 알림
        message = {
            'alert_type': 'CRITICAL_SECRET_DETECTED',
            'environment': ENVIRONMENT,
            'source': source,
            'summary': summary,
            'timestamp': scan_result['timestamp'],
            'action_required': True,
            'findings': [f for f in scan_result['findings'] if f['severity'] == 'CRITICAL']
        }
        
        sns_client.publish(
            TopicArn=EMERGENCY_SNS_TOPIC,
            Subject=f"🚨 CRITICAL: Secret Detected in {source['bucket']}/{source['key']}",
            Message=json.dumps(message, indent=2)
        )
        
        logger.error(f"CRITICAL_SECRET_DETECTED in {source['bucket']}/{source['key']}")
        
    elif summary['high'] > 0:
        # 높은 위험도 비밀 - 안전 알림
        message = {
            'alert_type': 'HIGH_SEVERITY_SECRET',
            'environment': ENVIRONMENT,
            'source': source,
            'summary': summary,
            'timestamp': scan_result['timestamp'],
            'findings': [f for f in scan_result['findings'] if f['severity'] == 'HIGH']
        }
        
        sns_client.publish(
            TopicArn=SAFETY_SNS_TOPIC,
            Subject=f"⚠️ HIGH: Secret Detected in {source['bucket']}/{source['key']}",
            Message=json.dumps(message, indent=2)
        )
        
        logger.warning(f"HIGH_SEVERITY_SECRET in {source['bucket']}/{source['key']}")
        
    elif summary['total_findings'] > 0:
        # 중간 위험도 비밀 - 로그만
        logger.info(f"Medium severity secrets detected in {source['bucket']}/{source['key']}: {summary}")

def lambda_handler(event, context):
    """Lambda 메인 핸들러"""
    logger.info(f"Secret scanner started. Event: {json.dumps(event)}")
    
    scanner = SecretScanner()
    processed = 0
    findings_total = 0
    
    try:
        # S3 이벤트 처리
        if 'Records' in event:
            for record in event['Records']:
                if record['eventSource'] == 'aws:s3':
                    bucket = record['s3']['bucket']['name']
                    key = unquote_plus(record['s3']['object']['key'])
                    
                    logger.info(f"Scanning S3 object: {bucket}/{key}")
                    scan_result = scanner.scan_s3_object(bucket, key)
                    
                    if scan_result.get('findings'):
                        findings_total += len(scan_result['findings'])
                        
                        # 알림 발송
                        send_alert(scan_result)
                        
                        # 중요한 비밀은 자동 격리
                        critical_findings = [
                            f for f in scan_result['findings'] 
                            if f['severity'] == 'CRITICAL'
                        ]
                        
                        for finding in critical_findings:
                            quarantine_secret(bucket, key, finding)
                    
                    processed += 1
        
        # 수동 전체 스캔 처리
        elif event.get('scan_type') == 'full':
            buckets = event.get('buckets', [])
            for bucket in buckets:
                logger.info(f"Starting full scan of bucket: {bucket}")
                
                paginator = s3_client.get_paginator('list_objects_v2')
                page_iterator = paginator.paginate(Bucket=bucket)
                
                for page in page_iterator:
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            key = obj['Key']
                            scan_result = scanner.scan_s3_object(bucket, key)
                            
                            if scan_result.get('findings'):
                                findings_total += len(scan_result['findings'])
                                send_alert(scan_result)
                            
                            processed += 1
                            
                            # Lambda 실행 시간 제한 고려 (4분 50초에서 중단)
                            if context.get_remaining_time_in_millis() < 10000:
                                logger.warning("Lambda timeout approaching, stopping scan")
                                break
        
        # 응답 구성
        response = {
            'statusCode': 200,
            'body': {
                'message': 'Secret scan completed',
                'processed_objects': processed,
                'total_findings': findings_total,
                'timestamp': datetime.utcnow().isoformat(),
                'environment': ENVIRONMENT
            }
        }
        
        logger.info(f"Scan completed. Processed: {processed}, Findings: {findings_total}")
        return response
        
    except Exception as e:
        logger.error(f"Secret scanner error: {str(e)}")
        
        # 에러 알림
        sns_client.publish(
            TopicArn=SAFETY_SNS_TOPIC,
            Subject=f"❌ Secret Scanner Error - {ENVIRONMENT}",
            Message=f"Secret scanner encountered an error: {str(e)}\n\nEvent: {json.dumps(event)}"
        )
        
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        }

# 테스트용 함수
if __name__ == "__main__":
    # 로컬 테스트
    test_event = {
        'scan_type': 'test',
        'test_content': '''
        # Test content with secrets
        AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
        AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        api_key = "sk-1234567890abcdef1234567890abcdef"
        password = "super_secret_password_123"
        '''
    }
    
    result = lambda_handler(test_event, type('Context', (), {'get_remaining_time_in_millis': lambda: 300000})())
    print(json.dumps(result, indent=2))