# 決策回測系統

## 概述

回測系統用於驗證歷史決策的績效，計算風險指標和收益分析。

## 核心功能

### 1. 回測配置

| 參數 | 類型 | 描述 |
|------|------|------|
| start_date | date | 回測起始日期 |
| end_date | date | 回測結束日期 |
| initial_capital | float | 初始資金 |
| commission_rate | float | 手續費率 |
| slippage_rate | float | 滑價率 |

### 2. 績效指標

| 指標 | 計算方式 |
|------|---------|
| 總收益率 | (最終資金 - 初始資金) / 初始資金 |
| 年化收益率 | (1 + 總收益率)^(365/天數) - 1 |
| 勝率 | 盈利交易數 / 總交易數 |
| 最大回撤 | 峰值到谷值的最大跌幅 |
| 夏普比率 | (收益率 - 無風險利率) / 波動率 |

## API 端點

### 創建回測

```http
POST /backtests
Content-Type: application/json

{
  "name": "2026Q1策略回測",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31",
  "initial_capital": 100000
}
```

### 執行回測

```http
POST /backtests/{id}/run
Content-Type: application/json

{
  "decisions": [
    {"date": "2026-01-05", "action": "buy", "price": 4800, "quantity": 10},
    {"date": "2026-02-10", "action": "sell", "price": 4850, "quantity": 10}
  ],
  "price_data": {
    "2026-01-05": 4800,
    "2026-02-10": 4850
  }
}
```

### 查看結果

```http
GET /backtests/{id}
```

**回應**

```json
{
  "id": "bt_abc123",
  "status": "completed",
  "total_return": 1.04,
  "annualized_return": 4.16,
  "win_rate": 75.0,
  "max_drawdown": 2.3,
  "sharpe_ratio": 1.82,
  "total_trades": 4,
  "winning_trades": 3,
  "losing_trades": 1
}
```

## 使用流程

```
創建回測 → 上傳決策數據 → 執行回測 → 查看結果 → 導出報告
```

## 相關模塊

- [報告生成](./report.md) - 回測報告導出
