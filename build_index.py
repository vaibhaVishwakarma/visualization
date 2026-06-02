from pathlib import Path

root = Path(".")

html = """
<!DOCTYPE html>
<html>
<head>
<title>Visualizations</title>
<style>
body{font-family:Arial;padding:20px;}
h2{margin-top:30px;}
li{margin:6px 0;}
</style>
</head>
<body>

<h1>Visualizations</h1>
"""

for folder in sorted(root.iterdir()):

    if not folder.is_dir():
        continue

    files = sorted(folder.glob("*.html"))

    if not files:
        continue

    html += f"<h2>{folder.name}</h2><ul>"

    for file in files:
        rel = file.as_posix()
        name = file.stem

        html += f'<li><a href="{rel}">{name}</a></li>'

    html += "</ul>"

html += "</body></html>"

Path("index.html").write_text(html, encoding="utf8")

print("Generated index.html")