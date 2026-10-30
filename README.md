# RedFox Bot 数据连接器

本地 MCP stdio 服务 + 可移植 Skill。Python 3.9 以上，无需安装依赖。

专属链接：https://redfox.hk/?source=gzh_zjbjb

## 已实现

- 抖音账号关键词搜索，接口与认证方式来自 RedFox 首页文档。
- 通用 POST 工具，可调用官方文档确认的 `/story/api/` 接口；请求体由调用方按官方文档提供。
- 返回原始 JSON，Agent 可继续分析与导出。

其他平台尚未逐个适配。定时监控、缓存、自动重试、Webhook、积分预算、字段标准化与多 Bot 共享部署尚未实现。MCP 使用 stdio，只能直接连接支持本地进程型 MCP 的客户端；远程或仅支持 HTTP MCP 的 Bot 需要另建远程服务。Grok Bot 和 Muse 的具体接入方式应以其产品实际支持为准。

## 配置

将 `.env.example` 复制为 `.env`，填入自己的密钥；或设置环境变量 `REDFOX_API_KEY`。环境变量优先。请勿公开 `.env`。

在支持 stdio MCP 的客户端配置（将路径替换为当前文件夹实际绝对路径）：

```json
{"mcpServers":{"redfox":{"command":"python3","args":["/项目绝对路径/redfox-bot-connector/server.py"]}}}
```

部分客户端的配置格式不同，以其文档为准。将 `skill/redfox-data` 复制到 Agent 支持的 Skills 目录后即可按其规则加载；这个项目并不会自动安装 Skill。

## 测试

```bash
python3 -m unittest discover -s tests
```

调用示例：让 Agent 搜索抖音上的 AI 工具账号，先查一页。通用接口先查 https://redfox.hk/apis 获取实际路径、参数和价格。每次调用可能产生费用，请在控制台确认余额。
