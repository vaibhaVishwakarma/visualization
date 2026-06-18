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
# UI Helper Functions
# ---------------------------------------------------------

def topic_id(name):
    return (
        "topic-" +
        name.lower()
            .replace("_", "-")
            .replace(" ", "-")
    )


def build_topic_nav(tree):

    html = """
    <div class="topic-nav">
    """

    for topic in sorted(
        k for k in tree.keys()
        if k != "__files__"
    ):

        html += f"""
        <a class="topic-card"
           href="#{topic_id(topic)}">
            {escape(topic.replace('_',' ').title())}
        </a>
        """

    html += """
    </div>
    """

    return html


# ---------------------------------------------------------
# Render recursive folder structure
# ---------------------------------------------------------

def render_node(node, level=0):

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

        indent = level * 24

        anchor = (
            topic_id(folder)
            if level == 0
            else ""
        )

        html += f"""
        <div class="folder-block"
             style="margin-left:{indent}px">

            <div class="folder-header"
                 id="{anchor}">
                {escape(folder.replace('_',' ').title())}
            </div>
        """

        html += render_node(
            node[folder],
            level + 1
        )

        html += """
        </div>
        """

    if files:

        html += """
        <div class="cards">
        """

        for file in files:

            rel = file.relative_to(ROOT).as_posix()

            file_id = ids[rel]

            title = escape(
                get_title(file)
            )

            html += f"""
            <a class="card"
               href="{rel}"
               data-id="{file_id}">

                <span class="num">
                    #{file_id}
                </span>

                <span class="title">
                    {title}
                </span>

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
*{{
    box-sizing:border-box;
}}

html{{
    scroll-behavior:smooth;
}}

body{{
    font-family:Arial,sans-serif;
    max-width:1600px;
    margin:auto;
    padding:24px;
    background:#fafafa;
}}

h1{{
    text-align:center;
    margin-bottom:12px;
}}

#progress{{
    text-align:center;
    font-weight:600;
    margin-bottom:12px;
}}

.progress-wrap{{
    height:10px;
    border-radius:999px;
    overflow:hidden;
    background:#e5e7eb;
    margin-bottom:25px;
}}

#progressBar{{
    height:100%;
    width:0%;
    background:#2563eb;
    transition:.25s;
}}

/* -------------------------- */
/* sticky topic navigation */
/* -------------------------- */

.topic-nav{{

    position:sticky;
    top:0;

    z-index:100;

    display:flex;
    flex-wrap:wrap;

    gap:10px;

    padding:12px 0;

    background:#fafafa;

    margin-bottom:25px;
}}

.topic-card{{

    text-decoration:none;

    color:#111;

    background:white;

    border:1px solid #ddd;

    border-radius:12px;

    padding:10px 18px;

    font-weight:600;

    transition:.15s;
}}

.topic-card:hover{{
    transform:translateY(-2px);

    box-shadow:
        0 4px 10px rgba(0,0,0,.08);
}}

/* -------------------------- */
/* folders */
/* -------------------------- */

.folder-block{{
    margin-top:12px;
}}

.folder-header{{

    background:white;

    border:1px solid #ddd;

    border-radius:12px;

    padding:12px 16px;

    margin:16px 0 10px;

    font-weight:700;

    box-shadow:
        0 2px 6px rgba(0,0,0,.04);
}}

/* -------------------------- */
/* visualization list */
/* -------------------------- */

.cards{{

    display:flex;

    flex-direction:column;

    gap:8px;

    margin-bottom:10px;
}}

.card{{

    width:100%;

    display:flex;

    align-items:center;

    gap:12px;

    text-decoration:none;

    background:white;

    border:1px solid #ddd;

    border-radius:10px;

    padding:10px 14px;

    transition:.15s;
}}

.card:hover{{

    transform:translateX(4px);

    box-shadow:
        0 3px 10px rgba(0,0,0,.08);
}}

.num{{

    min-width:60px;

    color:#666;

    font-size:14px;
}}

.title{{

    flex:1;

    color:#2563eb;

    white-space:nowrap;

    overflow:hidden;

    text-overflow:ellipsis;

    font-size:15px;
}}

/* -------------------------- */
/* visited */
/* -------------------------- */

.card.visited{{

    background:#faf5ff;

    border-left:4px solid #7e22ce;

    border-color:#d8b4fe;
}}

.card.visited .title{{
    color:#551A8B;
}}

.card.visited .num{{
    color:#7e22ce;
}}
</style>

</head>

<body>

<h1>Algorithm Visualizations</h1>

<div id="progress">
Loading...
</div>

<div class="progress-wrap">
    <div id="progressBar"></div>
</div>

{build_topic_nav(tree)}

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

        updateProgress();

    }});

}});

function updateProgress(){{

    const count =
        visited.size;

    const total =
        cards.length;

    const pct =
        total === 0
        ? 0
        : count * 100 / total;

    document
        .getElementById("progress")
        .textContent =
        `Visited ${{count}} / ${{total}} visualizations`;

    document
        .getElementById("progressBar")
        .style.width =
        pct + "%";
}}

updateProgress();
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
)m