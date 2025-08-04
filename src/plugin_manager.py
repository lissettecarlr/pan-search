"""
插件管理器
"""
import asyncio
import importlib
from typing import List, Dict, Any, Type, Optional
from .plugin_base import BasePlugin
from .plugin_adapter import PluginAdapter, setup_old_models
from .models import SearchResult


class PluginManager:
    """插件管理器，负责插件注册、调度与统一调用"""
    
    def __init__(self):
        self._plugins: List[BasePlugin] = []
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}
        # 设置旧插件模型
        setup_old_models()
    
    def register(self, plugin: BasePlugin) -> None:
        """注册单个插件实例"""
        if plugin.name() in [p.name() for p in self._plugins]:
            print(f"警告: 插件名称重复: {plugin.name()}")
            return
        
        self._plugins.append(plugin)
    
    def get_plugins(self) -> List[BasePlugin]:
        """获取所有已注册插件，按优先级排序"""
        return sorted(self._plugins, key=lambda p: p.priority())
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """根据名称获取插件"""
        for plugin in self._plugins:
            if plugin.name() == name:
                return plugin
        return None
    
    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """动态加载插件"""
        try:
            # 特殊处理类名不一致的插件
            class_name_map = {
                "hunhepan": "HunhepanPlugin",
                "tgsearch": "TGSearchPlugin"
            }
            
            class_name = class_name_map.get(plugin_name, f"{plugin_name.capitalize()}Plugin")
            
            # 导入插件模块
            module = importlib.import_module(f"plugins.{plugin_name}")
            plugin_class = getattr(module, class_name)
            
            # 创建插件实例并用适配器包装
            sync_plugin = plugin_class()
            plugin = PluginAdapter(sync_plugin)
            
            self.register(plugin)
            return plugin
            
        except Exception as e:
            print(f"加载插件 {plugin_name} 失败: {e}")
            return None
    
    def load_plugins(self, plugin_names: List[str]) -> List[BasePlugin]:
        """批量加载插件"""
        loaded_plugins = []
        for name in plugin_names:
            # 确保是字符串且不是配置键
            if isinstance(name, str) and name not in ['enabled', 'timeout', 'max_results']:
                plugin = self.load_plugin(name)
                if plugin:
                    loaded_plugins.append(plugin)
        return loaded_plugins
    
    async def search_all(self, keyword: str, **kwargs) -> List[SearchResult]:
        """并发调用所有插件的search，聚合结果"""
        if not self._plugins:
            return []
        
        # 创建搜索任务
        tasks = []
        for plugin in self.get_plugins():
            if plugin.is_enabled():
                task = self._search_plugin(plugin, keyword, **kwargs)
                tasks.append(task)
        
        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 合并结果
        all_results = []
        for i, result in enumerate(results):
            plugin = self.get_plugins()[i]
            if isinstance(result, Exception):
                print(f"插件 {plugin.name()} 搜索失败: {result}")
            else:
                all_results.extend(result)
        
        return all_results
    
    async def _search_plugin(self, plugin: BasePlugin, keyword: str, **kwargs) -> List[SearchResult]:
        """单个插件搜索"""
        import time
        start_time = time.time()
        try:
            print(f"开始搜索插件: {plugin.name()}")
            result = await plugin.search(keyword, **kwargs)
            elapsed_time = time.time() - start_time
            print(f"插件 {plugin.name()} 搜索完成，耗时: {elapsed_time:.2f}秒")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"插件 {plugin.name()} 搜索失败: {e}，耗时: {elapsed_time:.2f}秒")
            return []
    
    def get_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有插件状态"""
        status = {}
        for plugin in self.get_plugins():
            status[plugin.name()] = {
                "enabled": plugin.is_enabled(),
                "priority": plugin.priority(),
                "description": plugin.get_description()
            }
        return status 