from pathlib import Path
import json
import re
from html import escape

ROOT = Path(".")
INDEX_FILE = ROOT / "index.html"
ID_FILE = ROOT / "visualization_ids.json"


# ---------------------------------------------------------
# Extract HTML title
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Stable numbering
# ---------------------------------------------------------

if ID_FILE.exists():
    ids = json.loads(
        ID_FILE.read_text(
            encoding="utf-8"
        )
    )
else:
    ids = {}

next_id = (
    max(ids.values()) + 1
    if ids
    else 1
)

html_files = sorted(
    p for p in ROOT.rglob("*.html")
    if p.name != "index.html"
)

for file in html_files:

    rel = file.relative_to(ROOT).as_posix()

    if rel not in ids:
        ids[rel] = next_id
        next_id += 1

ID_FILE.write_text(
    json.dumps(ids, indent=2),
    encoding="utf-8"
)


# ---------------------------------------------------------
# Build tree
# ---------------------------------------------------------

tree = {}

for file in html_files:

    rel = file.relative_to(ROOT)

    node = tree

    for folder in rel.parts[:-1]:
        node = node.setdefault(folder, {})

    node.setdefault("__files__", []).append(file)


# ---------------------------------------------------------
# Render recursive folder structure
# ---------------------------------------------------------

def render_node(node, level=2):

    html = ""

    folders = sorted(
        k for k in node.keys()
        if k != "__files__"
    )

    files = sorted(
        node.get("__files__", []),
        key=lambda f: ids[
            f.relative_to(ROOT).as_posix()
        ]
    )

    for folder in folders:

        heading = min(level, 6)

        html += f"""
        <section class="topic">
            <h{heading}>
                {escape(folder.replace('_',' ').title())}
            </h{heading}>
        """

        html += render_node(
            node[folder],
            level + 1
        )

        html += """
        </section>
        """

    if files:

        html += """
        <div class="cards">
        """

        for file in files:

            rel = file.relative_to(ROOT).as_posix()

            html += f"""
            <a class="card"
               href="{rel}"
               data-id="{ids[rel]}">

                <div class="num">
                    #{ids[rel]}
                </div>

                <div class="title">
                    {escape(get_title(file))}
                </div>

            </a>
            """

        html += """
        </div>
        """

    return html


# ---------------------------------------------------------
# Generate page
# ---------------------------------------------------------

html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Algorithm Visualizations</title>

<style>

* {{
    box-sizing:border-box;
}}

body {{
    font-family:Arial, sans-serif;
    max-width:1500px;
    margin:auto;
    padding:30px;
    background:#fafafa;
}}

h1 {{
    text-align:center;
    margin-bottom:10px;
}}

#progress {{
    text-align:center;
    margin-bottom:25px;
    font-weight:600;
    color:#444;
}}

.topic {{
    margin-top:35px;
}}

h2,h3,h4,h5,h6 {{
    border-bottom:2px solid #ddd;
    padding-bottom:8px;
}}

.cards {{
    display:flex;
    flex-wrap:wrap;
    gap:14px;
    margin-top:15px;
}}

.card {{

    width:300px;

    text-decoration:none;

    background:white;

    border:1px solid #ddd;
    border-radius:12px;

    padding:16px;

    transition:.15s;
}}

.card:hover {{
    transform:translateY(-2px);
    box-shadow:0 4px 12px rgba(0,0,0,.08);
}}

.num {{
    font-size:12px;
    color:#666;
    margin-bottom:8px;
}}

.title {{
    font-size:16px;
    line-height:1.4;
    color:#2563eb;
}}

.card:visited .title {{
    color:#551A8B;
}}

/* localStorage based visited state */

.card.visited {{
    background:#faf5ff;
    border-color:#d8b4fe;
}}

.card.visited .title {{
    color:#551A8B;
}}

.card.visited .num {{
    color:#7e22ce;
}}

</style>

</head>

<body>

<h1>Algorithm Visualizations</h1>

<div id="progress">
Loading...
</div>

{render_node(tree)}

<script>

const STORAGE_KEY =
    "algo_visualizations_visited";

const visited =
    new Set(
        JSON.parse(
            localStorage.getItem(STORAGE_KEY)
            || "[]"
        )
    );

const cards =
    document.querySelectorAll(".card");

cards.forEach(card => {{

    const id = card.dataset.id;

    if (visited.has(id))
        card.classList.add("visited");

    card.addEventListener("click", () => {{

        visited.add(id);

        localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify([...visited])
        );

    }});

}});

document.getElementById(
    "progress"
).textContent =
    `Visited ${{visited.size}} / ${{cards.length}} visualizations`;

</script>

</body>
</html>
"""

INDEX_FILE.write_text(
    html,
    encoding="utf-8"
)

print(
    f"Generated index.html with "
    f"{len(html_files)} visualizations."
)