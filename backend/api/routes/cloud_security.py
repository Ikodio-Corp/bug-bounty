"""
Cloud Provider Security Integration
AWS Security Hub, GCP Security Command Center, Azure Defender
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import httpx
from datetime import datetime
import boto3
from google.cloud import securitycenter
from azure.identity import ClientSecretCredential
from azure.mgmt.security import SecurityCenter

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.bug import Bug
from sqlalchemy import select

router = APIRouter(prefix="/cloud-security", tags=["Cloud Security Integration"])


class AWSConfig(BaseModel):
    """AWS Security Hub configuration"""
    access_key_id: str
    secret_access_key: str
    region: str
    account_id: str


class GCPConfig(BaseModel):
    """GCP Security Command Center configuration"""
    project_id: str
    organization_id: str
    service_account_key: Dict[str, Any]


class AzureConfig(BaseModel):
    """Azure Defender configuration"""
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_id: str


class ImportFindingsRequest(BaseModel):
    """Request to import findings from cloud provider"""
    provider: str
    auto_create_bugs: bool = True


class ExportBugRequest(BaseModel):
    """Request to export bug to cloud provider"""
    bug_id: int
    provider: str
    severity_override: Optional[str] = None


class AWSSecurityHubClient:
    """AWS Security Hub client"""
    
    def __init__(self, access_key_id: str, secret_access_key: str, region: str):
        self.client = boto3.client(
            'securityhub',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
        self.region = region
    
    def get_findings(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get findings from Security Hub"""
        try:
            params = {}
            if filters:
                params['Filters'] = filters
            
            response = self.client.get_findings(**params)
            return response.get('Findings', [])
        except Exception as e:
            raise Exception(f"Failed to get AWS findings: {str(e)}")
    
    def import_finding(self, finding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import finding to Security Hub"""
        try:
            response = self.client.batch_import_findings(
                Findings=[finding_data]
            )
            return response
        except Exception as e:
            raise Exception(f"Failed to import AWS finding: {str(e)}")
    
    def update_finding(self, finding_id: str, product_arn: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update finding in Security Hub"""
        try:
            response = self.client.batch_update_findings(
                FindingIdentifiers=[{
                    'Id': finding_id,
                    'ProductArn': product_arn
                }],
                **updates
            )
            return response
        except Exception as e:
            raise Exception(f"Failed to update AWS finding: {str(e)}")


class GCPSecurityCenterClient:
    """GCP Security Command Center client"""
    
    def __init__(self, organization_id: str):
        self.client = securitycenter.SecurityCenterClient()
        self.organization_id = organization_id
        self.org_name = f"organizations/{organization_id}"
    
    def list_findings(self, source_name: str = None) -> List[Any]:
        """List findings from Security Command Center"""
        try:
            if source_name:
                parent = f"{self.org_name}/sources/{source_name}"
            else:
                parent = self.org_name
            
            findings = []
            for finding in self.client.list_findings(request={"parent": parent}):
                findings.append(finding)
            return findings
        except Exception as e:
            raise Exception(f"Failed to list GCP findings: {str(e)}")
    
    def create_finding(self, source_id: str, finding_id: str, finding_data: Dict[str, Any]) -> Any:
        """Create finding in Security Command Center"""
        try:
            source_name = f"{self.org_name}/sources/{source_id}"
            finding_name = f"{source_name}/findings/{finding_id}"
            
            finding = self.client.create_finding(
                request={
                    "parent": source_name,
                    "finding_id": finding_id,
                    "finding": finding_data
                }
            )
            return finding
        except Exception as e:
            raise Exception(f"Failed to create GCP finding: {str(e)}")
    
    def update_finding(self, finding_name: str, updates: Dict[str, Any]) -> Any:
        """Update finding in Security Command Center"""
        try:
            finding = self.client.update_finding(
                request={
                    "finding": updates
                }
            )
            return finding
        except Exception as e:
            raise Exception(f"Failed to update GCP finding: {str(e)}")


class AzureDefenderClient:
    """Azure Defender client"""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, subscription_id: str):
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        self.client = SecurityCenter(credential, subscription_id)
        self.subscription_id = subscription_id
    
    def list_alerts(self) -> List[Any]:
        """List alerts from Azure Defender"""
        try:
            alerts = []
            for alert in self.client.alerts.list():
                alerts.append(alert)
            return alerts
        except Exception as e:
            raise Exception(f"Failed to list Azure alerts: {str(e)}")
    
    def get_alert(self, resource_group: str, alert_name: str) -> Any:
        """Get specific alert"""
        try:
            alert = self.client.alerts.get_resource_group_level(
                resource_group_name=resource_group,
                alert_name=alert_name
            )
            return alert
        except Exception as e:
            raise Exception(f"Failed to get Azure alert: {str(e)}")
    
    def update_alert_state(self, resource_group: str, alert_name: str, state: str) -> Any:
        """Update alert state"""
        try:
            alert = self.client.alerts.update_resource_group_level_state(
                resource_group_name=resource_group,
                alert_name=alert_name,
                alert_update_action_type=state
            )
            return alert
        except Exception as e:
            raise Exception(f"Failed to update Azure alert: {str(e)}")


@router.post("/aws/configure")
async def configure_aws(
    config: AWSConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure AWS Security Hub integration
    
    Args:
        config: AWS configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Test connection
        client = AWSSecurityHubClient(
            access_key_id=config.access_key_id,
            secret_access_key=config.secret_access_key,
            region=config.region
        )
        
        # Store configuration (encrypt in production)
        current_user.aws_access_key_id = config.access_key_id
        current_user.aws_secret_access_key = config.secret_access_key
        current_user.aws_region = config.region
        current_user.aws_account_id = config.account_id
        
        await db.commit()
        
        return {
            "status": "configured",
            "provider": "aws",
            "region": config.region,
            "account_id": config.account_id,
            "message": "AWS Security Hub configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"AWS configuration failed: {str(e)}"
        )


@router.post("/aws/import-findings")
async def import_aws_findings(
    request: ImportFindingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Import findings from AWS Security Hub
    
    Args:
        request: Import request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Import status with findings count
    """
    try:
        if not current_user.aws_access_key_id:
            raise HTTPException(
                status_code=400,
                detail="AWS not configured"
            )
        
        client = AWSSecurityHubClient(
            access_key_id=current_user.aws_access_key_id,
            secret_access_key=current_user.aws_secret_access_key,
            region=current_user.aws_region
        )
        
        # Get findings
        findings = client.get_findings({
            'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
        })
        
        imported_count = 0
        created_bugs = []
        
        if request.auto_create_bugs:
            for finding in findings:
                # Map AWS severity to our severity
                severity_map = {
                    'CRITICAL': 'critical',
                    'HIGH': 'high',
                    'MEDIUM': 'medium',
                    'LOW': 'low',
                    'INFORMATIONAL': 'info'
                }
                
                aws_severity = finding.get('Severity', {}).get('Label', 'MEDIUM')
                our_severity = severity_map.get(aws_severity, 'medium')
                
                # Create bug from finding
                bug = Bug(
                    hunter_id=current_user.id,
                    title=finding.get('Title', 'AWS Security Hub Finding'),
                    description=finding.get('Description', ''),
                    bug_type='cloud_misconfiguration',
                    severity=our_severity,
                    target_url=finding.get('Resources', [{}])[0].get('Id', 'N/A'),
                    target_domain='aws',
                    cloud_provider='aws',
                    cloud_finding_id=finding.get('Id'),
                    cloud_finding_arn=finding.get('ProductArn'),
                    imported_at=datetime.utcnow()
                )
                
                db.add(bug)
                created_bugs.append({
                    'title': bug.title,
                    'severity': bug.severity,
                    'finding_id': finding.get('Id')
                })
                imported_count += 1
        
        await db.commit()
        
        return {
            "status": "imported",
            "provider": "aws",
            "total_findings": len(findings),
            "imported_count": imported_count,
            "created_bugs": created_bugs[:10],
            "message": f"Imported {imported_count} findings from AWS Security Hub"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"AWS import failed: {str(e)}"
        )


@router.post("/aws/export-bug")
async def export_bug_to_aws(
    request: ExportBugRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export bug to AWS Security Hub
    
    Args:
        request: Export request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Export status
    """
    try:
        result = await db.execute(
            select(Bug).where(Bug.id == request.bug_id)
        )
        bug = result.scalar_one_or_none()
        
        if not bug:
            raise HTTPException(status_code=404, detail="Bug not found")
        
        if not current_user.aws_access_key_id:
            raise HTTPException(
                status_code=400,
                detail="AWS not configured"
            )
        
        client = AWSSecurityHubClient(
            access_key_id=current_user.aws_access_key_id,
            secret_access_key=current_user.aws_secret_access_key,
            region=current_user.aws_region
        )
        
        # Map severity
        severity_map = {
            'critical': 'CRITICAL',
            'high': 'HIGH',
            'medium': 'MEDIUM',
            'low': 'LOW',
            'info': 'INFORMATIONAL'
        }
        
        severity = request.severity_override or bug.severity
        aws_severity = severity_map.get(severity, 'MEDIUM')
        
        # Create finding data
        finding_data = {
            'SchemaVersion': '2018-10-08',
            'Id': f"ikodio-bug-{bug.id}",
            'ProductArn': f"arn:aws:securityhub:{current_user.aws_region}:{current_user.aws_account_id}:product/{current_user.aws_account_id}/default",
            'GeneratorId': 'ikodio-bugbounty',
            'AwsAccountId': current_user.aws_account_id,
            'Types': ['Software and Configuration Checks/Vulnerabilities'],
            'CreatedAt': bug.created_at.isoformat(),
            'UpdatedAt': datetime.utcnow().isoformat(),
            'Severity': {
                'Label': aws_severity,
                'Normalized': {'critical': 90, 'high': 70, 'medium': 50, 'low': 30, 'info': 10}.get(severity, 50)
            },
            'Title': bug.title,
            'Description': bug.description or '',
            'Resources': [{
                'Type': 'Other',
                'Id': bug.target_url
            }]
        }
        
        # Import to Security Hub
        response = client.import_finding(finding_data)
        
        # Update bug
        bug.cloud_provider = 'aws'
        bug.cloud_finding_id = finding_data['Id']
        bug.exported_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "status": "exported",
            "provider": "aws",
            "bug_id": request.bug_id,
            "finding_id": finding_data['Id'],
            "message": "Bug exported to AWS Security Hub successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"AWS export failed: {str(e)}"
        )


@router.post("/gcp/configure")
async def configure_gcp(
    config: GCPConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure GCP Security Command Center integration
    
    Args:
        config: GCP configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Store configuration
        current_user.gcp_project_id = config.project_id
        current_user.gcp_organization_id = config.organization_id
        current_user.gcp_service_account_key = config.service_account_key
        
        await db.commit()
        
        return {
            "status": "configured",
            "provider": "gcp",
            "project_id": config.project_id,
            "organization_id": config.organization_id,
            "message": "GCP Security Command Center configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"GCP configuration failed: {str(e)}"
        )


@router.post("/gcp/import-findings")
async def import_gcp_findings(
    request: ImportFindingsRequest,
    source_id: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Import findings from GCP Security Command Center
    
    Args:
        request: Import request
        source_id: GCP source ID
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Import status with findings count
    """
    try:
        if not current_user.gcp_organization_id:
            raise HTTPException(
                status_code=400,
                detail="GCP not configured"
            )
        
        client = GCPSecurityCenterClient(
            organization_id=current_user.gcp_organization_id
        )
        
        findings = client.list_findings(source_name=source_id)
        
        imported_count = 0
        created_bugs = []
        
        if request.auto_create_bugs:
            for finding in findings:
                severity_map = {
                    'CRITICAL': 'critical',
                    'HIGH': 'high',
                    'MEDIUM': 'medium',
                    'LOW': 'low'
                }
                
                gcp_severity = finding.severity
                our_severity = severity_map.get(gcp_severity, 'medium')
                
                bug = Bug(
                    hunter_id=current_user.id,
                    title=finding.category,
                    description=finding.finding_class or '',
                    bug_type='cloud_misconfiguration',
                    severity=our_severity,
                    target_url=finding.resource_name,
                    target_domain='gcp',
                    cloud_provider='gcp',
                    cloud_finding_id=finding.name,
                    imported_at=datetime.utcnow()
                )
                
                db.add(bug)
                created_bugs.append({
                    'title': bug.title,
                    'severity': bug.severity,
                    'finding_id': finding.name
                })
                imported_count += 1
        
        await db.commit()
        
        return {
            "status": "imported",
            "provider": "gcp",
            "total_findings": len(findings),
            "imported_count": imported_count,
            "created_bugs": created_bugs[:10],
            "message": f"Imported {imported_count} findings from GCP Security Command Center"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"GCP import failed: {str(e)}"
        )


@router.post("/azure/configure")
async def configure_azure(
    config: AzureConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Azure Defender integration
    
    Args:
        config: Azure configuration
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Configuration status
    """
    try:
        # Store configuration
        current_user.azure_tenant_id = config.tenant_id
        current_user.azure_client_id = config.client_id
        current_user.azure_client_secret = config.client_secret
        current_user.azure_subscription_id = config.subscription_id
        
        await db.commit()
        
        return {
            "status": "configured",
            "provider": "azure",
            "tenant_id": config.tenant_id,
            "subscription_id": config.subscription_id,
            "message": "Azure Defender configured successfully"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Azure configuration failed: {str(e)}"
        )


@router.post("/azure/import-alerts")
async def import_azure_alerts(
    request: ImportFindingsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Import alerts from Azure Defender
    
    Args:
        request: Import request
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Import status with alerts count
    """
    try:
        if not current_user.azure_tenant_id:
            raise HTTPException(
                status_code=400,
                detail="Azure not configured"
            )
        
        client = AzureDefenderClient(
            tenant_id=current_user.azure_tenant_id,
            client_id=current_user.azure_client_id,
            client_secret=current_user.azure_client_secret,
            subscription_id=current_user.azure_subscription_id
        )
        
        alerts = client.list_alerts()
        
        imported_count = 0
        created_bugs = []
        
        if request.auto_create_bugs:
            for alert in alerts:
                severity_map = {
                    'High': 'high',
                    'Medium': 'medium',
                    'Low': 'low',
                    'Informational': 'info'
                }
                
                azure_severity = alert.properties.severity
                our_severity = severity_map.get(azure_severity, 'medium')
                
                bug = Bug(
                    hunter_id=current_user.id,
                    title=alert.properties.alert_display_name,
                    description=alert.properties.description or '',
                    bug_type='cloud_misconfiguration',
                    severity=our_severity,
                    target_url=alert.properties.compromised_entity or 'N/A',
                    target_domain='azure',
                    cloud_provider='azure',
                    cloud_finding_id=alert.name,
                    imported_at=datetime.utcnow()
                )
                
                db.add(bug)
                created_bugs.append({
                    'title': bug.title,
                    'severity': bug.severity,
                    'alert_id': alert.name
                })
                imported_count += 1
        
        await db.commit()
        
        return {
            "status": "imported",
            "provider": "azure",
            "total_alerts": len(alerts),
            "imported_count": imported_count,
            "created_bugs": created_bugs[:10],
            "message": f"Imported {imported_count} alerts from Azure Defender"
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Azure import failed: {str(e)}"
        )


@router.get("/status")
async def get_cloud_integration_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cloud integration status for all providers
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Integration status for all cloud providers
    """
    try:
        status = {
            "aws": {
                "configured": current_user.aws_access_key_id is not None,
                "region": current_user.aws_region,
                "account_id": current_user.aws_account_id
            },
            "gcp": {
                "configured": current_user.gcp_organization_id is not None,
                "project_id": current_user.gcp_project_id,
                "organization_id": current_user.gcp_organization_id
            },
            "azure": {
                "configured": current_user.azure_tenant_id is not None,
                "tenant_id": current_user.azure_tenant_id,
                "subscription_id": current_user.azure_subscription_id
            }
        }
        
        # Get import statistics
        result = await db.execute(
            select(Bug).where(
                Bug.hunter_id == current_user.id,
                Bug.cloud_provider.isnot(None)
            )
        )
        cloud_bugs = result.scalars().all()
        
        stats = {
            "total_imported": len(cloud_bugs),
            "by_provider": {
                "aws": len([b for b in cloud_bugs if b.cloud_provider == 'aws']),
                "gcp": len([b for b in cloud_bugs if b.cloud_provider == 'gcp']),
                "azure": len([b for b in cloud_bugs if b.cloud_provider == 'azure'])
            }
        }
        
        return {
            "status": status,
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )
