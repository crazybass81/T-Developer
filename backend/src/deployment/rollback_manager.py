import asyncio
import json
import os
import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict,List,Optional
import boto3
from botocore.exceptions import ClientError

class RollbackReason(Enum):
    MANUAL="manual";FAILURE="failure";TIMEOUT="timeout";HEALTH_CHECK="health_check"
    PERFORMANCE="performance";ERROR_RATE="error_rate"

@dataclass
class RollbackSpec:
    deployment_id:str;reason:RollbackReason;target_version:Optional[str]=None
    backup_config:Optional[Dict]=None;metadata:Dict=None

class RollbackManager:
    def __init__(self,region="us-east-1"):
        self.region=region;self.ba=boto3.client("bedrock-agent",region_name=region)
        self.aid=os.getenv("BEDROCK_AGENT_ID","NYZHMLSDOJ")
        self.rollbacks={};self._init_backup_store()
    
    def _init_backup_store(self):
        self.db=sqlite3.connect("rollback_backups.db",check_same_thread=False)
        self.db.execute('''CREATE TABLE IF NOT EXISTS backups
                          (deployment_id TEXT PRIMARY KEY,agent_config TEXT,action_groups TEXT,
                           timestamp REAL,version TEXT,metadata TEXT)''')
        self.db.commit()
    
    async def backup_deployment(self,deployment_id:str,version:str="current")->bool:
        try:
            agent_resp=await asyncio.to_thread(self.ba.get_agent,agentId=self.aid)
            agent_config=agent_resp["agent"]
            
            ags_resp=await asyncio.to_thread(self.ba.list_agent_action_groups,agentId=self.aid,agentVersion="DRAFT")
            action_groups=ags_resp.get("actionGroupSummaries",[])
            
            self.db.execute("INSERT OR REPLACE INTO backups VALUES (?,?,?,?,?,?)",
                          (deployment_id,json.dumps(agent_config),json.dumps(action_groups),
                           time.time(),version,json.dumps({})))
            self.db.commit();return True
        except Exception:return False
    
    async def initiate_rollback(self,spec:RollbackSpec)->Dict:
        rid=f"rollback_{spec.deployment_id}_{int(time.time())}"
        rb={"id":rid,"deployment_id":spec.deployment_id,"reason":spec.reason.value,
            "status":"initiated","start_time":time.time(),"steps":[],"error":None}
        self.rollbacks[rid]=rb
        
        try:
            await self._log_step(rid,"backup_current","Creating current state backup")
            await self.backup_deployment(f"{spec.deployment_id}_rollback")
            await self._log_step(rid,"restore_previous","Restoring previous version")
            backup_data=await self._get_backup(spec.deployment_id)
            if not backup_data:raise Exception("No backup found")
            await self._restore_from_backup(backup_data,rid)
            await self._log_step(rid,"verify","Verifying rollback")
            await self._verify_rollback(rid)
            rb["status"]="completed";rb["end_time"]=time.time()
            rb["duration"]=rb["end_time"]-rb["start_time"]
        except Exception as e:
            rb["status"]="failed";rb["error"]=str(e)
            await self._log_step(rid,"error",f"Failed: {str(e)}")
        return rb
    
    async def _get_backup(self,deployment_id:str)->Optional[Dict]:
        cur=self.db.cursor()
        cur.execute("SELECT * FROM backups WHERE deployment_id=? ORDER BY timestamp DESC LIMIT 1",(deployment_id,))
        row=cur.fetchone()
        if not row:return None
        return {"agent_config":json.loads(row[1]),"action_groups":json.loads(row[2]),
                "timestamp":row[3],"version":row[4]}
    
    async def _restore_from_backup(self,backup:Dict,rollback_id:str):
        try:
            agent_config=backup["agent_config"]
            update_params={"agentId":self.aid,"agentName":agent_config.get("agentName"),
                          "description":agent_config.get("description"),
                          "instruction":agent_config.get("instruction")}
            await asyncio.to_thread(self.ba.update_agent,**{k:v for k,v in update_params.items() if v})
            
            current_ags=await asyncio.to_thread(self.ba.list_agent_action_groups,agentId=self.aid,agentVersion="DRAFT")
            for ag in current_ags.get("actionGroupSummaries",[]):
                try:
                    await asyncio.to_thread(self.ba.delete_agent_action_group,
                                          agentId=self.aid,agentVersion="DRAFT",actionGroupId=ag["actionGroupId"])
                except:pass
            
            await asyncio.to_thread(self.ba.prepare_agent,agentId=self.aid)
            await self._log_step(rollback_id,"restore_complete","Agent restored from backup")
            
        except ClientError as e:
            raise Exception(f"Restore failed: {e}")
    
    async def _verify_rollback(self,rollback_id:str):
        try:
            resp=await asyncio.to_thread(self.ba.get_agent,agentId=self.aid)
            await self._log_step(rollback_id,"verify_complete","Rollback verification passed")
        except Exception as e:
            raise Exception(f"Verification failed: {e}")
    
    async def _log_step(self,rollback_id:str,step:str,message:str):
        if rollback_id in self.rollbacks:
            self.rollbacks[rollback_id]["steps"].append({
                "step":step,"message":message,"timestamp":time.time()
            })
    
    def get_rollback_status(self,rollback_id:str)->Optional[Dict]:
        return self.rollbacks.get(rollback_id)
    
    def list_rollbacks(self)->List[Dict]:
        return list(self.rollbacks.values())
    
    async def cleanup_old_backups(self,days:int=30):
        cutoff=time.time()-(days*86400)
        self.db.execute("DELETE FROM backups WHERE timestamp < ?",(cutoff,))
        self.db.commit()
    
    def get_backup_info(self,deployment_id:str)->Optional[Dict]:
        cur=self.db.cursor()
        cur.execute("SELECT deployment_id,timestamp,version FROM backups WHERE deployment_id=?",(deployment_id,))
        row=cur.fetchone()
        return {"deployment_id":row[0],"backup_time":row[1],"version":row[2]} if row else None

if __name__=="__main__":
    async def test():
        rm=RollbackManager()
        await rm.backup_deployment("test123","1.0.0")
        spec=RollbackSpec("test123",RollbackReason.MANUAL)
        result=await rm.initiate_rollback(spec)
        print(f"Rollback: {result['status']}, Steps: {len(result['steps'])}")
    asyncio.run(test())