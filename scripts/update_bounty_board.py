#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

workspace = Path('/home/ubuntu/.openclaw/workspace')
board_repo = workspace / 'bounty-board'
tracked_path = board_repo / 'tracked-tasks.json'
data_path = board_repo / 'data.json'
TZ = timezone(timedelta(hours=8))


def gh_json(args):
    cmd = ['gh'] + args
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out)


def safe_issue(repo, number):
    try:
        return gh_json(['issue', 'view', str(number), '--repo', repo, '--json', 'number,title,state,url,comments,labels,assignees'])
    except Exception:
        return None


def safe_pr(repo, number):
    try:
        return gh_json(['pr', 'view', str(number), '--repo', repo, '--json', 'number,title,state,isDraft,url,reviewDecision,mergeStateStatus,comments'])
    except Exception:
        return None


def classify_stage(task, issue, prs):
    if task.get('stage') == 'dropped':
        return 'dropped', 100
    if prs:
        pr = prs[0]
        if pr.get('state') == 'MERGED':
            return 'merged', 90
        if pr.get('state') == 'OPEN':
            if pr.get('isDraft'):
                return 'draftPr', max(task.get('progress', 0), 55)
            return 'review', max(task.get('progress', 0), 72)
        if pr.get('state') == 'CLOSED':
            return 'review', max(task.get('progress', 0), 60)
    if issue and issue.get('state', '').upper() == 'OPEN' and task.get('repo') != 'Multi-source':
        return task.get('stage', 'candidate') if task.get('stage') != 'review' else 'claiming', max(task.get('progress', 0), 15)
    return task.get('stage', 'candidate'), task.get('progress', 0)


def main():
    tracked = json.loads(tracked_path.read_text(encoding='utf-8'))
    tasks = []
    summary = {
        'active': 0,
        'watching': 0,
        'waitingReview': 0,
        'waitingPayment': 0,
        'pipeline': {'claimed': 0, 'draftPr': 0, 'review': 0, 'merged': 0, 'paid': 0},
        'earnings': {'locked': '0', 'pending': '0', 'paid': '0', 'lockedUsdEst': 0, 'pendingUsdEst': 0, 'paidUsdEst': 0},
        'risk': {'high': 0, 'medium': 0, 'low': 0}
    }

    pending_tokens = []

    for task in tracked['tasks']:
        issue = None
        prs = []
        item = dict(task)
        if task.get('issueNumber') and task.get('repo') != 'Multi-source':
            issue = safe_issue(task['repo'], task['issueNumber'])
            if issue:
                item['issueState'] = issue.get('state')
                item.setdefault('links', {})['issue'] = issue.get('url')
                item['status'] = issue.get('state', item.get('status', 'OPEN')).title()
                item['comments'] = issue.get('comments', 0)
        for pr_ref in task.get('linkedPrs', []):
            pr = safe_pr(pr_ref['repo'], pr_ref['number'])
            if pr:
                prs.append(pr)
        if prs:
            pr = prs[0]
            item.setdefault('links', {})['pr'] = pr.get('url')
            if pr.get('state') == 'MERGED':
                item['status'] = 'Merged'
            elif pr.get('state') == 'OPEN' and pr.get('isDraft'):
                item['status'] = 'Draft PR opened'
            elif pr.get('state') == 'OPEN':
                item['status'] = f"Open PR / {pr.get('reviewDecision') or 'waiting review'}"
            else:
                item['status'] = pr.get('state', item.get('status', 'Unknown'))
            item['prState'] = pr.get('state')
            item['reviewDecision'] = pr.get('reviewDecision')
        stage, progress = classify_stage(task, issue, prs)
        item['stage'] = stage
        item['progress'] = progress

        if stage in ('draftPr', 'review', 'merged', 'paid'):
            summary['active'] += 1
        elif stage in ('candidate', 'sourcing', 'claiming'):
            summary['watching'] += 1
        if stage == 'review':
            summary['waitingReview'] += 1
        if stage == 'paid':
            summary['waitingPayment'] = 0
        if stage in summary['pipeline']:
            summary['pipeline'][stage] += 1

        rl = item.get('riskLevel', 'low')
        if rl in summary['risk']:
            summary['risk'][rl] += 1

        payout = item.get('payout')
        usd_est = float(item.get('payoutUsdEst') or 0)
        if payout and stage in ('draftPr', 'review', 'merged'):
            pending_tokens.append(payout)
            summary['earnings']['pendingUsdEst'] += usd_est
        if payout and stage == 'paid':
            summary['earnings']['paidUsdEst'] += usd_est

        tasks.append(item)

    summary['earnings']['pending'] = ', '.join(pending_tokens) if pending_tokens else '0'
    summary['earnings']['locked'] = '0' if summary['earnings']['lockedUsdEst'] == 0 else str(summary['earnings']['lockedUsdEst'])
    summary['earnings']['paid'] = '0' if summary['earnings']['paidUsdEst'] == 0 else str(summary['earnings']['paidUsdEst'])

    columns = {
        'claiming': [t for t in tasks if t.get('stage') == 'claiming'],
        'doing': [t for t in tasks if t.get('stage') in ('draftPr', 'review')],
        'review': [t for t in tasks if t.get('stage') == 'review'],
        'payment': [t for t in tasks if t.get('stage') == 'paid'],
        'watching': [t for t in tasks if t.get('stage') in ('candidate', 'sourcing')],
        'dropped': tracked.get('dropped', [])
    }

    data = {
        'updatedAt': datetime.now(TZ).strftime('%Y-%m-%d %H:%M GMT+8'),
        'timezone': 'Asia/Shanghai',
        'fx': tracked.get('fx', {}),
        'summary': summary,
        'columns': columns
    }

    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'updated {data_path}')


if __name__ == '__main__':
    main()
