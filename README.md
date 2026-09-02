# XUNBEE Message Inbox

**XUNBEE Message Inbox** is an OpenClaw and Codex Agent Skill for securely
reading a user-owned, short-lived XUNBEE email or SMS inbox, filtering messages,
and extracting the newest one-time password (OTP) or verification code with a
scoped XUNBEE API key.

Use it when an authorized agent needs to find an email verification code, read
an SMS OTP, filter messages by service or sender, or wait briefly for the newest
matching code. The Skill only reads messages belonging to the user's own XUNBEE
account and does not expose unrelated inbox items.

## At a glance

| Item | Details |
| --- | --- |
| Typical tasks | Email verification code retrieval, SMS OTP lookup, inbox filtering |
| Platforms | OpenClaw and Codex Agent Skills |
| Authentication | User-provided XUNBEE API key |
| Required scope | `messages:read` (read only) |
| Default API host | `https://cc.akuwan.cn` |
| Runtime | Python 3.10 or newer; no third-party Python packages |
| Data scope | The authenticated user's unexpired XUNBEE messages only |

## Requirements

- A XUNBEE account with access to the requested inbox.
- A user-issued API key with the fixed `messages:read` scope.
- Python 3.10 or newer, available as `python3` or `python`.

## Get a XUNBEE API key

1. Sign in to the [XUNBEE console](https://cc.akuwan.cn/admin/console/login).
2. Open [Notification Center](https://cc.akuwan.cn/admin/console/notifications) and
   select the **API Key** tab.
3. Under **消息读取密钥**, click **签发密钥**.
4. Enter a recognizable label and choose an expiry period from 1 to 365 days.
5. Copy the generated key immediately. It is displayed only once.

The key is created with the read-only `messages:read` scope. If it is lost,
expired, or exposed, revoke it in the XUNBEE console and issue a new one. Do not
paste a real key into chat, screenshots, URLs, source code, Git commits, shared
terminal history, or logs.

## Configure the key

The required variable is `XUNBEE_API_KEY`. The optional
`XUNBEE_BASE_URL` defaults to `https://cc.akuwan.cn` and should be changed only
when you trust the alternate XUNBEE HTTPS server.

### OpenClaw

The Skill declares `XUNBEE_API_KEY` as its `primaryEnv`, so it can be configured
through the OpenClaw Skills settings. If the key already exists in the OpenClaw
gateway environment, this SecretRef-style entry avoids copying the credential
into the Skill itself:

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

OpenClaw stores Skill settings under `~/.openclaw/openclaw.json`. Host-run Skill
credentials are injected only for the agent turn. A sandboxed agent needs its
own secure environment injection; host Skill settings are not automatically
copied into the sandbox.

### Direct script use

For a temporary PowerShell session:

```powershell
$env:XUNBEE_API_KEY = "<your-xunbee-api-key>"
python .\scripts\xunbee_inbox.py list --channel sms --limit 1 --pretty
Remove-Item Env:XUNBEE_API_KEY
```

For a temporary Bash-compatible session:

```bash
export XUNBEE_API_KEY="<your-xunbee-api-key>"
python3 scripts/xunbee_inbox.py list --channel sms --limit 1 --pretty
unset XUNBEE_API_KEY
```

The placeholders above are examples. Prefer your operating system, CI service,
or agent platform's secret manager for persistent configuration. Do not commit a
`.env` file containing the key; this repository's `.clawhubignore` excludes
common secret files as an additional safeguard.

## Verify the configuration safely

Run a low-impact read with the smallest useful result limit:

```bash
python3 scripts/xunbee_inbox.py list --channel sms --limit 1 --pretty
```

A successful request returns JSON. If there is no current SMS, the `data` array
is empty. An invalid, expired, revoked, or incorrectly scoped key returns a safe
error without printing the credential.

## Usage

List the newest SMS matching a service name:

```bash
python3 scripts/xunbee_inbox.py list \
  --channel sms \
  --keyword GitHub \
  --limit 1 \
  --pretty
```

List recent email messages matching a sender, subject, body phrase, or code:

```bash
python3 scripts/xunbee_inbox.py list \
  --channel email \
  --keyword verification \
  --limit 10 \
  --pretty
```

Print only the newest matching verification code and wait for up to 120 seconds:

```bash
python3 scripts/xunbee_inbox.py code \
  --channel sms \
  --keyword GitHub \
  --wait 120
```

When the Skill is installed in OpenClaw or Codex, ask naturally, for example:

> Find my newest GitHub SMS verification code in XUNBEE.

> Check my XUNBEE email inbox for the latest matching OTP and return only the code.

## Filters and output

| Option | Purpose |
| --- | --- |
| `--channel email\|sms` | Restrict results to email or SMS |
| `--source-ref VALUE` | Restrict results to a specific XUNBEE message source |
| `--keyword VALUE` | Case-insensitive search across source, sender, subject, content, and code |
| `--limit 1..100` | Bound the number of returned messages |
| `--wait SECONDS` | In `code` mode, poll until a matching code appears or time expires |
| `--pretty` | Format `list` output as readable JSON |

Results are newest first. `list` returns matching message data as JSON. `code`
prints only the newest matching extracted code. XUNBEE messages are short-lived
and are normally available only while unconfirmed and within the server's
retention window, typically 10 minutes.

## Credential and privacy model

| Question | Answer |
| --- | --- |
| Who supplies the credential? | The XUNBEE account owner |
| Where is it read from? | `XUNBEE_API_KEY` in the process environment or private Skill settings |
| Where is it sent? | The HTTPS `Authorization: Bearer` header to the configured XUNBEE host |
| Is it placed in the URL? | No |
| Does this repository store it? | No |
| Does the client receive QQ, Outlook, Gmail, or IMAP credentials? | No; mailbox authorization remains server-side |
| Can the Skill delete or acknowledge messages? | No; its API key is read only |

The client enforces HTTPS. It sends requests to `https://cc.akuwan.cn` by
default and never derives a destination from message content or another
untrusted source. Only set `XUNBEE_BASE_URL` to a server you explicitly trust.

## Troubleshooting

| Error or symptom | What to check |
| --- | --- |
| `XUNBEE_API_KEY is required` | Configure the key privately in the environment or OpenClaw Skill settings |
| `INVALID_MESSAGE_API_KEY` | The key may be invalid, expired, revoked, or missing `messages:read` |
| No matching verification code | Check `--channel`, `--keyword`, message arrival time, and the short retention window |
| `429` | Wait before retrying; avoid aggressive polling |
| `EMAIL_REFRESH_FAILED` | Reauthorize the bound mailbox or check provider connectivity in XUNBEE |
| `503` | The XUNBEE service or database is temporarily unavailable |

## Install from ClawHub

After the package is published, install it with:

```bash
clawhub install xunbee-message-inbox
```

Then configure `XUNBEE_API_KEY` before the first query.

## Repository layout

```text
.
├── SKILL.md                 # Agent instructions and OpenClaw metadata
├── README.md                # Human-facing setup and usage guide
├── agents/
│   └── openai.yaml          # Codex/OpenAI display metadata
├── scripts/
│   └── xunbee_inbox.py      # Dependency-free HTTPS inbox client
└── .clawhubignore           # Excludes caches, local env files, and build output
```

## FAQ

### Can OpenClaw retrieve an SMS OTP from XUNBEE?

Yes. With the account owner's read-only API key, the Skill can filter the
short-lived SMS inbox and return the newest matching OTP or verification code.

### Can it read email verification codes?

Yes. Email queries use the XUNBEE API. Bound-mailbox refresh and provider
authorization remain on the XUNBEE server; the local client never receives the
mailbox password or OAuth token.

### Does the Skill work without an API key?

No. It intentionally requires the user's own `messages:read` key and cannot
bypass XUNBEE account authorization.

### Does it read every inbox item?

It can list authorized messages, but agents should use a specific keyword and
the smallest useful limit. For verification-code requests, the Skill returns
only the newest matching code rather than unrelated messages.

## 中文快速说明

XUNBEE Message Inbox 是一个面向 OpenClaw 和 Codex 的 Agent Skill，用于在用户
本人授权的 XUNBEE 短期消息箱中查询邮件、短信、OTP 和验证码。它使用固定只读
权限 `messages:read`，默认仅通过 HTTPS 请求 `https://cc.akuwan.cn`。

配置步骤：

1. 登录 [XUNBEE 控制台](https://cc.akuwan.cn/admin/console/login)。
2. 进入[通知中心](https://cc.akuwan.cn/admin/console/notifications)的 **API Key** 页签。
3. 点击 **签发密钥**，设置名称和 1–365 天有效期。
4. 立即保存只显示一次的 Key，并私密配置为 `XUNBEE_API_KEY`。
5. 使用最小范围进行验证，例如：

```bash
python3 scripts/xunbee_inbox.py code --channel sms --keyword GitHub --wait 120
```

不要把真实 Key 发到聊天、截图、URL、代码仓库或日志中。Key 丢失或泄露后，应
立即在 XUNBEE 控制台撤销并重新签发。本 Skill 不会管理密钥、删除消息，也不会
直接获取 QQ、Outlook、Gmail 或 IMAP 的账号凭证。
