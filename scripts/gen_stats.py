#!/usr/bin/env python3
"""강점 지표 카드 생성 — 연간 컨트리뷰션(비공개 포함 잔디 총합) · 개발 연차 · 운영 프로덕트 수.
GH_TOKEN 환경변수(gh CLI 또는 Actions GITHUB_TOKEN)로 GraphQL 조회 후 dist/에 SVG 2종(라이트/다크) 생성."""
import json
import os
import subprocess
import datetime

USER = os.environ.get("GH_USER", "jin7011")
PRODUCTS = os.environ.get("PRODUCTS_IN_OPERATION", "9")  # 앱 5 + 웹 4
OUT_DIR = os.environ.get("OUT_DIR", "dist")

query = (
    '{ user(login:"%s"){ createdAt contributionsCollection{ contributionCalendar{ totalContributions } } } }'
    % USER
)
raw = subprocess.check_output(["gh", "api", "graphql", "-f", f"query={query}"], text=True)
data = json.loads(raw)["data"]["user"]
total = data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
created_year = int(data["createdAt"][:4])
years = datetime.datetime.now(datetime.timezone.utc).year - created_year

stats = [
    (f"{total:,}+", "CONTRIBUTIONS", "LAST 12 MONTHS"),
    (f"{years}+", "YEARS", "BUILDING SINCE %d" % created_year),
    (PRODUCTS, "PRODUCTS", "운영중 · IN OPERATION"),
]

PALETTES = {
    "stats.svg": {"num": "#1e40af", "label": "#334155", "sub": "#64748b", "px": "#3b82f6", "px2": "#93c5fd"},
    "stats-dark.svg": {"num": "#93c5fd", "label": "#cbd5e1", "sub": "#94a3b8", "px": "#3b82f6", "px2": "#1e40af"},
}

W, H = 660, 150
COL = W // 3
FONT = "ui-monospace,'SF Mono',Consolas,Menlo,monospace"

def pixel_corner(x, y, flip_x, flip_y, c1, c2):
    """모서리 도트 장식(픽셀 3개)"""
    s = 6
    dx, dy = (-1 if flip_x else 1), (-1 if flip_y else 1)
    return (
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{c1}"/>'
        f'<rect x="{x + dx * s}" y="{y}" width="{s}" height="{s}" fill="{c2}"/>'
        f'<rect x="{x}" y="{y + dy * s}" width="{s}" height="{s}" fill="{c2}"/>'
    )

os.makedirs(OUT_DIR, exist_ok=True)
for fname, p in PALETTES.items():
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        pixel_corner(6, 6, False, False, p["px"], p["px2"]),
        pixel_corner(W - 12, 6, True, False, p["px"], p["px2"]),
        pixel_corner(6, H - 12, False, True, p["px"], p["px2"]),
        pixel_corner(W - 12, H - 12, True, True, p["px"], p["px2"]),
    ]
    for i, (num, label, sub) in enumerate(stats):
        cx = COL * i + COL // 2
        parts.append(
            f'<text x="{cx}" y="68" text-anchor="middle" font-family="{FONT}" '
            f'font-size="34" font-weight="700" fill="{p["num"]}">{num}</text>'
        )
        parts.append(
            f'<text x="{cx}" y="97" text-anchor="middle" font-family="{FONT}" '
            f'font-size="13" font-weight="700" letter-spacing="3" fill="{p["label"]}">{label}</text>'
        )
        parts.append(
            f'<text x="{cx}" y="118" text-anchor="middle" font-family="{FONT}" '
            f'font-size="9" letter-spacing="2" fill="{p["sub"]}">{sub}</text>'
        )
        if i < 2:  # 컬럼 사이 도트 구분선
            sx = COL * (i + 1)
            for j in range(4):
                parts.append(f'<rect x="{sx - 3}" y="{38 + j * 22}" width="6" height="6" fill="{p["px2"]}"/>')
    parts.append("</svg>")
    with open(os.path.join(OUT_DIR, fname), "w") as f:
        f.write("\n".join(parts))
    print(f"generated {fname}: {total:,} contributions, {years}y, {PRODUCTS} products")
