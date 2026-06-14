"""
報告生成模型
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from uuid import uuid4


class ReportType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    HTML = "html"


class ReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportSection(BaseModel):
    """報告章節"""
    title: str
    content: str = ""
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)


class Report(BaseModel):
    """報告"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    status: ReportStatus = ReportStatus.PENDING
    
    # 時間範圍
    start_date: date
    end_date: date
    
    # 內容
    sections: List[ReportSection] = Field(default_factory=list)
    summary: str = ""
    
    # 統計數據
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # 文件信息
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    # 元數據
    created_at: datetime = Field(default_factory=datetime.now)
    generated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    def add_section(self, section: ReportSection) -> None:
        self.sections.append(section)
    
    def set_metrics(self, metrics: Dict[str, Any]) -> None:
        self.metrics = metrics


class ReportConfig(BaseModel):
    """報告配置"""
    name: str
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    include_charts: bool = True
    include_tables: bool = True
    custom_sections: List[str] = Field(default_factory=list)
