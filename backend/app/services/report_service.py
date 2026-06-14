"""
報告生成服務
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from decimal import Decimal

from ..models.report import (
    Report, ReportConfig, ReportSection, ReportType,
    ReportFormat, ReportStatus
)


class ReportService:
    """報告生成服務"""
    
    def __init__(self, data_dir: str = "./data/reports"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Report] = {}
    
    def create(self, config: ReportConfig) -> Report:
        """創建報告"""
        today = date.today()
        
        if config.report_type == ReportType.DAILY:
            start_date = end_date = today
        elif config.report_type == ReportType.WEEKLY:
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif config.report_type == ReportType.MONTHLY:
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        else:
            start_date = end_date = today
        
        report = Report(
            name=config.name,
            report_type=config.report_type,
            format=config.format,
            start_date=start_date,
            end_date=end_date,
            status=ReportStatus.PENDING
        )
        
        self._save(report)
        return report
    
    def get(self, report_id: str) -> Optional[Report]:
        return self._cache.get(report_id)
    
    def list(self, report_type: ReportType = None) -> List[Report]:
        reports = list(self._cache.values())
        if report_type:
            reports = [r for r in reports if r.report_type == report_type]
        return sorted(reports, key=lambda x: x.created_at, reverse=True)
    
    def generate(self, report_id: str, data: Dict[str, Any]) -> Report:
        """生成報告內容"""
        report = self.get(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        report.status = ReportStatus.GENERATING
        
        try:
            # 摘要
            report.summary = self._generate_summary(data)
            
            # 價格分析章節
            price_section = ReportSection(
                title="價格分析",
                content=self._generate_price_content(data.get("prices", {})),
                charts=[{"type": "line", "data": data.get("prices", {}).get("history", [])}]
            )
            report.add_section(price_section)
            
            # 交易記錄章節
            if data.get("trades"):
                trades_section = ReportSection(
                    title="交易記錄",
                    content=self._generate_trades_content(data.get("trades", [])),
                    tables=[{"headers": ["日期", "操作", "價格", "數量"], "rows": data.get("trades", [])}]
                )
                report.add_section(trades_section)
            
            # 績效指標
            report.set_metrics(self._calculate_metrics(data))
            
            report.status = ReportStatus.COMPLETED
            report.generated_at = datetime.now()
            
        except Exception as e:
            report.status = ReportStatus.FAILED
            report.summary = f"生成失敗: {str(e)}"
        
        self._save(report)
        return report
    
    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """生成摘要"""
        prices = data.get("prices", {})
        current = prices.get("current", 0)
        change = prices.get("change_pct", 0)
        
        trend = "上漲" if change > 0 else "下跌" if change < 0 else "持平"
        return f"本報告期內黃金價格{trend}，當前價格為 {current:.2f}，漲跌幅 {change:.2f}%"
    
    def _generate_price_content(self, prices: Dict[str, Any]) -> str:
        """生成價格分析內容"""
        if not prices:
            return "暫無價格數據"
        
        current = prices.get("current", 0)
        high = prices.get("high", 0)
        low = prices.get("low", 0)
        
        return f"期間最高價: {high:.2f}，最低價: {low:.2f}，當前價: {current:.2f}"
    
    def _generate_trades_content(self, trades: List[Any]) -> str:
        """生成交易記錄內容"""
        if not trades:
            return "本期無交易記錄"
        return f"本期共 {len(trades)} 筆交易"
    
    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """計算績效指標"""
        return {
            "total_return": data.get("return_pct", 0),
            "trades_count": len(data.get("trades", [])),
            "generated_at": datetime.now().isoformat()
        }
    
    def delete(self, report_id: str) -> bool:
        report = self.get(report_id)
        if not report:
            return False
        
        path = self._get_path(report_id)
        if path.exists():
            path.unlink()
        del self._cache[report_id]
        return True
    
    def _get_path(self, report_id: str) -> Path:
        return self.data_dir / f"{report_id}.json"
    
    def _save(self, report: Report) -> None:
        path = self._get_path(report.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(mode="json"), f, ensure_ascii=False, indent=2, default=str)
        self._cache[report.id] = report
