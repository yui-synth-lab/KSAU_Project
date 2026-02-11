from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PARTICLES = [
    "Up",
    "Down",
    "Strange",
    "Charm",
    "Bottom",
    "Top",
    "Electron",
    "Muon",
    "Tau",
    "W",
    "Z",
    "Higgs",
]


LINK_RE = re.compile(r"\b(L\d{1,2}[an]\d+)\b")
KNOT_RE = re.compile(r"\b(\d+_\d+)\b")
KNOT_TEX_RE = re.compile(r"\b(\d+)_\{(\d+)\}\b")  # e.g. 8_{14}


@dataclass(frozen=True)
class Mention:
    file: Path
    line_no: int
    particle: str | None
    topology: str
    raw_line: str


def _load_assignments(path: Path) -> dict[str, dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict in {path}")
    return data


def _normalize_topology(topo: str) -> str:
    topo = topo.strip()
    if topo.startswith("$") and topo.endswith("$"):
        topo = topo[1:-1].strip()
    topo = topo.replace("\\", "")

    # Normalize TeX-style knot: 8_{14} -> 8_14
    m = KNOT_TEX_RE.search(topo)
    if m:
        topo = f"{m.group(1)}_{m.group(2)}"

    # If link includes braces, keep base link id only
    if topo.startswith("L"):
        m2 = LINK_RE.search(topo)
        if m2:
            topo = m2.group(1)
    return topo


def _official_topologies(assignments: dict[str, dict]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in PARTICLES:
        if p not in assignments:
            continue
        topo = str(assignments[p].get("topology", "")).strip()
        out[p] = _normalize_topology(topo)
    return out


def _iter_md_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.md"):
        if path.is_file():
            yield path


def _extract_mentions(md_file: Path) -> list[Mention]:
    mentions: list[Mention] = []

    try:
        text = md_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = md_file.read_text(encoding="utf-8", errors="replace")

    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        raw = line.rstrip("\n")

        topo_hits: list[str] = []
        topo_hits.extend(m.group(1) for m in LINK_RE.finditer(raw))
        topo_hits.extend(m.group(1) for m in KNOT_RE.finditer(raw))
        topo_hits.extend(f"{m.group(1)}_{m.group(2)}" for m in KNOT_TEX_RE.finditer(raw))

        if not topo_hits:
            continue

        particle_hit: str | None = None
        for p in PARTICLES:
            if re.search(rf"\b{re.escape(p)}\b", raw):
                particle_hit = p
                break

        for topo in topo_hits:
            mentions.append(
                Mention(
                    file=md_file,
                    line_no=idx,
                    particle=particle_hit,
                    topology=_normalize_topology(topo),
                    raw_line=raw.strip(),
                )
            )

    return mentions


def _find_particle_equals_topology(md_root: Path) -> list[Mention]:
    """
    Extract higher-confidence mentions like:
      Electron=$3_1$
      Up = L8a6
      Top Quark must be **L11a32**
    """
    mentions: list[Mention] = []

    # Accept both "Top=" and "Top Quark ... L11a32" styles, but still approximate.
    particle_group = "|".join(re.escape(p) for p in PARTICLES)
    eq_re = re.compile(
        rf"\b(?P<particle>{particle_group})\b\s*[:=]\s*(?P<topo>\$?L\d{{1,2}}[an]\d+\$?|\$?\d+_\d+\$?|\d+_\{{\d+\}})",
        re.IGNORECASE,
    )
    must_be_re = re.compile(
        rf"\b(?P<particle>{particle_group})\b.*?\b(?P<topo>L\d{{1,2}}[an]\d+)\b",
        re.IGNORECASE,
    )

    for md_file in _iter_md_files(md_root):
        try:
            text = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = md_file.read_text(encoding="utf-8", errors="replace")

        for idx, line in enumerate(text.splitlines(), start=1):
            raw = line.strip()
            if not raw:
                continue

            for m in eq_re.finditer(raw):
                particle = next((p for p in PARTICLES if p.lower() == m.group("particle").lower()), m.group("particle"))
                topo = _normalize_topology(m.group("topo"))
                mentions.append(Mention(md_file, idx, particle, topo, raw))

            # Only add "must be" style if line contains strong language
            if re.search(r"\b(must|only|唯一|must be)\b", raw, re.IGNORECASE):
                m2 = must_be_re.search(raw)
                if m2:
                    particle = next(
                        (p for p in PARTICLES if p.lower() == m2.group("particle").lower()), m2.group("particle")
                    )
                    topo = _normalize_topology(m2.group("topo"))
                    mentions.append(Mention(md_file, idx, particle, topo, raw))

    return mentions


def generate_report(md_root: Path, assignments_path: Path, out_md: Path, out_json: Path | None) -> None:
    assignments = _load_assignments(assignments_path)
    official = _official_topologies(assignments)

    all_mentions: list[Mention] = []
    for md_file in _iter_md_files(md_root):
        all_mentions.extend(_extract_mentions(md_file))
    high_conf = _find_particle_equals_topology(md_root)

    # Map high-confidence mentions to mismatches
    mismatches: list[dict] = []
    for m in high_conf:
        if not m.particle or m.particle not in official:
            continue
        if m.topology != official[m.particle]:
            mismatches.append(
                {
                    "particle": m.particle,
                    "mentioned_topology": m.topology,
                    "official_topology": official[m.particle],
                    "file": str(m.file.as_posix()),
                    "line": m.line_no,
                    "raw_line": m.raw_line,
                }
            )

    # Detect "simplest knots" lists that don't match current official leptons
    official_leptons = [official.get("Electron"), official.get("Muon"), official.get("Tau")]
    simplest_claims: list[dict] = []
    simplest_re = re.compile(r"\(\s*\$?(?P<a>\d+_\d+)\$?\s*,\s*\$?(?P<b>\d+_\d+)\$?\s*,\s*\$?(?P<c>\d+_\d+)\$?\s*\)")
    for md_file in _iter_md_files(md_root):
        try:
            text = md_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        for idx, line in enumerate(text.splitlines(), start=1):
            if "simplest" not in line.lower() and "Simplest" not in line and "最" not in line:
                continue
            m = simplest_re.search(line)
            if not m:
                continue
            claimed = [_normalize_topology(m.group("a")), _normalize_topology(m.group("b")), _normalize_topology(m.group("c"))]
            if claimed != official_leptons:
                simplest_claims.append(
                    {
                        "type": "simplest_knots_list",
                        "claimed": claimed,
                        "official_leptons": official_leptons,
                        "file": str(md_file.as_posix()),
                        "line": idx,
                        "raw_line": line.strip(),
                    }
                )

    # Summaries
    md_files = list(_iter_md_files(md_root))
    unique_topos_mentioned = sorted({m.topology for m in all_mentions})

    out_md.parent.mkdir(parents=True, exist_ok=True)
    report_lines: list[str] = []
    report_lines.append("# v6.0 Topology Consistency Report")
    report_lines.append("")
    report_lines.append(f"- Markdown root: `{md_root.as_posix()}`")
    report_lines.append(f"- Official assignments: `{assignments_path.as_posix()}`")
    report_lines.append(f"- Files scanned: {len(md_files)}")
    report_lines.append(f"- Unique topology tokens mentioned: {len(unique_topos_mentioned)}")
    report_lines.append(f"- High-confidence particle=topology mismatches: {len(mismatches)}")
    report_lines.append("")

    report_lines.append("## Official assignments (current)")
    report_lines.append("")
    report_lines.append("| Particle | Official topology |")
    report_lines.append("|---|---|")
    for p in PARTICLES:
        if p in official:
            report_lines.append(f"| {p} | `{official[p]}` |")
    report_lines.append("")

    if mismatches:
        report_lines.append("## Mismatches (particle mentions disagree with official JSON)")
        report_lines.append("")
        report_lines.append("| Particle | Mentioned | Official | Location |")
        report_lines.append("|---|---|---|---|")
        for mm in mismatches:
            loc = f"`{mm['file']}:{mm['line']}`"
            report_lines.append(
                f"| {mm['particle']} | `{mm['mentioned_topology']}` | `{mm['official_topology']}` | {loc} |"
            )
        report_lines.append("")
        report_lines.append("### Evidence lines")
        report_lines.append("")
        for mm in mismatches:
            report_lines.append(f"- `{mm['file']}:{mm['line']}`: {mm['raw_line']}")
        report_lines.append("")
    else:
        report_lines.append("## Mismatches")
        report_lines.append("")
        report_lines.append("- None found by the high-confidence extractor.")
        report_lines.append("")

    if simplest_claims:
        report_lines.append("## Simplest-knots list claims (do not match official Electron/Muon/Tau)")
        report_lines.append("")
        for c in simplest_claims:
            report_lines.append(
                f"- `{c['file']}:{c['line']}` claimed={c['claimed']} vs official={c['official_leptons']}: {c['raw_line']}"
            )
        report_lines.append("")

    report_lines.append("## Notes / limitations")
    report_lines.append("")
    report_lines.append("- The extractor is conservative: it only flags clear `Particle = Topology` (or strong-language) lines.")
    report_lines.append("- Generic topology mentions without particle names are not treated as contradictions.")
    report_lines.append("- TeX-style knots like `8_{14}` are normalized to `8_14` for comparison.")
    report_lines.append("")

    out_md.write_text("\n".join(report_lines), encoding="utf-8")

    if out_json is not None:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "md_root": md_root.as_posix(),
            "assignments_path": assignments_path.as_posix(),
            "official": official,
            "mismatches": mismatches,
            "simplest_claims": simplest_claims,
        }
        out_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan v6.0 markdowns for topology claims and compare to official JSON.")
    parser.add_argument("--md-root", type=Path, default=Path("v6.0"), help="Root directory to scan for *.md")
    parser.add_argument(
        "--assignments",
        type=Path,
        default=Path("v6.0/data/topology_assignments.json"),
        help="Official topology assignments JSON path",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("audit/reports/v6_topology_consistency_report.md"),
        help="Output markdown report path",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("audit/reports/v6_topology_consistency_report.json"),
        help="Optional JSON output path",
    )
    args = parser.parse_args()

    generate_report(args.md_root, args.assignments, args.out_md, args.out_json)
    print(f"Wrote report: {args.out_md}")
    if args.out_json:
        print(f"Wrote JSON  : {args.out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

