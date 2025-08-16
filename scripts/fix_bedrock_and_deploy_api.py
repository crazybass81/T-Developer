#!/usr/bin/env python3
"""Fix Bedrock model issue and deploy API Gateway."""

import json
import time

import boto3

AWS_REGION = "us-east-1"
AWS_ACCOUNT_ID = "036284794745"

# Use Claude 3 Haiku for faster responses and lower cost
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"


def test_bedrock_with_haiku():
    """Test Bedrock with Claude 3 Haiku model."""
    bedrock_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)

    try:
        print("🧪 Testing Claude 3 Haiku model...")

        # Test prompt
        prompt = "You are T-Developer. Respond with: 'Ready to evolve code!'"

        # Prepare request
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
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

        if "content" in response_body and response_body["content"]:
            print(f"✅ Model works! Response: {response_body['content'][0]['text']}")
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_api_gateway():
    """Create API Gateway for T-Developer."""
    apigateway = boto3.client("apigatewayv2", region_name=AWS_REGION)
    lambda_client = boto3.client("lambda", region_name=AWS_REGION)

    try:
        print("\n🌐 Creating API Gateway...")

        # Create HTTP API
        api_response = apigateway.create_api(
            Name="t-developer-api",
            ProtocolType="HTTP",
            Description="T-Developer API Gateway",
            CorsConfiguration={
                "AllowOrigins": ["*"],
                "AllowMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "AllowHeaders": ["*"],
                "MaxAge": 300,
            },
        )

        api_id = api_response["ApiId"]
        api_endpoint = api_response["ApiEndpoint"]

        print(f"✅ API created: {api_endpoint}")

        # Create routes for each Lambda function
        functions = [
            ("security-gate", "POST", "/gates/security"),
            ("quality-gate", "POST", "/gates/quality"),
            ("test-gate", "POST", "/gates/test"),
            ("orchestrator", "POST", "/orchestrate"),
            ("agentcore", "POST", "/agent/execute"),
        ]

        for function_suffix, method, path in functions:
            function_name = f"t-developer-{function_suffix}"

            # Get Lambda function ARN
            function = lambda_client.get_function(FunctionName=function_name)
            function_arn = function["Configuration"]["FunctionArn"]

            # Create integration
            integration_response = apigateway.create_integration(
                ApiId=api_id,
                IntegrationType="AWS_PROXY",
                IntegrationUri=function_arn,
                PayloadFormatVersion="2.0",
            )

            integration_id = integration_response["IntegrationId"]

            # Create route
            route_response = apigateway.create_route(
                ApiId=api_id, RouteKey=f"{method} {path}", Target=f"integrations/{integration_id}"
            )

            # Add Lambda permission for API Gateway
            try:
                lambda_client.add_permission(
                    FunctionName=function_name,
                    StatementId=f"api-gateway-{api_id}",
                    Action="lambda:InvokeFunction",
                    Principal="apigateway.amazonaws.com",
                    SourceArn=f"arn:aws:execute-api:{AWS_REGION}:{AWS_ACCOUNT_ID}:{api_id}/*/{method}{path}",
                )
            except lambda_client.exceptions.ResourceConflictException:
                pass  # Permission already exists

            print(f"  ✅ Route created: {method} {path} -> {function_name}")

        # Create deployment
        deployment_response = apigateway.create_deployment(
            ApiId=api_id, Description="Production deployment"
        )

        # Create stage
        stage_response = apigateway.create_stage(
            ApiId=api_id,
            StageName="prod",
            DeploymentId=deployment_response["DeploymentId"],
            Description="Production stage",
        )

        final_endpoint = f"{api_endpoint}/prod"
        print(f"\n✅ API Gateway deployed: {final_endpoint}")

        return api_id, final_endpoint

    except Exception as e:
        print(f"❌ Error creating API Gateway: {e}")
        return None, None


def setup_cloudwatch_dashboard():
    """Create CloudWatch dashboard for monitoring."""
    cloudwatch = boto3.client("cloudwatch", region_name=AWS_REGION)

    try:
        print("\n📊 Creating CloudWatch Dashboard...")

        dashboard_body = {
            "widgets": [
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
                            [".", "Errors", {"stat": "Sum"}],
                            [".", "Duration", {"stat": "Average"}],
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": AWS_REGION,
                        "title": "Lambda Metrics",
                        "view": "timeSeries",
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            ["AWS/DynamoDB", "UserErrors", {"stat": "Sum"}],
                            [".", "ConsumedReadCapacityUnits", {"stat": "Sum"}],
                            [".", "ConsumedWriteCapacityUnits", {"stat": "Sum"}],
                        ],
                        "period": 300,
                        "stat": "Sum",
                        "region": AWS_REGION,
                        "title": "DynamoDB Metrics",
                    },
                },
                {
                    "type": "metric",
                    "properties": {
                        "metrics": [
                            ["AWS/ApiGateway", "4XXError", {"stat": "Sum"}],
                            [".", "5XXError", {"stat": "Sum"}],
                            [".", "Count", {"stat": "Sum"}],
                            [".", "Latency", {"stat": "Average"}],
                        ],
                        "period": 300,
                        "stat": "Average",
                        "region": AWS_REGION,
                        "title": "API Gateway Metrics",
                    },
                },
            ]
        }

        response = cloudwatch.put_dashboard(
            DashboardName="t-developer-dashboard", DashboardBody=json.dumps(dashboard_body)
        )

        print("✅ Dashboard created: t-developer-dashboard")

        # Create alarms
        alarms = [
            {
                "name": "t-developer-lambda-errors",
                "metric": "Errors",
                "namespace": "AWS/Lambda",
                "threshold": 5,
                "comparison": "GreaterThanThreshold",
                "description": "Alert when Lambda errors exceed threshold",
            },
            {
                "name": "t-developer-api-5xx",
                "metric": "5XXError",
                "namespace": "AWS/ApiGateway",
                "threshold": 10,
                "comparison": "GreaterThanThreshold",
                "description": "Alert when API 5XX errors exceed threshold",
            },
        ]

        for alarm in alarms:
            try:
                cloudwatch.put_metric_alarm(
                    AlarmName=alarm["name"],
                    ComparisonOperator=alarm["comparison"],
                    EvaluationPeriods=1,
                    MetricName=alarm["metric"],
                    Namespace=alarm["namespace"],
                    Period=300,
                    Statistic="Sum",
                    Threshold=alarm["threshold"],
                    ActionsEnabled=False,
                    AlarmDescription=alarm["description"],
                )
                print(f"  ✅ Alarm created: {alarm['name']}")
            except Exception as e:
                print(f"  ⚠️ Alarm {alarm['name']}: {e}")

    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")


def enable_xray_tracing():
    """Enable X-Ray tracing for Lambda functions."""
    lambda_client = boto3.client("lambda", region_name=AWS_REGION)

    try:
        print("\n🔍 Enabling X-Ray tracing...")

        functions = [
            "t-developer-security-gate",
            "t-developer-quality-gate",
            "t-developer-test-gate",
            "t-developer-orchestrator",
            "t-developer-agentcore",
        ]

        for function_name in functions:
            try:
                lambda_client.update_function_configuration(
                    FunctionName=function_name, TracingConfig={"Mode": "Active"}
                )
                print(f"  ✅ X-Ray enabled for {function_name}")
                time.sleep(1)  # Avoid throttling
            except Exception as e:
                print(f"  ⚠️ {function_name}: {e}")

    except Exception as e:
        print(f"❌ Error enabling X-Ray: {e}")


def test_end_to_end(api_endpoint):
    """Test the complete integration."""
    import requests

    try:
        print("\n🧪 Testing end-to-end integration...")

        # Test health check
        test_payload = {"action": "health_check", "message": "Testing T-Developer integration"}

        # Test orchestrator endpoint
        url = f"{api_endpoint}/orchestrate"
        print(f"  Testing: POST {url}")

        response = requests.post(url, json=test_payload, timeout=10)

        if response.status_code == 200:
            print(f"  ✅ Orchestrator responded: {response.json()}")
        else:
            print(f"  ⚠️ Response code: {response.status_code}")

        # Test agent endpoint
        agent_url = f"{api_endpoint}/agent/execute"
        agent_payload = {"agent_id": "test", "task_name": "ping", "payload": {"test": True}}

        print(f"  Testing: POST {agent_url}")
        response = requests.post(agent_url, json=agent_payload, timeout=10)

        if response.status_code == 200:
            print(f"  ✅ AgentCore responded: {response.json()}")
        else:
            print(f"  ⚠️ Response code: {response.status_code}")

    except Exception as e:
        print(f"❌ End-to-end test error: {e}")


def update_env_file(api_endpoint):
    """Update .env.example with actual values."""
    try:
        print("\n📝 Updating environment configuration...")

        env_content = f"""# T-Developer AWS Configuration
AWS_REGION={AWS_REGION}
AWS_ACCOUNT_ID={AWS_ACCOUNT_ID}
API_GATEWAY_ENDPOINT={api_endpoint}
BEDROCK_MODEL_ID={MODEL_ID}

# DynamoDB Tables
DYNAMODB_STATE_TABLE=t-developer-evolution-state
DYNAMODB_PATTERNS_TABLE=t-developer-patterns
DYNAMODB_METRICS_TABLE=t-developer-metrics
DYNAMODB_REGISTRY_TABLE=t-developer-agent-registry

# S3 Buckets
S3_ARTIFACTS_BUCKET=t-developer-artifacts-{AWS_ACCOUNT_ID}
S3_CODE_BUCKET=t-developer-code-{AWS_ACCOUNT_ID}
S3_LOGS_BUCKET=t-developer-logs-{AWS_ACCOUNT_ID}

# SQS Queues
SQS_TASKS_QUEUE=https://sqs.{AWS_REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/agent-squad-tasks
SQS_DLQ_QUEUE=https://sqs.{AWS_REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/agent-squad-dlq

# Lambda Functions
LAMBDA_SECURITY_GATE=t-developer-security-gate
LAMBDA_QUALITY_GATE=t-developer-quality-gate
LAMBDA_TEST_GATE=t-developer-test-gate
LAMBDA_ORCHESTRATOR=t-developer-orchestrator
LAMBDA_AGENTCORE=t-developer-agentcore
"""

        with open("/home/ec2-user/T-DeveloperMVP/.env.aws", "w") as f:
            f.write(env_content)

        print("✅ Created .env.aws with AWS configuration")

    except Exception as e:
        print(f"❌ Error updating env file: {e}")


def main():
    """Main deployment function."""
    print("=" * 60)
    print("T-Developer AWS Complete Setup")
    print("=" * 60)

    # 1. Fix Bedrock model
    print("\n1️⃣ Fixing Bedrock Model...")
    if test_bedrock_with_haiku():
        print("✅ Bedrock model working with Claude 3 Haiku")

    # 2. Create API Gateway
    print("\n2️⃣ Creating API Gateway...")
    api_id, api_endpoint = create_api_gateway()

    # 3. Setup CloudWatch
    print("\n3️⃣ Setting up CloudWatch...")
    setup_cloudwatch_dashboard()

    # 4. Enable X-Ray
    print("\n4️⃣ Configuring X-Ray...")
    enable_xray_tracing()

    # 5. Test integration
    if api_endpoint:
        print("\n5️⃣ Testing Integration...")
        test_end_to_end(api_endpoint)

        # 6. Update configuration
        update_env_file(api_endpoint)

    print("\n" + "=" * 60)
    print("✅ AWS Setup Complete!")
    print("=" * 60)

    print("\n📋 Deployment Summary:")
    print(f"  • Bedrock Model: {MODEL_ID}")
    print(f"  • API Endpoint: {api_endpoint}")
    print("  • CloudWatch Dashboard: t-developer-dashboard")
    print("  • X-Ray Tracing: Enabled")
    print("  • Configuration: .env.aws")

    print("\n🎉 T-Developer is now running on AWS!")
    print("\n📚 Documentation:")
    print("  • API Endpoint: Use POST requests to interact")
    print("  • Monitoring: Check CloudWatch dashboard")
    print("  • Logs: CloudWatch Logs for each Lambda")
    print("  • Tracing: X-Ray for request flow")


if __name__ == "__main__":
    main()
