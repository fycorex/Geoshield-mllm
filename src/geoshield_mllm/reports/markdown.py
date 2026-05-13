from __future__ import annotations

from geoshield_mllm.reports.run_card import RunCard


def run_card_markdown(card: RunCard) -> str:
    data = card.to_dict()
    lines = [f"# Run {card.run_id}", "", f"Goal: {card.goal}", "", "## Metadata"]
    for key, value in data.items():
        lines.append(f"- `{key}`: {value}")
    lines.append("")
    lines.append("## Interpretation Notes")
    lines.append("No interpretation has been recorded yet.")
    lines.append("")
    return "\n".join(lines)

