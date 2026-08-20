import aiohttp
from astrbot.api import logger

CZ_API = "https://api.czcn.xyz/api/qqyykp"
OIAPI_URL = "https://oiapi.net/api/QQMusicJSONArk"


class CardSigner:
    """调用 OIAPI 或 CZ-API 生成音乐 Ark 卡片"""

    def __init__(self, sign_api: str = CZ_API):
        self.sign_api = sign_api.rstrip("/")
        self._session = None

    async def _get_session(self):
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def sign(self, *, url: str, audio: str, title: str, desc: str, image: str, type_: str = "163") -> dict | None:
        """先尝试 OIAPI，失败则用 CZ-API"""
        # 1) OIAPI
        oi_result = await self._sign_oiapi(
            url=url, audio=audio, title=title,
            desc=desc, image=image, type_=type_
        )
        if oi_result:
            return oi_result

        # 2) CZ-API fallback
        logger.info("OIAPI 失败，切换到 CZ-API")
        cz_result = await self._sign_cz(
            url=url, audio=audio, title=title,
            desc=desc, image=image, type_=type_
        )
        if cz_result:
            return cz_result

        return None

    async def _sign_oiapi(self, *, url: str, audio: str, title: str,
                          desc: str, image: str, type_: str) -> dict | None:
        """OIAPI 签名"""
        sess = await self._get_session()
        params = {
            "url": audio,
            "song": title,
            "singer": desc,
            "cover": image,
            "jump": url,
            "format": type_,
        }

        try:
            async with sess.get(OIAPI_URL, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                data = await resp.json()
        except Exception as e:
            logger.warning(f"OIAPI 请求失败: {e}")
            return None

        # OIAPI 返回结构: {"code": 1, "data": {...}}
        if isinstance(data, dict) and data.get("code") == 1:
            ark_data = data.get("data")
            if isinstance(ark_data, dict) and ark_data.get("view") == "music":
                return ark_data

        logger.warning(f"OIAPI 返回异常: {data}")
        return None

    async def _sign_cz(self, *, url: str, audio: str, title: str,
                       desc: str, image: str, type_: str) -> dict | None:
        """CZ-API 签名"""
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

        if isinstance(data, dict) and data.get("view") == "music":
            return data

        logger.warning(f"CZ 签名返回异常: {data}")
        return None

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
