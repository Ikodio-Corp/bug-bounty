"""
Base AI Agent
Abstract base class for all AI agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents
    
    All agents must implement:
    - execute(): Main execution logic
    - analyze(): Analyze situation
    - decide(): Make decisions
    - act(): Take actions
    """
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.config = config or {}
        self.state = "idle"
        self.executions = 0
        self.successes = 0
        self.failures = 0
        self.created_at = datetime.utcnow()
        self.last_execution = None
        
    @abstractmethod
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task
        
        Args:
            task_data: Task parameters
            
        Returns:
            Execution results
        """
        pass
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze input data
        
        Args:
            data: Input data to analyze
            
        Returns:
            Analysis results
        """
        pass
    
    @abstractmethod
    async def decide(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make decisions based on analysis
        
        Args:
            analysis: Analysis results
            
        Returns:
            Decision results
        """
        pass
    
    @abstractmethod
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Take action based on decision
        
        Args:
            decision: Decision results
            
        Returns:
            Action results
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        
        success_rate = 0
        if self.executions > 0:
            success_rate = self.successes / self.executions
        
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "executions": self.executions,
            "successes": self.successes,
            "failures": self.failures,
            "success_rate": success_rate,
            "last_execution": self.last_execution,
            "uptime_seconds": (datetime.utcnow() - self.created_at).total_seconds()
        }
    
    def _record_execution(self, success: bool):
        """Record execution statistics"""
        self.executions += 1
        if success:
            self.successes += 1
        else:
            self.failures += 1
        self.last_execution = datetime.utcnow()
