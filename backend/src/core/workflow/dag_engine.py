"""
DAG-based Workflow Engine
Directed Acyclic Graph workflow execution engine for agent orchestration
"""

import asyncio
import json
import logging
import traceback
import uuid
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """Workflow node execution status"""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
    TIMEOUT = "timeout"


class ExecutionStrategy(Enum):
    """Workflow execution strategy"""

    SEQUENTIAL = "sequential"  # Execute nodes one by one
    PARALLEL = "parallel"  # Execute all ready nodes in parallel
    PRIORITY = "priority"  # Execute based on priority
    RESOURCE_AWARE = "resource_aware"  # Consider resource constraints


@dataclass
class WorkflowNode:
    """Represents a node in the workflow DAG"""

    node_id: str
    agent_id: str
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    priority: int = 0
    retry_count: int = 3
    timeout_seconds: int = 300
    condition: Optional[str] = None  # Conditional execution expression


@dataclass
class NodeExecution:
    """Node execution state"""

    node_id: str
    status: NodeStatus = NodeStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    retries_left: int = 3
    execution_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Workflow execution state"""

    workflow_id: str
    execution_id: str
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    node_executions: Dict[str, NodeExecution] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class DAGWorkflowEngine:
    """DAG-based workflow execution engine"""

    def __init__(
        self,
        max_parallel_nodes: int = 10,
        max_retries: int = 3,
        default_timeout: int = 300,
    ):
        """
        Initialize the workflow engine

        Args:
            max_parallel_nodes: Maximum nodes to execute in parallel
            max_retries: Default retry count for failed nodes
            default_timeout: Default timeout in seconds
        """
        self.max_parallel_nodes = max_parallel_nodes
        self.max_retries = max_retries
        self.default_timeout = default_timeout

        # Workflow definitions
        self.workflows: Dict[str, nx.DiGraph] = {}
        self.workflow_metadata: Dict[str, Dict] = {}

        # Execution tracking
        self.executions: Dict[str, WorkflowExecution] = {}
        self.active_executions: Set[str] = set()

        # Executor for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=max_parallel_nodes)

        # Agent registry (would be injected in production)
        self.agent_registry = {}  # agent_id -> agent_instance

        # Event handlers
        self.event_handlers = defaultdict(list)

    def create_workflow(
        self,
        workflow_id: str,
        nodes: List[WorkflowNode],
        metadata: Optional[Dict] = None,
    ) -> bool:
        """Create a new workflow definition"""
        try:
            # Create directed graph
            dag = nx.DiGraph()

            # Add nodes
            for node in nodes:
                dag.add_node(
                    node.node_id,
                    agent_id=node.agent_id,
                    name=node.name,
                    config=node.config,
                    priority=node.priority,
                    retry_count=node.retry_count,
                    timeout_seconds=node.timeout_seconds,
                    condition=node.condition,
                )

                # Add edges based on dependencies
                for dep in node.dependencies:
                    dag.add_edge(dep, node.node_id)

            # Validate DAG (check for cycles)
            if not nx.is_directed_acyclic_graph(dag):
                raise ValueError(f"Workflow {workflow_id} contains cycles")

            # Validate all dependencies exist
            for node in nodes:
                for dep in node.dependencies:
                    if dep not in dag.nodes:
                        raise ValueError(f"Node {node.node_id} depends on non-existent node {dep}")

            # Store workflow
            self.workflows[workflow_id] = dag
            self.workflow_metadata[workflow_id] = metadata or {}

            logger.info(f"Created workflow {workflow_id} with {len(nodes)} nodes")
            return True

        except Exception as e:
            logger.error(f"Failed to create workflow {workflow_id}: {e}")
            return False

    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        strategy: ExecutionStrategy = ExecutionStrategy.PARALLEL,
    ) -> WorkflowExecution:
        """Execute a workflow"""

        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Create execution instance
        execution_id = str(uuid.uuid4())
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            execution_id=execution_id,
            started_at=datetime.utcnow(),
            context={"input": input_data or {}},
        )

        # Initialize node executions
        dag = self.workflows[workflow_id]
        for node_id in dag.nodes:
            execution.node_executions[node_id] = NodeExecution(
                node_id=node_id,
                retries_left=dag.nodes[node_id].get("retry_count", self.max_retries),
            )

        # Store execution
        self.executions[execution_id] = execution
        self.active_executions.add(execution_id)

        try:
            # Execute based on strategy
            if strategy == ExecutionStrategy.SEQUENTIAL:
                await self._execute_sequential(execution_id)
            elif strategy == ExecutionStrategy.PARALLEL:
                await self._execute_parallel(execution_id)
            elif strategy == ExecutionStrategy.PRIORITY:
                await self._execute_priority(execution_id)
            else:
                await self._execute_resource_aware(execution_id)

            # Mark completion
            execution.completed_at = datetime.utcnow()
            execution.status = "completed"

            # Calculate metrics
            execution.metrics = self._calculate_metrics(execution)

        except Exception as e:
            logger.error(f"Workflow execution {execution_id} failed: {e}")
            execution.status = "failed"
            execution.errors.append(str(e))

        finally:
            self.active_executions.discard(execution_id)

        return execution

    async def _execute_parallel(self, execution_id: str):
        """Execute workflow nodes in parallel when possible"""
        execution = self.executions[execution_id]
        dag = self.workflows[execution.workflow_id]

        # Track completed nodes
        completed = set()
        failed = set()

        while len(completed) + len(failed) < len(dag.nodes):
            # Find ready nodes
            ready_nodes = self._get_ready_nodes(dag, completed, failed, execution)

            if not ready_nodes and not self._has_running_nodes(execution):
                # No nodes to execute and nothing running - deadlock or all failed
                break

            # Execute ready nodes in parallel
            tasks = []
            for node_id in ready_nodes[: self.max_parallel_nodes]:
                node_exec = execution.node_executions[node_id]
                node_exec.status = NodeStatus.RUNNING
                node_exec.started_at = datetime.utcnow()

                task = asyncio.create_task(self._execute_node(execution_id, node_id))
                tasks.append((node_id, task))

            # Wait for tasks to complete
            for node_id, task in tasks:
                try:
                    result = await task
                    node_exec = execution.node_executions[node_id]

                    if result["success"]:
                        node_exec.status = NodeStatus.SUCCESS
                        node_exec.result = result["data"]
                        completed.add(node_id)
                    else:
                        node_exec.status = NodeStatus.FAILED
                        node_exec.error = result.get("error")

                        # Retry logic
                        if node_exec.retries_left > 0:
                            node_exec.retries_left -= 1
                            node_exec.status = NodeStatus.RETRYING
                            logger.info(
                                f"Retrying node {node_id}, {node_exec.retries_left} retries left"
                            )
                        else:
                            failed.add(node_id)

                    node_exec.completed_at = datetime.utcnow()
                    node_exec.execution_time_ms = int(
                        (node_exec.completed_at - node_exec.started_at).total_seconds() * 1000
                    )

                except asyncio.TimeoutError:
                    node_exec = execution.node_executions[node_id]
                    node_exec.status = NodeStatus.TIMEOUT
                    node_exec.error = "Execution timeout"
                    failed.add(node_id)

                except Exception as e:
                    node_exec = execution.node_executions[node_id]
                    node_exec.status = NodeStatus.FAILED
                    node_exec.error = str(e)
                    failed.add(node_id)

            # Small delay to prevent tight loop
            await asyncio.sleep(0.1)

    async def _execute_sequential(self, execution_id: str):
        """Execute workflow nodes sequentially based on topological order"""
        execution = self.executions[execution_id]
        dag = self.workflows[execution.workflow_id]

        # Get topological order
        try:
            topo_order = list(nx.topological_sort(dag))
        except nx.NetworkXError as e:
            raise ValueError(f"Cannot determine execution order: {e}")

        # Execute nodes in order
        for node_id in topo_order:
            node_exec = execution.node_executions[node_id]

            # Check if dependencies succeeded
            deps_failed = any(
                execution.node_executions[dep].status == NodeStatus.FAILED
                for dep in dag.predecessors(node_id)
            )

            if deps_failed:
                node_exec.status = NodeStatus.SKIPPED
                continue

            # Execute node
            node_exec.status = NodeStatus.RUNNING
            node_exec.started_at = datetime.utcnow()

            try:
                result = await self._execute_node(execution_id, node_id)

                if result["success"]:
                    node_exec.status = NodeStatus.SUCCESS
                    node_exec.result = result["data"]
                else:
                    node_exec.status = NodeStatus.FAILED
                    node_exec.error = result.get("error")

                    # Stop on failure in sequential mode
                    break

            except Exception as e:
                node_exec.status = NodeStatus.FAILED
                node_exec.error = str(e)
                break

            finally:
                node_exec.completed_at = datetime.utcnow()
                node_exec.execution_time_ms = int(
                    (node_exec.completed_at - node_exec.started_at).total_seconds() * 1000
                )

    async def _execute_priority(self, execution_id: str):
        """Execute nodes based on priority"""
        execution = self.executions[execution_id]
        dag = self.workflows[execution.workflow_id]

        completed = set()
        failed = set()

        while len(completed) + len(failed) < len(dag.nodes):
            # Get ready nodes sorted by priority
            ready_nodes = self._get_ready_nodes(dag, completed, failed, execution)

            if not ready_nodes:
                break

            # Sort by priority (higher first)
            ready_nodes.sort(key=lambda n: dag.nodes[n].get("priority", 0), reverse=True)

            # Execute highest priority node
            node_id = ready_nodes[0]
            node_exec = execution.node_executions[node_id]
            node_exec.status = NodeStatus.RUNNING
            node_exec.started_at = datetime.utcnow()

            try:
                result = await self._execute_node(execution_id, node_id)

                if result["success"]:
                    node_exec.status = NodeStatus.SUCCESS
                    node_exec.result = result["data"]
                    completed.add(node_id)
                else:
                    node_exec.status = NodeStatus.FAILED
                    node_exec.error = result.get("error")
                    failed.add(node_id)

            except Exception as e:
                node_exec.status = NodeStatus.FAILED
                node_exec.error = str(e)
                failed.add(node_id)

            finally:
                node_exec.completed_at = datetime.utcnow()
                node_exec.execution_time_ms = int(
                    (node_exec.completed_at - node_exec.started_at).total_seconds() * 1000
                )

    async def _execute_resource_aware(self, execution_id: str):
        """Execute nodes considering resource constraints"""
        # For now, fallback to parallel execution
        # In production, would check CPU, memory, etc.
        await self._execute_parallel(execution_id)

    def _get_ready_nodes(
        self,
        dag: nx.DiGraph,
        completed: Set[str],
        failed: Set[str],
        execution: WorkflowExecution,
    ) -> List[str]:
        """Get nodes that are ready to execute"""
        ready = []

        for node_id in dag.nodes:
            if node_id in completed or node_id in failed:
                continue

            node_exec = execution.node_executions[node_id]
            if node_exec.status in [
                NodeStatus.RUNNING,
                NodeStatus.SUCCESS,
                NodeStatus.FAILED,
            ]:
                continue

            # Check if all dependencies are completed
            deps_completed = all(dep in completed for dep in dag.predecessors(node_id))

            # Check if any dependency failed
            deps_failed = any(dep in failed for dep in dag.predecessors(node_id))

            if deps_completed and not deps_failed:
                # Check condition if specified
                node_data = dag.nodes[node_id]
                if node_data.get("condition"):
                    if not self._evaluate_condition(node_data["condition"], execution.context):
                        node_exec.status = NodeStatus.SKIPPED
                        completed.add(node_id)
                        continue

                ready.append(node_id)

        return ready

    def _has_running_nodes(self, execution: WorkflowExecution) -> bool:
        """Check if any nodes are currently running"""
        return any(node.status == NodeStatus.RUNNING for node in execution.node_executions.values())

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate a condition expression"""
        try:
            # Simple evaluation - in production use safe expression evaluator
            # For now, just check if condition is in context and truthy
            if condition in context:
                return bool(context[condition])
            return True
        except Exception:
            return True

    async def _execute_node(self, execution_id: str, node_id: str) -> Dict[str, Any]:
        """Execute a single node"""
        execution = self.executions[execution_id]
        dag = self.workflows[execution.workflow_id]
        node_data = dag.nodes[node_id]

        try:
            # Get agent instance (mock for now)
            agent_id = node_data["agent_id"]

            # Prepare input from dependencies
            input_data = self._prepare_node_input(dag, node_id, execution)

            # Add node config
            input_data.update(node_data.get("config", {}))

            # Execute with timeout
            timeout = node_data.get("timeout_seconds", self.default_timeout)

            # Mock execution - in production would call actual agent
            result = await asyncio.wait_for(
                self._mock_agent_execution(agent_id, input_data), timeout=timeout
            )

            # Store result in context for downstream nodes
            execution.context[f"{node_id}_output"] = result

            return {"success": True, "data": result}

        except asyncio.TimeoutError:
            return {"success": False, "error": "Execution timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _prepare_node_input(
        self, dag: nx.DiGraph, node_id: str, execution: WorkflowExecution
    ) -> Dict[str, Any]:
        """Prepare input data for a node from its dependencies"""
        input_data = {}

        # Get outputs from dependencies
        for dep_id in dag.predecessors(node_id):
            dep_output_key = f"{dep_id}_output"
            if dep_output_key in execution.context:
                input_data[dep_id] = execution.context[dep_output_key]

        # Add original input
        input_data["workflow_input"] = execution.context.get("input", {})

        return input_data

    async def _mock_agent_execution(self, agent_id: str, input_data: Dict) -> Dict:
        """Mock agent execution for testing"""
        # Simulate some processing time
        await asyncio.sleep(0.5)

        # Return mock result
        return {
            "agent_id": agent_id,
            "processed": True,
            "input_keys": list(input_data.keys()),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calculate_metrics(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Calculate execution metrics"""
        total_time = 0
        success_count = 0
        failed_count = 0
        skipped_count = 0

        for node_exec in execution.node_executions.values():
            if node_exec.execution_time_ms:
                total_time += node_exec.execution_time_ms

            if node_exec.status == NodeStatus.SUCCESS:
                success_count += 1
            elif node_exec.status == NodeStatus.FAILED:
                failed_count += 1
            elif node_exec.status == NodeStatus.SKIPPED:
                skipped_count += 1

        total_duration = None
        if execution.completed_at and execution.started_at:
            total_duration = (execution.completed_at - execution.started_at).total_seconds()

        return {
            "total_nodes": len(execution.node_executions),
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "total_execution_time_ms": total_time,
            "total_duration_seconds": total_duration,
            "success_rate": success_count / len(execution.node_executions)
            if execution.node_executions
            else 0,
        }

    def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get execution status"""
        return self.executions.get(execution_id)

    def visualize_workflow(self, workflow_id: str) -> str:
        """Generate workflow visualization (Mermaid format)"""
        if workflow_id not in self.workflows:
            return "Workflow not found"

        dag = self.workflows[workflow_id]
        mermaid = ["graph TD"]

        # Add nodes
        for node_id in dag.nodes:
            node_data = dag.nodes[node_id]
            label = node_data.get("name", node_id)
            mermaid.append(f"    {node_id}[{label}]")

        # Add edges
        for source, target in dag.edges:
            mermaid.append(f"    {source} --> {target}")

        return "\n".join(mermaid)

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        self.executions.clear()
        self.workflows.clear()
