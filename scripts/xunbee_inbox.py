from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://cc.akuwan.cn"
MESSAGES_PATH = "/api/v1/inbox/messages"


class InboxClientError(RuntimeError):
    pass


def _base_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if parsed.scheme != "https" or not parsed.netloc:
        raise InboxClientError("XUNBEE base URL must be an absolute HTTPS URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise InboxClientError(
            "XUNBEE base URL must not contain credentials, query, or fragment"
        )
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def _api_key() -> str:
    value = os.environ.get("XUNBEE_API_KEY", "").strip()
    if not value:
        raise InboxClientError("XUNBEE_API_KEY is required")
    return value


def _query_messages(
    args: argparse.Namespace,
    *,
    refresh: bool | None = None,
) -> list[dict[str, Any]]:
    query: dict[str, str | int] = {"limit": args.limit}
    if args.channel:
        query["channel"] = args.channel
    if args.source_ref:
        query["source_ref"] = args.source_ref
    if args.keyword:
        query["keyword"] = args.keyword
    if refresh is not None:
        query["refresh"] = "true" if refresh else "false"

    url = f"{_base_url(args.base_url)}{MESSAGES_PATH}?{urlencode(query)}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {_api_key()}",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=args.timeout) as response:
            payload = json.load(response)
    except HTTPError as exc:
        error_code = f"HTTP_{exc.code}"
        try:
            body = json.load(exc)
            error_code = str(body.get("detail", {}).get("error") or error_code)
        except (json.JSONDecodeError, AttributeError, TypeError):
            pass
        raise InboxClientError(
            f"XUNBEE request failed: {exc.code} {error_code}"
        ) from exc
    except (URLError, TimeoutError) as exc:
        reason = exc.reason if isinstance(exc, URLError) else exc
        raise InboxClientError(f"XUNBEE service is unavailable: {reason}") from exc

    if not isinstance(payload, dict) or payload.get("ok") is not True:
        raise InboxClientError("XUNBEE returned an invalid response")
    messages = payload.get("data")
    if not isinstance(messages, list):
        raise InboxClientError("XUNBEE response data must be a message list")
    return [item for item in messages if isinstance(item, dict)]


def _list_messages(args: argparse.Namespace) -> int:
    messages = _query_messages(args, refresh=args.channel != "sms")
    json.dump(
        {"ok": True, "data": messages},
        sys.stdout,
        ensure_ascii=False,
        indent=2 if args.pretty else None,
    )
    sys.stdout.write("\n")
    return 0


def _latest_code(args: argparse.Namespace) -> int:
    deadline = time.monotonic() + max(0, args.wait)
    next_email_refresh_at = 0.0
    while True:
        now = time.monotonic()
        refresh: bool | None = None
        if args.channel != "sms":
            refresh = now >= next_email_refresh_at
            if refresh:
                next_email_refresh_at = now + args.email_refresh_interval
        messages = _query_messages(args, refresh=refresh)
        for message in messages:
            payload = message.get("payload")
            code = payload.get("code") if isinstance(payload, dict) else None
            if isinstance(code, str) and code.strip():
                print(code.strip())
                return 0
        if time.monotonic() >= deadline:
            raise InboxClientError("No matching verification code was found")
        time.sleep(min(args.poll_interval, max(0.1, deadline - time.monotonic())))


def _add_filters(parser: argparse.ArgumentParser, *, default_limit: int) -> None:
    parser.add_argument("--channel", choices=("email", "sms"))
    parser.add_argument("--source-ref")
    parser.add_argument("--keyword")
    parser.add_argument(
        "--limit",
        type=int,
        choices=range(1, 101),
        default=default_limit,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read the short-lived XUNBEE message inbox"
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("XUNBEE_BASE_URL", DEFAULT_BASE_URL),
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser(
        "list", help="Return matching email/SMS messages as JSON"
    )
    _add_filters(list_parser, default_limit=20)
    list_parser.add_argument("--pretty", action="store_true")
    list_parser.set_defaults(handler=_list_messages)

    code_parser = subparsers.add_parser(
        "code", help="Print only the newest matching verification code"
    )
    _add_filters(code_parser, default_limit=10)
    code_parser.add_argument("--wait", type=float, default=0.0)
    code_parser.add_argument("--poll-interval", type=float, default=2.0)
    code_parser.add_argument("--email-refresh-interval", type=float, default=10.0)
    code_parser.set_defaults(handler=_latest_code)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.timeout <= 0:
        print("error: --timeout must be greater than zero", file=sys.stderr)
        return 2
    if (
        getattr(args, "wait", 0) < 0
        or getattr(args, "poll_interval", 1) <= 0
        or getattr(args, "email_refresh_interval", 1) <= 0
    ):
        print(
            "error: wait values must be non-negative and poll intervals must be positive",
            file=sys.stderr,
        )
        return 2
    try:
        return args.handler(args)
    except InboxClientError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
