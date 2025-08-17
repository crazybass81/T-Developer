#!/usr/bin/env python3
"""Update Lambda functions with HTTP handlers."""

import io
import zipfile
from pathlib import Path

import boto3

AWS_REGION = "us-east-1"
lambda_client = boto3.client("lambda", region_name=AWS_REGION)


def update_orchestrator():
    """Update orchestrator Lambda with HTTP handler."""

    print("📦 Updating Orchestrator Lambda...")

    # Create deployment package
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Add handler
        handler_path = Path(__file__).parent.parent / "lambda_handlers" / "orchestrator_handler.py"
        with open(handler_path) as f:
            zip_file.writestr("lambda_function.py", f.read())

    # Update Lambda function
    try:
        response = lambda_client.update_function_code(
            FunctionName="t-developer-orchestrator", ZipFile=zip_buffer.getvalue()
        )
        print(f"  ✅ Updated: {response['FunctionName']}")

        # Update handler
        lambda_client.update_function_configuration(
            FunctionName="t-developer-orchestrator", Handler="lambda_function.lambda_handler"
        )
        print("  ✅ Handler configured")

    except Exception as e:
        print(f"  ❌ Error: {e}")


def create_simple_agent_handlers():
    """Create simple handlers for agent Lambdas."""

    agents = ["research", "planner", "refactor", "evaluator"]

    for agent in agents:
        print(f"\n📦 Updating {agent}-agent Lambda...")

        # Create simple handler
        handler_code = f'''
import json
from datetime import datetime

def lambda_handler(event, context):
    """Simple handler for {agent} agent."""

    # Parse request
    body = json.loads(event.get('body', '{{}}')) if event.get('body') else {{}}

    # Mock response
    response = {{
        'agent': '{agent}',
        'status': 'completed',
        'timestamp': datetime.now().isoformat(),
        'result': {{
            'success': True,
            'data': f'{agent.capitalize()} agent executed successfully',
            'task': body
        }}
    }}

    return {{
        'statusCode': 200,
        'headers': {{
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }},
        'body': json.dumps(response)
    }}
'''

        # Create deployment package
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("lambda_function.py", handler_code)

        # Update Lambda
        try:
            response = lambda_client.update_function_code(
                FunctionName=f"t-developer-{agent}-agent", ZipFile=zip_buffer.getvalue()
            )
            print(f"  ✅ Updated: {response['FunctionName']}")

            # Update handler
            lambda_client.update_function_configuration(
                FunctionName=f"t-developer-{agent}-agent", Handler="lambda_function.lambda_handler"
            )

        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Updating Lambda Handlers for HTTP...")
    print("=" * 50)

    update_orchestrator()
    create_simple_agent_handlers()

    print("\n" + "=" * 50)
    print("✅ Lambda handlers updated!")
    print("\n📝 Test with:")
    print("  curl https://xwbc164gfg.execute-api.us-east-1.amazonaws.com/prod/agents")
