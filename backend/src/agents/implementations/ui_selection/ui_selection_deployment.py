#!/usr/bin/env python3
"""UI Selection Agent Deployment Script"""

import asyncio
import subprocess
import json
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class DeploymentResult:
    success: bool
    version: str
    replicas: int
    health_status: str
    error: str = ""

class UIAgentDeployer:
    def __init__(self):
        self.version = "v1.0.0"
        self.namespace = "t-developer"
        
    async def deploy(self) -> DeploymentResult:
        """Deploy UI Selection Agent"""
        try:
            # 1. Pre-deployment validation
            await self._validate_prerequisites()
            
            # 2. Build and push image
            await self._build_image()
            
            # 3. Deploy to Kubernetes
            await self._deploy_k8s()
            
            # 4. Health check
            health = await self._health_check()
            
            return DeploymentResult(
                success=True,
                version=self.version,
                replicas=3,
                health_status=health
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                version=self.version,
                replicas=0,
                health_status="failed",
                error=str(e)
            )
    
    async def _validate_prerequisites(self):
        """Validate deployment prerequisites"""
        # Check tests pass
        result = subprocess.run(["python", "-m", "pytest", "tests/"], 
                              capture_output=True)
        if result.returncode != 0:
            raise Exception("Tests failed")
    
    async def _build_image(self):
        """Build Docker image"""
        subprocess.run([
            "docker", "build", 
            "-t", f"t-developer/ui-selection-agent:{self.version}",
            "."
        ], check=True)
    
    async def _deploy_k8s(self):
        """Deploy to Kubernetes"""
        subprocess.run([
            "kubectl", "set", "image", 
            f"deployment/ui-selection-agent",
            f"agent=t-developer/ui-selection-agent:{self.version}",
            "-n", self.namespace
        ], check=True)
        
        # Wait for rollout
        subprocess.run([
            "kubectl", "rollout", "status",
            "deployment/ui-selection-agent",
            "-n", self.namespace
        ], check=True)
    
    async def _health_check(self) -> str:
        """Check deployment health"""
        await asyncio.sleep(30)  # Wait for startup
        
        result = subprocess.run([
            "kubectl", "get", "pods",
            "-l", "app=ui-selection-agent",
            "-n", self.namespace,
            "-o", "json"
        ], capture_output=True, text=True)
        
        pods = json.loads(result.stdout)
        ready_pods = sum(1 for pod in pods["items"] 
                        if pod["status"]["phase"] == "Running")
        
        return "healthy" if ready_pods >= 3 else "degraded"

if __name__ == "__main__":
    deployer = UIAgentDeployer()
    result = asyncio.run(deployer.deploy())
    
    if result.success:
        print(f"✅ Deployment successful: {result.version}")
    else:
        print(f"❌ Deployment failed: {result.error}")
        exit(1)