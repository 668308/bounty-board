# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 二娃聚合群 API

- Base URL: `http://88.222.241.169`
- Auth: `Authorization: Bearer <token>`
- Local token: `xXvErankGq0kU3Uio4pVQjstmPYbffLc`
- Daily limit: 100 requests/day
- Token expiry in doc: `2026-04-05`
- Admin contact from doc: WeChat `erwaNFT`

### 主要用途

- 飞书群聊 AI 总结查询
- CA（合约地址）反查来源群组
- 热门 CA 统计 / 最新 CA 记录
- 新闻快讯查询
- 配合 DexScreener / GMGN / Binance Web3 做链上分析

### 常用接口

#### 1) 根据 CA 查群组

- `GET /api/v1/group_ca/by-ca/{ca_address}`
- 用途：看到一个 CA，查哪些群在讨论

示例：

```bash
curl "http://88.222.241.169/api/v1/group_ca/by-ca/{CA}" \
  -H "Authorization: Bearer xXvErankGq0kU3Uio4pVQjstmPYbffLc"
```

#### 2) 查群组 CA 列表

- `GET /api/v1/group_ca`
- 常用参数：`ca` / `http` / `username` / `group_name` / `limit` / `skip` / `date` / `only_http`

#### 3) 热门 CA（按天）

- `GET /api/v1/group_ca/popular`
- 常用参数：`date=YYYY-MM-DD`、`min_count`、`group_name`

Linux 昨日示例：

```bash
curl "http://88.222.241.169/api/v1/group_ca/popular?date=$(date -d 'yesterday' +%F)" \
  -H "Authorization: Bearer xXvErankGq0kU3Uio4pVQjstmPYbffLc"
```

#### 4) 最新 CA 记录

- `GET /api/v1/group_ca/latest?limit=20`

#### 5) Token 使用情况

- `GET /api/v1/token/usage`
- 用途：看今日已用次数 / 剩余额度

```bash
curl "http://88.222.241.169/api/v1/token/usage" \
  -H "Authorization: Bearer xXvErankGq0kU3Uio4pVQjstmPYbffLc"
```

#### 6) 今日 / 指定日期快讯

- `GET /api/v1/newsflash/today`
- `GET /api/v1/newsflash/date/{date}`
- `GET /api/v1/newsflash/latest?limit=50`

#### 7) AI 群聊总结

- `GET /api/v1/summaries`
- 常用参数：`group_name` / `date` / `hour` / `limit`
- `date` 不传默认今天，但查询时最好显式写日期

示例：

```bash
curl "http://88.222.241.169/api/v1/summaries?group_name=crazySen聊天&date=2026-03-07&limit=5" \
  -H "Authorization: Bearer xXvErankGq0kU3Uio4pVQjstmPYbffLc"
```

### 群名映射速记

- 孙哥群 → `孙哥聊天` + `0xSun聊天`
- 镭射猫群 / LaserCat群 → `镭射猫聊天` + `镭射猫交流群`
- crazySen群 → `senCrazy群`
- 0xleng → `leng`
- 马丁森 → `martinSen`
- meta公子 → `meta群`
- AKA群 → `打新A群`
- GDC群 → `GDC社区`

### 配套外部分析工具

- DexScreener：`https://dexscreener.com/search?q={CA}`
- GMGN（只读代理）：`https://r.jina.ai/http://gmgn.ai/{chain}/token/{CA}`
  - `chain`: `sol` / `bsc` / `base` / `eth`
- Binance narrative：
  - `https://web3.binance.com/bapi/defi/v1/public/wallet-direct/buw/wallet/token/ai/narrative/query?chainId={chainId}&contractAddress={CA}`
- DexScreener token API：
  - `https://api.dexscreener.com/latest/dex/tokens/{ca}`

### 链识别速记

- `0x...` → 通常是 EVM 链
- 非 `0x` 且像 Base58 长串 → 通常是 Solana
- Binance chainId:
  - Solana → `CT_501`
  - BSC → `56`
  - Base → `8453`
  - Ethereum → `1`

### 工作流速记

1. 先用 `/api/v1/group_ca/by-ca/{CA}` 查是哪些群在聊
2. 再看 `/api/v1/group_ca/popular` 判断是否热
3. 用 `/api/v1/summaries` 拉群聊 AI 总结
4. 去 DexScreener / GMGN / Binance Web3 看链、流动性、叙事、安全性
5. 先查 `/api/v1/token/usage`，别把 100 次额度浪费掉

### 注意事项

- 这是 HTTP，不是 HTTPS
- 每日 100 次请求，别在 tight loop 里乱打
- 常见错误码：`401` / `403` / `404` / `429`
- 所有需要 token 的接口都走 Bearer Token
