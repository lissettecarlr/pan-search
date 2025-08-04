"""
数据模型定义
"""
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Link:
    """下载链接模型"""
    type: str
    url: str
    password: str = ""


@dataclass
class SearchResult:
    """搜索结果模型"""
    message_id: str = ""
    unique_id: str = ""
    channel: str = ""
    datetime: Optional[datetime] = None
    title: str = ""
    content: str = ""
    links: List[Link] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class MergedLink:
    """合并后的链接模型"""
    url: str
    password: str = ""
    note: str = ""
    datetime: Optional[datetime] = None
    source: str = ""


@dataclass
class SearchResponse:
    """搜索响应模型"""
    total: int
    results: List[SearchResult] = field(default_factory=list)
    merged_by_type: Optional[Dict[str, List[MergedLink]]] = None 