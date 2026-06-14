# 投資組合管理模塊

## 概述

投資組合管理模塊提供完整的投資組合追蹤和分析功能，支持多種資產類型和績效計算。

## 功能列表

### 1. 組合管理

| 功能 | 描述 |
|------|------|
| 創建組合 | 建立新的投資組合，設定初始資金 |
| 編輯組合 | 修改組合名稱和描述 |
| 刪除組合 | 移除不需要的組合 |
| 列表查詢 | 查看所有組合及其概況 |

### 2. 持倉管理

| 功能 | 描述 |
|------|------|
| 新增持倉 | 添加資產到組合 |
| 調整持倉 | 修改持倉數量或成本 |
| 移除持倉 | 從組合中移除資產 |
| 持倉查詢 | 查看持倉詳情 |

### 3. 績效分析

| 指標 | 計算方式 |
|------|---------|
| 總收益率 | (當前價值 - 初始資金) / 初始資金 × 100% |
| 未實現損益 | (當前價格 - 平均成本) × 持倉數量 |
| 持倉佔比 | 單一持倉價值 / 組合總價值 × 100% |

## API 端點

### 創建組合

```http
POST /portfolios
Content-Type: application/json

{
  "name": "黃金投資組合",
  "initial_capital": 100000
}
```

**回應**

```json
{
  "id": "port_abc123",
  "name": "黃金投資組合",
  "initial_capital": 100000,
  "current_value": 100000,
  "created_at": "2026-04-11T09:30:00Z"
}
```

### 新增持倉

```http
POST /portfolios/{id}/positions
Content-Type: application/json

{
  "asset": "GOLD",
  "asset_type": "commodity",
  "quantity": 20,
  "avg_cost": 4800
}
```

### 計算績效

```http
POST /portfolios/{id}/performance
Content-Type: application/json

{
  "current_prices": {
    "GOLD": 4887
  }
}
```

**回應**

```json
{
  "portfolio_id": "port_abc123",
  "initial_capital": 100000,
  "current_value": 106740,
  "total_return": 6.74,
  "positions": [
    {
      "asset": "GOLD",
      "quantity": 20,
      "avg_cost": 4800,
      "current_price": 4887,
      "market_value": 97740,
      "unrealized_pnl": 1740,
      "return_pct": 1.81
    }
  ]
}
```

## 資產類型

| 類型 | 代碼 | 描述 |
|------|------|------|
| 商品 | commodity | 黃金、白銀等貴金屬 |
| 股票 | stock | 股票證券 |
| 債券 | bond | 債券 |
| 現金 | cash | 現金等價物 |

## 數據模型

### Portfolio

```python
class Portfolio(BaseModel):
    id: str
    name: str
    initial_capital: float
    current_value: float = 0.0
    positions: List[Position] = []
    created_at: datetime
    updated_at: datetime
```

### Position

```python
class Position(BaseModel):
    id: str
    asset: str
    asset_type: AssetType
    quantity: float
    avg_cost: float
    current_price: float = 0.0
```

## 錯誤處理

| 錯誤碼 | 描述 |
|--------|------|
| 400 | 請求參數無效 |
| 404 | 組合不存在 |
| 409 | 資金不足 |

## 最佳實踐

1. **定期更新價格**: 建議每 10 分鐘更新一次當前價格
2. **備份數據**: 定期導出組合數據
3. **風險控制**: 設定單一持倉上限

## 相關模塊

- [告警系統](./alert.md) - 價格告警通知
- [報告生成](./report.md) - 組合報告導出
