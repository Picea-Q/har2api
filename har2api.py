"""har2api - 把一份抓包（HAR）读成一张接口清单。

用法:
    python har2api.py examples/sample.har
    python har2api.py examples/sample.har -o out.md
"""

import argparse
import json
import os
import sys
from collections import OrderedDict
from urllib.parse import urlsplit

VERSION = "0.1.0"

SENSITIVE_HEADERS = ("authorization", "cookie", "x-token", "x-sign", "sign", "token")


def load_entries(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "log" not in data or "entries" not in data["log"]:
        raise ValueError("这不是标准的 HAR 文件：缺少 log.entries")
    return data["log"]["entries"]


def to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def body_fields(entry):
    post = (entry.get("request") or {}).get("postData") or {}
    text = post.get("text")
    if not text:
        return ""
    try:
        payload = json.loads(text)
    except (TypeError, ValueError):
        return ""
    if isinstance(payload, dict):
        return ", ".join(list(payload.keys())[:8])
    return ""


def collect(entries):
    apis = OrderedDict()
    for entry in entries:
        req = entry.get("request") or {}
        url = req.get("url") or ""
        parts = urlsplit(url)
        method = (req.get("method") or "GET").upper()
        key = (method, f"{parts.scheme}://{parts.netloc}", parts.path or "/")

        item = apis.setdefault(key, {
            "count": 0, "status": set(), "time": [], "auth": set(), "fields": set(),
        })
        item["count"] += 1

        resp = entry.get("response") or {}
        if resp.get("status") is not None:
            item["status"].add(to_int(resp.get("status"), -1))

        item["time"].append(to_int(entry.get("time_ms", entry.get("time")), 0))

        for header in (req.get("headers") or []):
            name = header.get("name") or ""
            if name.lower() in SENSITIVE_HEADERS:
                item["auth"].add(name)

        fields = body_fields(entry)
        if fields:
            item["fields"].add(fields)

    return apis


def render(apis, source):
    lines = []
    lines.append(f"# 接口清单：{os.path.basename(source)}")
    lines.append("")
    lines.append(f"共 {len(apis)} 个接口，{sum(item['count'] for item in apis.values())} 条请求。")
    lines.append("")
    lines.append("| # | 方法 | 域名 | 路径 | 次数 | 状态码 | 平均耗时 | 鉴权头 | 请求体字段 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for idx, ((method, host, path), item) in enumerate(apis.items(), start=1):
        times = [t for t in item["time"] if t > 0]
        avg = f"{sum(times) / len(times):.0f} ms" if times else "-"
        status = ", ".join(str(s) for s in sorted(item["status"])) or "-"
        auth = ", ".join(sorted(item["auth"])) or "-"
        fields = " / ".join(sorted(item["fields"])) or "-"
        lines.append(
            f"| {idx} | {method} | {host} | {path} | {item['count']} | {status} | {avg} | {auth} | {fields} |"
        )
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="把 HAR 抓包转成接口清单（Markdown）")
    parser.add_argument("har", help="HAR 文件路径")
    parser.add_argument("-o", "--output", help="输出文件，默认打印到屏幕")
    parser.add_argument("-V", "--version", action="version", version=f"har2api {VERSION}")
    args = parser.parse_args(argv)

    try:
        entries = load_entries(args.har)
    except FileNotFoundError:
        print(f"找不到文件: {args.har}", file=sys.stderr)
        return 2
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"HAR 解析失败: {exc}", file=sys.stderr)
        return 2

    markdown = render(collect(entries), args.har)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"已写入 {args.output}")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
