#!/usr/bin/env python3
"""
Lambda Agent 배포 스크립트
Production-ready Python 에이전트를 AWS Lambda에 배포
"""

import os
import sys
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import boto3
from botocore.exceptions import ClientError

# AWS 클라이언트
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')
s3_client = boto3.client('s3')


class LambdaAgentDeployer:
    """Lambda Agent 배포 관리자"""
    
    def __init__(self, environment: str = 'development'):
        """
        초기화
        
        Args:
            environment: 배포 환경 (development/staging/production)
        """
        self.environment = environment
        self.project_root = Path(__file__).parent.parent.parent
        self.lambda_dir = self.project_root / 'backend' / 'src' / 'lambda' / 'agents'
        self.deployment_bucket = f't-developer-deployments-{environment}'
        
        # 에이전트 설정
        self.agents = [
            {
                'name': 'nl-input-agent',
                'file': 'nl_input_agent.py',
                'handler': 'nl_input_agent.lambda_handler',
                'memory': 512,
                'timeout': 30,
                'description': 'Natural Language Input Processing Agent'
            },
            {
                'name': 'ui-selection-agent',
                'file': 'ui_selection_agent.py',
                'handler': 'ui_selection_agent.lambda_handler',
                'memory': 256,
                'timeout': 10,
                'description': 'UI Framework Selection Agent'
            },
            {
                'name': 'parser-agent',
                'file': 'parser_agent.py',
                'handler': 'parser_agent.lambda_handler',
                'memory': 256,
                'timeout': 20,
                'description': 'Project Structure Parser Agent'
            },
            {
                'name': 'match-rate-agent',
                'file': 'match_rate_agent.py',
                'handler': 'match_rate_agent.lambda_handler',
                'memory': 256,
                'timeout': 15,
                'description': 'Template Match Rate Calculation Agent'
            },
            {
                'name': 'search-agent',
                'file': 'search_agent.py',
                'handler': 'search_agent.lambda_handler',
                'memory': 512,
                'timeout': 10,
                'description': 'Code Template Search Agent'
            }
        ]
        
        # Lambda Layer 설정
        self.layer_name = f't-developer-agent-dependencies-{environment}'
        
        print(f"🚀 Lambda Agent Deployer initialized for {environment}")
    
    def create_deployment_bucket(self):
        """배포용 S3 버킷 생성"""
        try:
            s3_client.head_bucket(Bucket=self.deployment_bucket)
            print(f"✅ Deployment bucket exists: {self.deployment_bucket}")
        except ClientError:
            try:
                s3_client.create_bucket(
                    Bucket=self.deployment_bucket,
                    CreateBucketConfiguration={'LocationConstraint': 'us-east-1'}
                )
                print(f"✅ Created deployment bucket: {self.deployment_bucket}")
            except Exception as e:
                print(f"❌ Failed to create bucket: {e}")
                sys.exit(1)
    
    def create_lambda_role(self) -> str:
        """Lambda 실행 역할 생성/확인"""
        role_name = f't-developer-lambda-role-{self.environment}'
        
        try:
            # 역할이 이미 존재하는지 확인
            response = iam_client.get_role(RoleName=role_name)
            print(f"✅ Using existing Lambda role: {role_name}")
            return response['Role']['Arn']
        except ClientError:
            # 역할 생성
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
            try:
                response = iam_client.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy),
                    Description='Lambda execution role for T-Developer agents'
                )
                
                # 정책 연결
                policies = [
                    'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
                    'arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess'
                ]
                
                for policy_arn in policies:
                    iam_client.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
                
                # 커스텀 정책 생성 및 연결
                custom_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "ssm:GetParameter",
                                "ssm:GetParameters",
                                "ssm:GetParametersByPath"
                            ],
                            "Resource": f"arn:aws:ssm:*:*:parameter/t-developer/{self.environment}/*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "secretsmanager:GetSecretValue"
                            ],
                            "Resource": f"arn:aws:secretsmanager:*:*:secret:t-developer/{self.environment}/*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:GetObject",
                                "s3:PutObject"
                            ],
                            "Resource": f"arn:aws:s3:::t-developer-*/*"
                        },
                        {
                            "Effect": "Allow",
                            "Action": [
                                "bedrock:InvokeModel",
                                "bedrock:InvokeAgent"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
                
                policy_name = f't-developer-lambda-policy-{self.environment}'
                iam_client.put_role_policy(
                    RoleName=role_name,
                    PolicyName=policy_name,
                    PolicyDocument=json.dumps(custom_policy)
                )
                
                print(f"✅ Created Lambda role: {role_name}")
                return response['Role']['Arn']
                
            except Exception as e:
                print(f"❌ Failed to create role: {e}")
                sys.exit(1)
    
    def create_lambda_layer(self) -> str:
        """의존성 Layer 생성"""
        print(f"📦 Creating Lambda layer: {self.layer_name}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            layer_dir = Path(temp_dir) / 'python'
            layer_dir.mkdir()
            
            # requirements.txt 복사
            requirements_file = self.lambda_dir.parent.parent.parent / 'requirements-lambda.txt'
            if not requirements_file.exists():
                # Lambda용 경량 requirements 생성
                requirements_content = """
boto3>=1.34.0
botocore>=1.34.0
aws-lambda-powertools>=2.28.0
pydantic>=2.5.0
"""
                requirements_file.write_text(requirements_content.strip())
            
            # 의존성 설치
            os.system(f"pip install -r {requirements_file} -t {layer_dir} --quiet")
            
            # ZIP 파일 생성
            zip_file = Path(temp_dir) / 'layer.zip'
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != 'layer.zip':
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(temp_dir)
                            zipf.write(file_path, arcname)
            
            # S3에 업로드
            layer_key = f'layers/{self.layer_name}.zip'
            s3_client.upload_file(
                str(zip_file),
                self.deployment_bucket,
                layer_key
            )
            
            # Layer 생성/업데이트
            try:
                response = lambda_client.publish_layer_version(
                    LayerName=self.layer_name,
                    Description='T-Developer agent dependencies',
                    Content={
                        'S3Bucket': self.deployment_bucket,
                        'S3Key': layer_key
                    },
                    CompatibleRuntimes=['python3.9', 'python3.10', 'python3.11']
                )
                
                print(f"✅ Created layer version: {response['Version']}")
                return response['LayerVersionArn']
                
            except Exception as e:
                print(f"❌ Failed to create layer: {e}")
                sys.exit(1)
    
    def package_agent(self, agent_config: Dict) -> str:
        """에이전트 코드 패키징"""
        agent_file = self.lambda_dir / agent_config['file']
        
        if not agent_file.exists():
            print(f"⚠️ Agent file not found: {agent_file}")
            print(f"   Skipping {agent_config['name']}")
            return None
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # 에이전트 파일 복사
            shutil.copy(agent_file, Path(temp_dir) / agent_config['file'])
            
            # __init__.py 생성
            init_file = Path(temp_dir) / '__init__.py'
            init_file.write_text('')
            
            # ZIP 생성
            zip_file = Path(temp_dir) / f"{agent_config['name']}.zip"
            with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in Path(temp_dir).glob('*.py'):
                    zipf.write(file, file.name)
            
            # S3에 업로드
            s3_key = f"agents/{agent_config['name']}.zip"
            s3_client.upload_file(
                str(zip_file),
                self.deployment_bucket,
                s3_key
            )
            
            return s3_key
    
    def deploy_agent(self, agent_config: Dict, role_arn: str, layer_arn: str):
        """개별 에이전트 배포"""
        function_name = f"t-developer-{agent_config['name']}-{self.environment}"
        
        # 코드 패키징
        s3_key = self.package_agent(agent_config)
        if not s3_key:
            return
        
        # Lambda 함수 생성/업데이트
        try:
            # 함수가 존재하는지 확인
            lambda_client.get_function(FunctionName=function_name)
            
            # 업데이트
            lambda_client.update_function_code(
                FunctionName=function_name,
                S3Bucket=self.deployment_bucket,
                S3Key=s3_key
            )
            
            # 설정 업데이트
            lambda_client.update_function_configuration(
                FunctionName=function_name,
                Runtime='python3.11',
                Handler=agent_config['handler'],
                Description=agent_config['description'],
                Timeout=agent_config['timeout'],
                MemorySize=agent_config['memory'],
                Environment={
                    'Variables': {
                        'ENVIRONMENT': self.environment,
                        'POWERTOOLS_SERVICE_NAME': agent_config['name'],
                        'POWERTOOLS_METRICS_NAMESPACE': 't-developer'
                    }
                },
                Layers=[layer_arn]
            )
            
            print(f"✅ Updated function: {function_name}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # 새 함수 생성
                try:
                    lambda_client.create_function(
                        FunctionName=function_name,
                        Runtime='python3.11',
                        Role=role_arn,
                        Handler=agent_config['handler'],
                        Code={
                            'S3Bucket': self.deployment_bucket,
                            'S3Key': s3_key
                        },
                        Description=agent_config['description'],
                        Timeout=agent_config['timeout'],
                        MemorySize=agent_config['memory'],
                        Environment={
                            'Variables': {
                                'ENVIRONMENT': self.environment,
                                'POWERTOOLS_SERVICE_NAME': agent_config['name'],
                                'POWERTOOLS_METRICS_NAMESPACE': 't-developer'
                            }
                        },
                        Layers=[layer_arn],
                        TracingConfig={'Mode': 'Active'}
                    )
                    
                    print(f"✅ Created function: {function_name}")
                    
                except Exception as create_error:
                    print(f"❌ Failed to create function {function_name}: {create_error}")
            else:
                print(f"❌ Error with function {function_name}: {e}")
    
    def deploy_all(self):
        """모든 에이전트 배포"""
        print(f"\n🚀 Deploying T-Developer Lambda Agents to {self.environment}")
        print("=" * 60)
        
        # 1. S3 버킷 준비
        self.create_deployment_bucket()
        
        # 2. IAM 역할 준비
        role_arn = self.create_lambda_role()
        
        # 3. Lambda Layer 생성
        layer_arn = self.create_lambda_layer()
        
        # 4. 각 에이전트 배포
        print(f"\n📦 Deploying {len(self.agents)} agents...")
        for agent_config in self.agents:
            print(f"\n🔧 Deploying {agent_config['name']}...")
            self.deploy_agent(agent_config, role_arn, layer_arn)
        
        print("\n" + "=" * 60)
        print(f"✅ Deployment complete for {self.environment} environment!")
        print(f"\n📋 Deployed functions:")
        for agent_config in self.agents:
            function_name = f"t-developer-{agent_config['name']}-{self.environment}"
            print(f"   - {function_name}")
        
        # API Gateway 통합 정보
        print(f"\n🔗 API Gateway integration:")
        print(f"   Use these function ARNs for API Gateway integration:")
        for agent_config in self.agents:
            function_name = f"t-developer-{agent_config['name']}-{self.environment}"
            print(f"   - arn:aws:lambda:*:*:function:{function_name}")
    
    def test_deployment(self):
        """배포된 함수 테스트"""
        print(f"\n🧪 Testing deployed functions...")
        
        test_payloads = {
            'nl-input-agent': {
                'body': json.dumps({
                    'query': 'React로 Todo 앱을 만들어줘',
                    'framework': 'react'
                })
            },
            'ui-selection-agent': {
                'body': json.dumps({
                    'project_type': 'web-application',
                    'requirements': {
                        'performance_critical': True
                    },
                    'preferences': {
                        'framework': 'react'
                    }
                })
            }
        }
        
        for agent_config in self.agents[:2]:  # 처음 2개만 테스트
            if agent_config['name'] in test_payloads:
                function_name = f"t-developer-{agent_config['name']}-{self.environment}"
                
                try:
                    response = lambda_client.invoke(
                        FunctionName=function_name,
                        InvocationType='RequestResponse',
                        Payload=json.dumps(test_payloads[agent_config['name']])
                    )
                    
                    status_code = response['StatusCode']
                    if status_code == 200:
                        print(f"   ✅ {agent_config['name']}: Test passed")
                    else:
                        print(f"   ❌ {agent_config['name']}: Test failed (status {status_code})")
                        
                except Exception as e:
                    print(f"   ❌ {agent_config['name']}: Test error - {e}")


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy T-Developer Lambda Agents')
    parser.add_argument(
        '--env',
        choices=['development', 'staging', 'production'],
        default='development',
        help='Deployment environment'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test deployed functions'
    )
    
    args = parser.parse_args()
    
    # 배포 실행
    deployer = LambdaAgentDeployer(args.env)
    deployer.deploy_all()
    
    # 테스트 실행
    if args.test:
        deployer.test_deployment()


if __name__ == '__main__':
    main()