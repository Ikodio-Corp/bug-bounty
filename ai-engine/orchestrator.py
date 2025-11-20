"""
AI Orchestrator
Coordinates multiple AI agents for complex tasks
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class AgentTask:
    """Represents a task assigned to an AI agent"""
    
    def __init__(self, agent_type: str, task_data: Dict[str, Any]):
        self.agent_type = agent_type
        self.task_data = task_data
        self.status = "pending"
        self.result = None
        self.created_at = datetime.utcnow()
        self.completed_at = None


class AIOrchestrator:
    """
    Central orchestrator for coordinating multiple AI agents
    
    Features:
    - Multi-agent collaboration
    - Task distribution
    - Result aggregation
    - Conflict resolution
    - Learning from outcomes
    """
    
    def __init__(self):
        self.agents = {}
        self.active_tasks = []
        self.completed_tasks = []
        self.knowledge_base = {}
        
    def register_agent(self, agent_type: str, agent_instance):
        """Register an AI agent with the orchestrator"""
        self.agents[agent_type] = agent_instance
        logger.info(f"Registered agent: {agent_type}")
    
    async def execute_task(
        self,
        task_type: str,
        task_data: Dict[str, Any],
        agents_required: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a task using one or more AI agents
        
        Args:
            task_type: Type of task (deploy, scan, optimize, etc)
            task_data: Task parameters
            agents_required: List of agent types needed
            
        Returns:
            Aggregated results from all agents
        """
        
        if agents_required is None:
            agents_required = self._determine_required_agents(task_type)
        
        tasks = []
        for agent_type in agents_required:
            if agent_type in self.agents:
                task = AgentTask(agent_type, task_data)
                self.active_tasks.append(task)
                tasks.append(self._execute_agent_task(task))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        aggregated = self._aggregate_results(results)
        
        self._learn_from_execution(task_type, task_data, aggregated)
        
        return aggregated
    
    async def _execute_agent_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a single agent task"""
        
        task.status = "running"
        agent = self.agents[task.agent_type]
        
        try:
            result = await agent.execute(task.task_data)
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.utcnow()
            
            self.active_tasks.remove(task)
            self.completed_tasks.append(task)
            
            return result
            
        except Exception as e:
            task.status = "failed"
            task.result = {"error": str(e)}
            logger.error(f"Agent {task.agent_type} failed: {e}")
            return {"error": str(e), "agent": task.agent_type}
    
    def _determine_required_agents(self, task_type: str) -> List[str]:
        """Determine which agents are needed for a task type"""
        
        agent_mapping = {
            "deploy": ["infrastructure", "security", "monitoring"],
            "scan": ["security", "bug_hunter"],
            "optimize": ["cost_optimizer", "performance"],
            "heal": ["infrastructure", "monitoring"],
            "provision": ["infrastructure", "security", "cost_optimizer"],
        }
        
        return agent_mapping.get(task_type, ["devops"])
    
    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate results from multiple agents"""
        
        aggregated = {
            "success": True,
            "results": [],
            "errors": [],
            "recommendations": [],
        }
        
        for result in results:
            if isinstance(result, Exception):
                aggregated["success"] = False
                aggregated["errors"].append(str(result))
            elif "error" in result:
                aggregated["success"] = False
                aggregated["errors"].append(result["error"])
            else:
                aggregated["results"].append(result)
                if "recommendations" in result:
                    aggregated["recommendations"].extend(result["recommendations"])
        
        return aggregated
    
    def _learn_from_execution(
        self,
        task_type: str,
        task_data: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """Learn from task execution to improve future performance"""
        
        if task_type not in self.knowledge_base:
            self.knowledge_base[task_type] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "avg_duration": 0,
                "patterns": []
            }
        
        kb = self.knowledge_base[task_type]
        kb["executions"] += 1
        
        if results["success"]:
            kb["successes"] += 1
        else:
            kb["failures"] += 1
        
        kb["success_rate"] = kb["successes"] / kb["executions"]
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        
        return {
            "total_agents": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "agents": list(self.agents.keys())
        }
    
    def get_knowledge_base(self) -> Dict[str, Any]:
        """Get accumulated knowledge from all executions"""
        return self.knowledge_base
