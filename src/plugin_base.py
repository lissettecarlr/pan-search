"""
插件基类定义
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BasePlugin(ABC):
    """网盘搜索插件基类"""
    
    @abstractmethod
    def name(self) -> str:
        """插件名称，唯一标识"""
        pass
    
    @abstractmethod
    def priority(self) -> int:
        """插件优先级，数值越小优先级越高"""
        pass
    
    @abstractmethod
    async def search(self, keyword: str, **kwargs) -> List:
        """
        执行搜索，返回标准化的SearchResult列表
        
        Args:
            keyword: 搜索关键词
            **kwargs: 扩展参数
            
        Returns:
            SearchResult列表
        """
        pass
    
    def get_description(self) -> str:
        """获取插件描述"""
        return f"{self.name()} 插件"
    
    def is_enabled(self) -> bool:
        """检查插件是否启用"""
        return True 