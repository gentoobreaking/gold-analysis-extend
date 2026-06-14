"""
投資組合 API 端點
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict

from ..models.portfolio import (
    Portfolio, PortfolioCreate, PortfolioUpdate,
    PositionCreate, PositionUpdate, Position
)
from ..services.portfolio_service import PortfolioService


router = APIRouter(prefix="/portfolios", tags=["portfolios"])


def get_service() -> PortfolioService:
    """獲取服務實例"""
    return PortfolioService()


@router.post("", response_model=Portfolio)
async def create_portfolio(
    request: PortfolioCreate,
    service: PortfolioService = Depends(get_service)
):
    """創建投資組合"""
    return service.create(request)


@router.get("", response_model=List[Portfolio])
async def list_portfolios(
    service: PortfolioService = Depends(get_service)
):
    """列出所有投資組合"""
    return service.list()


@router.get("/{portfolio_id}", response_model=Portfolio)
async def get_portfolio(
    portfolio_id: str,
    service: PortfolioService = Depends(get_service)
):
    """獲取單個投資組合"""
    portfolio = service.get(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.patch("/{portfolio_id}", response_model=Portfolio)
async def update_portfolio(
    portfolio_id: str,
    request: PortfolioUpdate,
    service: PortfolioService = Depends(get_service)
):
    """更新投資組合"""
    portfolio = service.update(portfolio_id, request)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    service: PortfolioService = Depends(get_service)
):
    """刪除投資組合"""
    if not service.delete(portfolio_id):
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return {"status": "deleted", "portfolio_id": portfolio_id}


@router.post("/{portfolio_id}/positions", response_model=Position)
async def add_position(
    portfolio_id: str,
    request: PositionCreate,
    service: PortfolioService = Depends(get_service)
):
    """新增持倉"""
    position = service.add_position(portfolio_id, request)
    if not position:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return position


@router.patch("/{portfolio_id}/positions/{position_id}", response_model=Position)
async def update_position(
    portfolio_id: str,
    position_id: str,
    request: PositionUpdate,
    service: PortfolioService = Depends(get_service)
):
    """更新持倉"""
    position = service.update_position(portfolio_id, position_id, request)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position


@router.delete("/{portfolio_id}/positions/{position_id}")
async def remove_position(
    portfolio_id: str,
    position_id: str,
    service: PortfolioService = Depends(get_service)
):
    """移除持倉"""
    if not service.remove_position(portfolio_id, position_id):
        raise HTTPException(status_code=404, detail="Position not found")
    return {"status": "removed", "position_id": position_id}


@router.post("/{portfolio_id}/performance")
async def calculate_performance(
    portfolio_id: str,
    service: PortfolioService = Depends(get_service)
):
    """計算績效指標"""
    performance = service.calculate_performance(portfolio_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return performance


@router.post("/update-prices")
async def update_prices(
    prices: Dict[str, float],
    service: PortfolioService = Depends(get_service)
):
    """更新所有組合的價格"""
    service.update_prices(prices)
    return {"status": "updated", "prices": prices}
