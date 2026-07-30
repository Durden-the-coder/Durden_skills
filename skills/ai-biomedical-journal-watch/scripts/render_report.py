from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ALLOWED_STATUS = {"include", "exclude", "needs_evidence", "context"}
DEFAULT_DETAIL_LIMIT = 20
DEFAULT_PER_JOURNAL_CEILING = 5
DEFAULT_INDEX_LIMIT = 30
DEFAULT_EVIDENCE_LIMIT = 10
DEFAULT_CONTEXT_LIMIT = 20
PRIORITY_PATH = Path(__file__).resolve().parents[1] / "references" / "journal-priority.json"


def compact(text: str, limit: int) -> str:
    value = " ".join((text or "").split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def load_priority_config(path: Path = PRIORITY_PATH) -> tuple[dict[str, dict], int, int]:
    value = json.loads(path.read_text(encoding="utf-8"))
    default_rank, default_cap = int(value.get("default_rank", 99)), int(value.get("default_detail_cap", 3))
    mapping = {}
    for tier in value.get("tiers", []):
        for journal in tier.get("journals", []):
            if journal in mapping:
                raise ValueError(f"duplicate journal priority: {journal}")
            mapping[journal] = {"rank": int(tier["rank"]), "label": tier["label"], "detail_cap": int(tier.get("detail_cap", default_cap))}
    return mapping, default_rank, default_cap


JOURNAL_PRIORITY, DEFAULT_JOURNAL_RANK, DEFAULT_JOURNAL_CAP = load_priority_config()


def journal_priority(journal: str) -> dict:
    return JOURNAL_PRIORITY.get(journal, {"rank": DEFAULT_JOURNAL_RANK, "label": "未分级期刊", "detail_cap": DEFAULT_JOURNAL_CAP})


def date_number(value: str) -> int:
    try:
        return int((value or "").replace("-", "")[:8])
    except ValueError:
        return 0


def display_date(row: dict) -> str:
    return row.get("date") or "日期待核验"


def load_records(path: Path) -> list[dict]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        missing = {"work_id", "journal", "title", "url", "tracks", "status", "priority"} - row.keys()
        if missing:
            raise ValueError(f"line {line_number}: missing {sorted(missing)}")
        if row["status"] not in ALLOWED_STATUS:
            raise ValueError(f"line {line_number}: invalid status {row['status']}")
        if row["status"] == "include" and not row.get("summary_cn"):
            raise ValueError(f"line {line_number}: included item lacks summary_cn")
        if row["status"] == "context" and not row.get("article_type"):
            raise ValueError(f"line {line_number}: context item lacks article_type")
        records.append(row)
    return records


def item_link(row: dict) -> str:
    title = compact(row["title"], 140).replace("[", "［").replace("]", "］")
    return f"[{title}]({row['url']})" if row.get("url") else title


def sort_key(row: dict) -> tuple:
    tier = journal_priority(row["journal"])
    return (tier["rank"], -int(row.get("priority", 1)), -date_number(row.get("date", "")), row["journal"], row["title"])


def render(records: list[dict], detail_limit: int, per_journal: int, index_limit: int, evidence_limit: int, context_limit: int = DEFAULT_CONTEXT_LIMIT) -> str:
    included = sorted((r for r in records if r["status"] == "include"), key=sort_key)
    unresolved = sorted((r for r in records if r["status"] == "needs_evidence"), key=sort_key)
    contexts = sorted((r for r in records if r["status"] == "context"), key=sort_key)
    excluded = [r for r in records if r["status"] == "exclude"]
    detailed, overflow, journal_counts = [], [], defaultdict(int)
    for row in included:
        cap = min(per_journal, journal_priority(row["journal"])["detail_cap"])
        if len(detailed) < detail_limit and journal_counts[row["journal"]] < cap:
            detailed.append(row)
            journal_counts[row["journal"]] += 1
        else:
            overflow.append(row)

    lines = ["# 生物医学 AI 期刊速览", "", f"> 候选 {len(records)}；纳入 {len(included)}；趋势观点 {len(contexts)}；待补证据 {len(unresolved)}；排除 {len(excluded)}。", f"> 正文详写 {len(detailed)} 篇；紧凑索引展示 {min(len(overflow), index_limit)} 篇；趋势观点展示 {min(len(contexts), context_limit)} 条。完整记录保存在输入 JSONL。", "> 排序：期刊层级 → 内容优先级 → 发布时间；Nature、Science、Cell 相关内容优先。", "", "## 优先详读", ""]
    if not detailed:
        lines.append("本轮没有达到详写条件的条目。")
    for row in detailed:
        tracks, tier = "/".join(row.get("tracks") or []) or "-", journal_priority(row["journal"])
        lines += [f"### {item_link(row)}", "", f"- **期刊/层级/轨道：** {row['journal']} · {tier['label']} · {tracks}", f"- **发布日期：** {display_date(row)}", f"- **AI角色：** {row.get('ai_role') or '-'}", f"- **内容：** {compact(row.get('summary_cn', ''), 220)}", f"- **意义：** {compact(row.get('importance_cn', ''), 120)}", ""]

    lines += ["## 其他符合项", ""]
    shown = overflow[:index_limit]
    if not shown:
        lines.append("无。")
    for row in shown:
        lines.append(f"- {row['journal']} · {display_date(row)} · {item_link(row)} · {row.get('ai_role') or '-'}")
    if len(overflow) > len(shown):
        lines.append(f"- 另有 {len(overflow)-len(shown)} 篇符合项因阅读长度限制未展开。")

    lines += ["", "## 趋势与观点（非研究内容）", ""]
    shown_context = contexts[:context_limit]
    if not shown_context:
        lines.append("无。")
    for row in shown_context:
        lines.append(f"- {row['journal']} · {display_date(row)} · {row.get('article_type')} · {item_link(row)}")
    if len(contexts) > len(shown_context):
        lines.append(f"- 另有 {len(contexts)-len(shown_context)} 条相关趋势观点未展示；完整记录见 JSONL。")

    lines += ["", "## 待补证据", ""]
    shown_unresolved = unresolved[:evidence_limit]
    if not shown_unresolved:
        lines.append("无。")
    for row in shown_unresolved:
        lines.append(f"- {row['journal']} · {display_date(row)} · {item_link(row)} · {row.get('exclusion_reason') or '证据不足'}")
    if len(unresolved) > len(shown_unresolved):
        lines.append(f"- 另有 {len(unresolved)-len(shown_unresolved)} 条待补证据记录未逐条展示。")

    lines += ["", "## 排除汇总", ""]
    reasons = Counter(r.get("exclusion_reason") or "unspecified" for r in excluded)
    if not reasons:
        lines.append("无。")
    for reason, count in reasons.most_common():
        lines.append(f"- {reason}: {count}")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--detail-limit", type=int, default=DEFAULT_DETAIL_LIMIT)
    parser.add_argument("--per-journal", type=int, default=DEFAULT_PER_JOURNAL_CEILING)
    parser.add_argument("--index-limit", type=int, default=DEFAULT_INDEX_LIMIT)
    parser.add_argument("--evidence-limit", type=int, default=DEFAULT_EVIDENCE_LIMIT)
    parser.add_argument("--context-limit", type=int, default=DEFAULT_CONTEXT_LIMIT)
    args = parser.parse_args()
    if min(args.detail_limit, args.per_journal, args.index_limit, args.evidence_limit, args.context_limit) < 0:
        raise ValueError("limits must be non-negative")
    records = load_records(args.input)
    report = render(records, args.detail_limit, args.per_journal, args.index_limit, args.evidence_limit, args.context_limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(json.dumps({"records": len(records), "characters": len(report), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

