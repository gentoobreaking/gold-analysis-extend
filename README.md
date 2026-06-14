# Gold Analysis Extend

黃金分析系統延伸功能模組，提供投資組合管理、告警系統、回測系統和報告生成功能。

## 功能模塊

### 1. 投資組合管理 (T001)

- 創建、編輯、刪除投資組合
- 持倉管理（新增、調整、移除）
- 績效計算（收益率、未實現損益）
- 實時價格更新

### 2. 告警通知系統 (T002)

- 價格告警（高於/低於目標價）
- 指標告警（技術指標交叉）
- 信號告警（交易信號觸發）
- 多渠道通知（Email、SMS、Telegram、Webhook）

### 3. 決策回測系統 (T003)

- 歷史決策回放
- 績效分析（收益率、勝率、最大回撤）
- 風險指標（夏普比率、索提諾比率）
- 交易明細記錄

### 4. 報告生成系統 (T004)

- 日報、週報、月報自動生成
- PDF/Excel 導出
- 自定義報告模板

### 5. 多語言支持 (T005)

- 繁體中文 / English
- react-i18next 框架
- 語言即時切換

## 技術棧

### Backend

- FastAPI
- Pydantic v2
- Python 3.9+

### Frontend

- React 18
- TypeScript
- react-i18next

## 快速開始

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

API 文檔: http://localhost:8001/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API 端點

### 投資組合

- `POST /portfolios` - 創建組合
- `GET /portfolios` - 列出所有組合
- `GET /portfolios/{id}` - 獲取單個組合
- `PATCH /portfolios/{id}` - 更新組合
- `DELETE /portfolios/{id}` - 刪除組合
- `POST /portfolios/{id}/positions` - 新增持倉
- `DELETE /portfolios/{id}/positions/{pos_id}` - 移除持倉
- `POST /portfolios/{id}/performance` - 計算績效

### 告警

- `POST /alerts` - 創建告警
- `GET /alerts` - 列出告警
- `PATCH /alerts/{id}` - 更新告警
- `DELETE /alerts/{id}` - 刪除告警

### 回測

- `POST /backtests` - 創建回測任務
- `GET /backtests` - 列出回測結果
- `POST /backtests/{id}/run` - 執行回測

## 依賴

本專案依賴 gold-analysis-core 完成以下任務：

- T011: 決策推薦 Agent
- T014: 前端儀表板
- T015: 即時價格推送

## 授權

MIT License
