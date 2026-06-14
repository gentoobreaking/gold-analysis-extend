"""
回測系統模型
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4


class BacktestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TradeAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


class Trade(BaseModel):
    """交易記錄"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime
    action: TradeAction
    price: float
    quantity: float
    value: float
    commission: float = Field(default=0)
    pnl: float = Field(default=0)
    notes: str = ""


class BacktestConfig(BaseModel):
    """回測配置"""
    name: str
    start_date: date
    end_date: date
    initial_capital: float = Field(gt=0, default=100000.0)
    commission_rate: float = Field(ge=0, default=0.001)
    slippage_rate: float = Field(ge=0, default=0.0005)


class BacktestResult(BaseModel):
    """回測結果"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    config: BacktestConfig
    status: BacktestStatus = BacktestStatus.PENDING
    
    # 績效指標
    total_return: float = Field(default=0, description="總收益率 (%)")
    annualized_return: float = Field(default=0, description="年化收益率 (%)")
    win_rate: float = Field(default=0, description="勝率 (%)")
    max_drawdown: float = Field(default=0, description="最大回撤 (%)")
    sharpe_ratio: float = Field(default=0, description="夏普比率")
    sortino_ratio: float = Field(default=0, description="索提諾比率")
    profit_factor: float = Field(default=0, description="盈虧比")
    
    # 統計數據
    total_trades: int = Field(default=0)
    winning_trades: int = Field(default=0)
    losing_trades: int = Field(default=0)
    avg_win: float = Field(default=0)
    avg_loss: float = Field(default=0)
    final_capital: float = Field(default=0)
    
    # 詳細記錄
    trades: List[Trade] = Field(default_factory=list)
    daily_values: List[Dict[str, Any]] = Field(default_factory=list)
    
    # 元數據
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def calculate_metrics(self) -> None:
        """計算績效指標"""
        if not self.trades:
            return
        
        # 基本統計
        self.total_trades = len(self.trades)
        pnl_list = [t.pnl for t in self.trades if t.action != TradeAction.HOLD]
        
        winning = [p for p in pnl_list if p > 0]
        losing = [p for p in pnl_list if p < 0]
        
        self.winning_trades = len(winning)
        self.losing_trades = len(losing)
        
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100
        
        if winning:
            self.avg_win = sum(winning) / len(winning)
        if losing:
            self.avg_loss = sum(losing) / len(losing)
        
        # 盈虧比
        if losing and self.avg_loss != 0:
            self.profit_factor = abs(sum(winning) / abs(sum(losing)))
        
        # 最終資金
        self.final_capital = self.config.initial_capital + sum(pnl_list)
        
        # 總收益率
        self.total_return = ((self.final_capital - self.config.initial_capital) / 
                           self.config.initial_capital) * 100
        
        # 年化收益率（簡化計算）
        days = (self.config.end_date - self.config.start_date).days
        if days > 0:
            years = days / 365.25
            if years > 0:
                self.annualized_return = ((self.final_capital / self.config.initial_capital) ** (1/years) - 1) * 100
        
        # 從每日價值計算夏普比率和最大回撤
        if self.daily_values:
            returns = []
            for i in range(1, len(self.daily_values)):
                prev = self.daily_values[i-1].get("value", 1)
                curr = self.daily_values[i].get("value", 1)
                if prev > 0:
                    returns.append((curr - prev) / prev)
            
            if returns:
                import statistics
                avg_return = statistics.mean(returns)
                std_return = statistics.stdev(returns) if len(returns) > 1 else 0.001
                
                # 夏普比率（假設無風險利率為 2%）
                if std_return > 0:
                    daily_rf = 0.02 / 252
                    self.sharpe_ratio = (avg_return - daily_rf) / std_return * (252 ** 0.5)
                
                # 最大回撤
                peak = self.daily_values[0].get("value", self.config.initial_capital)
                for dv in self.daily_values:
                    value = dv.get("value", peak)
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak * 100 if peak > 0 else 0
                    if drawdown > self.max_drawdown:
                        self.max_drawdown = drawdown
        
        self.completed_at = datetime.now()
        self.status = BacktestStatus.COMPLETED
