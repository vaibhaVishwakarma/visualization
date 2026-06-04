from pathlib import Path
import json
import re
from html import escape

ROOT = Path(".")
ID_FILE = ROOT / "visualization_ids.json"


# --------------------------
# Title extraction
# --------------------------

def get_title(html_file):
    try:
        content = html_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        m = re.search(
            r"<title>(.*?)</title>",
            content,
            re.IGNORECASE | re.DOTALL
        )

        if m:
            return m.group(1).strip()

    except Exception:
        pass

    return html_file.stem


# --------------------------
# Load persistent IDs
# --------------------------

if ID_FILE.exists():
    ids = json.loads(ID_FILE.read_text(encoding="utf-8"))
else:
    ids = {}

next_id = (
    max(ids.values()) + 1
    if ids
    else 1
)


# --------------------------
# Collect html files
# --------------------------

html_files = sorted(
    p for p in ROOT.rglob("*.html")
    if p.name != "index.html"
)

for file in html_files:

    rel = file.relative_to(ROOT).as_posix()

    if rel not in ids:
        ids[rel] = next_id
        next_id += 1


# Save updated IDs
ID_FILE.write_text(
    json.dumps(ids, indent=2),
    encoding="utf-8"
)


# --------------------------
# Build tree structure
# --------------------------

tree = {}

for file in html_files:

    rel = file.relative_to(ROOT)

    node = tree

    parts = rel.parts[:-1]

    for part in parts:
        node = node.setdefault(part, {})

    node.setdefault("__files__", []).append(file)


# --------------------------
# Recursive HTML rendering
# --------------------------

def render_node(node, level=2):

    html = ""

    folders = sorted(
        k for k in node.keys()
        if k != "__files__"
    )

    files = sorted(
        node.get("__files__", []),
        key=lambda x: ids[x.relative_to(ROOT).as_posix()]
    )

    for folder in folders:

        html += f"""
        <div class="topic level-{level}">
            <h{min(level,6)}>
                {escape(folder.replace('_',' ').title())}
            </h{min(level,6)}>
        """

        html += render_node(
            node[folder],
            level + 1
        )

        html += "</div>"

    if files:

        html += '<div class="cards">'

        for file in files:

            rel = file.relative_to(ROOT).as_posix()

            file_id = ids[rel]

            title = escape(
                get_title(file)
            )

            html += f"""
            <a class="card" href="{rel}">
                <span class="num">
                    #{file_id}
                </span>

                <span class="title">
                    {title}
                </span>
            </a>
            """

        html += "</div>"

    return html


# --------------------------
# Main page
# --------------------------

html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>Algorithm Visualizations</title>

<style>

body{{
    font-family:Arial,sans-serif;
    max-width:1400px;
    margin:auto;
    padding:30px;
    background:#fafafa;
}}

h1{{
    text-align:center;
}}

.topic{{
    margin-top:30px;
}}

.cards{{
    display:flex;
    flex-wrap:wrap;
    gap:12px;
}}

.card{{
    display:flex;
    flex-direction:column;

    width:280px;

    padding:14px;

    border:1px solid #ddd;
    border-radius:10px;

    background:white;

    text-decoration:none;
    color:#111;

    transition:0.15s;
}}

.card:hover{{
    transform:translateY(-2px);
    box-shadow:0 3px 10px rgba(0,0,0,.08);
}}

.num{{
    font-size:12px;
    color:#666;
    margin-bottom:6px;
}}

.title{{
    font-size:15px;
    font-weight:600;
}}

h2,h3,h4,h5,h6{{
    border-bottom:1px solid #ddd;
    padding-bottom:6px;
}}

</style>

</head>

<body>

<h1>Algorithm Visualizations</h1>

{render_node(tree)}

</body>
</html>
"""


Path("index.html").write_text(
    html,
    encoding="utf-8"
)

print(
    f"Generated index.html with "
    f"{len(html_files)} visualizations."
)