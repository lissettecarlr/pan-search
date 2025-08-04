"""
应用主入口
"""
import asyncio
from typing import Optional
from .config import ConfigManager
from .plugin_manager import PluginManager
from .search_service import SearchService


class PanSearchApp:
    """网盘搜索应用主类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_manager = ConfigManager(config_path)
        self.plugin_manager = PluginManager()
        self.search_service: Optional[SearchService] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化应用"""
        if self._initialized:
            return
        
        try:
            # 加载配置
            config = self.config_manager.get_config()
            
            # 加载插件
            enabled_plugins = config.get("plugins", {}).get("enabled", [])
            self.plugin_manager.load_plugins(enabled_plugins)
            
            # 初始化搜索服务
            self.search_service = SearchService(self.plugin_manager)
            
            self._initialized = True
            
        except Exception as e:
            print(f"应用初始化失败: {e}")
    
    async def search(self, keyword: str, **kwargs):
        """执行搜索"""
        if not self._initialized:
            await self.initialize()
        
        if not self.search_service:
            print("搜索服务未初始化")
            return None
        
        return await self.search_service.search(keyword, **kwargs)
    
    def get_plugin_status(self):
        """获取插件状态"""
        return self.plugin_manager.get_plugin_status()
    
    def get_config(self):
        """获取配置"""
        return self.config_manager.get_config()


# 全局应用实例
_app: Optional[PanSearchApp] = None


async def get_app(config_path: str = "config.yaml") -> PanSearchApp:
    """获取应用实例"""
    global _app
    if _app is None:
        _app = PanSearchApp(config_path)
        await _app.initialize()
    return _app


async def search(keyword: str, config_path: str = "config.yaml", **kwargs):
    """便捷搜索函数"""
    app = await get_app(config_path)
    return await app.search(keyword, **kwargs) 