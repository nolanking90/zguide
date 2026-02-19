#!/usr/bin/env python3
"""Generate HTML TODO cross-referencing guide examples with language ports, ordered by book appearance."""

import os
import re

REPO = "/home/nolan/zguide"
DOCS = os.path.join(REPO, "site/content/docs")
EXAMPLES = os.path.join(REPO, "examples")

# 1. Parse chapters in order, tracking sections and examples
chapters = ["chapter1.md", "chapter2.md", "chapter3.md", "chapter4.md",
            "chapter5.md", "chapter7.md", "chapter8.md"]

# Each entry: (label, name, title, chapter_num)
ordered_examples = []
seen_names = set()

for chapfile in chapters:
    chap_num = int(re.search(r'(\d+)', chapfile).group(1))
    path = os.path.join(DOCS, chapfile)
    with open(path) as f:
        lines = f.readlines()

    section_idx = 0
    example_in_section = 0

    for line in lines:
        # Detect ## section headers (not ### or deeper)
        if re.match(r'^## ', line):
            section_idx += 1
            example_in_section = 0
            continue

        # Detect example shortcodes
        m = re.search(r'\{\{<\s*examples?\s+name="([^"]+)"\s+title="([^"]+)"', line)
        if m:
            name, title = m.group(1), m.group(2)
            if name not in seen_names:
                seen_names.add(name)
                example_in_section += 1
                label = f"{chap_num}.{section_idx}.{example_in_section}"
                ordered_examples.append((label, name, title, chap_num))

example_names = [e[1] for e in ordered_examples]

# 2. Languages
languages = [
    ("Ada", "Ada"), ("Basic", "Basic"), ("C", "C"), ("C++", "C++"),
    ("CSharp", "C#"), ("CL", "CL"), ("Clojure", "Clojure"),
    ("Delphi", "Delphi"), ("Elixir", "Elixir"), ("Erlang", "Erlang"),
    ("FSharp", "F#"), ("Felix", "Felix"), ("Free Pascal", "FreePas"),
    ("Go", "Go"), ("GoCZMQ", "GoCZMQ"), ("Haskell", "Haskell"),
    ("Haxe", "Haxe"), ("Java", "Java"), ("Julia", "Julia"), ("Lua", "Lua"),
    ("Node.js", "Node.js"), ("OCaml", "OCaml"), ("Objective-C", "Obj-C"),
    ("ooc", "ooc"), ("Perl", "Perl"), ("PHP", "PHP"), ("Python", "Python"),
    ("Q", "Q"), ("Racket", "Racket"), ("Ruby", "Ruby"), ("Rust", "Rust"),
    ("Scala", "Scala"), ("Tcl", "Tcl"),
]

# 3. Scan directories
lang_files = {}
for dirn, display in languages:
    path = os.path.join(EXAMPLES, dirn)
    if not os.path.isdir(path):
        lang_files[dirn] = set()
        continue
    files = set()
    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)):
            continue
        files.add(os.path.splitext(f)[0])
    lang_files[dirn] = files

# 4. Stats
total = len(ordered_examples)
lang_stats = {}
for dirn, display in languages:
    lang_stats[dirn] = sum(1 for ex in example_names if ex in lang_files[dirn])

# 5. Extra files
IGNORE = {
    ".gitignore", "README", "build", "zhelpers", "zmsg", "zmsg_test", "index",
    "Makefile", "LICENSE", "c", "MDP", "mdp", "ZHelper", "ZHelpers",
    "ZMQHelper", "helpers", "project", "pom", "src", "run", "Run", "Cargo",
    "Setup", "zguide", "pkgIndex", "utils", "Dns", "ZMsg", "MsgQueue",
    "MultiThreadedRelay", "valgrind", "vg", "udplib", "compile",
    "AssemblyInfo", "Program", "ProgramRunner", "Z85Encode",
    "ZGuideExamples.VS", "ZGuideExamples.mono", "BUILDING", "ObjCExamples",
    "ChangeLog", "listings", "models", "buildLinux", "buildMac64",
    "buildWindows", "MDClientAPI", "MDPDef", "MDWorkerAPI", "stack",
    "asyncio_ioloop", "tornado_ioloop", "testit", "zmq", "zmq.helpers",
    "zmq.types", "mktestdata",
}
extras_by_lang = {}
for dirn, display in languages:
    extras = sorted(lang_files[dirn] - set(example_names) - IGNORE)
    if extras:
        extras_by_lang[(dirn, display)] = extras

# 6. Chapter titles for section headers
chapter_titles = {
    1: "Basics",
    2: "Sockets and Patterns",
    3: "Advanced Request-Reply Patterns",
    4: "Reliable Request-Reply Patterns",
    5: "Advanced Pub-Sub Patterns",
    7: "Advanced Architecture using ZeroMQ",
    8: "A Framework for Distributed Computing",
}

# 7. Generate HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ZeroMQ Guide - Example Port Status</title>
<style>
  :root {{
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #e6edf3;
    --text-dim: #8b949e;
    --green: #3fb950;
    --blue: #58a6ff;
    --yellow: #d29922;
    --chapter-bg: rgba(88,166,255,0.08);
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
    padding: 2rem;
  }}
  h1 {{ margin-bottom: 0.5rem; font-size: 1.8rem; }}
  h2 {{ margin: 2rem 0 1rem; font-size: 1.3rem; color: var(--blue); }}
  h3 {{ margin: 1.5rem 0 0.5rem; font-size: 1.1rem; }}
  p, .stats {{ color: var(--text-dim); margin-bottom: 1rem; }}
  .stats span {{
    display: inline-block; margin-right: 2rem;
    color: var(--text); font-weight: 600;
  }}
  .table-wrap {{
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 6px;
    margin: 1rem 0;
  }}
  table {{
    border-collapse: collapse;
    font-size: 0.8rem;
    white-space: nowrap;
    width: 100%;
  }}
  th, td {{
    padding: 4px 8px;
    border: 1px solid var(--border);
    text-align: center;
  }}
  th {{
    background: var(--surface);
    position: sticky;
    top: 0;
    z-index: 2;
    font-weight: 600;
  }}
  /* Sticky first three columns */
  td:nth-child(1), td:nth-child(2), td:nth-child(3),
  th:nth-child(1), th:nth-child(2), th:nth-child(3) {{
    position: sticky;
    background: var(--surface);
    z-index: 3;
    text-align: left;
  }}
  th:nth-child(1), td:nth-child(1) {{ left: 0; min-width: 55px; }}
  th:nth-child(2), td:nth-child(2) {{ left: 55px; min-width: 100px; }}
  th:nth-child(3), td:nth-child(3) {{ left: 155px; min-width: 200px; border-right: 2px solid var(--blue); }}
  th:nth-child(1), th:nth-child(2), th:nth-child(3) {{ z-index: 4; }}
  td:nth-child(1) {{ color: var(--text-dim); font-size: 0.75rem; font-family: monospace; }}
  th span.rot {{
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    display: inline-block;
    min-height: 60px;
    font-size: 0.75rem;
  }}
  .check {{ color: var(--green); font-weight: bold; }}
  .miss {{ color: var(--border); }}
  tr:hover td {{ background: rgba(255,255,255,0.03); }}
  tr:hover td:nth-child(1), tr:hover td:nth-child(2), tr:hover td:nth-child(3) {{ background: #1c2129; }}
  tr.chapter-row td {{
    background: var(--chapter-bg) !important;
    color: var(--blue);
    font-weight: 700;
    text-align: left;
    font-size: 0.85rem;
    padding: 6px 8px;
    border-bottom: 2px solid var(--blue);
  }}
  /* Summary table */
  .summary {{ max-width: 600px; }}
  .summary td:first-child {{ text-align: left; font-weight: 600; }}
  .summary td {{ text-align: right; }}
  .bar-cell {{ text-align: left !important; width: 200px; }}
  .bar {{
    height: 16px;
    background: var(--green);
    border-radius: 3px;
    display: inline-block;
    vertical-align: middle;
  }}
  .extras ul {{ list-style: none; padding: 0; }}
  .extras li {{
    font-family: 'SFMono-Regular', Consolas, monospace;
    font-size: 0.85rem;
    padding: 2px 0;
    color: var(--yellow);
  }}
</style>
</head>
<body>
<h1>ZeroMQ Guide - Example Port Status</h1>
<div class="stats">
  <span>{total} examples</span>
  <span>{len(languages)} languages</span>
</div>

<h2>Port Matrix</h2>
<div class="table-wrap">
<table>
<thead><tr>
  <th>#</th>
  <th>Example</th>
  <th>Title</th>
"""

for _, display in languages:
    html += f'  <th><span class="rot">{display}</span></th>\n'
html += "</tr></thead>\n<tbody>\n"

ncols = len(languages) + 3
current_chapter = None

for label, name, title, chap_num in ordered_examples:
    if chap_num != current_chapter:
        current_chapter = chap_num
        ch_title = chapter_titles.get(chap_num, f"Chapter {chap_num}")
        html += f'<tr class="chapter-row"><td colspan="{ncols}">Chapter {chap_num} &mdash; {ch_title}</td></tr>\n'

    html += f"<tr><td>{label}</td><td><code>{name}</code></td><td>{title}</td>"
    for dirn, _ in languages:
        if name in lang_files[dirn]:
            html += '<td class="check">&#10003;</td>'
        else:
            html += '<td class="miss">&middot;</td>'
    html += "</tr>\n"

html += "</tbody></table></div>\n"

# Summary
html += """
<h2>Summary by Language</h2>
<div class="table-wrap summary">
<table>
<thead><tr><th style="text-align:left">Language</th><th>Ported</th><th>Missing</th><th>%</th><th class="bar-cell">Coverage</th></tr></thead>
<tbody>
"""
for dirn, display in sorted(languages, key=lambda x: -lang_stats[x[0]]):
    ported = lang_stats[dirn]
    missing = total - ported
    pct = (ported / total) * 100 if total else 0
    bar_w = int(pct * 1.5)
    html += f'<tr><td>{display}</td><td>{ported}</td><td>{missing}</td><td>{pct:.0f}%</td>'
    html += f'<td class="bar-cell"><span class="bar" style="width:{bar_w}px"></span></td></tr>\n'
html += "</tbody></table></div>\n"

# Extra files
html += """
<h2>Extra Files Not Referenced in the Guide</h2>
<p>Files in language directories whose names don't match any guide example.
May be helpers, alternates, tests, or ports of removed examples.</p>
<div class="extras">
"""
for (dirn, display), extras in sorted(extras_by_lang.items(), key=lambda x: x[0][1]):
    html += f"<h3>{display} <code>examples/{dirn}/</code></h3>\n<ul>\n"
    for e in extras:
        html += f"  <li>{e}</li>\n"
    html += "</ul>\n"
html += "</div>\n</body></html>\n"

# Also update the markdown
md_lines = []
md_lines.append("# ZeroMQ Guide Examples - Language Port Status\n")
md_lines.append(f"- **{total}** examples referenced in the guide")
md_lines.append(f"- **{len(languages)}** languages tracked")
md_lines.append(f"- Examples ordered by appearance in the book\n")

header = "| # | Example | Title |"
sep = "|---|---|---|"
for _, display in languages:
    header += f" {display} |"
    sep += "---|"
md_lines.append(header)
md_lines.append(sep)

current_chapter = None
for label, name, title, chap_num in ordered_examples:
    if chap_num != current_chapter:
        current_chapter = chap_num
        ch_title = chapter_titles.get(chap_num, f"Chapter {chap_num}")
        spacer = f"| **Ch{chap_num}** | | **{ch_title}** |"
        for _ in languages:
            spacer += " |"
        md_lines.append(spacer)
    row = f"| {label} | {name} | {title} |"
    for dirn, _ in languages:
        if name in lang_files[dirn]:
            row += " :white_check_mark: |"
        else:
            row += " |"
    md_lines.append(row)

md_lines.append("")
md_lines.append("## Summary by Language\n")
md_lines.append("| Language | Ported | Missing | % Complete |")
md_lines.append("|---|---|---|---|")
for dirn, display in sorted(languages, key=lambda x: -lang_stats[x[0]]):
    ported = lang_stats[dirn]
    missing = total - ported
    pct = (ported / total) * 100 if total else 0
    md_lines.append(f"| {display} | {ported} | {missing} | {pct:.0f}% |")

md_lines.append("")
md_lines.append("## Extra Files Not Referenced in the Guide\n")
md_lines.append("Files in language directories whose names don't match any guide example.\n")
for (dirn, display), extras in sorted(extras_by_lang.items(), key=lambda x: x[0][1]):
    md_lines.append(f"### {display} (`examples/{dirn}/`)\n")
    for e in extras:
        md_lines.append(f"- `{e}`")
    md_lines.append("")

# Write both files
with open(os.path.join(REPO, "EXAMPLES_TODO.html"), "w") as f:
    f.write(html)
with open(os.path.join(REPO, "EXAMPLES_TODO.md"), "w") as f:
    f.write("\n".join(md_lines) + "\n")

print(f"Generated EXAMPLES_TODO.html and EXAMPLES_TODO.md")
print(f"  {total} examples in book order across {len(set(e[3] for e in ordered_examples))} chapters")
