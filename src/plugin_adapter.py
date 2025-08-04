"""
插件适配器，用于兼容现有的同步插件
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
from .plugin_base import BasePlugin


# 为旧插件提供模型导入
def setup_old_models():
    """设置旧插件的模型导入"""
    # 添加plugins目录到Python路径
    plugins_path = Path(__file__).parent.parent / "plugins"
    if plugins_path.exists():
        sys.path.insert(0, str(plugins_path.parent))
    
    # 为旧插件提供模型
    from .models import SearchResult, Link
    import models
    models.SearchResult = SearchResult
    models.Link = Link
    
    # 为旧插件提供基类
    import plugin_base
    plugin_base.BasePanPlugin = BasePlugin


class PluginAdapter(BasePlugin):
    """插件适配器，将同步插件转换为异步插件"""
    
    def __init__(self, sync_plugin):
        self.sync_plugin = sync_plugin
    
    def name(self) -> str:
        return self.sync_plugin.name()
    
    def priority(self) -> int:
        return self.sync_plugin.priority()
    
    async def search(self, keyword: str, **kwargs) -> List:
        """异步执行同步插件的搜索方法"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.sync_plugin.search, 
            keyword, 
            kwargs.get('ext', {})
        )
    
    def get_description(self) -> str:
        return getattr(self.sync_plugin, 'get_description', lambda: f"{self.name()} 插件")()
    
    def is_enabled(self) -> bool:
        return getattr(self.sync_plugin, 'is_enabled', lambda: True)() 