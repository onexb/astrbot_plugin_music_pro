import aiohttp
from astrbot.api import logger

CZ_API = "https://api.czcn.xyz/api/qqyykp"


class CardSigner:
    """调用 CZ-API 生成音乐 Ark 卡片"""

    def __init__(self, sign_api: str = CZ_API):
        self.sign_api = sign_api.rstrip("/")
        self._session = None

    async def _get_session(self):
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def sign(self, *, url: str, audio: str, title: str,
                   desc: str, image: str, type_: str = "163") -> dict | None:
        """调用 CZ-API 签名
        
        参数：
        - url: 跳转链接（歌曲详情页）
        - audio: 音乐文件（音频直链）
        - title: 卡片标题
        - desc: 卡片内容
        - image: 卡片图片
        - type_: 分享平台（163/qq/kugou/kuwo/migu/cz）
        """
        sess = await self._get_session()
        
        params = {
            "type": type_,
            "url": url,
            "audio": audio,
            "title": title,
            "desc": desc,
            "image": image,
        }

        try:
            async with sess.get(self.sign_api, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                data = await resp.json()
        except Exception as e:
            logger.warning(f"CZ 签名请求失败: {e}")
            return None

        if not isinstance(data, dict) or data.get("view") != "music":
            logger.warning(f"CZ 签名返回异常: {data}")
            return None

        return data

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
