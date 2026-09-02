# XUNBEE Message Inbox：邮件与短信验证码读取 Skill

[简体中文](README.md) | [English](README_EN.md)

XUNBEE Message Inbox 是面向 OpenClaw 和 Codex 的 Agent Skill。它通过用户本人
签发的只读 API Key，安全查询 XUNBEE 短期邮件与短信收件箱，按来源、发件人或
关键词筛选消息，并提取最新的一次性密码（OTP / one-time password）或验证码
（verification code）。

> **使用边界：** 本 Skill 仅用于查询用户本人授权的 XUNBEE 账号、邮箱和
> SIM/设备消息。禁止用于公共接码、号码池、批量注册、风控绕过、读取他人消息
> 或其他未经授权的自动化。

## 官方入口

| 资源 | 地址 | 用途 |
| --- | --- | --- |
| XUNBEE 官网 | [https://xunbee.akuwan.cn](https://xunbee.akuwan.cn) | 了解 XUNBEE 产品与服务 |
| 用户控制台 | [https://cc.akuwan.cn/admin/console/login](https://cc.akuwan.cn/admin/console/login) | 登录个人 XUNBEE 账号 |
| API Key 管理 | [https://cc.akuwan.cn/admin/console/notifications](https://cc.akuwan.cn/admin/console/notifications) | 签发或撤销消息读取 Key |
| API 服务地址 | `https://cc.akuwan.cn` | Skill 默认请求的 HTTPS 服务 |
| GitHub 源码 | [Zeraswang/xunbee-message-inbox](https://github.com/Zeraswang/xunbee-message-inbox) | 查看 Skill、脚本和更新记录 |

## 功能概览

| 能力 | 说明 |
| --- | --- |
| 查询邮件 | 读取 XUNBEE 账号中已绑定邮箱的短期消息 |
| 查询短信 | 读取本人已绑定 SIM/设备上传的短期短信 |
| 提取验证码 | 从消息中返回最新的数字或字母数字混合验证码 |
| 关键词筛选 | 按服务名、来源、发件人、主题、正文或验证码匹配 |
| 等待新消息 | 在指定时间内轮询，找到最新验证码后立即返回 |
| 最小化输出 | 验证码场景只返回匹配结果，不暴露无关收件箱内容 |
| 只读授权 | API Key 固定使用 `messages:read`，不能删除或确认消息 |

适合以下需求：

- 在 OpenClaw 中读取 XUNBEE 短信验证码或邮件验证码。
- 在 Codex 中查找最新 OTP，并只返回验证码。
- 按 `GitHub`、`Microsoft`、`支付宝` 等服务关键词筛选消息。
- 在自动化测试中等待本人账号收到新的登录或注册验证码。
- 通过 XUNBEE API 查询尚未确认且未过期的短期消息。

## 运行要求

- 已开通并可登录的 XUNBEE 个人账号。
- 用户本人签发、作用域为 `messages:read` 的 API Key。
- Python 3.10 或更高版本。
- 可用命令为 `python3` 或 `python`，不需要安装第三方 Python 包。
- 能够通过 HTTPS 访问 `https://cc.akuwan.cn`。

## 快速开始

### 1. 安装 Skill

发布到 ClawHub 后，可执行：

```bash
clawhub install xunbee-message-inbox
```

也可以从 GitHub 手动安装。OpenClaw 的 Windows PowerShell 示例：

```powershell
git clone https://github.com/Zeraswang/xunbee-message-inbox "$env:USERPROFILE\.openclaw\skills\xunbee-message-inbox"
```

安装到 Codex：

```powershell
git clone https://github.com/Zeraswang/xunbee-message-inbox "$env:USERPROFILE\.codex\skills\xunbee-message-inbox"
```

如果目标目录已经存在，请更新现有目录，不要在其中重复克隆一层同名文件夹。

### 2. 申请 XUNBEE API Key

1. 打开 [XUNBEE 用户控制台](https://cc.akuwan.cn/admin/console/login)并登录。
2. 进入[通知中心](https://cc.akuwan.cn/admin/console/notifications)。
3. 选择 **API Key** 页签。
4. 在“消息读取密钥”区域点击 **签发密钥**。
5. 填写便于识别的名称，例如“OpenClaw 消息读取”。
6. 设置 1–365 天的有效期。
7. 创建后立即复制并安全保存 Key。

API Key 只会在创建成功时显示一次。平台固定为它授予 `messages:read` 只读
作用域。如果 Key 丢失、过期或泄露，请在通知中心撤销旧 Key 并重新签发。

不要把真实 Key 放入：

- 聊天消息或 Agent 提示词；
- URL、截图或公开终端记录；
- `README.md`、`SKILL.md` 或其他源码；
- Git 提交、Issue、构建日志；
- 可公开下载的配置文件。

### 3. 配置 API Key

Skill 使用以下环境变量：

| 变量 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `XUNBEE_API_KEY` | 是 | 无 | 用户本人的 `messages:read` API Key |
| `XUNBEE_BASE_URL` | 否 | `https://cc.akuwan.cn` | 可信的 XUNBEE HTTPS 服务地址 |

除非正在连接自己明确配置并信任的 XUNBEE 实例，否则不要修改
`XUNBEE_BASE_URL`。客户端会拒绝非 HTTPS 地址。

**在 OpenClaw 中配置**

本 Skill 已在 `SKILL.md` 中把 `XUNBEE_API_KEY` 声明为 `primaryEnv`。
安装后可以在 OpenClaw 的 Skills 设置中为 `xunbee-message-inbox` 填写 API Key。

如果 OpenClaw Gateway 的环境中已经存在 `XUNBEE_API_KEY`，可以在
`~/.openclaw/openclaw.json` 中使用 SecretRef：

```json5
{
  skills: {
    entries: {
      "xunbee-message-inbox": {
        enabled: true,
        apiKey: {
          source: "env",
          provider: "default",
          id: "XUNBEE_API_KEY"
        }
      }
    }
  }
}
```

该设置适用于在宿主机运行的 Skill。OpenClaw 不会自动把宿主机 Skill
凭据复制到沙箱中；如果 Agent 在沙箱内执行，需要通过沙箱自己的安全机制注入
`XUNBEE_API_KEY`。

**在 Windows PowerShell 中临时配置**

下面的方式不会把真实 Key 直接写进命令历史：

```powershell
$xunbeeSecureKey = Read-Host "请输入 XUNBEE API Key" -AsSecureString
$env:XUNBEE_API_KEY = [System.Net.NetworkCredential]::new("", $xunbeeSecureKey).Password
Remove-Variable xunbeeSecureKey

python .\scripts\xunbee_inbox.py list --channel sms --limit 1 --pretty

Remove-Item Env:XUNBEE_API_KEY
```

关闭当前 PowerShell 窗口后，临时环境变量也会失效。

**在 Linux 或 macOS 中临时配置**

```bash
read -rsp "请输入 XUNBEE API Key: " XUNBEE_KEY_INPUT
echo
export XUNBEE_API_KEY="$XUNBEE_KEY_INPUT"
unset XUNBEE_KEY_INPUT

python3 scripts/xunbee_inbox.py list --channel sms --limit 1 --pretty

unset XUNBEE_API_KEY
```

长期配置时应优先使用操作系统、OpenClaw、CI/CD 平台或容器提供的 Secret
管理功能。本仓库的 `.clawhubignore` 会排除常见 `.env` 文件和缓存文件，但
这不能替代正确的密钥管理。

### 4. 验证配置

先执行帮助命令，确认 Python 和脚本路径正确：

```bash
python3 scripts/xunbee_inbox.py --help
```

再执行一次最小范围的只读查询：

```bash
python3 scripts/xunbee_inbox.py list --channel sms --limit 1 --pretty
```

如果 Key 有效但当前没有未过期短信，会返回：

```json
{
  "ok": true,
  "data": []
}
```

如果出现 `XUNBEE_API_KEY is required`，说明当前进程没有读取到环境变量。
如果出现 `INVALID_MESSAGE_API_KEY`，通常表示 Key 无效、已过期、已撤销或
不具备 `messages:read` 作用域。

## 在 OpenClaw 或 Codex 中使用

安装并配置后，可以直接使用自然语言：

> 使用 `$xunbee-message-inbox` 查找我最新的 GitHub 短信验证码，只返回验证码。

> 查询我的 XUNBEE 邮件收件箱，找主题包含“登录验证”的最新邮件。

> 等待 120 秒，查找来自 Microsoft 的最新邮件 OTP；没有收到就明确告诉我。

> 查询指定设备来源的最新短信，不要显示其他来源的消息。

Agent 应使用尽可能准确的关键词和最小结果数量。查询验证码时，应优先返回
最新匹配消息中的 `payload.code`，而不是完整展示无关正文。

## 命令行用法

以下命令均假设当前目录是 Skill 根目录。Windows 用户可以把 `python3`
替换为 `python`。

### 查询消息列表

查询最新一条包含 `GitHub` 的短信：

```bash
python3 scripts/xunbee_inbox.py list \
  --channel sms \
  --keyword GitHub \
  --limit 1 \
  --pretty
```

查询最近十封包含 `verification` 的邮件：

```bash
python3 scripts/xunbee_inbox.py list \
  --channel email \
  --keyword verification \
  --limit 10 \
  --pretty
```

限定具体消息来源：

```bash
python3 scripts/xunbee_inbox.py list \
  --channel sms \
  --source-ref air780e-example \
  --limit 5 \
  --pretty
```

### 只返回最新验证码

立即查找最新匹配验证码：

```bash
python3 scripts/xunbee_inbox.py code \
  --channel sms \
  --keyword GitHub
```

最多等待 120 秒：

```bash
python3 scripts/xunbee_inbox.py code \
  --channel email \
  --keyword Microsoft \
  --wait 120
```

`code` 模式成功时只向标准输出打印验证码，例如：

```text
729491
```

等待结束仍没有匹配结果时，命令会返回错误，不会猜测或编造验证码。

## 命令参数

### 全局参数

全局参数需要写在 `list` 或 `code` 子命令之前。

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--base-url URL` | `XUNBEE_BASE_URL` 或 `https://cc.akuwan.cn` | 指定可信的 XUNBEE HTTPS 服务 |
| `--timeout SECONDS` | `30` | 单次 HTTP 请求超时时间，必须大于 0 |

示例：

```bash
python3 scripts/xunbee_inbox.py --timeout 15 list --channel sms --limit 1
```

### 通用筛选参数

| 参数 | 可选值或范围 | 说明 |
| --- | --- | --- |
| `--channel` | `email`、`sms` | 只查询邮件或短信；省略时允许两种渠道 |
| `--source-ref` | 来源标识 | 限制到具体邮箱、设备或消息来源 |
| `--keyword` | 任意非空关键词 | 不区分大小写匹配渠道、来源、发件人、主题、正文和验证码 |
| `--limit` | 1–100 | 限制返回或扫描的消息数量 |

`list` 的 `--limit` 默认值为 20，`code` 的默认值为 10。

### `list` 专用参数

| 参数 | 说明 |
| --- | --- |
| `--pretty` | 使用缩进格式输出便于阅读的 JSON |

### `code` 专用参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `--wait SECONDS` | `0` | 最长等待时间；0 表示只查询一次 |
| `--poll-interval SECONDS` | `2` | 两次短期消息箱查询之间的间隔 |
| `--email-refresh-interval SECONDS` | `10` | 等待邮件时，服务端邮箱刷新的最小间隔 |

`--wait` 不能小于 0，两个轮询间隔必须大于 0。不要设置过短的轮询间隔，以免
触发限流。

## 输出格式

`list` 模式返回：

```json
{
  "ok": true,
  "data": [
    {
      "id": "msg_example",
      "channel": "sms",
      "source_ref": "air780e-example",
      "payload": {
        "sender": "GitHub",
        "content": "GitHub 验证码：729491",
        "code": "729491"
      }
    }
  ]
}
```

上面是脱敏示例。实际消息通常包含：

| 字段 | 说明 |
| --- | --- |
| `id` | XUNBEE 短期消息标识 |
| `channel` | `email` 或 `sms` |
| `source_ref` | 邮箱、设备或其他消息来源标识 |
| 时间字段 | 消息接收、创建或过期时间；以 API 实际响应为准 |
| `payload.code` | 自动提取的验证码，未识别到时可能为空 |
| `payload.content` | 邮件或短信正文 |
| `payload.sender` | 发件人或短信发送方 |
| `payload.subject` | 邮件主题 |
| `payload.received_at` | 邮件载荷中的接收时间 |
| `payload.content_truncated` | 邮件正文是否因长度限制被截断 |
| `payload.content_length` | 邮件原始正文长度 |

邮件纯文本正文最多保留 256,000 个字符。描述邮件为“完整正文”前，应检查
`content_truncated` 和 `content_length`。

## API 参考

底层只读接口：

```http
GET /api/v1/inbox/messages
Authorization: Bearer <XUNBEE_API_KEY>
```

Bash 调用示例：

```bash
curl --get "https://cc.akuwan.cn/api/v1/inbox/messages" \
  -H "Authorization: Bearer $XUNBEE_API_KEY" \
  --data-urlencode "channel=email" \
  --data-urlencode "keyword=GitHub" \
  --data-urlencode "limit=1"
```

查询参数：

| 参数 | 必填 | 说明 |
| --- | --- | --- |
| `channel` | 否 | `email` 或 `sms` |
| `source_ref` | 否 | 指定邮箱、设备或消息来源 |
| `keyword` | 否 | 按来源、发件人、主题、正文和验证码筛选 |
| `limit` | 否 | 返回数量；Skill 客户端限制为 1–100 |
| `refresh` | 否 | 邮件查询是否先刷新已绑定邮箱；`true` 或 `false` |

对于 `channel=email` 以及未指定渠道的混合查询，Skill 默认请求服务端刷新
已绑定邮箱。只有明确需要读取当前已同步的短期消息箱时，才使用
`refresh=false`。

## 邮件刷新与匹配机制

邮件查询与短信查询的行为不同：

1. 邮件查询先请求 XUNBEE 获取当前账号最新绑定邮箱的轻量未读列表。
2. 服务端按收件时间倒序排序，跳过已经完整入库的邮件。
3. 优先使用来源、发件人、主题和列表预览匹配 `keyword`。
4. 只下载命中候选的完整邮件详情，减少不必要的邮箱访问。
5. 如果关键词只能出现在正文中，服务端最多回查 10 封最新未读候选。
6. 单次请求最多新读取 20 封完整详情，因此应使用准确关键词和较小的
   `limit`。

IMAP 详情读取默认使用不会改变未读状态的方式。只有邮箱本身明确配置了
`mark_seen`，服务端才会把邮件标记为已读。等待邮件验证码时，客户端最多每
10 秒触发一次邮箱刷新，其余轮询只读取已经同步的短期消息箱。

短信查询不会连接任何邮箱。

## 消息保留与选择规则

- 结果按时间从新到旧排列。
- 关键词匹配不区分大小写。
- 消息通常只在“未确认且未过期”状态下可查询。
- 默认保留时间通常为 10 分钟；用户确认清除或消息到期后不再返回。
- 已知服务名或发件人时，应使用 `--keyword`，不要无筛选列出整个收件箱。
- 验证码请求应选择最新匹配消息并只返回 `payload.code`。
- 等待超时后应明确说明没有找到匹配的未过期消息，不能编造验证码。

## 凭据与隐私安全

| 问题 | 行为 |
| --- | --- |
| 谁提供 API Key | XUNBEE 账号本人 |
| Key 从哪里读取 | `XUNBEE_API_KEY` 环境变量或私密 Skill 设置 |
| Key 发送到哪里 | 配置的 XUNBEE 主机的 HTTPS `Authorization: Bearer` 请求头 |
| Key 是否进入 URL | 否 |
| Key 是否写入本仓库 | 否 |
| 客户端是否保存 Key | 否；只在当前进程中读取 |
| 是否获取 QQ、Outlook、Gmail 或 IMAP 密码 | 否；邮箱授权和凭据保留在 XUNBEE 服务端 |
| 是否能删除或确认消息 | 否；`messages:read` 仅允许读取 |

客户端默认只请求 `https://cc.akuwan.cn`，并强制要求 HTTPS。它不会从消息
正文、网页内容或其他不可信来源自动决定 API 地址。仅在用户明确配置并信任
目标服务器时才可使用 `XUNBEE_BASE_URL`。

## 常见错误与处理

| 错误或现象 | 原因与处理 |
| --- | --- |
| `XUNBEE_API_KEY is required` | 当前进程未配置 Key；在环境变量或 OpenClaw Skill 设置中私密配置 |
| `MISSING_BEARER_TOKEN` | 请求没有携带 Bearer Key；检查环境变量注入 |
| `INVALID_MESSAGE_API_KEY` | Key 无效、过期、已撤销或缺少 `messages:read` |
| `No matching verification code was found` | 没有匹配的未过期验证码；检查渠道、关键词、来源和到达时间 |
| `429` | 请求过于频繁；延长轮询间隔后重试 |
| `EMAIL_REFRESH_FAILED` | 已选邮箱全部刷新失败；检查邮箱授权和服务商连接 |
| `503` | XUNBEE 服务或数据库暂时不可用；稍后重试 |
| `XUNBEE base URL must be an absolute HTTPS URL` | `XUNBEE_BASE_URL` 不是完整 HTTPS 地址 |
| 返回空 `data` | Key 可能有效，但当前没有符合筛选条件的短期消息 |

## 常见问题

### 可以用 OpenClaw 读取 XUNBEE 短信验证码吗？

可以。安装 Skill 并配置用户本人的 `messages:read` API Key 后，可以按服务名、
来源或正文关键词筛选短期短信，并返回最新 OTP 或验证码。

### 可以读取邮件验证码吗？

可以。邮件查询通过 XUNBEE API 完成。已绑定邮箱的授权、OAuth Token 或 IMAP
密码保留在 XUNBEE 服务端，本地 Skill 客户端不会获得这些凭据。

### 没有 API Key 能使用吗？

不能。本 Skill 不会绕过 XUNBEE 身份验证，必须使用账号本人签发的只读 Key。

### 为什么刚收到的邮件没有立即出现？

邮件可能仍在服务端刷新过程中。使用 `code --wait 120` 可以等待新消息；同时
建议提供准确的 `--keyword`。等待邮件时，邮箱刷新最短间隔为 10 秒。

### 为什么已经看过的验证码查不到？

XUNBEE 消息是短期数据，通常保留 10 分钟。消息被确认清除或到期后不会继续
通过该只读接口返回。

### Skill 会把邮件标记为已读吗？

默认不会。服务端读取 IMAP 详情时保留未读状态；只有邮箱配置明确启用了
`mark_seen` 才会标记。

### Skill 能管理邮箱、设备或 API Key 吗？

不能。它只负责读取短期消息和提取验证码，不能绑定邮箱、修改设备、签发或撤销
Key、配置推送目标、确认或删除消息。

### Skill 会自动访问其他域名吗？

不会。默认 API 主机是 `https://cc.akuwan.cn`。自定义地址必须由用户通过
`XUNBEE_BASE_URL` 明确设置，并且必须是 HTTPS。

## 仓库结构

```text
.
├── SKILL.md                 # Agent 指令与 OpenClaw 运行元数据
├── README.md                # 当前中文安装和使用文档
├── README_EN.md             # English installation and usage guide
├── agents/
│   └── openai.yaml          # Codex/OpenAI 展示与调用元数据
├── scripts/
│   └── xunbee_inbox.py      # 无第三方依赖的 HTTPS 消息查询客户端
└── .clawhubignore           # 排除缓存、本地密钥和构建文件
```

## 发布信息

- Skill 名称：`xunbee-message-inbox`
- 展示名称：`XUNBEE Message Inbox`
- 建议分类：`integrations`、`communication`
- 建议主题：`xunbee`、`email`、`sms`、`otp`、`inbox`
- 官网：[https://xunbee.akuwan.cn](https://xunbee.akuwan.cn)
- 源码：[https://github.com/Zeraswang/xunbee-message-inbox](https://github.com/Zeraswang/xunbee-message-inbox)
