"""
告警服務層
提供告警 CRUD 和通知發送
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
from uuid import uuid4
import json
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
import asyncio

from ..models.alert import (
    Alert, AlertCreate, AlertUpdate, AlertTrigger,
    AlertType, AlertStatus, NotificationChannel
)


class NotificationService:
    """通知服務"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._email_config = self.config.get("email", {})
        self._telegram_token = self.config.get("telegram_token")
    
    async def send_email(
        self, to: str, subject: str, body: str
    ) -> bool:
        """發送郵件"""
        if not self._email_config:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self._email_config.get("from_addr")
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            with smtplib.SMTP(
                self._email_config.get("host"),
                self._email_config.get("port", 587)
            ) as server:
                server.starttls()
                server.login(
                    self._email_config.get("user"),
                    self._email_config.get("password")
                )
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False
    
    async def send_sms(self, phone: str, message: str) -> bool:
        """發送短信（需配置短信服務商）"""
        # TODO: 集成短信服務商 API
        print(f"SMS to {phone}: {message}")
        return False
    
    async def send_webhook(self, url: str, payload: Dict) -> bool:
        """發送 Webhook"""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=10)
                return resp.status_code < 400
        except Exception as e:
            print(f"Webhook send failed: {e}")
            return False
    
    async def send_telegram(
        self, chat_id: str, message: str
    ) -> bool:
        """發送 Telegram 消息"""
        if not self._telegram_token:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self._telegram_token}/sendMessage"
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url,
                    json={"chat_id": chat_id, "text": message},
                    timeout=10
                )
                return resp.status_code < 400
        except Exception as e:
            print(f"Telegram send failed: {e}")
            return False


class AlertService:
    """告警服務"""
    
    def __init__(
        self,
        data_dir: str = "./data/alerts",
        notification_config: Dict = None
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Alert] = {}
        self._trigger_history: List[AlertTrigger] = []
        self._notification = NotificationService(notification_config)
        self._load_all()
    
    def _get_alert_path(self, alert_id: str) -> Path:
        return self.data_dir / f"{alert_id}.json"
    
    def _load_all(self) -> None:
        for file in self.data_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                alert = Alert(**data)
                self._cache[alert.id] = alert
    
    def _save(self, alert: Alert) -> None:
        path = self._get_alert_path(alert.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(alert.model_dump(mode="json"), f, ensure_ascii=False, indent=2, default=str)
        self._cache[alert.id] = alert
    
    def create(self, request: AlertCreate) -> Alert:
        """創建告警"""
        alert = Alert(
            id=str(uuid4()),
            name=request.name,
            alert_type=request.alert_type,
            target_value=request.target_value,
            condition=request.condition,
            asset=request.asset,
            indicator=request.indicator,
            tolerance=request.tolerance,
            channels=request.channels,
            email=request.email,
            phone=request.phone,
            webhook_url=request.webhook_url,
            telegram_chat_id=request.telegram_chat_id,
            expires_at=request.expires_at,
            cooldown_minutes=request.cooldown_minutes,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._save(alert)
        return alert
    
    def get(self, alert_id: str) -> Optional[Alert]:
        return self._cache.get(alert_id)
    
    def list(self, status: AlertStatus = None) -> List[Alert]:
        alerts = list(self._cache.values())
        if status:
            alerts = [a for a in alerts if a.status == status]
        return alerts
    
    def update(self, alert_id: str, request: AlertUpdate) -> Optional[Alert]:
        alert = self.get(alert_id)
        if not alert:
            return None
        
        for field, value in request.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(alert, field, value)
        
        alert.updated_at = datetime.now()
        self._save(alert)
        return alert
    
    def delete(self, alert_id: str) -> bool:
        alert = self.get(alert_id)
        if not alert:
            return False
        
        path = self._get_alert_path(alert_id)
        if path.exists():
            path.unlink()
        del self._cache[alert_id]
        return True
    
    async def check_and_trigger(
        self,
        current_values: Dict[str, float]
    ) -> List[AlertTrigger]:
        """檢查並觸發告警"""
        triggers = []
        now = datetime.now()
        
        for alert in self.list(AlertStatus.ACTIVE):
            # 檢查是否過期
            if alert.expires_at and now > alert.expires_at:
                alert.status = AlertStatus.EXPIRED
                self._save(alert)
                continue
            
            # 檢查冷卻時間
            if alert.last_triggered_at:
                cooldown = timedelta(minutes=alert.cooldown_minutes)
                if now < alert.last_triggered_at + cooldown:
                    continue
            
            # 獲取當前值
            current_value = current_values.get(alert.asset)
            if current_value is None:
                continue
            
            # 檢查條件
            should_trigger = self._check_condition(
                current_value, alert.target_value, alert.condition, alert.tolerance
            )
            
            if should_trigger:
                trigger = await self._trigger_alert(alert, current_value)
                triggers.append(trigger)
        
        return triggers
    
    def _check_condition(
        self, current: float, target: float, condition: str, tolerance: float
    ) -> bool:
        """檢查觸發條件"""
        if condition == "gt":
            return current >= target * (1 - tolerance)
        elif condition == "lt":
            return current <= target * (1 + tolerance)
        elif condition == "eq":
            return abs(current - target) <= target * tolerance
        elif condition in ("cross_up", "cross_down"):
            # 需要歷史數據支持
            return False
        return False
    
    async def _trigger_alert(
        self, alert: Alert, current_value: float
    ) -> AlertTrigger:
        """觸發告警並發送通知"""
        now = datetime.now()
        deviation = abs(current_value - alert.target_value) / alert.target_value * 100
        
        trigger = AlertTrigger(
            alert_id=alert.id,
            triggered_at=now,
            trigger_value=current_value,
            target_value=alert.target_value,
            deviation=deviation
        )
        
        # 發送通知
        message = self._format_message(alert, current_value)
        channels_used = []
        
        for channel in alert.channels:
            success = False
            if channel == NotificationChannel.EMAIL and alert.email:
                success = await self._notification.send_email(
                    alert.email,
                    f"[告警] {alert.name}",
                    message
                )
            elif channel == NotificationChannel.SMS and alert.phone:
                success = await self._notification.send_sms(alert.phone, message)
            elif channel == NotificationChannel.WEBHOOK and alert.webhook_url:
                success = await self._notification.send_webhook(
                    alert.webhook_url,
                    {"alert_id": alert.id, "message": message, "value": current_value}
                )
            elif channel == NotificationChannel.TELEGRAM and alert.telegram_chat_id:
                success = await self._notification.send_telegram(
                    alert.telegram_chat_id, message
                )
            elif channel == NotificationChannel.PUSH:
                # TODO: 集成推送服務
                pass
            
            if success:
                channels_used.append(channel)
        
        trigger.channels_used = channels_used
        trigger.notification_sent = len(channels_used) > 0
        
        # 更新告警狀態
        alert.last_triggered_at = now
        alert.trigger_count += 1
        alert.updated_at = now
        self._save(alert)
        
        self._trigger_history.append(trigger)
        return trigger
    
    def _format_message(self, alert: Alert, current_value: float) -> str:
        """格式化通知消息"""
        action = "高於" if alert.condition == "gt" else "低於"
        return (
            f"📊 告警觸發: {alert.name}\n"
            f"當前價格: {current_value:.2f}\n"
            f"目標價格: {alert.target_value:.2f}\n"
            f"狀態: 價格已{action}目標"
        )
