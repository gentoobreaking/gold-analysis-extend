"""
投資組合數據模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class AssetType(str, Enum):
    """資產類型"""
    GOLD_SPOT = "gold_spot"
    GOLD_ETF = "gold_etf"
    GOLD_FUTURES = "gold_futures"
    CASH = "cash"


class Position(BaseModel):
    """持倉"""
    id: str = Field(..., description="持倉ID")
    asset_type: AssetType = Field(..., description="資產類型")
    asset_name: str = Field(..., description="資產名稱")
    quantity: float = Field(..., ge=0, description="持有數量")
    avg_cost: float = Field(..., ge=0, description="平均成本（每單位）")
    current_price: float = Field(default=0, ge=0, description="當前價格")
    market_value: float = Field(default=0, ge=0, description="市值")
    unrealized_pnl: float = Field(default=0, description="未實現損益")
    unrealized_pnl_pct: float = Field(default=0, description="未實現損益百分比")
    opened_at: datetime = Field(default_factory=datetime.now, description="建倉時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")


class Portfolio(BaseModel):
    """投資組合"""
    id: str = Field(..., description="組合ID")
    name: str = Field(..., min_length=1, max_length=100, description="組合名稱")
    description: Optional[str] = Field(default="", description="組合描述")
    initial_capital: float = Field(..., gt=0, description="初始資金")
    cash_balance: float = Field(default=0, ge=0, description="現金餘額")
    positions: List[Position] = Field(default_factory=list, description="持倉列表")
    total_value: float = Field(default=0, ge=0, description="總市值")
    total_return: float = Field(default=0, description="總收益率")
    total_pnl: float = Field(default=0, description="總損益")
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新時間")
    
    def calculate_metrics(self) -> None:
        """計算組合指標"""
        # 計算持倉市值
        position_value = sum(p.market_value for p in self.positions)
        
        # 總市值 = 持倉市值 + 現金
        self.total_value = position_value + self.cash_balance
        
        # 總損益 = 總市值 - 初始資金
        self.total_pnl = self.total_value - self.initial_capital
        
        # 總收益率
        if self.initial_capital > 0:
            self.total_return = (self.total_pnl / self.initial_capital) * 100
        
        self.updated_at = datetime.now()
    
    def add_position(self, position: Position) -> None:
        """新增持倉"""
        self.positions.append(position)
        self.calculate_metrics()
    
    def remove_position(self, position_id: str) -> bool:
        """移除持倉"""
        for i, p in enumerate(self.positions):
            if p.id == position_id:
                self.positions.pop(i)
                self.calculate_metrics()
                return True
        return False


class PortfolioCreate(BaseModel):
    """創建投資組合請求"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = ""
    initial_capital: float = Field(..., gt=0)


class PositionCreate(BaseModel):
    """新增持倉請求"""
    asset_type: AssetType
    asset_name: str
    quantity: float = Field(..., gt=0)
    avg_cost: float = Field(..., ge=0)


class PortfolioUpdate(BaseModel):
    """更新投資組合請求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class PositionUpdate(BaseModel):
    """更新持倉請求"""
    quantity: Optional[float] = Field(None, gt=0)
    avg_cost: Optional[float] = Field(None, ge=0)
