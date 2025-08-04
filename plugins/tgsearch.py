import re
import requests
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from models import SearchResult, Link
from plugin_base import BasePanPlugin

class TGSearchPlugin(BasePanPlugin):
    """
    以插件形式实现TG频道资源搜索，支持多频道，结果结构与其他插件统一
    ext 参数需包含 'channels'（list[str]），否则默认 tgsearchers2
    """

    def name(self) -> str:
        return "tgsearch"

    def priority(self) -> int:
        return 3  # TG频道优先级较低

    def search(self, keyword: str, ext: Dict[str, Any] = None) -> List[SearchResult]:
        channels = ["tgsearchers2"]
        if ext and "channels" in ext and isinstance(ext["channels"], list):
            channels = ext["channels"]
        results = []
        for channel in channels:
            results.extend(self._search_channel(channel, keyword))
        return results

    def _search_channel(self, channel: str, keyword: str) -> List[SearchResult]:
        url = f"https://t.me/s/{channel}?q={keyword}"
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
        except Exception:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        messages = soup.find_all("div", class_="tgme_widget_message_wrap")
        results = []
        for msg in messages:
            try:
                msg_id_tag = msg.find("a", class_="tgme_widget_message_date")
                if not msg_id_tag or not msg_id_tag.has_attr("href"):
                    continue
                msg_id = msg_id_tag["href"].split("/")[-1]
                date_str = msg_id_tag.find("time")["datetime"] if msg_id_tag.find("time") else ""
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if date_str else None
                title = msg.find("div", class_="tgme_widget_message_text")
                title_text = title.get_text(separator="\n") if title else ""
                content = title_text
                links = self._extract_links(title_text)
                result = SearchResult(
                    message_id=msg_id,
                    unique_id=f"{channel}_{msg_id}",
                    channel=self.name(),
                    datetime=dt,
                    title=title_text[:50],
                    content=content,
                    links=links,
                    tags=[]
                )
                results.append(result)
            except Exception:
                continue
        return results

    def _extract_links(self, text: str) -> List[Link]:
        # 支持常见网盘链接
        patterns = {
            "baidu": r"https?://pan\.baidu\.com/s/[a-zA-Z0-9]+",
            "aliyun": r"https?://www\.aliyundrive\.com/s/[a-zA-Z0-9]+",
            "quark": r"https?://pan\.quark\.cn/s/[a-zA-Z0-9]+",
            "tianyi": r"https?://cloud\.189\.cn/t/[a-zA-Z0-9]+",
            "115": r"https?://115\.com/s/[a-zA-Z0-9]+",
            "xunlei": r"https?://pan\.xunlei\.com/s/[a-zA-Z0-9]+",
            "123": r"https?://www\.123pan\.com/s/[a-zA-Z0-9]+",
            "uc": r"https?://drive\.uc\.cn/s/[a-zA-Z0-9]+",
        }
        links = []
        for typ, pat in patterns.items():
            for m in re.findall(pat, text):
                links.append(Link(type=typ, url=m))
        return links