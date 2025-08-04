import requests
from typing import List, Dict, Any
from models import SearchResult, Link
from plugin_base import BasePanPlugin

class OugePlugin(BasePanPlugin):
    def name(self) -> str:
        return "ouge"

    def priority(self) -> int:
        return 2

    def search(self, keyword: str, ext: Dict[str, Any] = None) -> List[SearchResult]:
        url = f"https://woog.nxog.eu.org/api.php/provide/vod?ac=detail&wd={keyword}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://woog.nxog.eu.org/",
            "Cache-Control": "no-cache"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            data = resp.json()
            if data.get("code") != 1:
                return []
            results = []
            for item in data.get("list", []):
                title = item.get("vod_name", "").strip()
                if not title:
                    continue
                unique_id = f"ouge-{item.get('vod_id')}"
                content = self._build_content(item)
                links = self._parse_links(item.get("vod_down_from", ""), item.get("vod_down_url", ""))
                tags = []
                if item.get("vod_year"):
                    tags.append(item["vod_year"])
                if item.get("vod_area"):
                    tags.append(item["vod_area"])
                results.append(SearchResult(
                    unique_id=unique_id,
                    channel=self.name(),
                    title=title,
                    content=content,
                    links=links,
                    tags=tags
                ))
            return results
        except Exception:
            return []

    def _build_content(self, item: dict) -> str:
        parts = []
        if item.get("vod_actor"):
            parts.append(f"主演: {item['vod_actor']}")
        if item.get("vod_director"):
            parts.append(f"导演: {item['vod_director']}")
        if item.get("vod_area"):
            parts.append(f"地区: {item['vod_area']}")
        if item.get("vod_year"):
            parts.append(f"年份: {item['vod_year']}")
        if item.get("vod_remarks"):
            parts.append(f"状态: {item['vod_remarks']}")
        return " | ".join(parts)

    def _parse_links(self, vod_down_from: str, vod_down_url: str) -> List[Link]:
        if not vod_down_from or not vod_down_url:
            return []
        from_parts = vod_down_from.split("$$$")
        url_parts = vod_down_url.split("$$$")
        min_len = min(len(from_parts), len(url_parts))
        links = []
        for i in range(min_len):
            link_type = self._map_ouge_type(from_parts[i])
            if not link_type:
                continue
            url_str = url_parts[i].strip()
            if not url_str or not self._is_valid_url(url_str):
                continue
            password = self._extract_password(url_str)
            links.append(Link(type=link_type, url=url_str, password=password))
        return links

    def _map_ouge_type(self, api_type: str) -> str:
        t = api_type.upper()
        return {
            "BD": "baidu",
            "KG": "quark",
            "UC": "uc",
            "ALY": "aliyun",
            "XL": "xunlei",
            "TY": "tianyi",
            "115": "115",
            "MB": "mobile",
            "WY": "weiyun",
            "LZ": "lanzou",
            "JGY": "jianguoyun",
            "123": "123",
            "PK": "pikpak"
        }.get(t, "")

    def _is_valid_url(self, url: str) -> bool:
        return url.startswith("http") or url.startswith("magnet:") or url.startswith("ed2k:")

    def _extract_password(self, url: str) -> str:
        import re
        m = re.search(r"\?pwd=([0-9a-zA-Z]+)", url)
        if m:
            return m.group(1)
        return ""