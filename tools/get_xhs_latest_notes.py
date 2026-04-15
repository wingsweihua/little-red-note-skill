#!/usr/bin/env python3
"""
Fetch the latest notes from a Xiaohongshu user via Spider_XHS.

Examples:
  python tools/get_xhs_latest_notes.py --user-id 61716aad000000000201caae --limit 10
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from contextlib import contextmanager

from dotenv import load_dotenv


@contextmanager
def pushd(path: Path):
    old_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Get latest Xiaohongshu notes by user id.")
    parser.add_argument("--user-id", required=True, help="Xiaohongshu user id")
    parser.add_argument("--limit", type=int, default=10, help="How many notes to print (default: 10)")
    parser.add_argument(
        "--page-size",
        type=int,
        default=30,
        help="How many notes requested per page from user_posted API (default: 30)",
    )
    parser.add_argument(
        "--env-file",
        default="third_party/Spider_XHS/.env",
        help="Path to env file that contains COOKIES (default: third_party/Spider_XHS/.env)",
    )
    parser.add_argument(
        "--xhs-root",
        default="third_party/Spider_XHS",
        help="Path to Spider_XHS repository root (default: third_party/Spider_XHS)",
    )
    parser.add_argument(
        "--json-out",
        default="",
        help="Optional output JSON file path (relative to project root or absolute path)",
    )
    parser.add_argument(
        "--with-detail",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Fetch note details/content via get_note_info (default: true)",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=1.0,
        help="Throttle delay between requests in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--colleague-out",
        default="",
        help="Optional colleague-format output dir (writes notes/*.json and notes_index.md)",
    )
    return parser


def _resolve_output_path(project_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = (project_root / path).resolve()
    return path


def _to_colleague_note(detail: dict, fallback: dict) -> dict:
    tags = detail.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    comments = detail.get("comments", [])
    if isinstance(comments, str):
        comments = [comments]
    return {
        "note_id": detail.get("note_id") or fallback.get("note_id", ""),
        "url": detail.get("url") or fallback.get("url", ""),
        "title": detail.get("title") or fallback.get("title") or "(无标题)",
        "content": detail.get("content") or "",
        "tags": tags,
        "time": detail.get("time") or "",
        "likes": detail.get("likes") or fallback.get("liked_count"),
        "comments": comments,
    }


def main() -> int:
    args = build_parser().parse_args()
    if args.limit <= 0:
        raise SystemExit("--limit must be greater than 0")
    if args.page_size <= 0:
        raise SystemExit("--page-size must be greater than 0")
    if args.sleep_seconds < 0:
        raise SystemExit("--sleep-seconds must be >= 0")

    project_root = Path(__file__).resolve().parents[1]
    xhs_root = (project_root / args.xhs_root).resolve()
    env_file = (project_root / args.env_file).resolve()

    if not xhs_root.exists():
        raise SystemExit(f"Spider_XHS path not found: {xhs_root}")
    if not env_file.exists():
        raise SystemExit(f"Env file not found: {env_file}")

    load_dotenv(env_file)
    cookies = os.getenv("COOKIES", "").strip()
    if not cookies:
        raise SystemExit(f"COOKIES is empty in env file: {env_file}")

    # Spider_XHS internally relies on relative paths and node_modules resolution.
    # Keep the whole fetch flow under xhs_root so both list and detail calls work.
    with pushd(xhs_root):
        sys.path.insert(0, str(xhs_root))
        from apis.xhs_pc_apis import XHS_Apis  # pylint: disable=import-outside-toplevel
        from xhs_utils.data_util import handle_note_info  # pylint: disable=import-outside-toplevel

        api = XHS_Apis()
        cursor = ""
        all_notes = []
        page = 0
        while len(all_notes) < args.limit:
            page += 1
            ok, msg, res = api.get_user_note_info(args.user_id, cursor, cookies)
            print(f"page={page} api: success={ok}, msg={msg}")
            if not ok:
                return 2

            data = (res or {}).get("data", {})
            notes = data.get("notes", [])
            if not notes:
                break
            all_notes.extend(notes[: args.page_size])
            has_more = bool(data.get("has_more"))
            cursor = str(data.get("cursor", ""))
            if not has_more or not cursor:
                break
            if args.sleep_seconds > 0:
                time.sleep(args.sleep_seconds)

        notes = all_notes[: args.limit]
        print(f"latest_notes={len(notes)}")

        json_notes = []
        colleague_notes = []
        for idx, note in enumerate(notes, start=1):
            card = note.get("note_card", {})
            title = card.get("display_title") or card.get("title") or "(无标题)"
            note_id = note.get("note_id") or note.get("id") or ""
            xsec_token = note.get("xsec_token", "")
            url = f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_user"
            publish_time = card.get("time") or card.get("last_update_time") or note.get("publish_time")
            interact = card.get("interact_info", {})
            detail_payload = {
                "title": title,
                "content": "",
                "tags": [],
                "time": publish_time,
                "likes": interact.get("liked_count"),
                "comments": [],
                "url": url,
                "note_id": note_id,
            }

            if args.with_detail:
                ok_detail, msg_detail, detail_res = api.get_note_info(url, cookies)
                if ok_detail:
                    item = (detail_res or {}).get("data", {}).get("items", [{}])[0]
                    if item:
                        item["id"] = item.get("id") or note_id
                        item["url"] = item.get("url") or url
                        normalized = handle_note_info(item)
                        detail_payload["title"] = normalized.get("title") or detail_payload["title"]
                        detail_payload["content"] = normalized.get("desc") or ""
                        detail_payload["tags"] = normalized.get("tags", [])
                        detail_payload["time"] = normalized.get("upload_time") or detail_payload["time"]
                        detail_payload["likes"] = normalized.get("liked_count") or detail_payload["likes"]
                else:
                    print(f"  [warn] detail failed for {note_id}: {msg_detail}")
                if args.sleep_seconds > 0:
                    time.sleep(args.sleep_seconds)

            json_notes.append(
                {
                    "index": idx,
                    "note_id": note_id,
                    "title": title,
                    "url": url,
                    "xsec_token": xsec_token,
                    "publish_time": publish_time,
                    "liked_count": interact.get("liked_count"),
                    "collected_count": interact.get("collected_count"),
                    "comment_count": interact.get("comment_count"),
                    "share_count": interact.get("share_count"),
                    "content": detail_payload["content"],
                    "tags": detail_payload["tags"],
                    "time": detail_payload["time"],
                    "likes": detail_payload["likes"],
                    "raw": note,
                }
            )
            colleague_notes.append(_to_colleague_note(detail_payload, json_notes[-1]))

            print(f"{idx}. {title}")
            print(f"   {url}")

    if args.json_out:
        out_path = _resolve_output_path(project_root, args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "user_id": args.user_id,
            "count": len(json_notes),
            "notes": json_notes,
            "colleague_notes": colleague_notes,
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"json_saved={out_path}")

    if args.colleague_out:
        out_dir = _resolve_output_path(project_root, args.colleague_out)
        notes_dir = out_dir / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)

        index_lines = [f"# 小红书用户 {args.user_id} 最新笔记\n"]
        for i, note in enumerate(colleague_notes, start=1):
            note_id = note.get("note_id", f"note_{i}")
            (notes_dir / f"{note_id}.json").write_text(
                json.dumps(note, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            index_lines.append(
                f"## {i}. {note.get('title') or '(无标题)'}\n"
                f"- 时间: {note.get('time', '')}  点赞: {note.get('likes', '')}\n"
                f"- 标签: {' '.join(note.get('tags', []))}\n"
                f"- 链接: {note.get('url', '')}\n\n{note.get('content', '')}\n"
            )
        (out_dir / "notes_index.md").write_text("\n".join(index_lines), encoding="utf-8")
        print(f"colleague_saved={out_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
