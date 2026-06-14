# 告警通知系統

## 概述

告警系統提供多種類型的價格和指標告警，支持多渠道通知。

## 告警類型

| 類型 | 代碼 | 觸發條件 |
|------|------|---------|
| 價格高於 | price_above | 當前價格 > 目標價格 |
| 價格低於 | price_below | 當前價格 < 目標價格 |
| 指標交叉 | indicator_cross | 技術指標發生交叉 |
| 交易信號 | signal_trigger | 系統發出交易信號 |

## 通知渠道

| 渠道 | 代碼 | 配置方式 |
|------|------|---------|
| Email | Email | 配置 SMTP |
| SMS | SMS | 配置簡訊服務 |
| Telegram | Telegram | 配置 Bot Token |
| Webhook | Webhook | 配置回調 URL |

## API 端點

### 創建告警

```http
POST /alerts
Content-Type: application/json

{
  "type": "price_above",
  "target_price": 4900,
  "channels": ["telegram", "email"]
}
```

### 列出告警

```http
GET /alerts
```

### 更新告警

```http
PATCH /alerts/{id}
Content-Type: application/json

{
  "target_price": 4950,
  "status": "active"
}
```

## 狀態說明

| 狀態 | 描述 |
|------|------|
| active | 告警啟用中 |
| triggered | 告警已觸發 |
| disabled | 告警已停用 |

## 模板配置

告警通知模板支持變量替換：

```
🔔 價格告警觸發
類型: {{alert_type}}
目標價格: {{target_price}}
當前價格: {{current_price}}
時間: {{timestamp}}
```

## 相關模塊

- [投資組合](./portfolio.md) - 持倉告警
- [回測系統](./backtest.md) - 回測告警
