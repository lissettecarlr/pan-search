"""
搜索服务模块
"""
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
from .models import SearchResult, SearchResponse, MergedLink
from .plugin_manager import PluginManager
from .config import ConfigManager


class SearchService:
    """聚合搜索服务"""
    
    def __init__(self, plugin_manager: PluginManager):
        self.plugin_manager = plugin_manager
        self.config = ConfigManager()
    
    async def search(self, keyword: str, **kwargs) -> SearchResponse:
        """
        执行聚合搜索
        
        Args:
            keyword: 搜索关键词
            **kwargs: 扩展参数
            
        Returns:
            SearchResponse: 搜索响应
        """
        import time
        start_time = time.time()
        print(f"开始聚合搜索关键词: {keyword}")
        
        if not keyword.strip():
            return SearchResponse(total=0)
        
        try:
            # 1. 调用所有插件并记录来源
            all_results = await self.plugin_manager.search_all(keyword, **kwargs)
            
            # 打印插件搜索完成信息
            elapsed_time = time.time() - start_time
            print(f"所有插件搜索完成，共获得 {len(all_results)} 个结果，耗时: {elapsed_time:.2f}秒")
            
            # 2. 去重处理
            merged_results = self._deduplicate_results(all_results)
            
            # 3. 排序处理
            merged_results = self._sort_results(merged_results)
            
            # 4. 按类型分组链接
            merged_links = self._group_links_by_type(merged_results)
            
            # 5. 应用类型过滤
            filter_mode = self.config.get('type_filter.filter_mode', 'none')
            if filter_mode != 'none':
                merged_links = self._filter_links_by_type(merged_links)
            
            # 6. 组装响应
            response = SearchResponse(
                total=len(merged_results),
                results=merged_results,
                merged_by_type=merged_links
            )
            
            total_elapsed_time = time.time() - start_time
            print(f"搜索处理完成，最终结果数: {response.total}，总耗时: {total_elapsed_time:.2f}秒")
            return response
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return SearchResponse(total=0)
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """去重处理"""
        unique = {}
        for result in results:
            # 使用unique_id或title+channel作为去重键
            key = result.unique_id or f"{result.title}_{result.channel}"
            if key not in unique:
                unique[key] = result
            else:
                # 保留信息更完整的结果
                existing = unique[key]
                if len(result.links) > len(existing.links):
                    unique[key] = result
        
        return list(unique.values())
    
    def _sort_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """排序处理"""
        def get_sort_key(result: SearchResult) -> datetime:
            """获取排序键"""
            if result.datetime is None:
                return datetime.min
            # 处理时区信息
            dt = result.datetime
            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt
        
        return sorted(results, key=get_sort_key, reverse=True)
    
    def _group_links_by_type(self, results: List[SearchResult]) -> Dict[str, List[MergedLink]]:
        """按类型分组链接"""
        grouped_links = defaultdict(list)
        
        for result in results:
            for link in result.links:
                # 使用channel作为来源，如果为空则使用默认值
                source = result.channel if result.channel else "聚合搜索"
                merged_link = MergedLink(
                    url=link.url,
                    password=link.password,
                    note=result.title,
                    datetime=result.datetime,
                    source=source
                )
                grouped_links[link.type].append(merged_link)
        
        return dict(grouped_links)
    
    def _filter_links_by_type(self, merged_links: Dict[str, List[MergedLink]]) -> Dict[str, List[MergedLink]]:
        """根据配置过滤链接类型"""
        filter_mode = self.config.get('type_filter.filter_mode', 'none')
        enabled_types = self.config.get('type_filter.enabled_types', [])
        
        if filter_mode == 'none' or not enabled_types:
            return merged_links
        
        filtered_links = {}
        
        if filter_mode == 'include':
            # 正向过滤：只显示enabled_types中的类型
            for link_type, links in merged_links.items():
                if link_type in enabled_types:
                    filtered_links[link_type] = links
        elif filter_mode == 'exclude':
            # 反向屏蔽：不显示enabled_types中的类型
            for link_type, links in merged_links.items():
                if link_type not in enabled_types:
                    filtered_links[link_type] = links
        
        return filtered_links
    
    def get_search_stats(self, keyword: str) -> Dict[str, Any]:
        """获取搜索统计信息"""
        stats = {
            "keyword": keyword,
            "total_plugins": len(self.plugin_manager.get_plugins()),
            "enabled_plugins": len([p for p in self.plugin_manager.get_plugins() if p.is_enabled()]),
            "plugin_status": self.plugin_manager.get_plugin_status()
        }
        return stats 