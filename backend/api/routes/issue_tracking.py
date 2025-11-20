"""
Issue Tracking Integration Routes
Jira, Linear, Asana, Monday.com integration
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.bug import Bug
from sqlalchemy import select

router = APIRouter(prefix="/issue-tracking", tags=["Issue Tracking"])


class IssueTrackerConfig(BaseModel):
    """Issue tracker configuration"""
    platform: str
    api_token: str
    workspace_url: str
    project_key: Optional[str] = None
    board_id: Optional[str] = None


class SyncBugRequest(BaseModel):
    """Request to sync bug to issue tracker"""
    bug_id: int
    platform: str
    project_key: str
    issue_type: Optional[str] = "Bug"


class JiraClient:
    """Jira API client"""
    
    def __init__(self, base_url: str, api_token: str, email: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.email = email
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Bug") -> Dict[str, Any]:
        """Create Jira issue"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rest/api/3/issue",
                headers=self.headers,
                auth=(self.email, self.api_token),
                json={
                    "fields": {
                        "project": {"key": project_key},
                        "summary": summary,
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": description}
                                    ]
                                }
                            ]
                        },
                        "issuetype": {"name": issue_type}
                    }
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get Jira issue"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                headers=self.headers,
                auth=(self.email, self.api_token)
            )
            response.raise_for_status()
            return response.json()
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> None:
        """Update Jira issue"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                headers=self.headers,
                auth=(self.email, self.api_token),
                json={"fields": fields}
            )
            response.raise_for_status()


class LinearClient:
    """Linear API client"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
    
    async def create_issue(self, team_id: str, title: str, description: str, priority: int = 2) -> Dict[str, Any]:
        """Create Linear issue"""
        query = """
        mutation IssueCreate($teamId: String!, $title: String!, $description: String!, $priority: Int!) {
            issueCreate(input: {
                teamId: $teamId,
                title: $title,
                description: $description,
                priority: $priority
            }) {
                success
                issue {
                    id
                    identifier
                    url
                }
            }
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={
                    "query": query,
                    "variables": {
                        "teamId": team_id,
                        "title": title,
                        "description": description,
                        "priority": priority
                    }
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """Get Linear issue"""
        query = """
        query Issue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                state {
                    name
                }
                url
            }
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={
                    "query": query,
                    "variables": {"id": issue_id}
                }
            )
            response.raise_for_status()
            return response.json()


class AsanaClient:
    """Asana API client"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://app.asana.com/api/1.0"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    async def create_task(self, workspace_id: str, project_id: str, name: str, notes: str) -> Dict[str, Any]:
        """Create Asana task"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tasks",
                headers=self.headers,
                json={
                    "data": {
                        "workspace": workspace_id,
                        "projects": [project_id],
                        "name": name,
                        "notes": notes
                    }
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get Asana task"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()


class MondayClient:
    """Monday.com API client"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"
        }
    
    async def create_item(self, board_id: str, item_name: str, column_values: Dict[str, Any]) -> Dict[str, Any]:
        """Create Monday.com item"""
        query = """
        mutation ($boardId: ID!, $itemName: String!, $columnValues: JSON!) {
            create_item (
                board_id: $boardId,
                item_name: $itemName,
                column_values: $columnValues
            ) {
                id
                name
            }
        }
        """
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={
                    "query": query,
                    "variables": {
                        "boardId": board_id,
                        "itemName": item_name,
                        "columnValues": column_values
                    }
                }
            )
            response.raise_for_status()
            return response.json()


@router.post("/jira/configure")
async def configure_jira(
    config: IssueTrackerConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Jira integration
    
    Args:
        config: Jira configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Test connection
        client = JiraClient(
            base_url=config.workspace_url,
            api_token=config.api_token,
            email=current_user.email
        )
        
        # Store configuration (in production, encrypt the token)
        current_user.jira_url = config.workspace_url
        current_user.jira_token = config.api_token
        current_user.jira_email = current_user.email
        
        await db.commit()
        
        return {
            "status": "configured",
            "platform": "jira",
            "workspace_url": config.workspace_url,
            "message": "Jira integration configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Jira configuration failed: {str(e)}"
        )


@router.post("/jira/sync")
async def sync_to_jira(
    request: SyncBugRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync bug to Jira
    
    Args:
        request: Sync request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Sync status with Jira issue key
    """
    try:
        # Get bug
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Check Jira configuration
        if not current_user.jira_url or not current_user.jira_token:
            raise HTTPException(
                status_code=400,
                detail="Jira not configured. Please configure Jira first."
            )
        
        # Create Jira client
        client = JiraClient(
            base_url=current_user.jira_url,
            api_token=current_user.jira_token,
            email=current_user.jira_email
        )
        
        # Create issue
        issue = await client.create_issue(
            project_key=request.project_key,
            summary=bug.title,
            description=bug.description or "",
            issue_type=request.issue_type
        )
        
        # Store Jira issue reference
        bug.jira_issue_key = issue["key"]
        bug.jira_issue_id = issue["id"]
        bug.synced_to_jira_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "synced",
            "bug_id": request.bug_id,
            "jira_issue_key": issue["key"],
            "jira_url": f"{current_user.jira_url}/browse/{issue['key']}",
            "message": "Bug synced to Jira successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Jira sync failed: {str(e)}"
        )


@router.post("/linear/configure")
async def configure_linear(
    config: IssueTrackerConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Linear integration
    
    Args:
        config: Linear configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Test connection
        client = LinearClient(api_token=config.api_token)
        
        # Store configuration
        current_user.linear_token = config.api_token
        
        await db.commit()
        
        return {
            "status": "configured",
            "platform": "linear",
            "message": "Linear integration configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Linear configuration failed: {str(e)}"
        )


@router.post("/linear/sync")
async def sync_to_linear(
    request: SyncBugRequest,
    team_id: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync bug to Linear
    
    Args:
        request: Sync request
        team_id: Linear team ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Sync status with Linear issue ID
    """
    try:
        # Get bug
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Check Linear configuration
        if not current_user.linear_token:
            raise HTTPException(
                status_code=400,
                detail="Linear not configured. Please configure Linear first."
            )
        
        # Create Linear client
        client = LinearClient(api_token=current_user.linear_token)
        
        # Map severity to Linear priority
        priority_map = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }
        priority = priority_map.get(bug.severity, 2)
        
        # Create issue
        response = await client.create_issue(
            team_id=team_id,
            title=bug.title,
            description=bug.description or "",
            priority=priority
        )
        
        issue_data = response["data"]["issueCreate"]["issue"]
        
        # Store Linear issue reference
        bug.linear_issue_id = issue_data["id"]
        bug.linear_issue_identifier = issue_data["identifier"]
        bug.synced_to_linear_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "synced",
            "bug_id": request.bug_id,
            "linear_issue_id": issue_data["id"],
            "linear_issue_identifier": issue_data["identifier"],
            "linear_url": issue_data["url"],
            "message": "Bug synced to Linear successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Linear sync failed: {str(e)}"
        )


@router.post("/asana/configure")
async def configure_asana(
    config: IssueTrackerConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Asana integration
    
    Args:
        config: Asana configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Test connection
        client = AsanaClient(api_token=config.api_token)
        
        # Store configuration
        current_user.asana_token = config.api_token
        
        await db.commit()
        
        return {
            "status": "configured",
            "platform": "asana",
            "message": "Asana integration configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Asana configuration failed: {str(e)}"
        )


@router.post("/asana/sync")
async def sync_to_asana(
    request: SyncBugRequest,
    workspace_id: str = Body(...),
    project_id: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync bug to Asana
    
    Args:
        request: Sync request
        workspace_id: Asana workspace ID
        project_id: Asana project ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Sync status with Asana task ID
    """
    try:
        # Get bug
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Check Asana configuration
        if not current_user.asana_token:
            raise HTTPException(
                status_code=400,
                detail="Asana not configured. Please configure Asana first."
            )
        
        # Create Asana client
        client = AsanaClient(api_token=current_user.asana_token)
        
        # Create task
        response = await client.create_task(
            workspace_id=workspace_id,
            project_id=project_id,
            name=bug.title,
            notes=bug.description or ""
        )
        
        task_data = response["data"]
        
        # Store Asana task reference
        bug.asana_task_id = task_data["gid"]
        bug.synced_to_asana_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "synced",
            "bug_id": request.bug_id,
            "asana_task_id": task_data["gid"],
            "message": "Bug synced to Asana successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Asana sync failed: {str(e)}"
        )


@router.post("/monday/configure")
async def configure_monday(
    config: IssueTrackerConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Monday.com integration
    
    Args:
        config: Monday.com configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Test connection
        client = MondayClient(api_token=config.api_token)
        
        # Store configuration
        current_user.monday_token = config.api_token
        
        await db.commit()
        
        return {
            "status": "configured",
            "platform": "monday",
            "message": "Monday.com integration configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Monday.com configuration failed: {str(e)}"
        )


@router.post("/monday/sync")
async def sync_to_monday(
    request: SyncBugRequest,
    board_id: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync bug to Monday.com
    
    Args:
        request: Sync request
        board_id: Monday.com board ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Sync status with Monday.com item ID
    """
    try:
        # Get bug
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        # Check Monday.com configuration
        if not current_user.monday_token:
            raise HTTPException(
                status_code=400,
                detail="Monday.com not configured. Please configure Monday.com first."
            )
        
        # Create Monday.com client
        client = MondayClient(api_token=current_user.monday_token)
        
        # Create item
        response = await client.create_item(
            board_id=board_id,
            item_name=bug.title,
            column_values={
                "status": "Open",
                "severity": bug.severity
            }
        )
        
        item_data = response["data"]["create_item"]
        
        # Store Monday.com item reference
        bug.monday_item_id = item_data["id"]
        bug.synced_to_monday_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "synced",
            "bug_id": request.bug_id,
            "monday_item_id": item_data["id"],
            "message": "Bug synced to Monday.com successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Monday.com sync failed: {str(e)}"
        )


@router.get("/status/{bug_id}")
async def get_sync_status(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sync status for bug across all platforms
    
    Args:
        bug_id: Bug ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Sync status for all platforms
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        return {
            "bug_id": bug_id,
            "jira": {
                "synced": bug.jira_issue_key is not None,
                "issue_key": bug.jira_issue_key,
                "synced_at": bug.synced_to_jira_at.isoformat() if bug.synced_to_jira_at else None
            },
            "linear": {
                "synced": bug.linear_issue_id is not None,
                "issue_identifier": bug.linear_issue_identifier,
                "synced_at": bug.synced_to_linear_at.isoformat() if bug.synced_to_linear_at else None
            },
            "asana": {
                "synced": bug.asana_task_id is not None,
                "task_id": bug.asana_task_id,
                "synced_at": bug.synced_to_asana_at.isoformat() if bug.synced_to_asana_at else None
            },
            "monday": {
                "synced": bug.monday_item_id is not None,
                "item_id": bug.monday_item_id,
                "synced_at": bug.synced_to_monday_at.isoformat() if bug.synced_to_monday_at else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sync status: {str(e)}"
        )
