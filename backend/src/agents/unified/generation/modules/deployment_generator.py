"""
Deployment Generator Module for Generation Agent
Generates deployment configurations and infrastructure as code
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import yaml


class DeploymentTarget(Enum):
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    NETLIFY = "netlify"
    VERCEL = "vercel"
    HEROKU = "heroku"


@dataclass
class DeploymentConfig:
    filename: str
    content: str
    target: DeploymentTarget
    description: str = ""
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class DeploymentResult:
    success: bool
    deployment_configs: Dict[str, DeploymentConfig]
    total_configs: int
    processing_time: float
    metadata: Dict[str, Any]
    error: str = ""


class DeploymentGenerator:
    """Advanced deployment configuration generator"""

    def __init__(self):
        self.version = "1.0.0"

        self.generators = {
            DeploymentTarget.DOCKER: self._generate_docker_configs,
            DeploymentTarget.KUBERNETES: self._generate_k8s_configs,
            DeploymentTarget.AWS: self._generate_aws_configs,
            DeploymentTarget.NETLIFY: self._generate_netlify_configs,
            DeploymentTarget.VERCEL: self._generate_vercel_configs,
        }

    async def generate_deployment_configs(
        self, context: Dict[str, Any], output_path: str
    ) -> DeploymentResult:
        """Generate deployment configurations"""

        start_time = datetime.now()

        try:
            framework = context.get("target_framework", "react")
            deployment_configs = {}

            # Determine appropriate deployment targets
            targets = self._get_deployment_targets(framework, context)

            # Generate configs for each target
            for target in targets:
                if target in self.generators:
                    configs = await self.generators[target](context)
                    deployment_configs.update(configs)

            processing_time = (datetime.now() - start_time).total_seconds()

            return DeploymentResult(
                success=True,
                deployment_configs=deployment_configs,
                total_configs=len(deployment_configs),
                processing_time=processing_time,
                metadata={
                    "framework": framework,
                    "targets": [t.value for t in targets],
                },
            )

        except Exception as e:
            return DeploymentResult(
                success=False,
                deployment_configs={},
                total_configs=0,
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={},
                error=str(e),
            )

    def _get_deployment_targets(
        self, framework: str, context: Dict[str, Any]
    ) -> List[DeploymentTarget]:
        """Determine deployment targets based on framework"""

        targets = [DeploymentTarget.DOCKER]  # Always include Docker

        if framework in ["react", "vue", "angular"]:
            targets.extend([DeploymentTarget.NETLIFY, DeploymentTarget.VERCEL])
        elif framework in ["express", "fastapi", "django", "flask"]:
            targets.extend([DeploymentTarget.KUBERNETES, DeploymentTarget.AWS])

        return targets

    async def _generate_docker_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, DeploymentConfig]:
        """Generate Docker configurations"""

        framework = context.get("target_framework", "react")
        configs = {}

        # Generate Dockerfile
        dockerfile_content = self._generate_dockerfile(framework, context)
        configs["Dockerfile"] = DeploymentConfig(
            filename="Dockerfile",
            content=dockerfile_content,
            target=DeploymentTarget.DOCKER,
            description="Docker container configuration",
        )

        # Generate docker-compose.yml
        compose_content = self._generate_docker_compose(framework, context)
        configs["docker-compose.yml"] = DeploymentConfig(
            filename="docker-compose.yml",
            content=compose_content,
            target=DeploymentTarget.DOCKER,
            description="Docker Compose configuration",
        )

        return configs

    async def _generate_k8s_configs(self, context: Dict[str, Any]) -> Dict[str, DeploymentConfig]:
        """Generate Kubernetes configurations"""

        configs = {}

        # Generate deployment
        deployment_content = self._generate_k8s_deployment(context)
        configs["k8s/deployment.yaml"] = DeploymentConfig(
            filename="k8s/deployment.yaml",
            content=deployment_content,
            target=DeploymentTarget.KUBERNETES,
            description="Kubernetes deployment configuration",
        )

        # Generate service
        service_content = self._generate_k8s_service(context)
        configs["k8s/service.yaml"] = DeploymentConfig(
            filename="k8s/service.yaml",
            content=service_content,
            target=DeploymentTarget.KUBERNETES,
            description="Kubernetes service configuration",
        )

        return configs

    async def _generate_aws_configs(self, context: Dict[str, Any]) -> Dict[str, DeploymentConfig]:
        """Generate AWS deployment configurations"""

        configs = {}

        # Generate CloudFormation template
        cf_content = self._generate_cloudformation_template(context)
        configs["aws/cloudformation.yaml"] = DeploymentConfig(
            filename="aws/cloudformation.yaml",
            content=cf_content,
            target=DeploymentTarget.AWS,
            description="AWS CloudFormation template",
        )

        return configs

    async def _generate_netlify_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, DeploymentConfig]:
        """Generate Netlify configurations"""

        framework = context.get("target_framework", "react")

        # Only for frontend frameworks
        if framework not in ["react", "vue", "angular"]:
            return {}

        configs = {}

        # Generate netlify.toml
        netlify_content = self._generate_netlify_config(framework, context)
        configs["netlify.toml"] = DeploymentConfig(
            filename="netlify.toml",
            content=netlify_content,
            target=DeploymentTarget.NETLIFY,
            description="Netlify deployment configuration",
        )

        return configs

    async def _generate_vercel_configs(
        self, context: Dict[str, Any]
    ) -> Dict[str, DeploymentConfig]:
        """Generate Vercel configurations"""

        framework = context.get("target_framework", "react")

        # Only for frontend frameworks
        if framework not in ["react", "vue", "angular"]:
            return {}

        configs = {}

        # Generate vercel.json
        vercel_content = self._generate_vercel_config(framework, context)
        configs["vercel.json"] = DeploymentConfig(
            filename="vercel.json",
            content=vercel_content,
            target=DeploymentTarget.VERCEL,
            description="Vercel deployment configuration",
        )

        return configs

    def _generate_dockerfile(self, framework: str, context: Dict[str, Any]) -> str:
        """Generate Dockerfile content"""

        if framework in ["react", "vue", "angular"]:
            return f"""# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]"""

        elif framework in ["express"]:
            return f"""FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build TypeScript
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]"""

        elif framework in ["fastapi", "django", "flask"]:
            return f"""FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]"""

        return "# Generic Dockerfile"

    def _generate_docker_compose(self, framework: str, context: Dict[str, Any]) -> str:
        """Generate docker-compose.yml content"""

        project_name = context.get("project_name", "app").replace(" ", "-").lower()

        if framework in ["react", "vue", "angular"]:
            compose_config = {
                "version": "3.8",
                "services": {
                    "frontend": {
                        "build": ".",
                        "ports": ["80:80"],
                        "environment": [f"NODE_ENV=production"],
                    }
                },
            }
        else:
            compose_config = {
                "version": "3.8",
                "services": {
                    "app": {
                        "build": ".",
                        "ports": ["8000:8000"],
                        "environment": [
                            "NODE_ENV=production"
                            if framework == "express"
                            else "ENVIRONMENT=production"
                        ],
                        "depends_on": ["db"],
                    },
                    "db": {
                        "image": "postgres:13",
                        "environment": [
                            f"POSTGRES_DB={project_name}_db",
                            "POSTGRES_USER=user",
                            "POSTGRES_PASSWORD=password",
                        ],
                        "volumes": ["postgres_data:/var/lib/postgresql/data"],
                        "ports": ["5432:5432"],
                    },
                },
                "volumes": {"postgres_data": None},
            }

        return yaml.dump(compose_config, default_flow_style=False)

    def _generate_k8s_deployment(self, context: Dict[str, Any]) -> str:
        """Generate Kubernetes deployment"""

        project_name = context.get("project_name", "app").replace(" ", "-").lower()

        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{project_name}-deployment",
                "labels": {"app": project_name},
            },
            "spec": {
                "replicas": 3,
                "selector": {"matchLabels": {"app": project_name}},
                "template": {
                    "metadata": {"labels": {"app": project_name}},
                    "spec": {
                        "containers": [
                            {
                                "name": project_name,
                                "image": f"{project_name}:latest",
                                "ports": [{"containerPort": 8000}],
                                "env": [{"name": "NODE_ENV", "value": "production"}],
                            }
                        ]
                    },
                },
            },
        }

        return yaml.dump(deployment, default_flow_style=False)

    def _generate_k8s_service(self, context: Dict[str, Any]) -> str:
        """Generate Kubernetes service"""

        project_name = context.get("project_name", "app").replace(" ", "-").lower()

        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": f"{project_name}-service"},
            "spec": {
                "selector": {"app": project_name},
                "ports": [{"protocol": "TCP", "port": 80, "targetPort": 8000}],
                "type": "LoadBalancer",
            },
        }

        return yaml.dump(service, default_flow_style=False)

    def _generate_cloudformation_template(self, context: Dict[str, Any]) -> str:
        """Generate AWS CloudFormation template"""

        project_name = context.get("project_name", "app").replace(" ", "-").lower()

        template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"CloudFormation template for {project_name}",
            "Resources": {
                "ECSCluster": {
                    "Type": "AWS::ECS::Cluster",
                    "Properties": {"ClusterName": f"{project_name}-cluster"},
                },
                "TaskDefinition": {
                    "Type": "AWS::ECS::TaskDefinition",
                    "Properties": {
                        "Family": f"{project_name}-task",
                        "Cpu": "256",
                        "Memory": "512",
                        "NetworkMode": "awsvpc",
                        "RequiresCompatibilities": ["FARGATE"],
                        "ExecutionRoleArn": {"Ref": "ExecutionRole"},
                        "ContainerDefinitions": [
                            {
                                "Name": project_name,
                                "Image": f"{project_name}:latest",
                                "PortMappings": [{"ContainerPort": 8000}],
                            }
                        ],
                    },
                },
                "ExecutionRole": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "AssumeRolePolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                                    "Action": "sts:AssumeRole",
                                }
                            ],
                        },
                        "ManagedPolicyArns": [
                            "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
                        ],
                    },
                },
            },
        }

        return yaml.dump(template, default_flow_style=False)

    def _generate_netlify_config(self, framework: str, context: Dict[str, Any]) -> str:
        """Generate Netlify configuration"""

        build_command = {
            "react": "npm run build",
            "vue": "npm run build",
            "angular": "ng build --prod",
        }.get(framework, "npm run build")

        publish_dir = {"react": "build", "vue": "dist", "angular": "dist"}.get(framework, "build")

        config = f"""[build]
  command = "{build_command}"
  publish = "{publish_dir}"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[context.production.environment]
  NODE_ENV = "production"

[context.branch-deploy.environment]
  NODE_ENV = "development"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "same-origin"
"""

        return config

    def _generate_vercel_config(self, framework: str, context: Dict[str, Any]) -> str:
        """Generate Vercel configuration"""

        build_command = {
            "react": "npm run build",
            "vue": "npm run build",
            "angular": "ng build --prod",
        }.get(framework, "npm run build")

        output_directory = {"react": "build", "vue": "dist", "angular": "dist"}.get(
            framework, "build"
        )

        config = {
            "version": 2,
            "builds": [
                {
                    "src": "package.json",
                    "use": "@vercel/static-build",
                    "config": {"distDir": output_directory},
                }
            ],
            "routes": [{"src": "/(.*)", "dest": "/index.html"}],
            "buildCommand": build_command,
            "outputDirectory": output_directory,
            "headers": [
                {
                    "source": "/(.*)",
                    "headers": [
                        {"key": "X-Frame-Options", "value": "DENY"},
                        {"key": "X-Content-Type-Options", "value": "nosniff"},
                    ],
                }
            ],
        }

        return json.dumps(config, indent=2)
