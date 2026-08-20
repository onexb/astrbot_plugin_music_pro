import asyncio
import json

from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Plain
from astrbot.core.message.components import Record
from astrbot.core.utils.session_waiter import (
    SessionController,
    session_waiter,
)

from .core.music_api import MusicAPI
from .core.card_signer import CardSigner


@register("music_pro", "一只小白", "点歌插件Pro", "v1.2.1")
class MusicPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        cfg = context.get_config() or {}
        base_url = cfg.get("nodejs_base_url", "http://139.9.223.233:3000")

        self.music = MusicAPI(base_url)
        self.signer = CardSigner()

    async def terminate(self):
        await self.music.close()
        await self.signer.close()

    # ---------- 发送歌曲 ----------
    async def _send_song(self, event: AstrMessageEvent, song: dict):
        """发送歌曲卡片或语音"""
        logger.info(f"正在获取《{song['name']}》的播放链接...")

        # 获取音频直链
        audio = await self.music.get_song_url(song["id"])
        if not audio:
            await event.send(event.plain_result("该歌曲暂无可用音源"))
            event.stop_event()
            return

        # 通过 meting API 获取封面
        cover = await self.music.get_cover(song["id"])

        # ===== CZ-API 签名 → json 段发 Ark =====
        from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
            AiocqhttpMessageEvent,
        )
        if isinstance(event, AiocqhttpMessageEvent):
            try:
                # 构造歌曲详情页跳转链接
                song_url = f"https://music.163.com/song?id={song['id']}"
                
                card = await self.signer.sign(
                    url=song_url,
                    audio=audio,
                    title=song["name"],
                    desc=song["artist"],
                    image=cover,
                    type_="163",
                )
                
                if card and card.get("view") == "music":
                    payloads = {
                        "message": [
                            {
                                "type": "json",
                                "data": {
                                    "data": json.dumps(card, ensure_ascii=False)
                                },
                            }
                        ]
                    }
                    if event.is_private_chat():
                        payloads["user_id"] = event.get_sender_id()
                        await event.bot.api.call_action("send_private_msg", **payloads)
                    else:
                        payloads["group_id"] = event.get_group_id()
                        await event.bot.api.call_action("send_group_msg", **payloads)
                    event.stop_event()
                    return
            except Exception as e:
                logger.warning(f"Ark 卡片发送失败，回退语音: {e}")

        # ===== 兜底：语音 =====
        try:
            await event.send(event.chain_result([
                Plain(f"{song['name']} - {song['artist']}"),
                Record.fromURL(audio),
            ]))
            event.stop_event()
        except Exception as e:
            logger.error(f"语音也失败: {e}")
            await event.send(event.plain_result(f"{song['name']} - {song['artist']}\n{audio}"))
            event.stop_event()

    # ---------- /点歌 ----------
    @filter.command("点歌")
    async def on_search(self, event: AstrMessageEvent):
        ''' /点歌 名称'''
        kw = event.message_str.replace("/点歌", "").strip()
        if not kw:
            yield event.plain_result("请输入歌名，例如：/点歌 天下")
            return

        songs = await self.music.search(kw)
        if not songs:
            yield event.plain_result(f"没有找到与「{kw}」相关的歌曲")
            return

        songs = songs[:10]
        yield event.plain_result(self.music.format_search_result(songs))

        # 等待用户选择
        @session_waiter(timeout=60)
        async def waiter(controller: SessionController, event: AstrMessageEvent):
            txt = event.message_str.strip()
            if not txt.isdigit():
                return
            idx = int(txt) - 1
            if idx < 0 or idx >= len(songs):
                return
            
            controller.stop()
            song = songs[idx]
            await self._send_song(event, song)

        try:
            await waiter(event)
        except TimeoutError:
            yield event.plain_result("点歌已超时，请重新发送 /点歌 歌名")
        
        event.stop_event()

    # ========== LLM 工具函数 ==========

    @filter.llm_tool()
    async def play_song(self, event: AstrMessageEvent, song_name: str):
        """当用户想听歌时，根据歌名搜索并播放音乐。
        
        Args:
            song_name (str): 歌曲名称，可包含歌手名
        """
        songs = await self.music.search(song_name)
        if not songs:
            return f"没有找到与「{song_name}」相关的歌曲"

        song = songs[0]
        audio = await self.music.get_song_url(song["id"])
        if not audio:
            return f"歌曲《{song['name']}》暂无可用音源"

        cover = await self.music.get_cover(song["id"])
        song_url = f"https://music.163.com/song?id={song['id']}"

        from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import (
            AiocqhttpMessageEvent,
        )
        if isinstance(event, AiocqhttpMessageEvent):
            try:
                card = await self.signer.sign(
                    url=song_url,
                    audio=audio,
                    title=song["name"],
                    desc=song["artist"],
                    image=cover,
                    type_="163",
                )
                if card and card.get("view") == "music":
                    payloads = {
                        "message": [
                            {
                                "type": "json",
                                "data": {
                                    "data": json.dumps(card, ensure_ascii=False)
                                },
                            }
                        ]
                    }
                    if event.is_private_chat():
                        payloads["user_id"] = event.get_sender_id()
                        await event.bot.api.call_action("send_private_msg", **payloads)
                    else:
                        payloads["group_id"] = event.get_group_id()
                        await event.bot.api.call_action("send_group_msg", **payloads)
                    return f"已为您播放《{song['name']}》- {song['artist']}"
            except Exception as e:
                logger.warning(f"LLM 点歌卡片失败: {e}")

        # 兜底：返回文本信息
        return f"{song['name']} - {song['artist']}\n{audio}"
