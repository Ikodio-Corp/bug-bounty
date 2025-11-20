from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from models.user import User
from core.redis import get_redis
import json
import hashlib

class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.redis = get_redis()
    
    async def log_event(
        self,
        user_id: Optional[int],
        event_type: str,
        resource_type: str,
        resource_id: Optional[str],
        action: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        event = {
            "id": self._generate_event_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "details": details or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "status": status,
            "error_message": error_message
        }
        
        await self._store_event(event)
        await self._update_statistics(event)
        await self._check_anomalies(event)
        
        return event
    
    async def log_authentication(
        self,
        user_id: Optional[int],
        username: str,
        action: str,
        success: bool,
        method: str,
        ip_address: str,
        user_agent: str,
        details: Optional[Dict[str, Any]] = None
    ):
        return await self.log_event(
            user_id=user_id,
            event_type="authentication",
            resource_type="user",
            resource_id=str(user_id) if user_id else None,
            action=action,
            details={
                "username": username,
                "method": method,
                **(details or {})
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if success else "failure"
        )
    
    async def log_data_access(
        self,
        user_id: int,
        resource_type: str,
        resource_id: str,
        action: str,
        fields_accessed: Optional[List[str]] = None,
        ip_address: Optional[str] = None
    ):
        return await self.log_event(
            user_id=user_id,
            event_type="data_access",
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details={
                "fields_accessed": fields_accessed or []
            },
            ip_address=ip_address
        )
    
    async def log_data_modification(
        self,
        user_id: int,
        resource_type: str,
        resource_id: str,
        action: str,
        changes: Dict[str, Any],
        ip_address: Optional[str] = None
    ):
        sanitized_changes = self._sanitize_changes(changes)
        
        return await self.log_event(
            user_id=user_id,
            event_type="data_modification",
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details={
                "changes": sanitized_changes
            },
            ip_address=ip_address
        )
    
    async def log_security_event(
        self,
        user_id: Optional[int],
        event_type: str,
        severity: str,
        description: str,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        return await self.log_event(
            user_id=user_id,
            event_type="security",
            resource_type="system",
            resource_id=None,
            action=event_type,
            details={
                "severity": severity,
                "description": description,
                **(details or {})
            },
            ip_address=ip_address,
            status="alert"
        )
    
    async def log_api_call(
        self,
        user_id: Optional[int],
        method: str,
        path: str,
        status_code: int,
        response_time: float,
        ip_address: str,
        user_agent: str
    ):
        return await self.log_event(
            user_id=user_id,
            event_type="api_call",
            resource_type="api",
            resource_id=path,
            action=method,
            details={
                "status_code": status_code,
                "response_time_ms": response_time * 1000
            },
            ip_address=ip_address,
            user_agent=user_agent,
            status="success" if status_code < 400 else "failure"
        )
    
    async def get_user_activity(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        cache_key = f"audit:user:{user_id}:activity"
        
        cached = await self.redis.get(cache_key)
        if cached and not start_date and not end_date and not event_types:
            return json.loads(cached)
        
        pattern = f"audit:events:{user_id}:*"
        keys = await self.redis.keys(pattern)
        
        events = []
        for key in keys[-limit:]:
            event_data = await self.redis.get(key)
            if event_data:
                event = json.loads(event_data)
                
                if start_date and datetime.fromisoformat(event["timestamp"]) < start_date:
                    continue
                if end_date and datetime.fromisoformat(event["timestamp"]) > end_date:
                    continue
                if event_types and event["event_type"] not in event_types:
                    continue
                
                events.append(event)
        
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        
        await self.redis.setex(cache_key, 300, json.dumps(events[:limit]))
        
        return events[:limit]
    
    async def get_security_events(
        self,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        pattern = "audit:events:*:security:*"
        keys = await self.redis.keys(pattern)
        
        events = []
        for key in keys[-limit:]:
            event_data = await self.redis.get(key)
            if event_data:
                event = json.loads(event_data)
                
                if severity and event["details"].get("severity") != severity:
                    continue
                
                events.append(event)
        
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        return events[:limit]
    
    async def get_failed_login_attempts(
        self,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        pattern = "audit:events:*:authentication:*"
        keys = await self.redis.keys(pattern)
        
        events = []
        for key in keys:
            event_data = await self.redis.get(key)
            if event_data:
                event = json.loads(event_data)
                
                if event["status"] != "failure":
                    continue
                if event["action"] not in ["login", "login_attempt"]:
                    continue
                if username and event["details"].get("username") != username:
                    continue
                if ip_address and event["ip_address"] != ip_address:
                    continue
                if since and datetime.fromisoformat(event["timestamp"]) < since:
                    continue
                
                events.append(event)
        
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        return events
    
    async def get_statistics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        stats_key = f"audit:stats:{start_date.date()}:{end_date.date()}"
        
        cached = await self.redis.get(stats_key)
        if cached:
            return json.loads(cached)
        
        stats = {
            "total_events": 0,
            "by_type": {},
            "by_status": {},
            "unique_users": set(),
            "unique_ips": set(),
            "failed_logins": 0,
            "security_alerts": 0,
            "api_calls": 0
        }
        
        pattern = "audit:events:*"
        keys = await self.redis.keys(pattern)
        
        for key in keys:
            event_data = await self.redis.get(key)
            if event_data:
                event = json.loads(event_data)
                event_time = datetime.fromisoformat(event["timestamp"])
                
                if start_date <= event_time <= end_date:
                    stats["total_events"] += 1
                    
                    event_type = event["event_type"]
                    stats["by_type"][event_type] = stats["by_type"].get(event_type, 0) + 1
                    
                    status = event["status"]
                    stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                    
                    if event["user_id"]:
                        stats["unique_users"].add(event["user_id"])
                    
                    if event["ip_address"]:
                        stats["unique_ips"].add(event["ip_address"])
                    
                    if event["event_type"] == "authentication" and event["status"] == "failure":
                        stats["failed_logins"] += 1
                    
                    if event["event_type"] == "security":
                        stats["security_alerts"] += 1
                    
                    if event["event_type"] == "api_call":
                        stats["api_calls"] += 1
        
        stats["unique_users"] = len(stats["unique_users"])
        stats["unique_ips"] = len(stats["unique_ips"])
        
        await self.redis.setex(stats_key, 3600, json.dumps(stats))
        
        return stats
    
    async def export_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = "json"
    ) -> str:
        pattern = "audit:events:*"
        keys = await self.redis.keys(pattern)
        
        events = []
        for key in keys:
            event_data = await self.redis.get(key)
            if event_data:
                event = json.loads(event_data)
                event_time = datetime.fromisoformat(event["timestamp"])
                
                if start_date <= event_time <= end_date:
                    events.append(event)
        
        events.sort(key=lambda x: x["timestamp"])
        
        if format == "json":
            return json.dumps(events, indent=2)
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            if events:
                fieldnames = ["timestamp", "user_id", "event_type", "resource_type", 
                             "resource_id", "action", "status", "ip_address"]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for event in events:
                    writer.writerow({
                        k: event.get(k, "") for k in fieldnames
                    })
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_event_id(self) -> str:
        import uuid
        return str(uuid.uuid4())
    
    async def _store_event(self, event: Dict[str, Any]):
        user_id = event["user_id"] or "anonymous"
        event_type = event["event_type"]
        event_id = event["id"]
        
        key = f"audit:events:{user_id}:{event_type}:{event_id}"
        await self.redis.setex(key, 2592000, json.dumps(event))
        
        timeline_key = f"audit:timeline:{event['timestamp'][:10]}"
        await self.redis.zadd(timeline_key, {event_id: datetime.fromisoformat(event["timestamp"]).timestamp()})
        await self.redis.expire(timeline_key, 2592000)
    
    async def _update_statistics(self, event: Dict[str, Any]):
        date_key = event["timestamp"][:10]
        
        await self.redis.hincrby(f"audit:stats:{date_key}", "total_events", 1)
        await self.redis.hincrby(f"audit:stats:{date_key}", f"type:{event['event_type']}", 1)
        await self.redis.hincrby(f"audit:stats:{date_key}", f"status:{event['status']}", 1)
        
        await self.redis.expire(f"audit:stats:{date_key}", 2592000)
    
    async def _check_anomalies(self, event: Dict[str, Any]):
        if event["event_type"] == "authentication" and event["status"] == "failure":
            key = f"failed_logins:{event['ip_address']}"
            count = await self.redis.incr(key)
            await self.redis.expire(key, 3600)
            
            if count >= 5:
                await self.log_security_event(
                    user_id=event["user_id"],
                    event_type="brute_force_attempt",
                    severity="high",
                    description=f"Multiple failed login attempts from IP {event['ip_address']}",
                    ip_address=event["ip_address"],
                    details={"failed_attempts": count}
                )
        
        if event["event_type"] == "data_access":
            key = f"data_access:{event['user_id']}:{event['resource_type']}"
            count = await self.redis.incr(key)
            await self.redis.expire(key, 60)
            
            if count >= 100:
                await self.log_security_event(
                    user_id=event["user_id"],
                    event_type="excessive_data_access",
                    severity="medium",
                    description=f"User accessing {event['resource_type']} excessively",
                    details={"access_count": count}
                )
    
    def _sanitize_changes(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        sensitive_fields = ["password", "token", "secret", "api_key", "private_key"]
        
        sanitized = {}
        for key, value in changes.items():
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        
        return sanitized
