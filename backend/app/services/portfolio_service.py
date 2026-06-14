"""
投資組合服務層
提供 CRUD 操作和績效計算
"""
from datetime import datetime
from typing import Optional, List, Dict
from uuid import uuid4
import json
from pathlib import Path

from ..models.portfolio import (
    Portfolio, Position, PortfolioCreate, PortfolioUpdate,
    PositionCreate, PositionUpdate, AssetType
)


class PortfolioService:
    """投資組合服務"""
    
    def __init__(self, data_dir: str = "./data/portfolios"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Portfolio] = {}
        self._load_all()
    
    def _get_portfolio_path(self, portfolio_id: str) -> Path:
        """獲取組合文件路徑"""
        return self.data_dir / f"{portfolio_id}.json"
    
    def _load_all(self) -> None:
        """載入所有組合"""
        for file in self.data_dir.glob("*.json"):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                portfolio = Portfolio(**data)
                self._cache[portfolio.id] = portfolio
    
    def _save(self, portfolio: Portfolio) -> None:
        """保存組合到文件"""
        path = self._get_portfolio_path(portfolio.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(portfolio.model_dump(mode="json"), f, ensure_ascii=False, indent=2, default=str)
        self._cache[portfolio.id] = portfolio
    
    def create(self, request: PortfolioCreate) -> Portfolio:
        """創建新投資組合"""
        portfolio = Portfolio(
            id=str(uuid4()),
            name=request.name,
            description=request.description or "",
            initial_capital=request.initial_capital,
            cash_balance=request.initial_capital,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        portfolio.calculate_metrics()
        self._save(portfolio)
        return portfolio
    
    def get(self, portfolio_id: str) -> Optional[Portfolio]:
        """獲取投資組合"""
        return self._cache.get(portfolio_id)
    
    def list(self) -> List[Portfolio]:
        """列出所有投資組合"""
        return list(self._cache.values())
    
    def update(self, portfolio_id: str, request: PortfolioUpdate) -> Optional[Portfolio]:
        """更新投資組合"""
        portfolio = self.get(portfolio_id)
        if not portfolio:
            return None
        
        if request.name is not None:
            portfolio.name = request.name
        if request.description is not None:
            portfolio.description = request.description
        
        portfolio.updated_at = datetime.now()
        self._save(portfolio)
        return portfolio
    
    def delete(self, portfolio_id: str) -> bool:
        """刪除投資組合"""
        portfolio = self.get(portfolio_id)
        if not portfolio:
            return False
        
        path = self._get_portfolio_path(portfolio_id)
        if path.exists():
            path.unlink()
        
        del self._cache[portfolio_id]
        return True
    
    def add_position(self, portfolio_id: str, request: PositionCreate) -> Optional[Position]:
        """新增持倉"""
        portfolio = self.get(portfolio_id)
        if not portfolio:
            return None
        
        position = Position(
            id=str(uuid4()),
            asset_type=request.asset_type,
            asset_name=request.asset_name,
            quantity=request.quantity,
            avg_cost=request.avg_cost,
            current_price=request.avg_cost,  # 初始價格等於成本
            market_value=request.quantity * request.avg_cost,
            opened_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        portfolio.add_position(position)
        self._save(portfolio)
        return position
    
    def update_position(
        self, portfolio_id: str, position_id: str, request: PositionUpdate
    ) -> Optional[Position]:
        """更新持倉"""
        portfolio = self.get(portfolio_id)
        if not portfolio:
            return None
        
        for position in portfolio.positions:
            if position.id == position_id:
                if request.quantity is not None:
                    position.quantity = request.quantity
                if request.avg_cost is not None:
                    position.avg_cost = request.avg_cost
                
                position.updated_at = datetime.now()
                portfolio.calculate_metrics()
                self._save(portfolio)
                return position
        
        return None
    
    def remove_position(self, portfolio_id: str, position_id: str) -> bool:
        """移除持倉"""
        portfolio = self.get(portfolio_id)
        if not portfolio:
            return False
        
        result = portfolio.remove_position(position_id)
        if result:
            self._save(portfolio)
        return result
    
    def update_prices(self, prices: Dict[str, float]) -> None:
        """更新所有組合的價格（用於實時更新）"""
        for portfolio in self._cache.values():
            for position in portfolio.positions:
                # 根據資產類型匹配價格
                if position.asset_type == AssetType.GOLD_SPOT and "gold_spot" in prices:
                    position.current_price = prices["gold_spot"]
                elif position.asset_type == AssetType.GOLD_ETF and "gold_etf" in prices:
                    position.current_price = prices["gold_etf"]
                elif position.asset_type == AssetType.GOLD_FUTURES and "gold_futures" in prices:
                    position.current_price = prices["gold_futures"]
                
                # 重新計算市值和損益
                position.market_value = position.quantity * position.current_price
                position.unrealized_pnl = position.market_value - (position.quantity * position.avg_cost)
                if position.quantity * position.avg_cost > 0:
                    position.unrealized_pnl_pct = (position.unrealized_pnl / (position.quantity * position.avg_cost)) * 100
                position.updated_at = datetime.now()
            
            portfolio.calculate_metrics()
            self._save(portfolio)
    
    def calculate_performance(self, portfolio_id: str) -> Dict:
        """計算績效指標"""
        portfolio = self.get(portfolio_id)
        if not portfolio:
            return {}
        
        total_positions = len(portfolio.positions)
        profitable_positions = sum(1 for p in portfolio.positions if p.unrealized_pnl > 0)
        
        return {
            "portfolio_id": portfolio.id,
            "portfolio_name": portfolio.name,
            "initial_capital": portfolio.initial_capital,
            "current_value": portfolio.total_value,
            "cash_balance": portfolio.cash_balance,
            "total_pnl": portfolio.total_pnl,
            "total_return_pct": portfolio.total_return,
            "total_positions": total_positions,
            "profitable_positions": profitable_positions,
            "position_details": [
                {
                    "asset": p.asset_name,
                    "quantity": p.quantity,
                    "avg_cost": p.avg_cost,
                    "current_price": p.current_price,
                    "market_value": p.market_value,
                    "pnl": p.unrealized_pnl,
                    "pnl_pct": p.unrealized_pnl_pct
                }
                for p in portfolio.positions
            ],
            "calculated_at": datetime.now().isoformat()
        }
