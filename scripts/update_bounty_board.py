#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

TZ = 'GMT+8'
workspace = Path('/home/ubuntu/.openclaw/workspace')
board_repo = workspace / 'bounty-board'
data_path = board_repo / 'data.json'

# Source of truth for now: current active tasks maintained here.
# This can be expanded later to read GitHub APIs / local state files.
data = {
    "updatedAt": datetime.now().strftime(f"%Y-%m-%d %H:%M {TZ}"),
    "timezone": "Asia/Shanghai",
    "summary": {
        "active": 1,
        "watching": 2,
        "waitingReview": 1,
        "waitingPayment": 0
    },
    "columns": {
        "claiming": [],
        "doing": [
            {
                "title": "RustChain bounty #1494",
                "repo": "Scottcjn/rustchain-bounties",
                "type": "Docs / API walkthrough",
                "payout": "28 RTC",
                "status": "Draft PR opened",
                "priority": "high",
                "links": {
                    "issue": "https://github.com/Scottcjn/rustchain-bounties/issues/1494",
                    "pr": "https://github.com/Scottcjn/Rustchain/pull/729"
                },
                "notes": [
                    "已发 claim",
                    "已 fork / 开分支 / 提交第一版修正",
                    "已在 bounty issue 回进度",
                    "关键修正：RTC 地址格式 + signed transfer 签名格式对齐真实后端"
                ],
                "nextActions": [
                    "继续盯 maintainer review",
                    "如有反馈，快速迭代 PR",
                    "争取 merge 后确认 bounty 归属"
                ]
            }
        ],
        "review": [
            {
                "title": "RustChain #1494 / PR #729",
                "status": "Waiting review",
                "ownerRisk": "有人抢先 claim 过，存在撞车风险",
                "links": {
                    "pr": "https://github.com/Scottcjn/Rustchain/pull/729"
                }
            }
        ],
        "payment": [],
        "watching": [
            {
                "title": "RustChain bounty #1493",
                "repo": "Scottcjn/rustchain-bounties",
                "type": "Docs / quickstart",
                "payout": "25 RTC",
                "status": "Candidate",
                "links": {
                    "issue": "https://github.com/Scottcjn/rustchain-bounties/issues/1493"
                },
                "notes": [
                    "比 1494 碰撞略小",
                    "依然是 RTC 支付",
                    "如果要抢，最好直接开 draft PR 而不是空口 claim"
                ]
            },
            {
                "title": "Open public bounty scan",
                "repo": "Multi-source",
                "type": "USD/RMB/token mixed",
                "payout": "Varies",
                "status": "Scanning",
                "notes": [
                    "持续筛选低复杂度、可快速交付的赏金任务",
                    "优先真实 payout、低碰撞、可落袋",
                    "token 单接受，但会过滤空气单"
                ]
            }
        ],
        "dropped": [
            {
                "title": "High-collision cash bounties",
                "status": "Not prioritized",
                "notes": [
                    "高竞争但 payout 清晰的单子很多已经卷烂",
                    "当前优先做更可落地、更容易成交的任务"
                ]
            }
        ]
    }
}

board_repo.mkdir(parents=True, exist_ok=True)
data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'updated {data_path}')
