#!/usr/bin/env python3
"""Convert X's word-timed VTT captions to readable, traceable transcripts."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw"
OUT = ROOT / "transcripts"

VIDEOS = {
    "lauren_2500prs": (
        "Lauren: how I shipped 2,500 PRs last month",
        "https://x.com/poteto/status/2102050467505430555",
    ),
    "lauren_graph_harness": (
        "Lauren Tan: Cursor talk shared by @0xSoural",
        "https://x.com/0xSoural/status/2101310350956048793",
    ),
}

TIMING = re.compile(r"^(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})$")
TAG = re.compile(r"<[^>]+>")


def seconds(timestamp: str) -> float:
    hour, minute, second = timestamp.split(":")
    return int(hour) * 3600 + int(minute) * 60 + float(second)


def parse(path: Path) -> list[tuple[str, str, str]]:
    blocks = path.read_text(encoding="utf-8-sig").strip().split("\n\n")
    cues = []
    for block in blocks:
        lines = block.splitlines()
        for i, line in enumerate(lines):
            match = TIMING.match(line)
            if not match:
                continue
            content = " ".join(lines[i + 1 :])
            content = html.unescape(TAG.sub("", content)).strip()
            if content:
                cues.append((match.group(1), match.group(2), content))
            break
    return cues


def write(name: str, title: str, url: str) -> None:
    cues = parse(RAW / f"{name}.en.vtt")
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"{name}.cues.tsv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(("start", "end", "text"))
        writer.writerows(cues)

    lines = [
        f"# {title}",
        "",
        f"Source: {url}",
        f"Caption source: X English VTT, {len(cues)} cues.",
        "This is a complete caption-derived transcript. It is not a manually verified verbatim transcript.",
        "Time labels mark the first cue in each 30-second block; see the TSV for cue-level timing.",
        "",
    ]
    current_bucket = -1
    words: list[str] = []
    for start, _, content in cues:
        bucket = int(seconds(start) // 30)
        if bucket != current_bucket:
            if words:
                lines.append(" ".join(words))
                lines.append("")
                words = []
            stamp = f"{bucket // 120:02d}:{bucket // 2 % 60:02d}:{(bucket % 2) * 30:02d}"
            lines.append(f"## {stamp}")
            lines.append("")
            current_bucket = bucket
        words.append(content)
    if words:
        lines.append(" ".join(words))
        lines.append("")
    (OUT / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")
    print(name, len(cues), f"{seconds(cues[-1][1]):.1f}s")


if __name__ == "__main__":
    for key, (title, url) in VIDEOS.items():
        write(key, title, url)
