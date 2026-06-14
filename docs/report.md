# 報告生成系統

## 概述

報告系統自動生成日報、週報、月報，支持 PDF/Excel 導出。

## 報告類型

| 類型 | 代碼 | 時間範圍 |
|------|------|---------|
| 日報 | daily | 當日 |
| 週報 | weekly | 本週 |
| 月報 | monthly | 本月 |
| 自定義 | custom | 指定範圍 |

## API 端點

### 創建報告

```http
POST /reports
Content-Type: application/json

{
  "name": "2026年4月黃金投資月報",
  "report_type": "monthly",
  "format": "pdf"
}
```

### 生成報告

```http
POST /reports/{id}/generate
Content-Type: application/json

{
  "prices": {
    "current": 4887,
    "high": 4920,
    "low": 4850,
    "change_pct": 0.26
  },
  "trades": [
    {"date": "2026-04-05", "action": "buy", "price": 4850, "quantity": 10}
  ]
}
```

### 下載報告

```http
GET /reports/{id}/download
```

## 報告內容

### 標準章節

1. **摘要**: 本期市場概況和投資表現
2. **價格分析**: 價格走勢圖表和技術指標
3. **交易記錄**: 買賣明細和統計
4. **績效指標**: 收益率、風險指標

### 自定義章節

可在配置中添加自定義章節：

```json
{
  "custom_sections": ["持倉分析", "風險評估", "下期展望"]
}
```

## 導出格式

| 格式 | 副檔名 | 特點 |
|------|--------|------|
| PDF | .pdf | 適合打印和存檔 |
| Excel | .xlsx | 適合數據分析 |
| HTML | .html | 適合線上查看 |

## 相關模塊

- [回測系統](./backtest.md) - 回測報告來源
