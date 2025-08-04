import requests
from typing import List, Dict, Any
from models import SearchResult, Link
from plugin_base import BasePanPlugin

class DuoduoPlugin(BasePanPlugin):
    def name(self) -> str:
        return "duoduo"

    def priority(self) -> int:
        return 2

    def search(self, keyword: str, ext: Dict[str, Any] = None) -> List[SearchResult]:
        # 这里只实现主列表页抓取，详情页可后续补充
        url = f"https://tv.yydsys.top/index.php/vod/search/wd/{keyword}.html"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://tv.yydsys.top/"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            if resp.status_code != 200:
                return []
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            for item in soup.select(".module-search-item"):
                title_tag = item.select_one(".video-info-header h3 a")
                if not title_tag:
                    continue
                title = title_tag.get_text(strip=True)
                unique_id = "duoduo-" + (title_tag.get("href") or "")
                # 这里只抓主信息，不抓详情页
                results.append(SearchResult(
                    unique_id=unique_id,
                    channel=self.name(),
                    title=title,
                    content="",
                    links=[],
                    tags=[]
                ))
            return results
        except Exception:
            return []