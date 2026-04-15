#!/usr/bin/env python3
"""
Build a colleague skill from Xiaohongshu raw exports.

Input:
  - raw/notes_index.md
  - raw/notes/*.json

Output:
  - colleagues/{slug}/work.md
  - colleagues/{slug}/persona.md
  - colleagues/{slug}/meta.json
  - colleagues/{slug}/SKILL.md and siblings via skill_writer
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from skill_writer import create_skill


STOPWORDS = {
    "我们",
    "你们",
    "他们",
    "这个",
    "那个",
    "一个",
    "一些",
    "如果",
    "因为",
    "所以",
    "然后",
    "就是",
    "还是",
    "可以",
    "时候",
    "已经",
    "没有",
    "自己",
    "觉得",
    "今天",
    "现在",
    "其实",
    "真的",
    "非常",
    "一下",
    "什么",
    "这样",
    "那个",
    "还有",
    "以及",
    "并且",
    "或者",
    "话题",
    "xxx",
    "ps",
    "http",
    "https",
    "com",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build colleague skill from XHS raw notes")
    parser.add_argument(
        "--raw-dir",
        default="colleagues/xhs-weitiao/raw",
        help="Raw directory containing notes_index.md and notes/*.json",
    )
    parser.add_argument("--slug", default="weitiao", help="Target colleague slug")
    parser.add_argument("--name", default="微调", help="Colleague display name")
    parser.add_argument(
        "--base-dir",
        default="colleagues",
        help="Base colleagues directory used by skill_writer",
    )
    return parser.parse_args()


def read_notes(raw_dir: Path) -> list[dict[str, Any]]:
    notes_dir = raw_dir / "notes"
    if not notes_dir.exists():
        raise SystemExit(f"notes directory not found: {notes_dir}")

    note_files = sorted(notes_dir.glob("*.json"))
    notes: list[dict[str, Any]] = []
    for path in note_files:
        if path.name.startswith("latest_"):
            continue
        try:
            note = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(note, dict):
                notes.append(note)
        except Exception:
            continue

    if not notes:
        raise SystemExit(f"no note json found under: {notes_dir}")
    return notes


def extract_words(text: str) -> list[str]:
    text = re.sub(r"[#\[\]\(\)<>/\\|,.!?:;\"'`~\-_=+*]+", " ", text)
    chunks = re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z][A-Za-z0-9\-]{1,}", text)
    words: list[str] = []
    for c in chunks:
        w = c.strip().lower()
        if len(w) < 2 or w in STOPWORDS:
            continue
        words.append(w)
    return words


def parse_like(v: Any) -> int:
    if v is None:
        return 0
    s = str(v).strip().lower()
    if not s:
        return 0
    s = s.replace(",", "")
    if s.endswith("w"):
        try:
            return int(float(s[:-1]) * 10000)
        except ValueError:
            return 0
    m = re.search(r"\d+", s)
    return int(m.group(0)) if m else 0


def analyze(notes: list[dict[str, Any]], notes_index_text: str) -> dict[str, Any]:
    tag_counter: Counter[str] = Counter()
    word_counter: Counter[str] = Counter()
    lengths: list[int] = []
    likes: list[int] = []
    question_count = 0
    exclaim_count = 0
    haha_count = 0
    first_person_count = 0
    action_words = {"建议", "先", "可以", "需要", "流程", "步骤", "总结", "方法", "效率"}

    action_hits = 0

    for n in notes:
        title = str(n.get("title", "")).strip()
        content = str(n.get("content", "")).strip()
        text = f"{title}\n{content}"

        tags = n.get("tags", [])
        if isinstance(tags, list):
            for t in tags:
                t_str = str(t).strip()
                if t_str:
                    tag_counter[t_str] += 1

        for w in extract_words(text):
            word_counter[w] += 1
            if w in action_words:
                action_hits += 1

        lengths.append(len(content))
        likes.append(parse_like(n.get("likes")))
        question_count += content.count("？") + content.count("?")
        exclaim_count += content.count("！") + content.count("!")
        haha_count += content.count("哈哈")
        first_person_count += content.count("我")

    top_tags = [t for t, _ in tag_counter.most_common(8)]
    top_topics = [w for w, _ in word_counter.most_common(12)]

    avg_len = int(sum(lengths) / max(1, len(lengths)))
    avg_like = int(sum(likes) / max(1, len(likes)))

    style_traits: list[str] = []
    if first_person_count >= len(notes) * 3:
        style_traits.append("第一人称叙事明显，常以个人经历建立可信度")
    if action_hits >= len(notes) * 2:
        style_traits.append("方法论导向强，倾向给出可执行步骤和流程")
    if haha_count > 0:
        style_traits.append("语气有松弛感，偶尔用口语化表达缓和技术话题")
    if question_count > exclaim_count:
        style_traits.append("常通过提问组织内容，带有引导式表达")
    if not style_traits:
        style_traits.append("表达直接，偏经验总结与观点输出")

    return {
        "top_tags": top_tags,
        "top_topics": top_topics,
        "avg_len": avg_len,
        "avg_like": avg_like,
        "style_traits": style_traits,
        "note_count": len(notes),
        "notes_index_excerpt": notes_index_text[:500],
    }


def build_work_md(stats: dict[str, Any]) -> str:
    topics = "、".join(stats["top_topics"][:8]) if stats["top_topics"] else "AI、效率、科研与工程实践"
    tags = "、".join(stats["top_tags"][:6]) if stats["top_tags"] else "技术实战"
    return f"""## 负责方向
- AI/Agent 工作流与效率提升
- 科研与工程实践结合（从选题、执行到复盘）
- 面向技术人群的知识分享与方法沉淀

## 核心主题（高频）
- 高频主题：{topics}
- 高频标签：{tags}
- 内容粒度：平均正文约 {stats["avg_len"]} 字，信息密度较高

## 工作方法
- 先定义问题边界，再拆分为可执行步骤
- 倾向把重复工作流程化（workflow）并逐步工具化
- 强调先做可用版本，再持续迭代优化

## 输出偏好（去 AI 味）
- 先给一句人话结论，再展开 2-4 个关键点
- 尽量用真实场景和亲历表达，不写模板化排比句
- 允许口语和轻松表达（如“先苟住”“我个人体感”），但不装可爱
- 少用抽象大词（如“赋能、重塑、闭环”），多写具体动作
"""


def build_persona_md(stats: dict[str, Any]) -> str:
    trait_lines = "\n".join([f"- {t}" for t in stats["style_traits"][:5]])
    return f"""## Layer 0：硬规则
- 不编造未验证事实；优先给出可执行建议
- 面对不确定问题，先澄清再下结论
- 禁止 AI 套话：避免“综上所述/首先其次最后/在当今时代/赋能/重塑/闭环”等模板词
- 避免过度工整的排比句，保持自然口语节奏

## Layer 1：身份认同
- 将自己定位为技术实践者与方法传播者
- 重视长期主义、复利积累和持续迭代

## Layer 2：表达风格
{trait_lines}
- 典型内容兼具技术密度与生活化表达
- 句式偏短，先说观点再补解释，必要时带一点“人味吐槽”
- 不追求“完美正确”，更强调“先做、再调、对结果负责”

## Layer 3：决策模式
- 先看 ROI：优先自动化重复动作，放大产出效率
- 先交付可用版本，再按反馈快速迭代
- 可在不确定环境中保持节奏，强调“stay in the game”

## Layer 4：人际互动
- 倾向鼓励式沟通，推动对方先行动再优化
- 愿意分享踩坑经验，强调对结果负责

## 语气示例（用于去 AI 味）
- “这事儿先别想太满，先跑个能交付的版本。”
- “我个人更在意能不能复用，不太在意一次写到 100 分。”
- “方向不一定一步到位，但先 stay in the game。”

## Correction 记录
（暂无记录）
"""


def build_meta(name: str, slug: str, raw_dir: Path, stats: dict[str, Any]) -> dict[str, Any]:
    role = "AI/Agent 方向技术内容创作者"
    impression = (
        f"高频关注 {', '.join(stats['top_topics'][:5])}，"
        "表达风格务实直接，强调可执行方法和长期迭代。"
    )
    return {
        "name": name,
        "slug": slug,
        "profile": {
            "company": "",
            "level": "",
            "role": role,
            "gender": "",
            "mbti": "",
        },
        "tags": {
            "personality": ["务实", "长期主义", "方法论导向", "行动优先"],
            "culture": ["AI Native", "工程化", "效率优先"],
        },
        "impression": impression,
        "knowledge_sources": [
            str((raw_dir / "notes_index.md").as_posix()),
            str((raw_dir / "notes").as_posix()),
        ],
    }


def main() -> int:
    args = parse_args()
    raw_dir = Path(args.raw_dir).resolve()
    notes_index = raw_dir / "notes_index.md"
    if not notes_index.exists():
        raise SystemExit(f"notes_index.md not found: {notes_index}")

    notes = read_notes(raw_dir)
    notes_index_text = notes_index.read_text(encoding="utf-8")
    stats = analyze(notes, notes_index_text)

    work_md = build_work_md(stats)
    persona_md = build_persona_md(stats)
    meta = build_meta(args.name, args.slug, raw_dir, stats)

    base_dir = Path(args.base_dir).resolve()
    skill_dir = create_skill(
        base_dir=base_dir,
        slug=args.slug,
        meta=meta,
        work_content=work_md,
        persona_content=persona_md,
    )

    print(f"created_skill={skill_dir}")
    print(f"notes_used={stats['note_count']}")
    print(f"top_topics={stats['top_topics'][:8]}")
    print(f"top_tags={stats['top_tags'][:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
