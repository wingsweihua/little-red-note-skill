<div align="center">

# little-red-note-skill

> 🍃 Fork of [titanwings/colleague-skill](https://github.com/titanwings/colleague-skill) — adds **Xiaohongshu (小红书)** as a data source, so you can distill any 小红书 blogger into an AI Skill that writes in their voice.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)

</div>

---

## What this is

Feed in someone's writing → get a Claude Code Skill that talks like them.

This fork keeps the upstream framework intact (Feishu / DingTalk / Slack / Email collectors, Persona engine, version control) and **adds a Xiaohongshu pipeline**:

```
Xiaohongshu user_id  →  scrape notes  →  build colleague skill  →  /your-blogger
```

For the broader feature set (corporate-culture tags, evolution, rollback, etc.), see the [upstream README](https://github.com/titanwings/colleague-skill).

---

## Supported Data Sources

| Source | Messages | Docs | Notes |
|---|:-:|:-:|---|
| **Xiaohongshu (小红书)** | ✅ Notes + comments | — | **This fork.** Spider_XHS API or Playwright fallback |
| Feishu (auto) | ✅ API | ✅ | Upstream |
| DingTalk (auto) | ⚠️ Browser | ✅ | Upstream |
| Slack (auto) | ✅ API | — | Upstream |
| PDF / Image / Email / Markdown | ✅ | ✅ | Upstream — manual upload |
| Paste text | ✅ | — | Always works |

---

## Install

```bash
# Clone with submodules (Spider_XHS lives in third_party/)
git clone --recurse-submodules https://github.com/wingsweihua/little-red-note-skill \
  ~/.claude/skills/create-colleague

cd ~/.claude/skills/create-colleague
pip3 install -r requirements.txt

# For the XHS collector
cd third_party/Spider_XHS && pip3 install -r requirements.txt && npm install && cd ../..
cp .env.example .env   # then fill in COOKIES=...
```

> Forgot `--recurse-submodules`? Run `git submodule update --init --recursive` inside the repo.
>
> Full install guide for all data sources: [INSTALL.md](INSTALL.md)

---

## Usage

### Distill a Xiaohongshu blogger

```bash
# 1. Grab their notes (find user_id in the profile URL)
python3 tools/get_xhs_latest_notes.py \
  --user-id 61716aad000000000201caae \
  --limit 30 \
  --out ./colleagues/my-blogger/raw

# 2. Build the skill
python3 tools/build_colleague_from_xhs.py \
  --raw ./colleagues/my-blogger/raw \
  --slug my-blogger
```

Then in Claude Code: `/my-blogger`

### Distill a colleague (upstream flow)

In Claude Code:
```
/create-colleague
```
Walks you through alias → background → personality → data source.

| Command | Description |
|---|---|
| `/list-colleagues` | List all generated skills |
| `/{slug}` | Invoke skill (Persona + Work) |
| `/delete-colleague {slug}` | Delete |

---

## ⚠️ Disclaimer / 免责声明

**Read this before running any collector.**

This project is **for personal learning, research, and lawful productivity use only.** By using it you agree to:

1. **Respect platform Terms of Service.** Xiaohongshu / Feishu / DingTalk / Slack / Email collectors interact with platforms whose ToS may prohibit automated access. **You** are responsible for compliance. No commercial scraping, no mass harvesting, no rate-limit abuse.
2. **Get consent from real people.** Distilling someone means processing their writing and behavioral patterns. **Obtain informed consent** before shipping a skill that imitates a real person. Distilling minors or non-consenting public figures is not supported.
3. **Handle personal data responsibly.** Raw data often contains PII and confidential info. Store locally, never commit `colleagues/`, `.env`, or `.xhs_user_data/`. The bundled `.gitignore` already excludes them.
4. **No warranty.** Provided AS IS under MIT. No liability for account bans, data loss, legal action, or HR conversations.
5. **Third-party code.** `third_party/Spider_XHS` is under its upstream license — review and comply separately.

中文：仅供个人学习研究，须遵守目标平台 ToS，须获得当事人同意，不得用于商业批量爬取。详见上方英文版第 1–5 条。

**If you can't agree, don't use this software.**

---

<div align="center">

MIT License © Original framework by [titanwings](https://github.com/titanwings) · XHS extension by [wingsweihua](https://github.com/wingsweihua)

</div>
