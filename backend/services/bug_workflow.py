"""
Bug Validation Workflow - Comprehensive Bug Lifecycle Management

This module provides workflow management for bug reports including:
- State machine for bug lifecycle
- Triage and validation workflow
- Automated severity scoring
- SLA tracking
- Notification system
"""

import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime, timedelta

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class BugStatus(str, Enum):
    """Bug report status."""
    NEW = "new"
    TRIAGING = "triaging"
    NEEDS_INFO = "needs_info"
    VALIDATED = "validated"
    DUPLICATE = "duplicate"
    NOT_APPLICABLE = "not_applicable"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    WONT_FIX = "wont_fix"
    RESOLVED = "resolved"
    REWARDED = "rewarded"
    CLOSED = "closed"


class BugSeverity(str, Enum):
    """Bug severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class BugPriority(str, Enum):
    """Bug priority levels."""
    P0 = "p0"  # Immediate
    P1 = "p1"  # High
    P2 = "p2"  # Medium
    P3 = "p3"  # Low
    P4 = "p4"  # Backlog


class StateTransition(BaseModel):
    """State transition definition."""
    from_state: BugStatus
    to_state: BugStatus
    required_role: str
    conditions: List[str] = []


class WorkflowAction(BaseModel):
    """Workflow action."""
    action: str
    user_id: str
    timestamp: datetime
    comment: Optional[str] = None
    data: Dict[str, Any] = {}


class BugReport(BaseModel):
    """Bug report model."""
    id: str
    title: str
    description: str
    status: BugStatus = BugStatus.NEW
    severity: BugSeverity = BugSeverity.MEDIUM
    priority: BugPriority = BugPriority.P2
    reporter_id: str
    assignee_id: Optional[str] = None
    program_id: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    validated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    reward_amount: Optional[float] = None
    cvss_score: Optional[float] = None
    vulnerability_type: str = ""
    affected_component: str = ""
    reproduction_steps: str = ""
    proof_of_concept: str = ""
    impact: str = ""
    suggested_fix: str = ""
    attachments: List[str] = []
    tags: List[str] = []
    duplicate_of: Optional[str] = None
    history: List[WorkflowAction] = []


class SLAConfig(BaseModel):
    """SLA configuration."""
    triage_hours: int = 24
    response_hours: int = 48
    resolution_days: Dict[str, int] = {
        "critical": 7,
        "high": 14,
        "medium": 30,
        "low": 60
    }


class BugWorkflowService:
    """
    Bug Validation Workflow Service.

    Provides:
    - State machine management
    - Transition validation
    - Automated scoring
    - SLA tracking
    - Workflow automation
    """

    def __init__(self):
        """Initialize workflow service."""
        self._bugs: Dict[str, BugReport] = {}
        self._transitions = self._define_transitions()
        self._sla_config = SLAConfig()

    def _define_transitions(self) -> List[StateTransition]:
        """Define valid state transitions."""
        return [
            # From NEW
            StateTransition(from_state=BugStatus.NEW, to_state=BugStatus.TRIAGING, required_role="triager"),
            StateTransition(from_state=BugStatus.NEW, to_state=BugStatus.DUPLICATE, required_role="triager"),
            StateTransition(from_state=BugStatus.NEW, to_state=BugStatus.NOT_APPLICABLE, required_role="triager"),

            # From TRIAGING
            StateTransition(from_state=BugStatus.TRIAGING, to_state=BugStatus.NEEDS_INFO, required_role="triager"),
            StateTransition(from_state=BugStatus.TRIAGING, to_state=BugStatus.VALIDATED, required_role="analyst"),
            StateTransition(from_state=BugStatus.TRIAGING, to_state=BugStatus.DUPLICATE, required_role="triager"),
            StateTransition(from_state=BugStatus.TRIAGING, to_state=BugStatus.NOT_APPLICABLE, required_role="triager"),

            # From NEEDS_INFO
            StateTransition(from_state=BugStatus.NEEDS_INFO, to_state=BugStatus.TRIAGING, required_role="researcher"),
            StateTransition(from_state=BugStatus.NEEDS_INFO, to_state=BugStatus.CLOSED, required_role="triager"),

            # From VALIDATED
            StateTransition(from_state=BugStatus.VALIDATED, to_state=BugStatus.IN_PROGRESS, required_role="analyst"),
            StateTransition(from_state=BugStatus.VALIDATED, to_state=BugStatus.WONT_FIX, required_role="program_manager"),

            # From IN_PROGRESS
            StateTransition(from_state=BugStatus.IN_PROGRESS, to_state=BugStatus.FIXED, required_role="analyst"),
            StateTransition(from_state=BugStatus.IN_PROGRESS, to_state=BugStatus.WONT_FIX, required_role="program_manager"),

            # From FIXED
            StateTransition(from_state=BugStatus.FIXED, to_state=BugStatus.RESOLVED, required_role="analyst"),
            StateTransition(from_state=BugStatus.FIXED, to_state=BugStatus.IN_PROGRESS, required_role="researcher"),

            # From RESOLVED
            StateTransition(from_state=BugStatus.RESOLVED, to_state=BugStatus.REWARDED, required_role="program_manager"),

            # From REWARDED
            StateTransition(from_state=BugStatus.REWARDED, to_state=BugStatus.CLOSED, required_role="program_manager"),

            # General closures
            StateTransition(from_state=BugStatus.DUPLICATE, to_state=BugStatus.CLOSED, required_role="triager"),
            StateTransition(from_state=BugStatus.NOT_APPLICABLE, to_state=BugStatus.CLOSED, required_role="triager"),
            StateTransition(from_state=BugStatus.WONT_FIX, to_state=BugStatus.CLOSED, required_role="program_manager")
        ]

    def create_bug(
        self,
        bug_data: Dict[str, Any],
        reporter_id: str
    ) -> BugReport:
        """
        Create a new bug report.

        Args:
            bug_data: Bug report data
            reporter_id: Reporter user ID

        Returns:
            Created bug report
        """
        import uuid

        bug = BugReport(
            id=str(uuid.uuid4()),
            title=bug_data.get("title", ""),
            description=bug_data.get("description", ""),
            reporter_id=reporter_id,
            program_id=bug_data.get("program_id", ""),
            vulnerability_type=bug_data.get("vulnerability_type", ""),
            affected_component=bug_data.get("affected_component", ""),
            reproduction_steps=bug_data.get("reproduction_steps", ""),
            proof_of_concept=bug_data.get("proof_of_concept", ""),
            impact=bug_data.get("impact", ""),
            suggested_fix=bug_data.get("suggested_fix", ""),
            tags=bug_data.get("tags", [])
        )

        # Add creation action to history
        bug.history.append(WorkflowAction(
            action="created",
            user_id=reporter_id,
            timestamp=datetime.utcnow(),
            comment="Bug report created"
        ))

        # Calculate initial severity and priority
        self._auto_score_bug(bug)

        self._bugs[bug.id] = bug
        logger.info(f"Created bug {bug.id}: {bug.title}")

        return bug

    def transition(
        self,
        bug_id: str,
        to_state: BugStatus,
        user_id: str,
        user_role: str,
        comment: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> BugReport:
        """
        Transition bug to new state.

        Args:
            bug_id: Bug ID
            to_state: Target state
            user_id: User performing transition
            user_role: User's role
            comment: Optional comment
            data: Additional data

        Returns:
            Updated bug report
        """
        if bug_id not in self._bugs:
            raise ValueError(f"Bug {bug_id} not found")

        bug = self._bugs[bug_id]
        from_state = bug.status

        # Validate transition
        valid_transition = self._validate_transition(from_state, to_state, user_role)
        if not valid_transition:
            raise ValueError(
                f"Invalid transition from {from_state.value} to {to_state.value} "
                f"for role {user_role}"
            )

        # Perform transition
        bug.status = to_state
        bug.updated_at = datetime.utcnow()

        # Handle specific state changes
        if to_state == BugStatus.VALIDATED:
            bug.validated_at = datetime.utcnow()
        elif to_state in [BugStatus.RESOLVED, BugStatus.CLOSED]:
            bug.resolved_at = datetime.utcnow()
        elif to_state == BugStatus.REWARDED and data:
            bug.reward_amount = data.get("reward_amount")

        # Handle duplicate
        if to_state == BugStatus.DUPLICATE and data:
            bug.duplicate_of = data.get("duplicate_of")

        # Add to history
        bug.history.append(WorkflowAction(
            action=f"transitioned_to_{to_state.value}",
            user_id=user_id,
            timestamp=datetime.utcnow(),
            comment=comment,
            data=data or {}
        ))

        logger.info(f"Bug {bug_id} transitioned from {from_state.value} to {to_state.value}")

        return bug

    def _validate_transition(
        self,
        from_state: BugStatus,
        to_state: BugStatus,
        user_role: str
    ) -> bool:
        """Validate if transition is allowed."""
        for transition in self._transitions:
            if (transition.from_state == from_state and
                transition.to_state == to_state):
                # Check role hierarchy
                role_hierarchy = [
                    "guest", "researcher", "triager", "analyst",
                    "team_lead", "program_manager", "org_admin", "super_admin"
                ]

                if user_role in role_hierarchy:
                    required_idx = role_hierarchy.index(transition.required_role)
                    user_idx = role_hierarchy.index(user_role)
                    return user_idx >= required_idx

        return False

    def _auto_score_bug(self, bug: BugReport) -> None:
        """Automatically score bug severity and priority."""
        # Severity scoring based on vulnerability type
        severity_map = {
            "sql_injection": BugSeverity.HIGH,
            "command_injection": BugSeverity.CRITICAL,
            "xss": BugSeverity.MEDIUM,
            "csrf": BugSeverity.MEDIUM,
            "ssrf": BugSeverity.HIGH,
            "idor": BugSeverity.HIGH,
            "authentication_bypass": BugSeverity.CRITICAL,
            "rce": BugSeverity.CRITICAL,
            "path_traversal": BugSeverity.HIGH,
            "information_disclosure": BugSeverity.LOW
        }

        vuln_type = bug.vulnerability_type.lower().replace(" ", "_")
        bug.severity = severity_map.get(vuln_type, BugSeverity.MEDIUM)

        # Priority based on severity
        priority_map = {
            BugSeverity.CRITICAL: BugPriority.P0,
            BugSeverity.HIGH: BugPriority.P1,
            BugSeverity.MEDIUM: BugPriority.P2,
            BugSeverity.LOW: BugPriority.P3,
            BugSeverity.INFO: BugPriority.P4
        }

        bug.priority = priority_map.get(bug.severity, BugPriority.P2)

    def assign(
        self,
        bug_id: str,
        assignee_id: str,
        assigned_by: str
    ) -> BugReport:
        """Assign bug to user."""
        if bug_id not in self._bugs:
            raise ValueError(f"Bug {bug_id} not found")

        bug = self._bugs[bug_id]
        bug.assignee_id = assignee_id
        bug.updated_at = datetime.utcnow()

        bug.history.append(WorkflowAction(
            action="assigned",
            user_id=assigned_by,
            timestamp=datetime.utcnow(),
            data={"assignee_id": assignee_id}
        ))

        return bug

    def update_severity(
        self,
        bug_id: str,
        severity: BugSeverity,
        cvss_score: Optional[float],
        user_id: str
    ) -> BugReport:
        """Update bug severity and CVSS score."""
        if bug_id not in self._bugs:
            raise ValueError(f"Bug {bug_id} not found")

        bug = self._bugs[bug_id]
        old_severity = bug.severity

        bug.severity = severity
        bug.cvss_score = cvss_score
        bug.updated_at = datetime.utcnow()

        # Update priority based on new severity
        priority_map = {
            BugSeverity.CRITICAL: BugPriority.P0,
            BugSeverity.HIGH: BugPriority.P1,
            BugSeverity.MEDIUM: BugPriority.P2,
            BugSeverity.LOW: BugPriority.P3,
            BugSeverity.INFO: BugPriority.P4
        }
        bug.priority = priority_map.get(severity, bug.priority)

        bug.history.append(WorkflowAction(
            action="severity_updated",
            user_id=user_id,
            timestamp=datetime.utcnow(),
            data={
                "old_severity": old_severity.value,
                "new_severity": severity.value,
                "cvss_score": cvss_score
            }
        ))

        return bug

    def add_comment(
        self,
        bug_id: str,
        user_id: str,
        comment: str,
        is_internal: bool = False
    ) -> BugReport:
        """Add comment to bug."""
        if bug_id not in self._bugs:
            raise ValueError(f"Bug {bug_id} not found")

        bug = self._bugs[bug_id]
        bug.updated_at = datetime.utcnow()

        bug.history.append(WorkflowAction(
            action="comment_added",
            user_id=user_id,
            timestamp=datetime.utcnow(),
            comment=comment,
            data={"is_internal": is_internal}
        ))

        return bug

    def get_bug(self, bug_id: str) -> Optional[BugReport]:
        """Get bug by ID."""
        return self._bugs.get(bug_id)

    def get_bugs_by_status(self, status: BugStatus) -> List[BugReport]:
        """Get bugs by status."""
        return [b for b in self._bugs.values() if b.status == status]

    def get_bugs_by_program(self, program_id: str) -> List[BugReport]:
        """Get bugs by program."""
        return [b for b in self._bugs.values() if b.program_id == program_id]

    def get_sla_status(self, bug_id: str) -> Dict[str, Any]:
        """
        Get SLA status for a bug.

        Returns:
            SLA status with deadlines and violations
        """
        if bug_id not in self._bugs:
            return {}

        bug = self._bugs[bug_id]
        now = datetime.utcnow()

        # Triage SLA
        triage_deadline = bug.created_at + timedelta(hours=self._sla_config.triage_hours)
        triage_met = bug.status != BugStatus.NEW or now < triage_deadline

        # Response SLA
        response_deadline = bug.created_at + timedelta(hours=self._sla_config.response_hours)
        response_met = len(bug.history) > 1 or now < response_deadline

        # Resolution SLA
        resolution_days = self._sla_config.resolution_days.get(
            bug.severity.value, 30
        )
        resolution_deadline = bug.created_at + timedelta(days=resolution_days)
        resolution_met = (
            bug.resolved_at is not None or
            bug.status in [BugStatus.CLOSED, BugStatus.RESOLVED] or
            now < resolution_deadline
        )

        return {
            "bug_id": bug_id,
            "triage": {
                "deadline": triage_deadline.isoformat(),
                "met": triage_met,
                "overdue_hours": max(0, (now - triage_deadline).total_seconds() / 3600)
                if not triage_met else 0
            },
            "response": {
                "deadline": response_deadline.isoformat(),
                "met": response_met,
                "overdue_hours": max(0, (now - response_deadline).total_seconds() / 3600)
                if not response_met else 0
            },
            "resolution": {
                "deadline": resolution_deadline.isoformat(),
                "met": resolution_met,
                "overdue_days": max(0, (now - resolution_deadline).days)
                if not resolution_met else 0
            }
        }

    def get_available_transitions(
        self,
        bug_id: str,
        user_role: str
    ) -> List[str]:
        """Get available transitions for a bug."""
        if bug_id not in self._bugs:
            return []

        bug = self._bugs[bug_id]
        available = []

        for transition in self._transitions:
            if transition.from_state == bug.status:
                if self._validate_transition(
                    bug.status, transition.to_state, user_role
                ):
                    available.append(transition.to_state.value)

        return available

    def get_workflow_stats(self, program_id: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow statistics."""
        bugs = self._bugs.values()
        if program_id:
            bugs = [b for b in bugs if b.program_id == program_id]

        bugs = list(bugs)

        # Status distribution
        status_counts = {}
        for bug in bugs:
            status_counts[bug.status.value] = status_counts.get(bug.status.value, 0) + 1

        # Severity distribution
        severity_counts = {}
        for bug in bugs:
            severity_counts[bug.severity.value] = severity_counts.get(bug.severity.value, 0) + 1

        # Average resolution time
        resolved = [b for b in bugs if b.resolved_at]
        avg_resolution = 0
        if resolved:
            total_days = sum(
                (b.resolved_at - b.created_at).days for b in resolved
            )
            avg_resolution = total_days / len(resolved)

        return {
            "total_bugs": len(bugs),
            "by_status": status_counts,
            "by_severity": severity_counts,
            "avg_resolution_days": round(avg_resolution, 1),
            "sla_compliance": self._calculate_sla_compliance(bugs)
        }

    def _calculate_sla_compliance(self, bugs: List[BugReport]) -> Dict[str, float]:
        """Calculate SLA compliance rates."""
        if not bugs:
            return {"triage": 100, "response": 100, "resolution": 100}

        triage_met = 0
        response_met = 0
        resolution_met = 0

        for bug in bugs:
            sla = self.get_sla_status(bug.id)
            if sla.get("triage", {}).get("met", True):
                triage_met += 1
            if sla.get("response", {}).get("met", True):
                response_met += 1
            if sla.get("resolution", {}).get("met", True):
                resolution_met += 1

        total = len(bugs)
        return {
            "triage": round(triage_met / total * 100, 1),
            "response": round(response_met / total * 100, 1),
            "resolution": round(resolution_met / total * 100, 1)
        }


# Singleton instance
_workflow_service: Optional[BugWorkflowService] = None


def get_workflow_service() -> BugWorkflowService:
    """Get the global workflow service instance."""
    global _workflow_service
    if _workflow_service is None:
        _workflow_service = BugWorkflowService()
    return _workflow_service


__all__ = [
    "BugWorkflowService",
    "BugStatus",
    "BugSeverity",
    "BugPriority",
    "BugReport",
    "WorkflowAction",
    "get_workflow_service"
]
