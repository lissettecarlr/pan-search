import asyncio
import aiohttp
import json
from typing import List, Dict, Any
from datetime import datetime
from plugin_base import BasePanPlugin
from models import SearchResult, Link

class HunhepanPlugin(BasePanPlugin):
    """
    混合盘搜索插件
    """

    HUNHEPAN_API = "https://hunhepan.com/open/search/disk"
    
    DEFAULT_PAGE_SIZE = 30
    MAX_PAGES = 3

    def name(self) -> str:
        return "hunhepan"

    def priority(self) -> int:
        return 3

    async def _search_api(self, session: aiohttp.ClientSession, api_url: str, keyword: str) -> List[Dict]:
        """
        向单个API发送请求
        """
        all_items = []
        
        for page in range(1, self.MAX_PAGES + 1):
            try:
                payload = {
                    "q": keyword,
                    "exact": True,
                    "page": page,
                    "size": self.DEFAULT_PAGE_SIZE,
                    "type": "",
                    "time": "",
                    "from": "web",
                    "user_id": 0,
                    "filter": True,
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                
                if "hunhepan.com" in api_url:
                    headers["Referer"] = "https://hunhepan.com/search"
                
                async with session.post(api_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        continue
                    
                    data = await response.json()
                    
                    if data.get("code") != 200:
                        continue
                    
                    items = data.get("data", {}).get("list", [])
                    all_items.extend(items)
                    
            except Exception as e:
                # 忽略单个页面的错误，继续处理其他页面
                continue
                
        return all_items

    def _clean_title(self, title: str) -> str:
        """
        清理标题中的HTML标签
        """
        replacements = {
            "<em>": "",
            "</em>": "",
            "<b>": "",
            "</b>": "",
            "<strong>": "",
            "</strong>": "",
            "<i>": "",
            "</i>": "",
        }
        
        result = title
        for tag, replacement in replacements.items():
            result = result.replace(tag, replacement)
        
        return result.strip()

    def _deduplicate_items(self, items: List[Dict]) -> List[Dict]:
        """
        去重处理
        """
        unique_map = {}
        
        for item in items:
            # 清理DiskName中的HTML标签
            cleaned_name = self._clean_title(item.get("disk_name", ""))
            item["disk_name"] = cleaned_name
            
            # 创建复合键
            disk_id = item.get("disk_id", "")
            link = item.get("link", "")
            disk_type = item.get("disk_type", "")
            
            if disk_id:
                key = disk_id
            elif link:
                key = f"{link}|{cleaned_name}"
            else:
                key = f"{cleaned_name}|{disk_type}"
            
            # 如果已存在，保留信息更丰富的那个
            if key in unique_map:
                existing = unique_map[key]
                existing_score = len(existing.get("files", ""))
                new_score = len(item.get("files", ""))
                
                # 如果新项有密码而现有项没有，增加新项分数
                if not existing.get("disk_pass") and item.get("disk_pass"):
                    new_score += 5
                
                # 如果新项有时间而现有项没有，增加新项分数
                if not existing.get("shared_time") and item.get("shared_time"):
                    new_score += 3
                
                if new_score > existing_score:
                    unique_map[key] = item
            else:
                unique_map[key] = item
        
        return list(unique_map.values())

    def _convert_disk_type(self, disk_type: str) -> str:
        """
        将API的网盘类型转换为标准链接类型
        """
        type_mapping = {
            "BDY": "baidu",
            "ALY": "aliyun",
            "QUARK": "quark",
            "TIANYI": "tianyi",
            "UC": "uc",
            "CAIYUN": "mobile",
            "115": "115",
            "XUNLEI": "xunlei",
            "123PAN": "123",
            "PIKPAK": "pikpak",
        }
        return type_mapping.get(disk_type, "others")

    def _convert_results(self, items: List[Dict]) -> List[SearchResult]:
        """
        将API响应转换为标准SearchResult格式
        """
        results = []
        
        for i, item in enumerate(items):
            # 创建链接
            disk_type = item.get("disk_type", "")
            link_type = self._convert_disk_type(disk_type)
            
            link = Link(
                type=link_type,
                url=item.get("link", ""),
                password=item.get("disk_pass", "")
            )
            
            # 创建唯一ID
            disk_id = item.get("disk_id", "")
            if disk_id:
                unique_id = f"hunhepan-{disk_id}"
            else:
                unique_id = f"hunhepan-{i}"
            
            # 解析时间
            shared_time = item.get("shared_time", "")
            dt = None
            if shared_time:
                try:
                    dt = datetime.strptime(shared_time, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    pass
            
            # 创建搜索结果
            result = SearchResult(
                unique_id=unique_id,
                channel=self.name(),
                title=self._clean_title(item.get("disk_name", "")),
                content=item.get("files", ""),
                datetime=dt,
                links=[link]
            )
            
            results.append(result)
        
        return results

    async def _do_search(self, keyword: str, ext: Dict[str, Any] = None) -> List[SearchResult]:
        """
        实际的搜索实现
        """
        async with aiohttp.ClientSession() as session:
            # 只请求hunhepan API
            items = await self._search_api(session, self.HUNHEPAN_API, keyword)
            
            # 去重处理
            unique_items = self._deduplicate_items(items)
            
            # 转换为标准格式
            return self._convert_results(unique_items)

    def search(self, keyword: str, ext: Dict[str, Any] = None) -> List[SearchResult]:
        """
        执行搜索，返回标准化的SearchResult列表
        """
        try:
            return asyncio.run(self._do_search(keyword, ext))
        except Exception as e:
            # 发生异常时返回空列表而不是抛出异常
            return []