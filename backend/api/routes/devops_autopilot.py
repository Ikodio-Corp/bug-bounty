"""
DevOps Autopilot API Routes
Autonomous DevOps operations endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict

from core.database import get_db
from core.security import get_current_user
from services.devops_autopilot_service import DevOpsAutopilotService
from models.user import User


router = APIRouter(prefix="/api/devops", tags=["DevOps Autopilot"])


@router.post("/provision")
async def provision_infrastructure(
    config: Dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Autonomous infrastructure provisioning
    Auto-detects and provisions optimal resources
    """
    
    service = DevOpsAutopilotService(db)
    
    try:
        job = await service.provision_infrastructure(
            company_id=current_user.id,
            config=config,
            triggered_by=current_user.id
        )
        
        return {
            "success": True,
            "data": {
                "job_id": job.id,
                "job_type": job.job_type,
                "status": job.status,
                "estimated_duration_minutes": job.estimated_duration_minutes,
                "resources_created": job.resources_created
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deploy")
async def deploy_application(
    pipeline_id: int,
    commit_hash: str,
    environment: str = "production",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Zero-downtime autonomous deployment
    """
    
    service = DevOpsAutopilotService(db)
    
    try:
        execution = await service.deploy_application(
            pipeline_id=pipeline_id,
            commit_hash=commit_hash,
            environment=environment,
            triggered_by=current_user.id
        )
        
        return {
            "success": True,
            "data": {
                "execution_id": execution.id,
                "deployment_number": execution.deployment_number,
                "status": execution.status,
                "environment": execution.environment,
                "started_at": execution.started_at
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/heal")
async def self_heal_incident(
    resource_id: int,
    incident_type: str,
    symptoms: Dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Autonomous incident detection and self-healing
    AI detects and fixes issues without human intervention
    """
    
    service = DevOpsAutopilotService(db)
    
    try:
        healing_event = await service.self_heal_incident(
            resource_id=resource_id,
            incident_type=incident_type,
            symptoms=symptoms
        )
        
        return {
            "success": True,
            "data": {
                "event_id": healing_event.id,
                "incident_type": healing_event.incident_type,
                "severity": healing_event.severity,
                "healing_action_taken": healing_event.healing_action_taken,
                "healing_status": healing_event.healing_status,
                "resolution_time_seconds": healing_event.resolution_time_seconds,
                "ai_confidence_score": healing_event.ai_confidence_score
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/optimize-costs")
async def optimize_costs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-powered cost optimization
    Target: 40-60% cost reduction
    """
    
    service = DevOpsAutopilotService(db)
    
    try:
        recommendations = await service.optimize_costs(
            company_id=current_user.id
        )
        
        total_current_cost = sum(r.current_cost_monthly for r in recommendations)
        total_projected_cost = sum(r.projected_cost_monthly for r in recommendations)
        total_savings = sum(r.savings_monthly for r in recommendations)
        
        return {
            "success": True,
            "data": {
                "total_recommendations": len(recommendations),
                "total_current_cost_monthly": total_current_cost,
                "total_projected_cost_monthly": total_projected_cost,
                "total_savings_monthly": total_savings,
                "savings_percentage": (total_savings / total_current_cost * 100) if total_current_cost > 0 else 0,
                "recommendations": [
                    {
                        "recommendation_id": r.id,
                        "resource_id": r.resource_id,
                        "recommendation_type": r.recommendation_type,
                        "savings_monthly": r.savings_monthly,
                        "savings_percentage": r.savings_percentage,
                        "recommendation_details": r.recommendation_details,
                        "action_required": r.action_required,
                        "priority": r.priority
                    }
                    for r in recommendations
                ]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pipelines")
async def create_pipeline(
    pipeline_name: str,
    repository_url: str,
    branch: str = "main",
    pipeline_config: Optional[Dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create autonomous CI/CD pipeline
    Auto-configures based on repository analysis
    """
    
    service = DevOpsAutopilotService(db)
    
    try:
        pipeline = await service.create_pipeline(
            company_id=current_user.id,
            pipeline_name=pipeline_name,
            repository_url=repository_url,
            branch=branch,
            pipeline_config=pipeline_config
        )
        
        return {
            "success": True,
            "data": {
                "pipeline_id": pipeline.id,
                "pipeline_name": pipeline.pipeline_name,
                "repository_url": pipeline.repository_url,
                "branch": pipeline.branch,
                "stages": pipeline.stages,
                "auto_deploy": pipeline.auto_deploy
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/resources")
async def get_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all infrastructure resources
    """
    
    from models.devops import InfrastructureResource
    
    resources = db.query(InfrastructureResource).filter(
        InfrastructureResource.company_id == current_user.id,
        InfrastructureResource.status == "active"
    ).all()
    
    return {
        "success": True,
        "data": [
            {
                "resource_id": resource.id,
                "resource_type": resource.resource_type,
                "resource_name": resource.resource_name,
                "cloud_provider": resource.cloud_provider,
                "region": resource.region,
                "monthly_cost": resource.monthly_cost,
                "auto_scaling_enabled": resource.auto_scaling_enabled,
                "created_at": resource.created_at
            }
            for resource in resources
        ]
    }


@router.get("/jobs")
async def get_automation_jobs(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get DevOps automation jobs
    """
    
    from models.devops import DevOpsAutomationJob
    
    query = db.query(DevOpsAutomationJob).filter(
        DevOpsAutomationJob.company_id == current_user.id
    )
    
    if status:
        query = query.filter(DevOpsAutomationJob.status == status)
    
    jobs = query.order_by(DevOpsAutomationJob.created_at.desc()).limit(50).all()
    
    return {
        "success": True,
        "data": [
            {
                "job_id": job.id,
                "job_type": job.job_type,
                "status": job.status,
                "target_environment": job.target_environment,
                "estimated_duration_minutes": job.estimated_duration_minutes,
                "actual_duration_minutes": job.actual_duration_minutes,
                "triggered_by_ai": job.triggered_by_ai,
                "created_at": job.created_at,
                "completed_at": job.completed_at
            }
            for job in jobs
        ]
    }


@router.get("/self-healing/events")
async def get_healing_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get self-healing events
    """
    
    from models.devops import SelfHealingEvent, InfrastructureResource
    
    events = db.query(SelfHealingEvent).join(
        InfrastructureResource,
        SelfHealingEvent.resource_id == InfrastructureResource.id
    ).filter(
        InfrastructureResource.company_id == current_user.id
    ).order_by(SelfHealingEvent.detected_at.desc()).limit(50).all()
    
    return {
        "success": True,
        "data": [
            {
                "event_id": event.id,
                "incident_type": event.incident_type,
                "severity": event.severity,
                "healing_action_taken": event.healing_action_taken,
                "healing_status": event.healing_status,
                "resolution_time_seconds": event.resolution_time_seconds,
                "ai_confidence_score": event.ai_confidence_score,
                "detected_at": event.detected_at,
                "resolved_at": event.resolved_at
            }
            for event in events
        ]
    }
