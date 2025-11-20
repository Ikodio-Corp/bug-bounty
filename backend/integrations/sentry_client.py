from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
import os

router = APIRouter()

class SentryService:
    def __init__(self):
        self.initialized = False
        self.dsn = os.getenv("SENTRY_DSN")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.release = os.getenv("RELEASE_VERSION", "unknown")
        
    def initialize(self):
        if not self.dsn:
            logging.warning("Sentry DSN not configured, skipping initialization")
            return
            
        sentry_sdk.init(
            dsn=self.dsn,
            environment=self.environment,
            release=self.release,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
                CeleryIntegration(),
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR
                )
            ],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
            before_send=self.before_send,
            before_breadcrumb=self.before_breadcrumb,
            send_default_pii=False,
            attach_stacktrace=True,
            max_breadcrumbs=50,
        )
        
        self.initialized = True
        logging.info(f"Sentry initialized for environment: {self.environment}, release: {self.release}")
    
    def before_send(self, event, hint):
        if "exc_info" in hint:
            exc_type, exc_value, tb = hint["exc_info"]
            if isinstance(exc_value, HTTPException):
                if exc_value.status_code < 500:
                    return None
        return event
    
    def before_breadcrumb(self, crumb, hint):
        if crumb.get("category") == "query":
            query = crumb.get("message", "")
            if "password" in query.lower() or "token" in query.lower():
                crumb["message"] = "REDACTED SQL QUERY"
        return crumb
    
    def set_user(self, user: User):
        if not self.initialized:
            return
            
        sentry_sdk.set_user({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "subscription_tier": user.subscription_tier,
        })
    
    def set_context(self, name: str, context: Dict[str, Any]):
        if not self.initialized:
            return
        sentry_sdk.set_context(name, context)
    
    def add_breadcrumb(
        self,
        message: str,
        category: str,
        level: str = "info",
        data: Optional[Dict[str, Any]] = None
    ):
        if not self.initialized:
            return
            
        sentry_sdk.add_breadcrumb({
            "message": message,
            "category": category,
            "level": level,
            "data": data or {}
        })
    
    def capture_exception(
        self,
        error: Exception,
        contexts: Optional[Dict[str, Dict[str, Any]]] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        if not self.initialized:
            logging.error(f"Error (Sentry not initialized): {str(error)}")
            return None
            
        with sentry_sdk.push_scope() as scope:
            if contexts:
                for name, context in contexts.items():
                    scope.set_context(name, context)
            
            if tags:
                for key, value in tags.items():
                    scope.set_tag(key, value)
            
            return sentry_sdk.capture_exception(error)
    
    def capture_message(
        self,
        message: str,
        level: str = "info",
        contexts: Optional[Dict[str, Dict[str, Any]]] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        if not self.initialized:
            logging.info(f"Message (Sentry not initialized): {message}")
            return None
            
        with sentry_sdk.push_scope() as scope:
            if contexts:
                for name, context in contexts.items():
                    scope.set_context(name, context)
            
            if tags:
                for key, value in tags.items():
                    scope.set_tag(key, value)
            
            return sentry_sdk.capture_message(message, level)
    
    def start_transaction(self, name: str, op: str):
        if not self.initialized:
            return DummyTransaction()
        return sentry_sdk.start_transaction(name=name, op=op)
    
    def start_span(self, op: str, description: Optional[str] = None):
        if not self.initialized:
            return DummySpan()
        return sentry_sdk.start_span(op=op, description=description)

class DummyTransaction:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def start_child(self, op: str, description: Optional[str] = None):
        return DummySpan()

class DummySpan:
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

sentry_service = SentryService()

@router.post("/sentry/test-error")
async def test_error(current_user: User = Depends(get_current_user)):
    sentry_service.set_user(current_user)
    sentry_service.add_breadcrumb(
        message="User requested test error",
        category="test",
        level="info"
    )
    raise Exception("This is a test error for Sentry")

@router.post("/sentry/test-message")
async def test_message(current_user: User = Depends(get_current_user)):
    sentry_service.set_user(current_user)
    event_id = sentry_service.capture_message(
        "Test message from IKODIO BugBounty",
        level="info",
        tags={"test": "true"},
        contexts={"user_action": {"action": "test_message"}}
    )
    return {"event_id": event_id}

@router.post("/sentry/test-transaction")
async def test_transaction(current_user: User = Depends(get_current_user)):
    sentry_service.set_user(current_user)
    
    with sentry_service.start_transaction(name="test_transaction", op="test") as transaction:
        with sentry_service.start_span(op="db.query", description="Fetch user data"):
            await asyncio.sleep(0.1)
        
        with sentry_service.start_span(op="http.client", description="External API call"):
            await asyncio.sleep(0.2)
    
    return {"message": "Transaction completed"}

@router.get("/sentry/health")
async def sentry_health():
    return {
        "initialized": sentry_service.initialized,
        "environment": sentry_service.environment,
        "release": sentry_service.release,
        "dsn_configured": bool(sentry_service.dsn)
    }

@router.post("/sentry/capture-feedback")
async def capture_feedback(
    feedback: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    sentry_service.set_user(current_user)
    event_id = sentry_service.capture_message(
        f"User feedback: {feedback.get('message', 'No message')}",
        level="info",
        tags={"type": "user_feedback"},
        contexts={
            "feedback": {
                "rating": feedback.get("rating"),
                "category": feedback.get("category"),
                "message": feedback.get("message")
            }
        }
    )
    return {"event_id": event_id}

import asyncio
