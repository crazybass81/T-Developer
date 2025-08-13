import asyncio
import json
import sqlite3
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, List, Optional

import boto3


class DeployStatus(Enum):
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLBACK = "rollback"
    TERMINATED = "terminated"


@dataclass
class DeployEvent:
    id: str
    timestamp: float
    status: DeployStatus
    message: str
    metadata: Dict = None


@dataclass
class DeployRecord:
    deployment_id: str
    agent_name: str
    version: str
    status: DeployStatus
    start_time: float
    end_time: Optional[float] = None
    error: Optional[str] = None
    events: List[DeployEvent] = None
    metadata: Dict = None


class DeploymentTracker:
    def __init__(self, db_path="deployments.db"):
        self.db_path = db_path
        self._init_db()
        self.active_tracks = {}
        self.observers = []

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """CREATE TABLE IF NOT EXISTS deployments
                       (id TEXT PRIMARY KEY,agent_name TEXT,version TEXT,status TEXT,
                        start_time REAL,end_time REAL,error TEXT)"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS events
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,deployment_id TEXT,
                        timestamp REAL,status TEXT,message TEXT,metadata TEXT)"""
        )
        conn.commit()
        conn.close()

    async def start_tracking(
        self, deployment_id: str, agent_name: str, version: str
    ) -> DeployRecord:
        record = DeployRecord(
            deployment_id, agent_name, version, DeployStatus.PENDING, time.time(), None, None, []
        )
        self.active_tracks[deployment_id] = record
        await self._log_event(deployment_id, DeployStatus.PENDING, "Deployment started")
        await self._persist_record(record)
        return record

    async def update_status(
        self, deployment_id: str, status: DeployStatus, message: str = "", metadata: Dict = None
    ):
        if deployment_id not in self.active_tracks:
            return
        record = self.active_tracks[deployment_id]
        record.status = status
        if status in [DeployStatus.DEPLOYED, DeployStatus.FAILED, DeployStatus.TERMINATED]:
            record.end_time = time.time()
        await self._log_event(deployment_id, status, message, metadata)
        await self._persist_record(record)
        await self._notify_observers(record)

    async def _log_event(
        self, deployment_id: str, status: DeployStatus, message: str, metadata: Dict = None
    ):
        event = DeployEvent(deployment_id, time.time(), status, message, metadata)
        if deployment_id in self.active_tracks:
            if not self.active_tracks[deployment_id].events:
                self.active_tracks[deployment_id].events = []
            self.active_tracks[deployment_id].events.append(event)
        await self._persist_event(event)

    async def _persist_record(self, record: DeployRecord):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT OR REPLACE INTO deployments VALUES (?,?,?,?,?,?,?)""",
            (
                record.deployment_id,
                record.agent_name,
                record.version,
                record.status.value,
                record.start_time,
                record.end_time,
                record.error,
            ),
        )
        conn.commit()
        conn.close()

    async def _persist_event(self, event: DeployEvent):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT INTO events VALUES (NULL,?,?,?,?,?)""",
            (
                event.id,
                event.timestamp,
                event.status.value,
                event.message,
                json.dumps(event.metadata or {}),
            ),
        )
        conn.commit()
        conn.close()

    def get_deployment(self, deployment_id: str) -> Optional[DeployRecord]:
        if deployment_id in self.active_tracks:
            return self.active_tracks[deployment_id]
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM deployments WHERE id=?", (deployment_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return None
        record = DeployRecord(row[0], row[1], row[2], DeployStatus(row[3]), row[4], row[5], row[6])
        cur.execute(
            "SELECT * FROM events WHERE deployment_id=? ORDER BY timestamp", (deployment_id,)
        )
        events = [
            DeployEvent(r[1], r[2], DeployStatus(r[3]), r[4], json.loads(r[5]))
            for r in cur.fetchall()
        ]
        record.events = events
        conn.close()
        return record

    def list_deployments(self, status_filter: Optional[DeployStatus] = None) -> List[DeployRecord]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        query = "SELECT * FROM deployments"
        params = []
        if status_filter:
            query += " WHERE status=?"
            params.append(status_filter.value)
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return [DeployRecord(r[0], r[1], r[2], DeployStatus(r[3]), r[4], r[5], r[6]) for r in rows]

    def get_active_deployments(self) -> List[DeployRecord]:
        return [
            r
            for r in self.active_tracks.values()
            if r.status not in [DeployStatus.DEPLOYED, DeployStatus.FAILED, DeployStatus.TERMINATED]
        ]

    async def register_observer(self, callback):
        self.observers.append(callback)

    async def _notify_observers(self, record: DeployRecord):
        for obs in self.observers:
            try:
                await obs(record)
            except Exception:
                pass

    def get_metrics(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT status,COUNT(*) FROM deployments GROUP BY status")
        status_counts = dict(cur.fetchall())
        cur.execute("SELECT AVG(end_time-start_time) FROM deployments WHERE end_time IS NOT NULL")
        avg_duration = cur.fetchone()[0] or 0
        cur.execute(
            "SELECT COUNT(*) FROM deployments WHERE status='deployed' AND start_time > ?",
            (time.time() - 86400,),
        )
        last_24h = cur.fetchone()[0]
        conn.close()
        return {
            "status_counts": status_counts,
            "avg_duration": avg_duration,
            "deployments_24h": last_24h,
            "active_count": len(self.get_active_deployments()),
        }


if __name__ == "__main__":

    async def test():
        t = DeploymentTracker()
        r = await t.start_tracking("test123", "sample", "1.0.0")
        await t.update_status("test123", DeployStatus.BUILDING, "Building agent")
        await t.update_status("test123", DeployStatus.DEPLOYED, "Deployed successfully")
        print(f"Final status: {r.status}")
        print(f"Events: {len(r.events)}")
        m = t.get_metrics()
        print(f"Metrics: {m}")

    asyncio.run(test())
