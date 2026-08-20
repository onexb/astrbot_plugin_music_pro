# 更新日志

## v1.3.0 (2026-08-20)

### 新增
- 新增 OIAPI 签名通道，优先使用 `oiapi.net` 生成 Ark 卡片，失败自动回退 CZ-API
- 插件配置改为官方推荐的 `AstrBotConfig` 注入方式

### 优化
- 简化卡片有效性判断，`sign` 方法内部已校验 `view == "music"`，外部只需判断返回值是否为 `None`
- 移除 `CardSigner` 中无用的 `_session` 连接池管理

### 修复
- 修复插件配置读取方式，改为从 `AstrBotConfig` 获取而非 `context.get_config()`


## v1.2.1 (2026-08-19)

### 修复
- 修复 `_send_song` 中使用 `yield` 导致语音兜底消息未被发送的问题，改用 `await event.send()` 直接发送
- 修复 `session_waiter` 中 `async for ... pass` 丢弃消息的问题，改为直接 `await` 调用


## v1.1.0 (2026-08-17)

### 优化
- 重构选歌逻辑，改用 `session_waiter` 替代手动状态管理
- 删除冗余的 `_cleanup_loop` 后台任务和 `user_states` 字典
- 抽取 `_send_song` 公共方法，点歌和 LLM 调用复用同一套发送逻辑

### 修复
- 修复私聊点歌后 LLM 二次回复的问题
- 在所有出口添加 `event.stop_event()`，防止事件继续传播

## v1.0.0 (2026-08-17)

### 新增
- 基础点歌功能：`/点歌 歌名`
- 网易云音乐 Ark 卡片分享
- 语音消息降级播放
- LLM 工具调用支持
- 选歌超时自动清理
