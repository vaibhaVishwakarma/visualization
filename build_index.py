from pathlib import Path
import json
import re
from html import escape

ROOT = Path(".")
INDEX_FILE = ROOT / "index.html"
ID_FILE = ROOT / "visualization_ids.json"


# --------------------------------------------------
# Extract title from html
# --------------------------------------------------

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


# --------------------------------------------------
# Persistent numbering
# --------------------------------------------------

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


# --------------------------------------------------
# Discover all visualizations recursively
# --------------------------------------------------

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


# --------------------------------------------------
# Build nested tree
# --------------------------------------------------

tree = {}

for file in html_files:

    rel = file.relative_to(ROOT)

    node = tree

    for folder in rel.parts[:-1]:
        node = node.setdefault(folder, {})

    node.setdefault("__files__", []).append(file)


# --------------------------------------------------
# Render folders recursively
# --------------------------------------------------

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
                {escape(folder.replace('_', ' ').title())}
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


# --------------------------------------------------
# Generate page
# --------------------------------------------------

html = f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>Algorithm Visualizations</title>

<style>

* {{
    box-sizing:border-box;
}}

body {{
    font-family:Arial,sans-serif;
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
    font-size:18px;
    font-weight:600;
    margin-bottom:20px;
}}

#controls {{
    text-align:center;
    margin-bottom:30px;
}}

button {{
    cursor:pointer;
    padding:10px 18px;
    border:none;
    border-radius:8px;
    background:#2563eb;
    color:white;
    font-weight:600;
}}

button:hover {{
    opacity:.9;
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

    width:280px;

    text-decoration:none;
    color:#111;

    background:white;

    border:1px solid #ddd;
    border-radius:12px;

    padding:16px;

    transition:.15s;
}}

.card:hover {{
    transform:translateY(-3px);
    box-shadow:
        0 5px 15px rgba(0,0,0,.08);
}}

.card.visited {{

    background:#ecfdf5;

    border-color:#10b981;
}}

.card.visited .num {{
    color:#047857;
}}

.card.visited .title {{
    color:#065f46;
}}

.num {{
    font-size:12px;
    color:#666;
    margin-bottom:8px;
}}

.title {{
    font-size:15px;
    font-weight:600;
    line-height:1.4;
}}

</style>

</head>

<body>

<h1>Algorithm Visualizations</h1>

<div id="progress">
Loading...
</div>

<div id="controls">
    <button id="resetProgress">
        Reset Progress
    </button>
</div>

{render_node(tree)}

<script>

const STORAGE_KEY =
    "algo_visualization_progress";

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

function updateProgress() {{

    document.getElementById(
        "progress"
    ).textContent =
        `Completed ${{visited.size}} / ${{cards.length}} visualizations`;

}}

updateProgress();

document
    .getElementById("resetProgress")
    .addEventListener(
        "click",
        () => {{

            if (
                confirm(
                    "Reset all progress?"
                )
            ) {{

                localStorage.removeItem(
                    STORAGE_KEY
                );

                location.reload();

            }}

        }}
    );

</script>

</body>
</html>
"""

INDEX_FILE.write_text(
    html,
    encoding="utf-8"
)

print(
    f"Generated index.html "
    f"with {len(html_files)} visualizations."
)