'''投資組合模組測試'''
import pytest
import sys
sys.path.insert(0, '.')

from app.models.portfolio import Portfolio, Position, PortfolioCreate, AssetType
from app.services.portfolio_service import PortfolioService


def test_create_portfolio():
    '''測試創建投資組合'''
    service = PortfolioService(data_dir='/tmp/test_portfolios')
    request = PortfolioCreate(
        name='測試組合',
        description='這是一個測試組合',
        initial_capital=100000.0
    )
    portfolio = service.create(request)
    
    assert portfolio.id is not None
    assert portfolio.name == '測試組合'
    assert portfolio.initial_capital == 100000.0
    assert portfolio.cash_balance == 100000.0
    assert portfolio.total_value == 100000.0


def test_add_position():
    '''測試新增持倉'''
    service = PortfolioService(data_dir='/tmp/test_portfolios')
    
    # 先創建組合
    portfolio = service.create(PortfolioCreate(
        name='持倉測試',
        initial_capital=50000.0
    ))
    
    # 新增持倉
    from app.models.portfolio import PositionCreate
    position = service.add_position(portfolio.id, PositionCreate(
        asset_type=AssetType.GOLD_SPOT,
        asset_name='黃金存摺',
        quantity=10.0,
        avg_cost=5000.0
    ))
    
    assert position is not None
    assert position.quantity == 10.0
    assert position.avg_cost == 5000.0
    
    # 檢查組合更新
    updated_portfolio = service.get(portfolio.id)
    assert len(updated_portfolio.positions) == 1


def test_portfolio_performance():
    '''測試績效計算'''
    service = PortfolioService(data_dir='/tmp/test_portfolios')
    
    portfolio = service.create(PortfolioCreate(
        name='績效測試',
        initial_capital=100000.0
    ))
    
    performance = service.calculate_performance(portfolio.id)
    
    assert performance['portfolio_id'] == portfolio.id
    assert performance['initial_capital'] == 100000.0
    assert 'total_return_pct' in performance


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
