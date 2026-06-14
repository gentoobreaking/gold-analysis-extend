"""
告警系統數據模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4


class AlertType(str, Enum):
    """告警類型"""
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    INDICATOR_CROSS = "indicator_cross"
    SIGNAL_ALERT = "signal_alert"
    PERFORMANCE = "performance"


class AlertStatus(str, Enum):
    """告警狀態"""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    DISABLED = "disabled"
    EXPIRED = "expired"


class NotificationChannel(str, Enum):
    """通知渠道"""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    TELEGRAM = "telegram"


class Alert(BaseModel):
    """告警"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    alert_type: AlertType
    status: AlertStatus = AlertStatus.ACTIVE
    
    # 觸發條件
    target_value: float = Field(..., description="目標值（價格/指標值）")
    condition: str = Field(default="gt", description="條件：gt, lt, eq, cross_up, cross_down")
    
    # 可選參數
    asset: Optional[str] = Field(default="gold_spot", description="監控資產")
    indicator: Optional[str] = Field(default=None, description="指標名稱")
    tolerance: float = Field(default=0.01, description="容差（百分比）")
    
    # 通知設置
    channels: List[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.PUSH])
    email: Optional[str] = None
    phone: Optional[str] = None
    webhook_url: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # 時間設置
    expires_at: Optional[datetime] = None
    cooldown_minutes: int = Field(default=60, description="觸發後冷卻時間（分鐘）")
    last_triggered_at: Optional[datetime] = None
    
    # 元數據
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    trigger_count: int = Field(default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AlertCreate(BaseModel):
    """創建告警請求"""
    name: str = Field(..., min_length=1, max_length=100)
    alert_type: AlertType
    target_value: float
    condition: str = "gt"
    asset: str = "gold_spot"
    indicator: Optional[str] = None
    tolerance: float = 0.01
    channels: List[NotificationChannel] = ["push"]
    email: Optional[str] = None
    phone: Optional[str] = None
    webhook_url: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    expires_at: Optional[datetime] = None
    cooldown_minutes: int = 60


class AlertUpdate(BaseModel):
    """更新告警請求"""
    name: Optional[str] = None
    target_value: Optional[float] = None
    condition: Optional[str] = None
    tolerance: Optional[float] = None
    channels: Optional[List[NotificationChannel]] = None
    status: Optional[AlertStatus] = None
    expires_at: Optional[datetime] = None
    cooldown_minutes: Optional[int] = None


class AlertTrigger(BaseModel):
    """告警觸發記錄"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    alert_id: str
    triggered_at: datetime = Field(default_factory=datetime.now)
    trigger_value: float
    target_value: float
    deviation: float
    notification_sent: bool = False
    channels_used: List[NotificationChannel] = []
