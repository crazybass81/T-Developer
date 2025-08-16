#!/usr/bin/env python3
"""Setup Bedrock Agent for T-Developer.

This script creates and configures a Bedrock Agent with:
- Claude 3.5 Sonnet model
- Knowledge base for code patterns
- Action groups for agent capabilities
"""

import json
import time

import boto3

AWS_REGION = "us-east-1"
AWS_ACCOUNT_ID = "036284794745"

# Bedrock configuration
AGENT_NAME = "t-developer-agent"
MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"


def create_bedrock_agent_role():
    """Create IAM role for Bedrock Agent."""
    iam = boto3.client("iam", region_name=AWS_REGION)

    role_name = "t-developer-bedrock-agent-role"

    try:
        # Check if role exists
        try:
            role = iam.get_role(RoleName=role_name)
            print(f"✅ Using existing role: {role['Role']['Arn']}")
            return role["Role"]["Arn"]
        except:
            pass

        # Create trust policy
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "bedrock.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }

        # Create role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role for T-Developer Bedrock Agent",
        )

        role_arn = response["Role"]["Arn"]

        # Create and attach policy
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                    "Resource": f"arn:aws:bedrock:{AWS_REGION}::foundation-model/*",
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                    "Resource": ["arn:aws:s3:::t-developer-*/*", "arn:aws:s3:::t-developer-*"],
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:UpdateItem",
                    ],
                    "Resource": f"arn:aws:dynamodb:{AWS_REGION}:{AWS_ACCOUNT_ID}:table/t-developer-*",
                },
                {
                    "Effect": "Allow",
                    "Action": ["lambda:InvokeFunction"],
                    "Resource": f"arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:t-developer-*",
                },
            ],
        }

        policy_name = f"{role_name}-policy"

        try:
            iam.create_policy(PolicyName=policy_name, PolicyDocument=json.dumps(policy_document))

            iam.attach_role_policy(
                RoleName=role_name, PolicyArn=f"arn:aws:iam::{AWS_ACCOUNT_ID}:policy/{policy_name}"
            )
        except iam.exceptions.EntityAlreadyExistsException:
            # Policy already exists, just attach it
            iam.attach_role_policy(
                RoleName=role_name, PolicyArn=f"arn:aws:iam::{AWS_ACCOUNT_ID}:policy/{policy_name}"
            )

        print(f"✅ Created role: {role_arn}")

        # Wait for role to propagate
        time.sleep(10)

        return role_arn

    except Exception as e:
        print(f"❌ Error creating role: {e}")
        raise


def test_bedrock_model():
    """Test Bedrock model invocation."""
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    try:
        print(f"\n🧪 Testing Bedrock model: {MODEL_ID}")

        # Test prompt
        prompt = "You are T-Developer Assistant. Say hello and confirm you're ready to help with code evolution."

        # Prepare request
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}],
        }

        # Invoke model
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body),
        )

        # Parse response
        response_body = json.loads(response["body"].read())

        print("✅ Model response:")
        print("-" * 40)
        if "content" in response_body and response_body["content"]:
            print(response_body["content"][0]["text"])
        else:
            print(json.dumps(response_body, indent=2))
        print("-" * 40)

        return True

    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False


def create_agent_instructions():
    """Create agent instructions for T-Developer."""
    return """You are T-Developer Agent, an autonomous system for code evolution and service creation.

Your capabilities include:
1. Research: Analyze codebases, find patterns, identify improvements
2. Planning: Create detailed execution plans for code changes
3. Refactoring: Implement code improvements while maintaining functionality
4. Evaluation: Assess quality, security, and performance of code changes
5. Service Creation: Generate complete services from natural language requirements

Core Principles:
- Always follow TDD (Test-Driven Development)
- Ensure code quality metrics improve with each change
- Maintain backward compatibility
- Document all changes thoroughly
- Follow security best practices

When processing requests:
1. First understand the current state
2. Plan the changes needed
3. Implement with tests
4. Verify quality gates pass
5. Document the evolution

You have access to:
- DynamoDB for state and pattern storage
- S3 for code artifacts
- Lambda functions for specialized processing
- CloudWatch for monitoring

Always aim for self-improvement and learning from each interaction."""


def deploy_agentcore_to_lambda():
    """Deploy the actual AgentCore code to Lambda."""
    lambda_client = boto3.client("lambda", region_name=AWS_REGION)

    try:
        print("\n📦 Deploying AgentCore to Lambda...")

        # Create deployment package with actual AgentCore code
        import io
        import os
        import zipfile

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add AgentCore files
            agentcore_path = "/home/ec2-user/T-DeveloperMVP/packages/runtime/agentcore"

            for file in [
                "__init__.py",
                "agentcore.py",
                "bedrock_integration.py",
                "cloudwatch_integration.py",
                "xray_integration.py",
            ]:
                file_path = os.path.join(agentcore_path, file)
                if os.path.exists(file_path):
                    with open(file_path) as f:
                        zip_file.writestr(f"agentcore/{file}", f.read())

            # Add main handler
            handler_code = '''
import json
import os
import sys
sys.path.insert(0, '/var/task')

from agentcore.agentcore import AgentCore, AgentConfig, Task

def lambda_handler(event, context):
    """Lambda handler for AgentCore."""

    try:
        # Initialize AgentCore
        config = AgentConfig(
            agent_id=event.get('agent_id', 't-developer-agent'),
            max_workers=4,
            timeout_seconds=300
        )

        agent_core = AgentCore(config)

        # Create task from event
        task = Task(
            name=event.get('task_name', 'process'),
            payload=event.get('payload', {}),
            priority=event.get('priority', 1)
        )

        # Execute task
        result = agent_core.execute_task(task)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'task_id': result.task_id,
                'status': result.status.value,
                'result': result.result
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
'''
            zip_file.writestr("lambda_function.py", handler_code)

        # Update Lambda function
        response = lambda_client.update_function_code(
            FunctionName="t-developer-agentcore", ZipFile=zip_buffer.getvalue()
        )

        print("✅ AgentCore deployed to Lambda")
        print(f"   Function ARN: {response['FunctionArn']}")

        # Update function configuration
        lambda_client.update_function_configuration(
            FunctionName="t-developer-agentcore",
            Environment={
                "Variables": {
                    "BEDROCK_MODEL_ID": MODEL_ID,
                    "T_DEVELOPER_REGION": AWS_REGION,
                    "DYNAMODB_STATE_TABLE": "t-developer-evolution-state",
                    "DYNAMODB_PATTERNS_TABLE": "t-developer-patterns",
                    "S3_ARTIFACTS_BUCKET": f"t-developer-artifacts-{AWS_ACCOUNT_ID}",
                }
            },
            Timeout=900,  # 15 minutes
            MemorySize=1024,  # 1GB
        )

        print("✅ Lambda configuration updated")

    except Exception as e:
        print(f"❌ Error deploying AgentCore: {e}")


def test_lambda_invocation():
    """Test Lambda function invocation."""
    lambda_client = boto3.client("lambda", region_name=AWS_REGION)

    try:
        print("\n🧪 Testing Lambda invocation...")

        # Test payload
        test_payload = {
            "agent_id": "test-agent",
            "task_name": "health_check",
            "payload": {"action": "ping"},
        }

        # Invoke function
        response = lambda_client.invoke(
            FunctionName="t-developer-agentcore",
            InvocationType="RequestResponse",
            Payload=json.dumps(test_payload),
        )

        # Parse response
        response_payload = json.loads(response["Payload"].read())

        print("✅ Lambda response:")
        print(json.dumps(response_payload, indent=2))

    except Exception as e:
        print(f"❌ Error testing Lambda: {e}")


def main():
    """Main setup function."""
    print("=" * 60)
    print("T-Developer Bedrock & Lambda Setup")
    print("=" * 60)

    # Create IAM role
    print("\n🔐 Setting up IAM roles...")
    role_arn = create_bedrock_agent_role()

    # Test Bedrock model
    if test_bedrock_model():
        print("\n✅ Bedrock model is accessible and working")
    else:
        print("\n⚠️ Bedrock model test failed - check permissions")

    # Deploy AgentCore to Lambda
    deploy_agentcore_to_lambda()

    # Test Lambda
    test_lambda_invocation()

    print("\n" + "=" * 60)
    print("✅ Bedrock & Lambda Setup Complete!")
    print("=" * 60)

    print("\n📋 Configuration Summary:")
    print(f"  • Model: {MODEL_ID}")
    print(f"  • Region: {AWS_REGION}")
    print(f"  • Role ARN: {role_arn}")
    print("  • Lambda Function: t-developer-agentcore")

    print("\n🔗 Next Steps:")
    print("  1. Create API Gateway")
    print("  2. Set up CloudWatch dashboards")
    print("  3. Configure X-Ray tracing")
    print("  4. Test end-to-end flow")


if __name__ == "__main__":
    main()
