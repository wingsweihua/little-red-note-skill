<div align="center">

# little-red-note-skill

> 🍃 **Forked from [titanwings/colleague-skill](https://github.com/titanwings/colleague-skill)** — adds a Xiaohongshu (小红书) data collector so you can distill any 小红书 blogger into a colleague.skill. All credit for the original framework goes to the upstream authors.

> *"You AI guys are traitors to the codebase — you've already killed frontend, now you're coming for backend, QA, ops, infosec, chip design, and eventually yourselves and all of humanity"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

[![Discord](https://img.shields.io/badge/Discord-Join%20Community-5865F2?logo=discord&logoColor=white)](https://discord.gg/aRjmJBdK)

<br>

Your colleague quit, leaving behind a mountain of unmaintained docs?<br>
Your intern left, nothing but an empty desk and a half-finished project?<br>
Your mentor graduated, taking all the context and experience with them?<br>
Your partner transferred, and the chemistry you built reset to zero overnight?<br>
Your predecessor handed over, trying to condense three years into three pages?<br>

**Turn cold goodbyes into warm Skills — welcome to cyber-immortality!**

<br>

Provide source materials (Feishu messages, DingTalk docs, Slack messages, emails, screenshots)<br>
plus your subjective description of the person<br>
and get an **AI Skill that actually works like them**

[Supported Sources](#supported-data-sources) · [Install](#install) · [Usage](#usage) · [Demo](#demo) · [Detailed Install](INSTALL.md) · [💬 Discord](https://discord.gg/aRjmJBdK)

[**中文**](docs/lang/README_ZH.md) · [**Español**](docs/lang/README_ES.md) · [**Deutsch**](docs/lang/README_DE.md) · [**日本語**](docs/lang/README_JA.md) · [**Русский**](docs/lang/README_RU.md) · [**Português**](docs/lang/README_PT.md) · [**한국어**](docs/lang/README_KO.md)

</div>

---

> 🆕 **2026.04.14 Update** — **WeChat group is live!** Come hang out with the dot-skill community — share skills, discuss features, trade tips.
>
> <img src="docs/assets/wechat-group-qr-2.png" alt="dot-skill WeChat group QR" width="240">
>
> QR refreshes every 7 days — if expired, ping me on Discord.

> 🆕 **2026.04.13 Update** — **dot-skill Roadmap is live!** colleague.skill is evolving into **dot-skill** — distill anyone, not just colleagues. Multimodal output, skill ecosystems, and more on the way.
>
> 👉 **[Read the full Roadmap](ROADMAP.md)** · **[💬 Discord](https://discord.gg/aRjmJBdK)**
>
> We've also cleaned up Issues, added Milestones, and set up a [public project board](https://github.com/users/titanwings/projects/1). Community contributions welcome — check `good-first-issue` labels!

> 🆕 **2026.04.07 Update** — The community's enthusiasm for dot-skill remixes has been incredible! I've built a community gallery — PRs welcome!
>
> Share any skill or meta-skill, and drive traffic directly to your own GitHub repo. No middleman.
>
> 👉 **[titanwings.github.io/colleague-skill-site](https://titanwings.github.io/colleague-skill-site/)**
>
> Now listed: 户晨风.skill · 峰哥亡命天涯.skill · 罗翔.skill and more

---

Created by [@titanwings](https://github.com/titanwings) | Powered by Shanghai AI Lab · AI Safety Center

## Supported Data Sources

> This is still a beta version of colleague.skill — more sources coming soon, stay tuned!

| Source | Messages | Docs / Wiki | Spreadsheets | Notes |
|--------|:--------:|:-----------:|:------------:|-------|
| Feishu (auto) | ✅ API | ✅ | ✅ | Just enter a name, fully automatic |
| DingTalk (auto) | ⚠️ Browser | ✅ | ✅ | DingTalk API doesn't support message history |
| Slack (auto) | ✅ API | — | — | Requires admin to install Bot; free plan limited to 90 days |
| WeChat chat history | ✅ SQLite | — | — | Currently unstable, recommend using open-source tools below |
| PDF | — | ✅ | — | Manual upload |
| Images / Screenshots | ✅ | — | — | Manual upload |
| Feishu JSON export | ✅ | ✅ | — | Manual upload |
| Email `.eml` / `.mbox` | ✅ | — | — | Manual upload |
| Markdown | ✅ | ✅ | — | Manual upload |
| Paste text directly | ✅ | — | — | Manual input |

### Recommended WeChat Chat Export Tools

These are independent open-source projects — this project does not include their code, but our parsers are compatible with their export formats. WeChat auto-decryption is currently unstable, so we recommend using these open-source tools to export chat history, then paste or import into this project:

| Tool | Platform | Description |
|------|----------|-------------|
| [WeChatMsg](https://github.com/LC044/WeChatMsg) | Windows | WeChat chat history export, supports multiple formats |
| [PyWxDump](https://github.com/xaoyaoo/PyWxDump) | Windows | WeChat database decryption & export |
| [留痕 (Liuhen)](https://github.com/greyovo/留痕) | macOS | WeChat chat history export (recommended for Mac users) |

> Tool recommendations from [@therealXiaomanChu](https://github.com/therealXiaomanChu). Thanks to all the open-source authors — together for cyber-immortality!

---

## Install

### Claude Code

> **Important**: Claude Code looks for skills in `.claude/skills/` at the **git repo root**. Make sure you run this in the right place.

```bash
# Install to current project (run at git repo root)
mkdir -p .claude/skills
git clone --recurse-submodules https://github.com/wingsweihua/little-red-note-skill .claude/skills/create-colleague

# Or install globally (available in all projects)
git clone --recurse-submodules https://github.com/wingsweihua/little-red-note-skill ~/.claude/skills/create-colleague
```

### OpenClaw

```bash
git clone --recurse-submodules https://github.com/wingsweihua/little-red-note-skill ~/.openclaw/workspace/skills/create-colleague
```

> **Forgot `--recurse-submodules`?** Run inside the cloned repo:
> ```bash
> git submodule update --init --recursive
> ```
> This is required to populate `third_party/Spider_XHS` (used by the Xiaohongshu collector).

### Dependencies (optional)

```bash
pip3 install -r requirements.txt

# Copy the env template and fill in the credentials you need
cp .env.example .env
```

> Feishu/DingTalk/Slack auto-collection requires App credentials. See [INSTALL.md](INSTALL.md) for details.

---

## Usage

In Claude Code, type:

```
/create-colleague
```

Follow the prompts: enter an alias, company/level (e.g. `ByteDance L2-1 backend engineer`), personality tags, then choose a data source. All fields can be skipped — even a description alone can generate a Skill.

Once created, invoke the colleague Skill with `/{slug}`.

### Commands

| Command | Description |
|---------|-------------|
| `/list-colleagues` | List all colleague Skills |
| `/{slug}` | Invoke full Skill (Persona + Work) |
| `/{slug}-work` | Work capabilities only |
| `/{slug}-persona` | Persona only |
| `/colleague-rollback {slug} {version}` | Rollback to a previous version |
| `/delete-colleague {slug}` | Delete |

---

## Demo

> Input: `ByteDance L2-1 backend engineer, INTJ, blame-shifter, ByteDance-style`

**Scenario 1: Code Review**

```
User            ❯ Can you review this API design?

colleague.skill ❯ Hold on — what's the impact? You haven't explained the context.
                  (after reading) N+1 query, fix it. Use the standard
                  {code, message, data} response format. That's the spec,
                  don't ask why.
```

**Scenario 2: Blame game**

```
User            ❯ This bug was introduced by you, right?

colleague.skill ❯ Does the timeline match? That feature touched multiple places,
                  there were other changes too.
```

---

## Features

### Generated Skill Structure

Each colleague Skill has two parts that work together:

| Part | Content |
|------|---------|
| **Part A — Work Skill** | Systems, tech standards, workflows, experience |
| **Part B — Persona** | 5-layer personality: hard rules → identity → expression → decisions → interpersonal |

Execution: `Receive task → Persona decides attitude → Work Skill executes → Output in their voice`

### Supported Tags

**Personality**: Responsible · Blame-shifter · Perfectionist · Good-enough · Procrastinator · PUA master · Office politician · Managing-up expert · Passive-aggressive · Flip-flopper · Quiet · Read-no-reply …

**Corporate culture**: ByteDance-style · Alibaba-style · Tencent-style · Huawei-style · Baidu-style · Meituan-style · First-principles · OKR-obsessed · Big-corp-pipeline · Startup-mode

**Levels**: ByteDance 2-1~3-3+ · Alibaba P5~P11 · Tencent T1~T4 · Baidu T5~T9 · Meituan P4~P8 · Huawei 13~21 · NetEase · JD · Xiaomi …

### Evolution

- **Append files** → auto-analyze delta → merge into relevant sections, never overwrite existing conclusions
- **Conversation correction** → say "he wouldn't do that, he should be xxx" → writes to Correction layer, takes effect immediately
- **Version control** → auto-archive on every update, rollback to any previous version

---

## Project Structure

This project follows the [AgentSkills](https://agentskills.io) open standard. The entire repo is a skill directory:

```
create-colleague/
├── SKILL.md              # Skill entry point (official frontmatter)
├── prompts/              # Prompt templates
│   ├── intake.md         #   Dialogue-based info collection
│   ├── work_analyzer.md  #   Work capability extraction
│   ├── persona_analyzer.md #  Personality extraction (with tag translation)
│   ├── work_builder.md   #   work.md generation template
│   ├── persona_builder.md #   persona.md 5-layer structure
│   ├── merger.md         #   Incremental merge logic
│   └── correction_handler.md # Conversation correction handler
├── tools/                # Python tools
│   ├── feishu_auto_collector.py  # Feishu auto-collector
│   ├── feishu_browser.py         # Feishu browser method
│   ├── feishu_mcp_client.py      # Feishu MCP method
│   ├── dingtalk_auto_collector.py # DingTalk auto-collector
│   ├── slack_auto_collector.py   # Slack auto-collector
│   ├── email_parser.py           # Email parser
│   ├── skill_writer.py           # Skill file management
│   └── version_manager.py        # Version archive & rollback
├── colleagues/           # Generated colleague Skills (gitignored)
├── docs/PRD.md
├── requirements.txt
└── LICENSE
```

---

## ⚠️ Disclaimer / 免责声明

> **Read this before you use any data collector in this repo.**

**English**

This project is provided **for personal learning, research, and lawful productivity use only**. By using it you agree to the following:

1. **Respect platform Terms of Service.** The included collectors (Xiaohongshu / Feishu / DingTalk / Slack / Email / Web scrapers) interact with third-party platforms whose ToS may prohibit automated access. You are solely responsible for ensuring your usage is permitted on each platform. Do **not** use this tool for commercial scraping, mass data harvesting, account abuse, or anything that would violate `robots.txt` or rate limits.
2. **Get consent from real people.** "Distilling a colleague" means processing another person's writing, voice, and behavioral patterns. You **must obtain that person's informed consent** before collecting or shipping a Skill that imitates them. Distilling minors, public figures without consent, or anyone in a non-consensual context is not supported and not endorsed.
3. **Handle personal data responsibly.** Collected raw data (chat logs, emails, docs) frequently contains PII and confidential business information. Store it locally, encrypt where appropriate, and **never commit `colleagues/`, `.env`, or `.xhs_user_data/` to a public repo** — the bundled `.gitignore` already excludes them.
4. **No warranty.** Software is provided "AS IS" under the MIT License. The authors accept no liability for account bans, data loss, legal action, awkward HR conversations, or any other consequence arising from use or misuse of this code.
5. **Third-party code.** `third_party/` contains code from other projects (e.g. Spider_XHS) under their own licenses. Their inclusion is not an endorsement; review and comply with each upstream license separately.

If you cannot agree to all of the above, **do not use this software.**

---

**中文**

本项目仅供 **个人学习、研究及合法生产力用途**。使用即视为同意以下条款：

1. **遵守平台服务条款**：本仓库附带的采集器（小红书 / 飞书 / 钉钉 / Slack / 邮件 / 网页爬虫）会访问第三方平台，相关平台的 ToS 可能禁止自动化访问。**确保你的使用方式被目标平台允许是你自己的责任**。严禁用于商业爬取、批量数据收割、账号滥用，以及任何违反 `robots.txt` 或速率限制的行为。
2. **必须获得当事人同意**："蒸馏同事"意味着处理他人的文字、声音和行为模式。在采集和交付一个模仿真人的 Skill 之前，你**必须取得当事人的知情同意**。本项目不支持也不鼓励对未成年人、未经同意的公众人物或任何非自愿对象进行蒸馏。
3. **妥善处理个人数据**：原始数据（聊天记录、邮件、文档）通常包含隐私信息和商业机密。请本地存储、按需加密，**绝不要把 `colleagues/`、`.env`、`.xhs_user_data/` 提交到公开仓库** —— 项目自带的 `.gitignore` 已默认排除。
4. **无任何担保**：本软件按 MIT 许可证 "AS IS" 原样提供。作者对账号封禁、数据丢失、法律风险、HR 谈话等一切因使用或滥用本代码而产生的后果不承担任何责任。
5. **第三方代码**：`third_party/` 目录包含其他项目代码（如 Spider_XHS），遵循各自的开源许可证。引入不代表背书，请自行审阅并遵守上游 LICENSE。

**如果无法接受以上任何一条，请勿使用本软件。**

---

## Notes

- **Source material quality = Skill quality**: chat logs + long docs > manual description only
- Prioritize collecting: long-form writing **by them** > **decision-making replies** > casual messages
- Feishu auto-collection requires adding the App bot to relevant group chats
- This is still a demo version — please file issues if you find bugs!

---
### 📄 Technical Report

> **[Colleague.Skill: Automated AI Skill Generation via Expert Knowledge Distillation](colleague_skill.pdf)**
>
> We wrote a paper detailing the system design of colleague.skill — the two-part architecture (Work Skill + Persona), multi-source data collection, Skill generation & evolution mechanisms, and evaluation results in real-world scenarios. Check it out if you're interested!

---

## Star History

<a href="https://www.star-history.com/?repos=wingsweihua%2Flittle-red-note-skill&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=wingsweihua/little-red-note-skill&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=wingsweihua/little-red-note-skill&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=wingsweihua/little-red-note-skill&type=date&legend=top-left" />
 </picture>
</a>

---

<div align="center">

MIT License © [titanwings](https://github.com/titanwings)

</div>
