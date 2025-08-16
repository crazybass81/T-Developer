#!/usr/bin/env python3
"""Deploy actual Agent code to AWS Lambda functions."""

import io
import sys
import zipfile
from pathlib import Path

import boto3

AWS_REGION = "us-east-1"
AWS_ACCOUNT_ID = "036284794745"

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_agent_deployment_package(agent_type: str) -> bytes:
    """Create deployment package for specific agent.

    Args:
        agent_type: Type of agent (research, planner, refactor, evaluator)

    Returns:
        Zip file contents as bytes
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add packages directory structure
        packages_dir = Path("/home/ec2-user/T-DeveloperMVP/packages")

        # Add all agent files
        for agent_file in ["base.py", f"{agent_type}.py"]:
            file_path = packages_dir / "agents" / agent_file
            if file_path.exists():
                with open(file_path) as f:
                    zip_file.writestr(f"packages/agents/{agent_file}", f.read())

        # Add research_references if research agent
        if agent_type == "research":
            ref_file = packages_dir / "agents" / "research_references.py"
            if ref_file.exists():
                with open(ref_file) as f:
                    zip_file.writestr("packages/agents/research_references.py", f.read())

        # Add __init__ files
        zip_file.writestr("packages/__init__.py", "")
        zip_file.writestr("packages/agents/__init__.py", "")

        # Create Lambda handler
        handler_code = f'''
import json
import os
import sys
import boto3
from datetime import datetime

# Add packages to path
sys.path.insert(0, '/var/task')

# Import agent
from packages.agents.base import AgentInput, AgentStatus
from packages.agents.{agent_type} import {agent_type.capitalize()}Agent, {agent_type.capitalize()}Config

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='{AWS_REGION}')
s3 = boto3.client('s3', region_name='{AWS_REGION}')

def lambda_handler(event, context):
    """Lambda handler for {agent_type.capitalize()} Agent."""

    try:
        # Parse input
        body = event if 'task_id' in event else json.loads(event.get('body', '{{}}'))

        # Create agent configuration
        config = {agent_type.capitalize()}Config()

        # Initialize agent
        agent = {agent_type.capitalize()}Agent(
            agent_id=f"{agent_type}-agent-{{context.request_id}}",
            config=config
        )

        # Create agent input
        agent_input = AgentInput(
            intent=body.get('intent', '{agent_type}'),
            task_id=body.get('task_id', f'{agent_type}-{{context.request_id}}'),
            payload=body.get('payload', {{}})
        )

        # Execute agent
        result = agent.execute(agent_input)

        # Save to DynamoDB
        table = dynamodb.Table(os.environ.get('STATE_TABLE', 't-developer-evolution-state'))
        table.put_item(
            Item={{
                'id': result.task_id,
                'timestamp': int(datetime.now().timestamp()),
                'agent_type': '{agent_type}',
                'status': result.status.value,
                'artifacts': [a.to_dict() for a in result.artifacts] if result.artifacts else [],
                'metadata': result.metadata or {{}},
                'error': result.error
            }}
        )

        # Save artifacts to S3 if present
        if result.artifacts:
            bucket = os.environ.get('ARTIFACTS_BUCKET', 't-developer-artifacts-{AWS_ACCOUNT_ID}')
            for artifact in result.artifacts:
                key = f"{{result.task_id}}/{{artifact.name}}"
                s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=json.dumps(artifact.to_dict()),
                    ContentType='application/json'
                )

        # Return response
        return {{
            'statusCode': 200 if result.status == AgentStatus.COMPLETED else 500,
            'body': json.dumps({{
                'task_id': result.task_id,
                'status': result.status.value,
                'artifacts_count': len(result.artifacts) if result.artifacts else 0,
                'metadata': result.metadata,
                'error': result.error
            }})
        }}

    except Exception as e:
        print(f"Error in {agent_type} agent: {{e}}")

        # Log error to DynamoDB
        try:
            table = dynamodb.Table(os.environ.get('STATE_TABLE', 't-developer-evolution-state'))
            table.put_item(
                Item={{
                    'id': f'error-{{context.request_id}}',
                    'timestamp': int(datetime.now().timestamp()),
                    'agent_type': '{agent_type}',
                    'status': 'error',
                    'error': str(e)
                }}
            )
        except:
            pass

        return {{
            'statusCode': 500,
            'body': json.dumps({{
                'error': str(e),
                'agent': '{agent_type}'
            }})
        }}
'''

        zip_file.writestr("lambda_function.py", handler_code)

    return zip_buffer.getvalue()


def deploy_orchestrator_lambda():
    """Deploy the orchestrator Lambda that coordinates all agents."""

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        orchestrator_code = '''
import json
import boto3
import os
from datetime import datetime

lambda_client = boto3.client('lambda', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

AGENT_FUNCTIONS = {
    'research': 't-developer-research-agent',
    'planner': 't-developer-planner-agent',
    'refactor': 't-developer-refactor-agent',
    'evaluator': 't-developer-evaluator-agent'
}

def lambda_handler(event, context):
    """Orchestrate the complete agent workflow."""

    try:
        body = event if 'workflow' in event else json.loads(event.get('body', '{}'))
        workflow = body.get('workflow', 'full')
        task_id = body.get('task_id', f'workflow-{context.request_id}')
        payload = body.get('payload', {})

        results = {}

        if workflow == 'full':
            # Execute full workflow: Research -> Plan -> Refactor -> Evaluate
            agents_sequence = ['research', 'planner', 'refactor', 'evaluator']
        else:
            # Execute specific agent only
            agents_sequence = [workflow] if workflow in AGENT_FUNCTIONS else []

        previous_output = payload

        for agent_type in agents_sequence:
            if agent_type not in AGENT_FUNCTIONS:
                continue

            # Prepare input for agent
            agent_input = {
                'intent': agent_type,
                'task_id': f'{task_id}-{agent_type}',
                'payload': previous_output
            }

            # Invoke agent Lambda
            response = lambda_client.invoke(
                FunctionName=AGENT_FUNCTIONS[agent_type],
                InvocationType='RequestResponse',
                Payload=json.dumps(agent_input)
            )

            # Parse response
            result = json.loads(response['Payload'].read())

            if response['StatusCode'] != 200:
                results[agent_type] = {'status': 'error', 'error': result.get('error')}
                break

            result_body = json.loads(result.get('body', '{}'))
            results[agent_type] = result_body

            # Use output as input for next agent
            if result_body.get('metadata'):
                previous_output = result_body['metadata']

        # Save workflow result
        table = dynamodb.Table('t-developer-evolution-state')
        table.put_item(
            Item={
                'id': task_id,
                'timestamp': int(datetime.now().timestamp()),
                'agent_type': 'orchestrator',
                'workflow': workflow,
                'results': results,
                'status': 'completed'
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'task_id': task_id,
                'workflow': workflow,
                'results': results
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'type': 'orchestrator'
            })
        }
'''

        zip_file.writestr("lambda_function.py", orchestrator_code)

    return zip_buffer.getvalue()


def main():
    """Main deployment function."""
    print("=" * 60)
    print("Deploying T-Developer Agents to AWS Lambda")
    print("=" * 60)

    lambda_client = boto3.client("lambda", region_name=AWS_REGION)

    # Agent configurations
    agents = [
        ("research", "t-developer-security-gate"),  # Reuse existing Lambda
        ("planner", "t-developer-quality-gate"),  # Reuse existing Lambda
        ("refactor", "t-developer-test-gate"),  # Reuse existing Lambda
        ("evaluator", "t-developer-agentcore"),  # Reuse existing Lambda
    ]

    # Create new Lambda functions for agents
    print("\n📦 Creating Agent Lambda Functions...")

    for agent_type, _ in agents:
        function_name = f"t-developer-{agent_type}-agent"

        try:
            print(f"\nDeploying {agent_type.capitalize()} Agent...")

            # Check if function exists
            try:
                lambda_client.get_function(FunctionName=function_name)
                exists = True
            except:
                exists = False

            # Create deployment package
            deployment_package = create_agent_deployment_package(agent_type)

            if exists:
                # Update existing function
                response = lambda_client.update_function_code(
                    FunctionName=function_name, ZipFile=deployment_package
                )
                print(f"  ✅ Updated: {function_name}")
            else:
                # Create new function
                response = lambda_client.create_function(
                    FunctionName=function_name,
                    Runtime="python3.9",
                    Role=f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/t-developer-lambda-role",
                    Handler="lambda_function.lambda_handler",
                    Code={"ZipFile": deployment_package},
                    Description=f"T-Developer {agent_type.capitalize()} Agent",
                    Timeout=300,
                    MemorySize=512,
                    Environment={
                        "Variables": {
                            "STATE_TABLE": "t-developer-evolution-state",
                            "PATTERNS_TABLE": "t-developer-patterns",
                            "ARTIFACTS_BUCKET": f"t-developer-artifacts-{AWS_ACCOUNT_ID}",
                            "AGENT_TYPE": agent_type,
                        }
                    },
                    TracingConfig={"Mode": "Active"},
                )
                print(f"  ✅ Created: {function_name}")

        except Exception as e:
            print(f"  ❌ Error with {agent_type}: {e}")

    # Deploy orchestrator
    print("\n🎭 Updating Orchestrator...")
    try:
        orchestrator_package = deploy_orchestrator_lambda()

        lambda_client.update_function_code(
            FunctionName="t-developer-orchestrator", ZipFile=orchestrator_package
        )

        lambda_client.update_function_configuration(
            FunctionName="t-developer-orchestrator",
            Environment={
                "Variables": {
                    "STATE_TABLE": "t-developer-evolution-state",
                    "PATTERNS_TABLE": "t-developer-patterns",
                }
            },
            Timeout=900,  # 15 minutes for full workflow
        )

        print("  ✅ Orchestrator updated")

    except Exception as e:
        print(f"  ❌ Orchestrator error: {e}")

    print("\n" + "=" * 60)
    print("✅ Agent Deployment Complete!")
    print("=" * 60)

    print("\n📋 Deployed Functions:")
    print("  • t-developer-research-agent")
    print("  • t-developer-planner-agent")
    print("  • t-developer-refactor-agent")
    print("  • t-developer-evaluator-agent")
    print("  • t-developer-orchestrator (updated)")

    print("\n🔗 Test with:")
    print("  curl -X POST https://4sxw6pfgzi.execute-api.us-east-1.amazonaws.com/prod/orchestrate")
    print("    -H 'Content-Type: application/json'")
    print('    -d \'{"workflow": "full", "payload": {"target": "test"}}\'')


if __name__ == "__main__":
    main()
