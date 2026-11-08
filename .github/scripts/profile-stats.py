import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


def fetch(path):
    request = Request(
        f"https://api.github.com{path}",
        headers={"Accept": "application/vnd.github+json"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response), response.headers.get("Link", "")


owner = os.environ["GITHUB_REPOSITORY_OWNER"]
user, _ = fetch(f"/users/{owner}")
repositories = []
page = 1
while True:
    batch, links = fetch(f"/users/{owner}/repos?type=owner&per_page=100&page={page}")
    repositories.extend(batch)
    if 'rel="next"' not in links:
        break
    page += 1

originals = [repo for repo in repositories if not repo["fork"]]
rows = (
    ("公开仓库", user["public_repos"]),
    ("获星数", sum(repo["stargazers_count"] for repo in originals)),
    ("Fork 数", sum(repo["forks_count"] for repo in originals)),
    ("关注者", user["followers"]),
)
lines = []
for index, (label, value) in enumerate(rows):
    y = 61 + index * 23
    lines.append(f'<text x="24" y="{y}">{label}</text>')
    lines.append(f'<text x="296" y="{y}" text-anchor="end">{value:,}</text>')

destination = Path("profile/stats.svg")
destination.parent.mkdir(exist_ok=True)
destination.write_text(
    f"""<svg xmlns="http://www.w3.org/2000/svg" width="320" height="165" viewBox="0 0 320 165" role="img" aria-labelledby="title">
  <title id="title">GitHub 统计</title>
  <rect width="320" height="165" rx="5" fill="#fffefe"/>
  <text x="24" y="34" fill="#2f80ed" font-family="system-ui,sans-serif" font-size="18" font-weight="600">GitHub 统计</text>
  <g fill="#434d58" font-family="system-ui,sans-serif" font-size="14">
    {chr(10).join(lines)}
  </g>
</svg>
""",
    encoding="utf-8",
)
