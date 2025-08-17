#!/usr/bin/env python3
"""Create API Gateway for T-Developer Lambda functions."""

from datetime import datetime
from pathlib import Path

import boto3

AWS_REGION = "us-east-1"
AWS_ACCOUNT_ID = "036284794745"

# Initialize clients
apigateway = boto3.client("apigateway", region_name=AWS_REGION)
lambda_client = boto3.client("lambda", region_name=AWS_REGION)


def create_api_gateway():
    """Create REST API Gateway for T-Developer."""

    print("🌐 Creating API Gateway...")

    # Create REST API
    try:
        response = apigateway.create_rest_api(
            name="T-Developer-API",
            description="API Gateway for T-Developer Agent System",
            endpointConfiguration={"types": ["REGIONAL"]},
        )
        api_id = response["id"]
        print(f"  ✅ Created API: {api_id}")
    except Exception as e:
        # Check if API already exists
        apis = apigateway.get_rest_apis()
        for api in apis["items"]:
            if api["name"] == "T-Developer-API":
                api_id = api["id"]
                print(f"  ℹ️ Using existing API: {api_id}")
                break
        else:
            raise e

    # Get root resource
    resources = apigateway.get_resources(restApiId=api_id)
    root_id = resources["items"][0]["id"]

    # Create resources and methods
    endpoints = [
        {"path": "agents", "methods": ["GET"], "lambda": "t-developer-orchestrator"},
        {
            "path": "agents/{agentId}/execute",
            "methods": ["POST"],
            "lambda": "t-developer-agentcore",
        },
        {"path": "evolution/start", "methods": ["POST"], "lambda": "t-developer-orchestrator"},
        {"path": "evolution/status", "methods": ["GET"], "lambda": "t-developer-orchestrator"},
        {"path": "metrics", "methods": ["GET"], "lambda": "t-developer-orchestrator"},
    ]

    for endpoint in endpoints:
        print(f"\n📍 Creating endpoint: {endpoint['path']}")

        # Create resource path
        path_parts = endpoint["path"].split("/")
        parent_id = root_id

        for part in path_parts:
            # Check if resource exists
            existing = None
            resources = apigateway.get_resources(restApiId=api_id)
            for resource in resources["items"]:
                if resource.get("pathPart") == part and resource.get("parentId") == parent_id:
                    existing = resource
                    break

            if existing:
                parent_id = existing["id"]
                print(f"    Using existing resource: {part}")
            else:
                # Create new resource
                try:
                    if "{" in part:  # Path parameter
                        response = apigateway.create_resource(
                            restApiId=api_id, parentId=parent_id, pathPart=part
                        )
                    else:
                        response = apigateway.create_resource(
                            restApiId=api_id, parentId=parent_id, pathPart=part
                        )
                    parent_id = response["id"]
                    print(f"    Created resource: {part}")
                except Exception as e:
                    print(f"    Error creating resource {part}: {e}")
                    continue

        # Create methods
        for method in endpoint["methods"]:
            try:
                # Create method
                apigateway.put_method(
                    restApiId=api_id,
                    resourceId=parent_id,
                    httpMethod=method,
                    authorizationType="NONE",
                )
                print(f"    ✅ Created method: {method}")

                # Create integration
                lambda_arn = (
                    f"arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:{endpoint['lambda']}"
                )

                apigateway.put_integration(
                    restApiId=api_id,
                    resourceId=parent_id,
                    httpMethod=method,
                    type="AWS_PROXY",
                    integrationHttpMethod="POST",
                    uri=f"arn:aws:apigateway:{AWS_REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations",
                )
                print("    ✅ Created Lambda integration")

                # Add Lambda permission
                try:
                    lambda_client.add_permission(
                        FunctionName=endpoint["lambda"],
                        StatementId=f"apigateway-{api_id}-{method}-{parent_id}",
                        Action="lambda:InvokeFunction",
                        Principal="apigateway.amazonaws.com",
                        SourceArn=f"arn:aws:execute-api:{AWS_REGION}:{AWS_ACCOUNT_ID}:{api_id}/*/{method}{endpoint['path']}",
                    )
                    print("    ✅ Added Lambda permission")
                except lambda_client.exceptions.ResourceConflictException:
                    print("    ℹ️ Lambda permission already exists")

            except apigateway.exceptions.ConflictException:
                print(f"    ℹ️ Method {method} already exists")

    # Enable CORS
    print("\n🔧 Enabling CORS...")
    resources = apigateway.get_resources(restApiId=api_id)
    for resource in resources["items"]:
        if resource["id"] != root_id:
            try:
                apigateway.put_method(
                    restApiId=api_id,
                    resourceId=resource["id"],
                    httpMethod="OPTIONS",
                    authorizationType="NONE",
                )

                apigateway.put_integration(
                    restApiId=api_id,
                    resourceId=resource["id"],
                    httpMethod="OPTIONS",
                    type="MOCK",
                    requestTemplates={"application/json": '{"statusCode": 200}'},
                )

                apigateway.put_method_response(
                    restApiId=api_id,
                    resourceId=resource["id"],
                    httpMethod="OPTIONS",
                    statusCode="200",
                    responseParameters={
                        "method.response.header.Access-Control-Allow-Headers": False,
                        "method.response.header.Access-Control-Allow-Methods": False,
                        "method.response.header.Access-Control-Allow-Origin": False,
                    },
                )

                apigateway.put_integration_response(
                    restApiId=api_id,
                    resourceId=resource["id"],
                    httpMethod="OPTIONS",
                    statusCode="200",
                    responseParameters={
                        "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                        "method.response.header.Access-Control-Allow-Methods": "'GET,POST,OPTIONS'",
                        "method.response.header.Access-Control-Allow-Origin": "'*'",
                    },
                )
                print(f"  ✅ CORS enabled for {resource.get('path', '/')}")
            except:
                pass

    # Deploy API
    print("\n🚀 Deploying API...")
    try:
        apigateway.create_deployment(
            restApiId=api_id,
            stageName="prod",
            description=f"Deployment at {datetime.now().isoformat()}",
        )
        print("  ✅ API deployed to 'prod' stage")
    except Exception as e:
        print(f"  ⚠️ Deployment warning: {e}")

    # Get endpoint URL
    endpoint_url = f"https://{api_id}.execute-api.{AWS_REGION}.amazonaws.com/prod"

    print("\n" + "=" * 60)
    print("✅ API Gateway Setup Complete!")
    print("=" * 60)
    print(f"\n🔗 API Endpoint: {endpoint_url}")
    print("\n📝 Example Usage:")
    print(f"  curl {endpoint_url}/agents")
    print(f"  curl -X POST {endpoint_url}/evolution/start")

    # Save endpoint to file for frontend
    with open("api_endpoint.txt", "w") as f:
        f.write(endpoint_url)
    print("\n💾 Endpoint saved to api_endpoint.txt")

    return api_id, endpoint_url


if __name__ == "__main__":
    api_id, endpoint = create_api_gateway()

    # Update frontend config
    env_file = Path(__file__).parent.parent / "frontend" / ".env"
    if env_file.exists():
        with open(env_file) as f:
            lines = f.readlines()

        # Update or add API endpoint
        found = False
        for i, line in enumerate(lines):
            if line.startswith("REACT_APP_API_ENDPOINT="):
                lines[i] = f"REACT_APP_API_ENDPOINT={endpoint}\n"
                found = True
                break

        if not found:
            lines.append(f"REACT_APP_API_ENDPOINT={endpoint}\n")

        with open(env_file, "w") as f:
            f.writelines(lines)

        print("✅ Updated frontend/.env with API endpoint")
