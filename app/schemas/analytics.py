"""Analytics schemas."""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel


class ActivityMetric(BaseModel):
    label: str
    value: int


class DashboardAnalytics(BaseModel):
    totalMembers: int
    activeMembers: int
    newMembersThisMonth: int
    messagesSentThisMonth: int
    averageOpenRate: float
    averageClickRate: float
    automationRulesActive: int
    recentActivities: List[ActivityMetric]
    generatedAt: datetime
