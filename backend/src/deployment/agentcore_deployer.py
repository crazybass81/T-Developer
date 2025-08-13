import asyncio
import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError


class Status(Enum):
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"


@dataclass
class AgentSpec:
    name: str
    code: str
    version: str
    description: str = ""
    runtime: str = "python3.11"
    timeout: int = 900
    memory: int = 128
    env_vars: Dict[str, str] = None


class AgentCoreDeployer:
    def __init__(self, region="us-east-1"):
        self.region = region
        self.ba = boto3.client("bedrock-agent", region_name=region)
        self.br = boto3.client("bedrock-agent-runtime", region_name=region)
        self.aid = os.getenv("BEDROCK_AGENT_ID", "NYZHMLSDOJ")
        self.alias = os.getenv("BEDROCK_AGENT_ALIAS_ID", "IBQK7SYNGG")
        self.deps = {}

    async def deploy_agent(self, spec: AgentSpec) -> Dict[str, Any]:
        did = f"{spec.name}_{int(time.time())}"
        st = time.time()
        dep = {
            "id": did,
            "name": spec.name,
            "status": Status.PENDING,
            "start": st,
            "ver": spec.version,
            "error": None,
        }
        try:
            if len(spec.code.encode("utf-8")) > 6656:
                raise ValueError(f"Agent too large")
            dep["status"] = Status.BUILDING
            self.deps[did] = dep
            ag = await self._create_ag(spec, did)
            dep["ag_id"] = ag["actionGroupId"]
            dep["status"] = Status.DEPLOYING
            await self._update_agent(spec, ag["actionGroupId"])
            pr = await self._prep_agent()
            dep["prep_id"] = pr.get("agentId")
            dep["status"] = Status.DEPLOYED
            dep["end"] = time.time()
            dep["duration"] = dep["end"] - dep["start"]
        except Exception as e:
            dep["status"] = Status.FAILED
            dep["error"] = str(e)
            dep["end"] = time.time()
        self.deps[did] = dep
        return dep

    async def _create_ag(self, spec: AgentSpec, did: str) -> Dict:
        try:
            cfg = {
                "agentId": self.aid,
                "agentVersion": "DRAFT",
                "actionGroupName": f"{spec.name}_{did[-8:]}",
                "description": spec.description or f"Agent: {spec.name}",
                "actionGroupExecutor": {
                    "lambda": {"lambdaArn": f"arn:aws:lambda:{self.region}:*:function:placeholder"}
                },
                "apiSchema": {
                    "payload": json.dumps(
                        {
                            "openapi": "3.0.0",
                            "info": {"title": spec.name, "version": spec.version},
                            "paths": {
                                "/execute": {
                                    "post": {
                                        "description": f"Execute {spec.name}",
                                        "requestBody": {"required": True},
                                        "responses": {"200": {"description": "Success"}},
                                    }
                                }
                            },
                        }
                    )
                },
            }
            resp = await asyncio.to_thread(self.ba.create_agent_action_group, **cfg)
            return resp["agentActionGroup"]
        except ClientError as e:
            raise Exception(f"Create AG failed: {e}")

    async def _update_agent(self, spec: AgentSpec, ag_id: str):
        try:
            cfg = {
                "agentId": self.aid,
                "agentName": f"T-Dev-{spec.name}",
                "description": f"T-Dev: {spec.description}",
                "instruction": f"Execute {spec.name}",
            }
            await asyncio.to_thread(self.ba.update_agent, **cfg)
        except ClientError as e:
            raise Exception(f"Update failed: {e}")

    async def _prep_agent(self) -> Dict:
        try:
            resp = await asyncio.to_thread(self.ba.prepare_agent, agentId=self.aid)
            await asyncio.sleep(2)
            return resp
        except ClientError as e:
            raise Exception(f"Prep failed: {e}")

    def get_deployment(self, did: str) -> Optional[Dict]:
        return self.deps.get(did)

    def list_deployments(self) -> List[Dict]:
        return list(self.deps.values())

    async def test_deployment(self, did: str) -> Dict[str, Any]:
        dep = self.deps.get(did)
        if not dep or dep["status"] != Status.DEPLOYED:
            return {"status": "error", "message": "Not ready"}
        try:
            resp = await asyncio.to_thread(
                self.br.invoke_agent,
                agentId=self.aid,
                agentAliasId=self.alias,
                sessionId=f"test_{did}",
                inputText="test",
            )
            return {"status": "success", "response": resp}
        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":

    async def test():
        d = AgentCoreDeployer()
        s = AgentSpec(
            "sample_agent", 'def execute(): return {"result": "success"}', "1.0.0", "Test agent"
        )
        r = await d.deploy_agent(s)
        print(f"Status: {r['status']}, Duration: {r.get('duration',0):.2f}s")

    asyncio.run(test())
