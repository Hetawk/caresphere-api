"""Automation schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AutomationRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    triggerType: str = Field(alias="trigger_type")
    triggerConfig: dict = Field(default_factory=dict, alias="trigger_config")
    actionType: str = Field(alias="action_type")
    actionConfig: dict = Field(default_factory=dict, alias="action_config")
    conditions: dict = Field(default_factory=dict)
    isActive: bool = Field(default=True, alias="is_active")


class AutomationRuleCreate(AutomationRuleBase):
    pass


class AutomationRuleUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    name: Optional[str] = None
    description: Optional[str] = None
    triggerType: Optional[str] = Field(default=None, alias="trigger_type")
    triggerConfig: Optional[dict] = Field(default=None, alias="trigger_config")
    actionType: Optional[str] = Field(default=None, alias="action_type")
    actionConfig: Optional[dict] = Field(default=None, alias="action_config")
    conditions: Optional[dict] = None
    isActive: Optional[bool] = Field(default=None, alias="is_active")


class AutomationRulePublic(AutomationRuleBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    lastRunAt: Optional[datetime] = Field(default=None, alias="last_run_at")
    runCount: int = Field(alias="run_count")
    successCount: int = Field(alias="success_count")
    failureCount: int = Field(alias="failure_count")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")


class AutomationLogPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    status: str
    triggerData: dict = Field(alias="trigger_data")
    actionResult: dict = Field(alias="action_result")
    errorMessage: Optional[str] = Field(default=None, alias="error_message")
    executionTimeMs: Optional[int] = Field(default=None, alias="execution_time_ms")
    executedAt: Optional[datetime] = Field(default=None, alias="executed_at")
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")


class AutomationExecutePayload(BaseModel):
    triggerData: dict = Field(default_factory=dict, alias="trigger_data")