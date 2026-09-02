# XUNBEE Message Inbox: Email and SMS verification code skill

[简体中文](README.md) | [English](README_EN.md)

XUNBEE Message Inbox is an Agent Skill for OpenClaw and Codex. With a
user-issued, read-only API key, it securely queries the user's short-lived
XUNBEE email and SMS inbox, filters messages by source, sender, or keyword, and
extracts the newest one-time password (OTP) or verification code.

> **Usage boundary:** This Skill may access only the XUNBEE account, mailboxes,
> SIM, and devices owned or explicitly authorized by the user. Do not use it for
> public SMS receiving, phone-number pools, bulk account registration, risk
> control bypass, other people's messages, or any unauthorized automation.

## Official links

| Resource | URL | Purpose |
| --- | --- | --- |
| XUNBEE website | [https://xunbee.akuwan.cn](https://xunbee.akuwan.cn) | Product and service information |
| User console | [https://cc.akuwan.cn/admin/console/login](https://cc.akuwan.cn/admin/console/login) | Sign in to a personal XUNBEE account |
| API key management | [https://cc.akuwan.cn/admin/console/notifications](https://cc.akuwan.cn/admin/console/notifications) | Issue or revoke a message-reading key |
| API service | `https://cc.akuwan.cn` | Default HTTPS service used by the Skill |
| GitHub source | [Zeraswang/xunbee-message-inbox](https://github.com/Zeraswang/xunbee-message-inbox) | Skill source, client script, and updates |

## Features

| Capability | Description |
| --- | --- |
| Read email | Query short-lived messages from mailboxes already bound to the XUNBEE account |
| Read SMS | Query short-lived SMS messages uploaded by the user's bound SIM/device |
| Extract codes | Return the newest numeric or alphanumeric verification code |
| Filter messages | Match a service, source, sender, subject, body, or code |
| Wait for arrival | Poll for a limited time and return as soon as a matching code arrives |
| Minimize disclosure | Return only the requested code instead of unrelated inbox content |
| Read-only access | Use the fixed `messages:read` scope; no delete or acknowledge permission |

Typical use cases include:

- Retrieve a XUNBEE SMS verification code from OpenClaw.
- Find the newest email OTP from Codex and return only the code.
- Filter messages for services such as `GitHub`, `Microsoft`, or another named
  sender.
- Wait for a sign-in or registration code sent to the user's own account during
  authorized automation or testing.
- Query unconfirmed and unexpired short-lived messages through the XUNBEE API.

## Requirements

- A personal XUNBEE account that the user can sign in to.
- A user-issued API key with the `messages:read` scope.
- Python 3.10 or newer.
- Either `python3` or `python` on `PATH`.
- HTTPS access to `https://cc.akuwan.cn`.

The bundled Python client uses only the standard library.

## Quick start

### 1. Install the Skill

After the package is published to ClawHub, install it with:

```bash
clawhub install xunbee-message-inbox
```

To install directly from GitHub into OpenClaw on Windows:

```powershell
git clone https://github.com/Zeraswang/xunbee-message-inbox "$env:USERPROFILE\.openclaw\skills\xunbee-message-inbox"
```

To install directly into Codex:

```powershell
git clone https://github.com/Zeraswang/xunbee-message-inbox "$env:USERPROFILE\.codex\skills\xunbee-message-inbox"
```

If the destination already exists, update that directory instead of cloning a
second nested copy.

### 2. Get a XUNBEE API key

1. Sign in to the [XUNBEE user console](https://cc.akuwan.cn/admin/console/login).
2. Open [Notification Center](https://cc.akuwan.cn/admin/console/notifications).
3. Select the **API Key** tab.
4. Under **消息读取密钥**, click **签发密钥**.
5. Enter a recognizable label such as “OpenClaw message reader.”
6. Choose an expiration period from 1 to 365 days.
7. Copy the generated key immediately and store it securely.

The key is shown only once and receives the fixed, read-only `messages:read`
scope. If it is lost, expired, or exposed, revoke it in Notification Center and
issue a replacement.

Never place a real key in:

- a chat message or agent prompt;
- a URL, screenshot, or shared terminal transcript;
- `README.md`, `SKILL.md`, or source code;
- a Git commit, issue, or build log;
- a publicly downloadable configuration file.

### 3. Configure the API key

The Skill uses these environment variables:

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `XUNBEE_API_KEY` | Yes | None | The user's API key with `messages:read` |
| `XUNBEE_BASE_URL` | No | `https://cc.akuwan.cn` | A trusted XUNBEE HTTPS service URL |

Do not change `XUNBEE_BASE_URL` unless you are connecting to an XUNBEE instance
that you explicitly configured and trust. The client rejects non-HTTPS URLs.

**Configure in OpenClaw**

`SKILL.md` declares `XUNBEE_API_KEY` as the Skill's `primaryEnv`. After
installation, you can enter the API key in OpenClaw's Skills settings for
`xunbee-message-inbox`.

If `XUNBEE_API_KEY` is already available in the OpenClaw Gateway environment,
reference it from `~/.openclaw/openclaw.json`:

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

This setting applies to a Skill running on the host. OpenClaw does not
automatically copy host Skill credentials into a sandbox. If the agent runs in
a sandbox, inject `XUNBEE_API_KEY` through that sandbox's own secure mechanism.

**Configure temporarily in Windows PowerShell**

The following method avoids writing the real key directly into command history:

```powershell
$xunbeeSecureKey = Read-Host "Enter the XUNBEE API key" -AsSecureString
$env:XUNBEE_API_KEY = [System.Net.NetworkCredential]::new("", $xunbeeSecureKey).Password
Remove-Variable xunbeeSecureKey

python .\scripts\xunbee_inbox.py list --channel sms --limit 1 --pretty

Remove-Item Env:XUNBEE_API_KEY
```

The temporary environment variable also disappears when that PowerShell
process closes.

**Configure temporarily in Linux or macOS**

```bash
read -rsp "Enter the XUNBEE API key: " XUNBEE_KEY_INPUT
echo
export XUNBEE_API_KEY="$XUNBEE_KEY_INPUT"
unset XUNBEE_KEY_INPUT

python3 scripts/xunbee_inbox.py list --channel sms --limit 1 --pretty

unset XUNBEE_API_KEY
```

For persistent configuration, prefer the secret manager provided by the
operating system, OpenClaw, CI/CD platform, or container runtime. The bundled
`.clawhubignore` excludes common `.env` and cache files, but ignore rules are
not a substitute for proper secret handling.

### 4. Verify the setup

First verify Python and the script path:

```bash
python3 scripts/xunbee_inbox.py --help
```

Then make a minimal read-only request:

```bash
python3 scripts/xunbee_inbox.py list --channel sms --limit 1 --pretty
```

If the key is valid but no unexpired SMS message is available, the result is:

```json
{
  "ok": true,
  "data": []
}
```

`XUNBEE_API_KEY is required` means the current process cannot see the
environment variable. `INVALID_MESSAGE_API_KEY` usually means the key is
invalid, expired, revoked, or missing the `messages:read` scope.

## Use with OpenClaw or Codex

After installation and configuration, use natural-language requests such as:

> Use `$xunbee-message-inbox` to find my newest GitHub SMS verification code.
> Return only the code.

> Search my XUNBEE email inbox for the newest message whose subject contains
> “sign-in verification.”

> Wait up to 120 seconds for my newest Microsoft email OTP. Clearly report if
> nothing arrives.

> Query SMS messages from the specified device source and do not show messages
> from other sources.

The agent should use the most specific useful keyword and the smallest result
limit. For a verification-code request, it should prefer `payload.code` from
the newest matching message instead of displaying unrelated message bodies.

## Command-line usage

The following commands assume the current directory is the Skill root. Windows
users may replace `python3` with `python`.

### List matching messages

Return the newest SMS message matching `GitHub`:

```bash
python3 scripts/xunbee_inbox.py list \
  --channel sms \
  --keyword GitHub \
  --limit 1 \
  --pretty
```

Return up to ten email messages matching `verification`:

```bash
python3 scripts/xunbee_inbox.py list \
  --channel email \
  --keyword verification \
  --limit 10 \
  --pretty
```

Restrict a query to one message source:

```bash
python3 scripts/xunbee_inbox.py list \
  --channel sms \
  --source-ref air780e-example \
  --limit 5 \
  --pretty
```

### Print only the newest code

Check once for the newest matching code:

```bash
python3 scripts/xunbee_inbox.py code \
  --channel sms \
  --keyword GitHub
```

Wait for up to 120 seconds:

```bash
python3 scripts/xunbee_inbox.py code \
  --channel email \
  --keyword Microsoft \
  --wait 120
```

On success, `code` prints only the code to standard output:

```text
729491
```

If the wait expires without a match, the command returns an error. It never
guesses or invents a verification code.

## Command options

### Global options

Global options must appear before the `list` or `code` subcommand.

| Option | Default | Description |
| --- | --- | --- |
| `--base-url URL` | `XUNBEE_BASE_URL` or `https://cc.akuwan.cn` | Use a trusted XUNBEE HTTPS service |
| `--timeout SECONDS` | `30` | Per-request HTTP timeout; must be greater than zero |

Example:

```bash
python3 scripts/xunbee_inbox.py --timeout 15 list --channel sms --limit 1
```

### Shared filter options

| Option | Values or range | Description |
| --- | --- | --- |
| `--channel` | `email` or `sms` | Restrict the query to email or SMS; omit to allow both |
| `--source-ref` | Source identifier | Restrict the query to a mailbox, device, or message source |
| `--keyword` | Non-empty text | Case-insensitive match across channel, source, sender, subject, content, and code |
| `--limit` | 1–100 | Bound the number of returned or scanned messages |

The default `--limit` is 20 for `list` and 10 for `code`.

### `list` option

| Option | Description |
| --- | --- |
| `--pretty` | Print indented, human-readable JSON |

### `code` options

| Option | Default | Description |
| --- | --- | --- |
| `--wait SECONDS` | `0` | Maximum wait time; zero makes one query |
| `--poll-interval SECONDS` | `2` | Delay between short-lived inbox queries |
| `--email-refresh-interval SECONDS` | `10` | Minimum server-side mailbox refresh interval while waiting |

`--wait` must not be negative, and both polling intervals must be greater than
zero. Do not use an unnecessarily short interval because it can trigger rate
limits.

## Output format

`list` returns JSON:

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
        "content": "GitHub verification code: 729491",
        "code": "729491"
      }
    }
  ]
}
```

The example is sanitized. Actual messages commonly include:

| Field | Description |
| --- | --- |
| `id` | XUNBEE short-lived message identifier |
| `channel` | `email` or `sms` |
| `source_ref` | Mailbox, device, or other source identifier |
| Time fields | Received, created, or expiration times; use the actual API response |
| `payload.code` | Extracted verification code; it may be empty |
| `payload.content` | Email or SMS text |
| `payload.sender` | Email sender or SMS sender |
| `payload.subject` | Email subject |
| `payload.received_at` | Received time stored in the email payload |
| `payload.content_truncated` | Whether a long email body was truncated |
| `payload.content_length` | Original email body length |

Plain-text email content is preserved up to 256,000 characters. Before
describing an email as complete, check `content_truncated` and
`content_length`.

## API reference

The underlying read-only endpoint is:

```http
GET /api/v1/inbox/messages
Authorization: Bearer <XUNBEE_API_KEY>
```

Bash example:

```bash
curl --get "https://cc.akuwan.cn/api/v1/inbox/messages" \
  -H "Authorization: Bearer $XUNBEE_API_KEY" \
  --data-urlencode "channel=email" \
  --data-urlencode "keyword=GitHub" \
  --data-urlencode "limit=1"
```

Query parameters:

| Parameter | Required | Description |
| --- | --- | --- |
| `channel` | No | `email` or `sms` |
| `source_ref` | No | Restrict to a mailbox, device, or message source |
| `keyword` | No | Match source, sender, subject, body, or code |
| `limit` | No | Result count; the Skill client accepts 1–100 |
| `refresh` | No | Refresh bound mailboxes before an email query; `true` or `false` |

For `channel=email` and combined queries without a channel, the Skill asks the
server to refresh bound mailboxes by default. Use `refresh=false` only when you
deliberately want to read the currently synchronized short-lived inbox without
another provider request.

## Email refresh and matching

Email and SMS queries behave differently:

1. For email, XUNBEE first retrieves lightweight unread summaries from the
   account's latest bound mailboxes.
2. The server sorts summaries newest first and skips messages that have already
   been fully ingested.
3. It first matches `keyword` against source, sender, subject, and preview.
4. It downloads full details only for selected candidates.
5. If a keyword may occur only in the body, the server checks at most ten of the
   newest unread candidates.
6. One request reads at most 20 new full message details, so use an accurate
   keyword and a small `limit`.

IMAP detail reads preserve the unread flag by default. A message is explicitly
marked as seen only when that mailbox was configured with `mark_seen`. While
waiting for an email code, the client triggers a mailbox refresh no more than
once every ten seconds and reads the already synchronized inbox between
refreshes.

SMS-only queries never connect to a mailbox.

## Retention and selection rules

- Results are ordered newest first.
- Keyword matching is case-insensitive.
- Messages are normally available only while unconfirmed and unexpired.
- The default retention window is typically ten minutes. Acknowledged or
  expired messages are no longer returned.
- When a service or sender is known, use `--keyword` instead of listing the
  entire inbox.
- For a code request, select the newest matching message and return
  `payload.code`.
- If a wait expires, report that no matching unexpired message was found. Never
  invent a code.

## Credentials and privacy

| Question | Behavior |
| --- | --- |
| Who provides the API key? | The XUNBEE account owner |
| Where is it read from? | `XUNBEE_API_KEY` or private Skill settings |
| Where is it sent? | The HTTPS `Authorization: Bearer` header to the configured XUNBEE host |
| Is it placed in the URL? | No |
| Is it written to this repository? | No |
| Does the client store it? | No; it reads the key only from the current process |
| Does it receive QQ, Outlook, Gmail, or IMAP passwords? | No; mailbox authorization remains on the XUNBEE server |
| Can it delete or acknowledge messages? | No; `messages:read` is read only |

The client uses `https://cc.akuwan.cn` by default and requires HTTPS. It never
derives an API destination from message content, a webpage, or another
untrusted source. Set `XUNBEE_BASE_URL` only to a server the user explicitly
trusts.

## Troubleshooting

| Error or symptom | Cause and resolution |
| --- | --- |
| `XUNBEE_API_KEY is required` | Configure the key privately in the environment or OpenClaw Skill settings |
| `MISSING_BEARER_TOKEN` | The request did not receive a Bearer key; check environment injection |
| `INVALID_MESSAGE_API_KEY` | The key is invalid, expired, revoked, or lacks `messages:read` |
| `No matching verification code was found` | Check the channel, keyword, source, arrival time, and retention window |
| `429` | Wait and use a longer polling interval |
| `EMAIL_REFRESH_FAILED` | Reauthorize the bound mailbox or check provider connectivity |
| `503` | The XUNBEE service or database is temporarily unavailable |
| `XUNBEE base URL must be an absolute HTTPS URL` | `XUNBEE_BASE_URL` is not a complete HTTPS URL |
| Empty `data` array | The key may be valid, but no current message matches the filters |

## FAQ

### Can OpenClaw retrieve an SMS OTP from XUNBEE?

Yes. After installing the Skill and configuring the account owner's
`messages:read` key, OpenClaw can filter short-lived SMS messages and return the
newest matching OTP or verification code.

### Can it read email verification codes?

Yes. Email queries use the XUNBEE API. Authorization tokens, OAuth credentials,
and IMAP passwords for bound mailboxes remain on the XUNBEE server and are
never returned to the local Skill client.

### Can the Skill work without an API key?

No. The Skill cannot bypass XUNBEE authentication and requires a read-only key
issued by the account owner.

### Why did a newly arrived email not appear immediately?

The server may still be refreshing the mailbox. Use `code --wait 120` and a
specific `--keyword`. While waiting, the minimum email refresh interval is ten
seconds.

### Why is an older verification code no longer available?

XUNBEE inbox messages are short-lived and are normally retained for ten
minutes. Acknowledged or expired messages are not returned by this read-only
endpoint.

### Does the Skill mark email as read?

Not by default. Server-side IMAP detail reads preserve unread state unless the
mailbox explicitly enables `mark_seen`.

### Can it manage mailboxes, devices, or API keys?

No. It reads short-lived messages and extracts codes. It cannot bind mailboxes,
modify devices, issue or revoke keys, configure push destinations, acknowledge
messages, or delete messages.

### Does it automatically contact other domains?

No. The default API host is `https://cc.akuwan.cn`. A custom host must be
explicitly set through `XUNBEE_BASE_URL` and must use HTTPS.

## Repository layout

```text
.
├── SKILL.md                 # Agent instructions and OpenClaw runtime metadata
├── README.md                # Complete Chinese guide
├── README_EN.md             # Complete English guide
├── agents/
│   └── openai.yaml          # Codex/OpenAI display and invocation metadata
├── scripts/
│   └── xunbee_inbox.py      # Dependency-free HTTPS inbox client
└── .clawhubignore           # Excludes caches, local secrets, and build output
```

## Publishing information

- Skill name: `xunbee-message-inbox`
- Display name: `XUNBEE Message Inbox`
- Suggested categories: `integrations` and `communication`
- Suggested topics: `xunbee`, `email`, `sms`, `otp`, and `inbox`
- Website: [https://xunbee.akuwan.cn](https://xunbee.akuwan.cn)
- Source: [https://github.com/Zeraswang/xunbee-message-inbox](https://github.com/Zeraswang/xunbee-message-inbox)
