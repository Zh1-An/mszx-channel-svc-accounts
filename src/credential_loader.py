# -*- coding: utf-8 -*-
"""民生直销银行渠道服务账号清单加载。

校验账号命名（``svc_`` 前缀）、令牌前缀（``int_``）、环境取值，
并按系统聚合统计与最近到期日。
"""
from __future__ import annotations

import csv
import datetime as dt
import re
import sys
from collections import defaultdict
from typing import Dict, List

CHANNEL_NAME = "民生直销银行"
SYSTEM_PREFIX = "mszx"
ACCOUNT_NAME = re.compile(r"^svc_[a-z0-9_]+$")
TOKEN_PREFIX = "int_"
TOKEN_LEN = 32
ENVS = ("prod", "uat")
WARN_DAYS = 15


def load(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        if row.get("渠道") != CHANNEL_NAME:
            raise ValueError("清单混入其他渠道：%s" % row.get("渠道"))
    return rows


def mask(token: str) -> str:
    if len(token) <= len(TOKEN_PREFIX) + 8:
        return TOKEN_PREFIX + "****"
    return "%s%s****%s" % (TOKEN_PREFIX, token[len(TOKEN_PREFIX):len(TOKEN_PREFIX) + 4], token[-4:])


def validate(rows: List[Dict[str, str]]) -> List[str]:
    warnings: List[str] = []
    for idx, row in enumerate(rows, start=2):
        account = row["账号"]
        token = row["令牌"]
        if not ACCOUNT_NAME.match(account):
            warnings.append("第 %d 行 账号命名不合规：%s" % (idx, account))
        if SYSTEM_PREFIX not in account:
            warnings.append("第 %d 行 账号缺少系统前缀 %s：%s" % (idx, SYSTEM_PREFIX, account))
        if not token.startswith(TOKEN_PREFIX):
            warnings.append("第 %d 行 令牌前缀非 %s：%s" % (idx, TOKEN_PREFIX, mask(token)))
        if len(token) - len(TOKEN_PREFIX) != TOKEN_LEN:
            warnings.append("第 %d 行 令牌长度异常：%s" % (idx, mask(token)))
        if row["环境"] not in ENVS:
            warnings.append("第 %d 行 环境取值异常：%s" % (idx, row["环境"]))
    return warnings


def expiry_report(rows: List[Dict[str, str]], today: dt.date | None = None) -> List[str]:
    today = today or dt.date.today()
    out: List[str] = []
    for row in rows:
        due = dt.date.fromisoformat(row["过期日"])
        left = (due - today).days
        if left <= WARN_DAYS:
            out.append("%s 将于 %s 到期（剩 %d 天）" % (row["账号"], row["过期日"], left))
    return out


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("用法: python src/credential_loader.py accounts/service-accounts.csv")
        return 2
    rows = load(argv[1])
    per_system: Dict[str, int] = defaultdict(int)
    for row in rows:
        per_system[row["系统"]] += 1
    print("%s 共 %d 个服务账号" % (CHANNEL_NAME, len(rows)))
    for system, count in sorted(per_system.items()):
        print("  %s: %d" % (system, count))
    for line in expiry_report(rows):
        print("DUE  " + line)
    warnings = validate(rows)
    if warnings:
        for line in warnings:
            print("WARN " + line)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
