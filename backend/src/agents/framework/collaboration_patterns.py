# backend/src/agents/framework/collaboration_patterns.py
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio

class PatternType(Enum):
    PIPELINE = "pipeline"
    MAP_REDUCE = "map_reduce"
    SCATTER_GATHER = "scatter_gather"
    MASTER_WORKER = "master_worker"
    CONSENSUS = "consensus"
    AUCTION = "auction"
    CHAIN_OF_RESPONSIBILITY = "chain_of_responsibility"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    REQUEST_RESPONSE = "request_response"

@dataclass
class CollaborationPattern:
    name: str
    type: PatternType
    participants: List[str]
    coordinator: Optional[str] = None
    config: Dict[str, Any] = None

class PatternLibrary:
    def __init__(self):
        self.patterns: Dict[str, CollaborationPattern] = {}
        self.pattern_implementations: Dict[PatternType, Callable] = {
            PatternType.PIPELINE: self._execute_pipeline,
            PatternType.MAP_REDUCE: self._execute_map_reduce,
            PatternType.SCATTER_GATHER: self._execute_scatter_gather,
            PatternType.MASTER_WORKER: self._execute_master_worker,
            PatternType.CONSENSUS: self._execute_consensus,
            PatternType.AUCTION: self._execute_auction
        }
        self.agent_handlers: Dict[str, Callable] = {}
    
    def register_pattern(self, pattern: CollaborationPattern):
        self.patterns[pattern.name] = pattern
    
    def register_agent_handler(self, agent_id: str, handler: Callable):
        self.agent_handlers[agent_id] = handler
    
    async def execute_pattern(self, pattern_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            raise ValueError(f"Pattern {pattern_name} not found")
        
        implementation = self.pattern_implementations.get(pattern.type)
        if not implementation:
            raise ValueError(f"No implementation for pattern type {pattern.type}")
        
        return await implementation(pattern, inputs)
    
    async def _execute_pipeline(self, pattern: CollaborationPattern, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipeline pattern: A -> B -> C"""
        current_data = inputs
        results = {}
        
        for agent_id in pattern.participants:
            handler = self.agent_handlers.get(agent_id)
            if handler:
                result = await handler("process", current_data)
                results[agent_id] = result
                current_data = result
        
        return {"final_result": current_data, "intermediate_results": results}
    
    async def _execute_map_reduce(self, pattern: CollaborationPattern, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute map-reduce pattern"""
        data_chunks = inputs.get("data_chunks", [])
        map_agents = pattern.participants[:-1]  # All but last agent
        reduce_agent = pattern.participants[-1]  # Last agent is reducer
        
        # Map phase
        map_tasks = []
        for i, chunk in enumerate(data_chunks):
            agent_id = map_agents[i % len(map_agents)]
            handler = self.agent_handlers.get(agent_id)
            if handler:
                task = asyncio.create_task(handler("map", chunk))
                map_tasks.append(task)
        
        map_results = await asyncio.gather(*map_tasks)
        
        # Reduce phase
        reduce_handler = self.agent_handlers.get(reduce_agent)
        if reduce_handler:
            final_result = await reduce_handler("reduce", {"results": map_results})
        else:
            final_result = map_results
        
        return {"map_results": map_results, "final_result": final_result}
    
    async def _execute_scatter_gather(self, pattern: CollaborationPattern, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scatter-gather pattern"""
        # Scatter: Send same data to all agents
        tasks = []
        for agent_id in pattern.participants:
            handler = self.agent_handlers.get(agent_id)
            if handler:
                task = asyncio.create_task(handler("process", inputs))
                tasks.append((agent_id, task))
        
        # Gather: Collect all results
        results = {}
        for agent_id, task in tasks:
            try:
                result = await task
                results[agent_id] = result
            except Exception as e:
                results[agent_id] = {"error": str(e)}
        
        return results
    
    async def _execute_master_worker(self, pattern: CollaborationPattern, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute master-worker pattern"""
        master_id = pattern.coordinator or pattern.participants[0]
        workers = [p for p in pattern.participants if p != master_id]
        
        # Master distributes work
        master_handler = self.agent_handlers.get(master_id)
        if not master_handler:
            raise ValueError(f"No handler for master {master_id}")
        
        work_distribution = await master_handler("distribute_work", {
            "workers": workers,
            "data": inputs
        })
        
        # Workers execute tasks
        worker_tasks = []
        for worker_id in workers:
            worker_handler = self.agent_handlers.get(worker_id)
            if worker_handler:
                work_item = work_distribution.get(worker_id, {})
                task = asyncio.create_task(worker_handler("execute_work", work_item))
                worker_tasks.append((worker_id, task))
        
        # Collect worker results
        worker_results = {}
        for worker_id, task in worker_tasks:
            worker_results[worker_id] = await task
        
        # Master aggregates results
        final_result = await master_handler("aggregate_results", worker_results)
        
        return {"worker_results": worker_results, "final_result": final_result}
    
    async def _execute_consensus(self, pattern: CollaborationPattern, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute consensus pattern"""
        proposal = inputs.get("proposal")
        votes = {}
        
        # Collect votes from all participants
        vote_tasks = []
        for agent_id in pattern.participants:
            handler = self.agent_handlers.get(agent_id)
            if handler:
                task = asyncio.create_task(handler("vote", {"proposal": proposal}))
                vote_tasks.append((agent_id, task))
        
        for agent_id, task in vote_tasks:
            try:
                vote = await task
                votes[agent_id] = vote
            except Exception as e:
                votes[agent_id] = {"error": str(e)}
        
        # Determine consensus
        valid_votes = [v for v in votes.values() if "error" not in v]
        if not valid_votes:
            return {"consensus": False, "votes": votes}
        
        # Simple majority consensus
        yes_votes = sum(1 for v in valid_votes if v.get("vote") == "yes")
        consensus_reached = yes_votes > len(valid_votes) / 2
        
        return {
            "consensus": consensus_reached,
            "votes": votes,
            "yes_votes": yes_votes,
            "total_votes": len(valid_votes)
        }
    
    async def _execute_auction(self, pattern: CollaborationPattern, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute auction pattern"""
        auction_item = inputs.get("item")
        bids = {}
        
        # Collect bids from all participants
        bid_tasks = []
        for agent_id in pattern.participants:
            handler = self.agent_handlers.get(agent_id)
            if handler:
                task = asyncio.create_task(handler("bid", {"item": auction_item}))
                bid_tasks.append((agent_id, task))
        
        for agent_id, task in bid_tasks:
            try:
                bid = await task
                bids[agent_id] = bid
            except Exception as e:
                bids[agent_id] = {"error": str(e)}
        
        # Determine winner (highest bid)
        valid_bids = {k: v for k, v in bids.items() if "error" not in v and "amount" in v}
        
        if not valid_bids:
            return {"winner": None, "bids": bids}
        
        winner = max(valid_bids.items(), key=lambda x: x[1]["amount"])
        
        return {
            "winner": winner[0],
            "winning_bid": winner[1]["amount"],
            "all_bids": bids
        }
    
    # Additional collaboration patterns
    
    def create_pipeline_pattern(self, agents: List[str]) -> CollaborationPattern:
        """Create a pipeline collaboration pattern"""
        return CollaborationPattern(
            name=f"pipeline_{len(agents)}_agents",
            type=PatternType.PIPELINE,
            participants=agents
        )
    
    def create_map_reduce_pattern(self, mappers: List[str], reducer: str) -> CollaborationPattern:
        """Create a map-reduce collaboration pattern"""
        return CollaborationPattern(
            name=f"mapreduce_{len(mappers)}_to_1",
            type=PatternType.MAP_REDUCE,
            participants=mappers + [reducer],
            coordinator=reducer
        )
    
    def create_scatter_gather_pattern(self, agents: List[str], coordinator: str = None) -> CollaborationPattern:
        """Create a scatter-gather collaboration pattern"""
        return CollaborationPattern(
            name=f"scatter_gather_{len(agents)}_agents",
            type=PatternType.SCATTER_GATHER,
            participants=agents,
            coordinator=coordinator
        )
    
    def create_master_worker_pattern(self, master: str, workers: List[str]) -> CollaborationPattern:
        """Create a master-worker collaboration pattern"""
        return CollaborationPattern(
            name=f"master_worker_1_to_{len(workers)}",
            type=PatternType.MASTER_WORKER,
            participants=[master] + workers,
            coordinator=master
        )
    
    def create_consensus_pattern(self, agents: List[str]) -> CollaborationPattern:
        """Create a consensus collaboration pattern"""
        return CollaborationPattern(
            name=f"consensus_{len(agents)}_agents",
            type=PatternType.CONSENSUS,
            participants=agents
        )
    
    def create_auction_pattern(self, bidders: List[str], auctioneer: str = None) -> CollaborationPattern:
        """Create an auction collaboration pattern"""
        participants = bidders + ([auctioneer] if auctioneer else [])
        return CollaborationPattern(
            name=f"auction_{len(bidders)}_bidders",
            type=PatternType.AUCTION,
            participants=participants,
            coordinator=auctioneer
        )
    
    async def get_pattern_recommendations(self, task_description: str, available_agents: List[str]) -> List[str]:
        """Get pattern recommendations based on task description"""
        recommendations = []
        
        # Simple heuristics for pattern recommendation
        if "sequential" in task_description.lower() or "pipeline" in task_description.lower():
            recommendations.append("pipeline")
        
        if "parallel" in task_description.lower() or "concurrent" in task_description.lower():
            recommendations.append("scatter_gather")
        
        if "aggregate" in task_description.lower() or "combine" in task_description.lower():
            recommendations.append("map_reduce")
        
        if "vote" in task_description.lower() or "agree" in task_description.lower():
            recommendations.append("consensus")
        
        if "compete" in task_description.lower() or "bid" in task_description.lower():
            recommendations.append("auction")
        
        if "coordinate" in task_description.lower() or "manage" in task_description.lower():
            recommendations.append("master_worker")
        
        return recommendations
    
    def get_pattern_metrics(self, pattern_name: str) -> Dict[str, Any]:
        """Get performance metrics for a pattern"""
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            return {}
        
        # This would be populated with actual execution metrics
        return {
            "pattern_type": pattern.type.value,
            "participant_count": len(pattern.participants),
            "execution_count": 0,  # Would track actual executions
            "average_duration": 0.0,
            "success_rate": 0.0,
            "last_executed": None
        }