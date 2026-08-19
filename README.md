# 点歌插件Pro

基于 AstrBot 的音乐点歌插件，支持网易云音乐搜索、播放和卡片分享。

## 功能

- `/点歌 歌名` - 搜索歌曲，回复数字选择
- 自动生成网易云音乐 Ark 卡片（点击跳转、在线播放）
- 卡片发送失败自动降级为语音消息
- 支持 LLM 调用（对 AI 说"放首歌"即可）

## 安装

### 方式一
https://github.com/onexb/astrbot_plugin_music_pro 安装

### 方式二：压缩包上传安装

1. 从 https://github.com/onexb/astrbot_plugin_music_pro 下载插件压缩包
2. 在 AstrBot 管理面板上传安装
3. 重启 AstrBot

## 配置

无需额外配置，默认使用内置 Node.js API 服务，可在插件界面->插件设置->nodejs_base_url设置其他的API

## 贡献指南

- Star 这个项目！（点右上角的星星，感谢支持！）
- 提交 Issue 报告问题
- 提出新功能建议
- 提交 Pull Request 改进代码

## 特别鸣谢

- [CZ-API](https://api.czcn.xyz/) - 提供 Ark 卡片签名服务，让网易云音乐卡片能正常发送
- [qijieya.cn](https://api.qijieya.cn/) - 提供音乐封面代理 API，网易云音乐封面获取
- [网易云音乐 Node.js API](https://www.npmjs.com/package/NeteaseCloudMusicApi) - 底层音乐搜索和播放链接获取
- AstrBot 插件框架 - 提供 LLM 工具调用和事件系统支持
- [AstrBot](https://github.com/AstrBotDevs/AstrBot) - 提供优秀的机器人框架

