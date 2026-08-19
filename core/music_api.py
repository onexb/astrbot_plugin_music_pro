import aiohttp
from astrbot.api import logger


class MusicAPI:
    """网易云音乐 Nodejs API 封装"""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._session = None

    async def _get_session(self):
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def search(self, keyword: str, limit: int = 10) -> list:
        session = await self._get_session()
        url = f"{self.base_url}/search"
        params = {"keywords": keyword, "limit": limit}

        try:
            async with session.get(url, params=params) as resp:
                data = await resp.json()

                if data.get("code") != 200:
                    logger.error(f"搜索失败: {data}")
                    return []

                songs = []
                for item in data.get("result", {}).get("songs", []):
                    album = item.get("album", {})
                    artists = item.get("artists", [])

                    artist = artists[0]["name"] if artists else "未知歌手"

                    songs.append({
                        "id": item.get("id"),
                        "name": item.get("name", "未知歌曲"),
                        "artist": artist,
                        "cover": "",
                    })
                return songs

        except Exception as e:
            logger.error(f"搜索异常: {e}")
            return []

    async def get_cover(self, song_id: int) -> str:
        """通过 meting API 获取封面真实地址"""
        session = await self._get_session()
        info_url = f"https://api.qijieya.cn/meting/?type=song&id={song_id}"
        try:
            async with session.get(info_url) as resp:
                data = await resp.json()
                if not isinstance(data, list) or len(data) == 0:
                    return ""
                pic_url = data[0].get("pic", "")
                if not pic_url:
                    return ""

            # 请求 pic 链接，跟随重定向拿到真实图片地址
            async with session.get(pic_url, allow_redirects=True) as resp:
                if resp.status == 200:
                    return str(resp.url)
        except Exception as e:
            logger.error(f"获取封面失败: {e}")
        return ""

    async def get_song_url(self, song_id: int) -> str:
        """获取歌曲播放地址"""
        session = await self._get_session()
        url = f"{self.base_url}/song/url"
        params = {"id": song_id, "br": 999000}

        try:
            async with session.get(url, params=params) as resp:
                data = await resp.json()

                if data.get("code") != 200:
                    logger.error(f"获取音源失败: {data}")
                    return ""

                songs = data.get("data", [])
                if not songs:
                    return ""
                return songs[0].get("url", "") or ""

        except Exception as e:
            logger.error(f"获取音源异常: {e}")
            return ""

    @staticmethod
    def format_search_result(songs: list) -> str:
        lines = ["Nodejs网易云点歌"]
        for i, s in enumerate(songs, 1):
            lines.append(f"{i}. {s['name']} - {s['artist']}")
        lines.append("──────────────")
        lines.append("回复数字选择歌曲")
        return "\n".join(lines)

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
