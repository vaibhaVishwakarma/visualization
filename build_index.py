from pathlib import Path
import re

ROOT = Path(".")

def get_title(html_file):
    try:
        content = html_file.read_text(encoding="utf-8", errors="ignore")

        match = re.search(
            r"<title>(.*?)</title>",
            content,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            return match.group(1).strip()

    except Exception:
        pass

    return html_file.stem


html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">

<title>Algorithm Visualizations</title>

<style>

body{
    font-family:Arial,sans-serif;
    max-width:1200px;
    margin:auto;
    padding:30px;
    background:#fafafa;
}

h1{
    text-align:center;
}

.topic{
    margin-top:35px;
}

.topic h2{
    border-bottom:2px solid #ddd;
    padding-bottom:8px;
}

ul{
    list-style:none;
    padding-left:0;
}

li{
    margin:8px 0;
}

a{
    text-decoration:none;
    color:#2563eb;
}

a:hover{
    text-decoration:underline;
}

</style>
</head>

<body>

<h1>Algorithm Visualizations</h1>
"""

for folder in sorted(ROOT.iterdir()):

    if not folder.is_dir():
        continue

    files = sorted(folder.glob("*.html"))

    if not files:
        continue

    html += f"""
    <div class="topic">
        <h2>{folder.name.title()}</h2>
        <ul>
    """

    for file in files:

        title = get_title(file)

        html += f"""
        <li>
            <a href="{file.as_posix()}">
                {title}
            </a>
        </li>
        """

    html += """
        </ul>
    </div>
    """

html += """
</body>
</html>
"""

Path("index.html").write_text(
    html,
    encoding="utf-8"
)

print("Generated index.html")