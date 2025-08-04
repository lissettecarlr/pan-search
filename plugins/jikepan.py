import requests
from typing import List, Dict, Any

# 将上一级目录路径添加到系统路径
import sys
import os
import requests
from typing import List, Dict, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import SearchResult, Link
from plugin_base import BasePanPlugin
import re

class JikepanPlugin(BasePanPlugin):
    def name(self) -> str:
        return "jikepan"

    def priority(self) -> int:
        return 2

    def search(self, keyword: str, ext: Dict[str, Any] = None) -> List[SearchResult]:
        url = "https://api.jikepan.xyz/search"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json",
            "referer": "https://jikepan.xyz/"
        }
        payload = {
            "name": keyword,
            "is_all": False
        }
        if ext and isinstance(ext, dict) and ext.get("is_all") is True:
            payload["is_all"] = True
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            data = resp.json()
            if data.get("msg") != "success":
                return []
            results = []
            for idx, item in enumerate(data.get("list", [])):
                title = item.get("name", "").strip()
                if not title:
                    continue
                unique_id = f"jikepan-{idx}"
                links = []
                for link in item.get("links", []):
                    link_type = self._determine_type_by_service(link.get("service", ""))
                    link_url = link.get("link", "")
                    password = link.get("pwd", "")
                    if link_type and link_url:
                        links.append(Link(type=link_type, url=link_url, password=password))
                if not links:
                    continue
                results.append(SearchResult(
                    unique_id=unique_id,
                    channel=self.name(),
                    title=title,
                    content="",
                    links=links,
                    tags=[]
                ))
            return results
        except Exception:
            return []

    def _determine_type_by_service(self, service: str) -> str:
        service = service.lower()
        if service == "baidu":
            return "baidu"
        if service == "aliyun":
            return "aliyun"
        if service == "xunlei":
            return "xunlei"
        if service == "quark":
            return "quark"
        if service == "189cloud":
            return "tianyi"
        if service == "115":
            return "115"
        if service == "123":
            return "123"
        if service == "weiyun":
            return "weiyun"
        if service == "pikpak":
            return "pikpak"
        if service == "lanzou":
            return "lanzou"
        if service == "jianguoyun":
            return "jianguoyun"
        if service == "caiyun":
            return "mobile"
        if service == "chengtong":
            return "chengtong"
        if service == "ed2k":
            return "ed2k"
        if service == "magnet":
            return "magnet"
        if service == "unknown":
            return ""
        return "others"

if __name__ == "__main__":
    plugin = JikepanPlugin()
    results = plugin.search("芙莉莲")
    print(results)