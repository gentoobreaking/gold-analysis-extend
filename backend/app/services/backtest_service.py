"""
回測服務
提供決策回放和績效分析
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Callable
import json
from pathlib import Path

from ..models.backtest import (
    BacktestConfig, BacktestResult, BacktestStatus,
    Trade, TradeAction
)


class BacktestService:
    """回測服務"""
    
    def __init__(self, data_dir: str = "./data/backtests"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, BacktestResult] = {}
        self._load_all()
    
    def _get_path(self, backtest_id: str) -> Path:
        return self.data_dir / f"{backtest_id}.json"
    
    def _load_all(self) -> None:
        for file in self.data_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                result = BacktestResult(**data)
                self._cache[result.id] = result
    
    def _save(self, result: BacktestResult) -> None:
        path = self._get_path(result.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(mode="json"), f, ensure_ascii=False, indent=2, default=str)
        self._cache[result.id] = result
    
    def create(self, config: BacktestConfig) -> BacktestResult:
        """創建回測任務"""
        result = BacktestResult(config=config)
        self._save(result)
        return result
    
    def get(self, backtest_id: str) -> Optional[BacktestResult]:
        return self._cache.get(backtest_id)
    
    def list(self) -> List[BacktestResult]:
        return list(self._cache.values())
    
    def run(
        self,
        backtest_id: str,
        decisions: List[Dict[str, Any]],
        price_data: Dict[date, float]
    ) -> BacktestResult:
        """執行回測
        
        Args:
            backtest_id: 回測ID
            decisions: 決策列表，每條包含 date, action, price, quantity 等
            price_data: 日期對應的價格數據
        """
        result = self.get(backtest_id)
        if not result:
            raise ValueError(f"Backtest {backtest_id} not found")
        
        result.status = BacktestStatus.RUNNING
        self._save(result)
        
        try:
            capital = result.config.initial_capital
            position = 0.0  # 持倉數量
            
            for decision in decisions:
                trade_date = decision.get("date")
                if isinstance(trade_date, str):
                    trade_date = date.fromisoformat(trade_date)
                
                action = decision.get("action", "hold")
                if action == "hold":
                    continue
                
                # 獲取當前價格
                current_price = price_data.get(trade_date, decision.get("price", 0))
                if current_price <= 0:
                    continue
                
                quantity = decision.get("quantity", 0)
                
                # 計算交易成本
                commission = current_price * quantity * result.config.commission_rate
                slippage = current_price * quantity * result.config.slippage_rate
                total_cost = current_price * quantity + commission + slippage
                
                trade = Trade(
                    timestamp=datetime.combine(trade_date, datetime.min.time()),
                    action=TradeAction(action),
                    price=current_price,
                    quantity=quantity,
                    value=current_price * quantity,
                    commission=commission
                )
                
                if action == "buy":
                    if total_cost <= capital:
                        capital -= total_cost
                        position += quantity
                        trade.notes = "建倉"
                elif action == "sell":
                    if quantity <= position:
                        sell_value = current_price * quantity - commission
                        capital += sell_value
                        position -= quantity
                        trade.pnl = (current_price - result.trades[-1].price if result.trades else 0) * quantity
                        trade.notes = "平倉"
                
                result.trades.append(trade)
            
            # 計算每日市值
            sorted_dates = sorted(price_data.keys())
            for d in sorted_dates:
                price = price_data[d]
                position_value = position * price
                total_value = capital + position_value
                result.daily_values.append({
                    "date": d.isoformat(),
                    "price": price,
                    "position": position,
                    "cash": capital,
                    "value": total_value
                })
            
            result.calculate_metrics()
            self._save(result)
            return result
            
        except Exception as e:
            result.status = BacktestStatus.FAILED
            result.error_message = str(e)
            self._save(result)
            raise
    
    def delete(self, backtest_id: str) -> bool:
        result = self.get(backtest_id)
        if not result:
            return False
        
        path = self._get_path(backtest_id)
        if path.exists():
            path.unlink()
        del self._cache[backtest_id]
        return True
