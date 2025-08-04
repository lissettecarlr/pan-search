import requests
from typing import List, Dict, Any
from models import SearchResult, Link
from plugin_base import BasePanPlugin

class WanouPlugin(BasePanPlugin):
    def name(self) -> str:
        return "wanou"

    def priority(self) -> int:
        return 1

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
                unique_id = f"wanou-{item.get('vod_id')}"
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
            from_type = from_parts[i].strip()
            url_str = url_parts[i].strip()
            if not url_str:
                continue
            link_type = self._determine_link_type(from_type, url_str)
            if not link_type:
                continue
            password = self._extract_password(url_str)
            links.append(Link(type=link_type, url=url_str, password=password))
        return links

    def _determine_link_type(self, api_type: str, url: str) -> str:
        # 只实现常见类型，便于扩展
        if "baidu" in url:
            return "baidu"
        if "quark" in url:
            return "quark"
        if "aliyundrive" in url or "alipan" in url:
            return "aliyun"
        if "xunlei" in url:
            return "xunlei"
        if "cloud.189" in url:
            return "tianyi"
        if "115.com" in url:
            return "115"
        if "weiyun" in url:
            return "weiyun"
        if "lanzou" in url or "lanzo" in url:
            return "lanzou"
        if "jianguoyun" in url:
            return "jianguoyun"
        if "123pan" in url:
            return "123"
        if "mypikpak" in url:
            return "pikpak"
        if url.startswith("magnet:"):
            return "magnet"
        if url.startswith("ed2k:"):
            return "ed2k"
        return ""

    def _extract_password(self, url: str) -> str:
        import re
        m = re.search(r"\?pwd=([0-9a-zA-Z]+)", url)
        if m:
            return m.group(1)
        return ""