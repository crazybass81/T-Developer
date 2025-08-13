"""
API Gateway Manager
Manages API Gateway integration for agent endpoints
"""
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import boto3


@dataclass
class RouteConfig:
    path: str
    method: str
    integration_uri: str
    auth_required: bool = True
    api_key_required: bool = False
    throttle_limit: int = 100
    burst_limit: int = 200


class APIGatewayManager:
    def __init__(self, api_name: str = "T-Developer-Agents"):
        self.api_name = api_name
        self.api_gateway_client = boto3.client("apigatewayv2", region_name="us-east-1")
        self.api_id = None
        self.stage_name = "prod"
        self._load_or_create_api()

    def _load_or_create_api(self):
        """Load existing API or create new one"""
        try:
            # Check if API exists
            response = self.api_gateway_client.get_apis()
            for api in response.get("Items", []):
                if api["Name"] == self.api_name:
                    self.api_id = api["ApiId"]
                    self.api_endpoint = api.get("ApiEndpoint")
                    return

            # Create new API if not exists
            self._create_api()
        except Exception as e:
            print(f"Error loading API: {e}")

    def _create_api(self):
        """Create new API Gateway"""
        try:
            response = self.api_gateway_client.create_api(
                Name=self.api_name,
                ProtocolType="HTTP",
                Version="1.0",
                Description="T-Developer Agent API Gateway",
                CorsConfiguration={
                    "AllowOrigins": ["*"],
                    "AllowMethods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "AllowHeaders": ["*"],
                    "MaxAge": 300,
                },
            )
            self.api_id = response["ApiId"]
            self.api_endpoint = response["ApiEndpoint"]

            # Create default stage
            self._create_stage()
        except Exception as e:
            print(f"Error creating API: {e}")

    def _create_stage(self):
        """Create deployment stage"""
        try:
            # Create deployment
            deployment = self.api_gateway_client.create_deployment(
                ApiId=self.api_id, Description=f'Deployment at {time.strftime("%Y-%m-%d %H:%M:%S")}'
            )

            # Create or update stage
            try:
                self.api_gateway_client.create_stage(
                    ApiId=self.api_id,
                    StageName=self.stage_name,
                    DeploymentId=deployment["DeploymentId"],
                    Description="Production stage",
                    ThrottleSettings={"RateLimit": 1000, "BurstLimit": 2000},
                )
            except:
                # Stage might already exist, update it
                self.api_gateway_client.update_stage(
                    ApiId=self.api_id,
                    StageName=self.stage_name,
                    DeploymentId=deployment["DeploymentId"],
                )
        except Exception as e:
            print(f"Error creating stage: {e}")

    def create_route(self, route_config: RouteConfig) -> Optional[str]:
        """Create or update a route"""
        if not self.api_id:
            return None

        try:
            # Create integration first
            integration_response = self.api_gateway_client.create_integration(
                ApiId=self.api_id,
                IntegrationType="HTTP_PROXY",
                IntegrationUri=route_config.integration_uri,
                IntegrationMethod=route_config.method,
                PayloadFormatVersion="2.0",
                TimeoutInMillis=29000,
                ConnectionType="INTERNET",
            )
            integration_id = integration_response["IntegrationId"]

            # Create route
            route_key = f"{route_config.method} {route_config.path}"
            route_response = self.api_gateway_client.create_route(
                ApiId=self.api_id,
                RouteKey=route_key,
                Target=f"integrations/{integration_id}",
                AuthorizationType="JWT" if route_config.auth_required else "NONE",
                ApiKeyRequired=route_config.api_key_required,
            )

            return route_response["RouteId"]

        except Exception as e:
            print(f"Error creating route: {e}")
            return None

    def delete_route(self, route_id: str) -> bool:
        """Delete a route"""
        if not self.api_id:
            return False

        try:
            self.api_gateway_client.delete_route(ApiId=self.api_id, RouteId=route_id)
            return True
        except Exception as e:
            print(f"Error deleting route: {e}")
            return False

    def list_routes(self) -> List[Dict[str, Any]]:
        """List all routes"""
        if not self.api_id:
            return []

        try:
            response = self.api_gateway_client.get_routes(ApiId=self.api_id)
            return response.get("Items", [])
        except Exception as e:
            print(f"Error listing routes: {e}")
            return []

    def sync_with_registry(self, registry) -> Dict[str, Any]:
        """Sync routes with endpoint registry"""
        results = {"created": [], "updated": [], "deleted": [], "errors": []}

        # Get current routes
        existing_routes = {route["RouteKey"]: route for route in self.list_routes()}

        # Get active endpoints from registry
        active_endpoints = registry.get_active_endpoints()
        expected_routes = {}

        for endpoint in active_endpoints:
            route_key = f"{endpoint.method} /agents/{endpoint.agent_name}/{endpoint.version}"
            expected_routes[route_key] = endpoint

            if route_key not in existing_routes:
                # Create new route
                route_config = RouteConfig(
                    path=f"/agents/{endpoint.agent_name}/{endpoint.version}",
                    method=endpoint.method,
                    integration_uri=endpoint.url,
                    auth_required=True,
                )
                route_id = self.create_route(route_config)
                if route_id:
                    results["created"].append(route_key)
                else:
                    results["errors"].append(f"Failed to create {route_key}")

        # Delete routes for inactive endpoints
        for route_key, route in existing_routes.items():
            if route_key not in expected_routes and route_key.startswith("POST /agents/"):
                if self.delete_route(route["RouteId"]):
                    results["deleted"].append(route_key)
                else:
                    results["errors"].append(f"Failed to delete {route_key}")

        return results

    def get_api_url(self, agent_name: str, version: str) -> Optional[str]:
        """Get full API URL for an agent"""
        if not self.api_endpoint:
            return None
        return f"{self.api_endpoint}/{self.stage_name}/agents/{agent_name}/{version}"

    def create_api_key(self, name: str, description: str = "") -> Optional[Dict[str, str]]:
        """Create API key for access"""
        try:
            # Note: API Gateway V2 doesn't have native API key support
            # This would integrate with a custom authorizer
            return {
                "api_key": f"tdv-{name}-{int(time.time())}",
                "created_at": time.time(),
                "description": description,
            }
        except Exception as e:
            print(f"Error creating API key: {e}")
            return None

    def get_usage_metrics(self) -> Dict[str, Any]:
        """Get API usage metrics from CloudWatch"""
        try:
            cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")

            # Get metrics for last hour
            end_time = time.time()
            start_time = end_time - 3600

            response = cloudwatch.get_metric_statistics(
                Namespace="AWS/ApiGateway",
                MetricName="Count",
                Dimensions=[
                    {"Name": "ApiId", "Value": self.api_id},
                    {"Name": "Stage", "Value": self.stage_name},
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=["Sum"],
            )

            total_requests = sum(point["Sum"] for point in response.get("Datapoints", []))

            return {
                "api_id": self.api_id,
                "stage": self.stage_name,
                "period_hours": 1,
                "total_requests": total_requests,
                "endpoint": self.api_endpoint,
            }
        except Exception as e:
            print(f"Error getting metrics: {e}")
            return {}

    def deploy_changes(self) -> bool:
        """Deploy any pending changes"""
        if not self.api_id:
            return False

        try:
            deployment = self.api_gateway_client.create_deployment(
                ApiId=self.api_id,
                Description=f'Auto-deployment at {time.strftime("%Y-%m-%d %H:%M:%S")}',
            )

            # Update stage with new deployment
            self.api_gateway_client.update_stage(
                ApiId=self.api_id,
                StageName=self.stage_name,
                DeploymentId=deployment["DeploymentId"],
            )
            return True
        except Exception as e:
            print(f"Error deploying: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create manager
    manager = APIGatewayManager()

    # Create a test route
    test_route = RouteConfig(
        path="/agents/test/v1",
        method="POST",
        integration_uri="https://example.com/test",
        auth_required=True,
    )

    route_id = manager.create_route(test_route)
    print(f"Created route: {route_id}")

    # List routes
    routes = manager.list_routes()
    print(f"Current routes: {json.dumps(routes, indent=2)}")

    # Get API URL
    url = manager.get_api_url("test", "v1")
    print(f"API URL: {url}")

    # Get usage metrics
    metrics = manager.get_usage_metrics()
    print(f"Usage metrics: {json.dumps(metrics, indent=2)}")
