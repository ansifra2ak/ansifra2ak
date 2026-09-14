import re
import urllib.request
from datetime import datetime


USER = "ansifra2ak"
OUT = "contrib-heatmap.svg"

CELL = 13
GAP = 3
RADIUS = 2.5
LEFT = 34
TOP = 24

COLORS = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
]

GRAY = "#7d8590"

MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]


def get_contributions(username):
    url = f"https://github.com/users/{username}/contributions"

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8")

    pattern = re.compile(
        r'data-date="(\d{4}-\d{2}-\d{2})"'
        r'[^>]*data-level="(\d)"'
        r'[^>]*>'
    )

    matches = pattern.findall(html)

    if not matches:
        raise RuntimeError(
            "Could not read contribution data from GitHub."
        )

    contributions = []

    for date, level in matches:
        contributions.append({
            "date": date,
            "level": int(level),
        })

    total_match = re.search(
        r'([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year',
        html,
        re.IGNORECASE,
    )

    if total_match:
        total = int(total_match.group(1).replace(",", ""))
    else:
        total = 0

    return contributions, total


contributions, total = get_contributions(USER)

contributions.sort(
    key=lambda item: datetime.strptime(
        item["date"],
        "%Y-%m-%d"
    )
)

n = len(contributions)
weeks = (n + 6) // 7
step = CELL + GAP

width = LEFT + weeks * step + 6
height = TOP + 7 * step + 22

labels = []
rects = []


# -------------------------------------------------------
# Month labels
# -------------------------------------------------------

last_month = None

for week in range(weeks):

    index = week * 7

    if index >= len(contributions):
        break

    date = contributions[index]["date"]

    month = int(
        date.split("-")[1]
    )

    if month != last_month:

        last_month = month

        x = (
            LEFT
            + week * step
        )

        labels.append(
            f'''
<text
    class="label"
    x="{x}"
    y="{TOP - 8}"
>
    {MONTHS[month - 1]}
</text>
'''
        )


# -------------------------------------------------------
# Weekday labels
# -------------------------------------------------------

for name, row in [
    ("Mon", 1),
    ("Wed", 3),
    ("Fri", 5),
]:

    y = (
        TOP
        + row * step
        + CELL
        - 2
    )

    labels.append(
        f'''
<text
    class="label"
    x="2"
    y="{y}"
>
    {name}
</text>
'''
    )


# -------------------------------------------------------
# Contribution cells
# -------------------------------------------------------

max_order = (
    (weeks - 1)
    + 6 * 0.55
)

REVEAL = 3.6
DURATION = 0.55


for i, contribution in enumerate(contributions):

    week = i // 7
    row = i % 7

    level = contribution["level"]

    x = (
        LEFT
        + week * step
    )

    y = (
        TOP
        + row * step
    )

    delay = round(
        (
            week
            + row * 0.55
        )
        / max_order
        * REVEAL,
        3
    )

    rects.append(
        f'''
<rect
    class="cell"
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="{RADIUS}"
    fill="{COLORS[level]}"
    style="animation-delay:{delay}s"
/>
'''
    )


# -------------------------------------------------------
# SVG
# -------------------------------------------------------

svg = f'''
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
    font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Helvetica, Arial, sans-serif"
>

<style>

    .label {{
        fill: {GRAY};
        font-size: 13px;
        font-weight: 600;
    }}

    .total {{
        fill: #e6edf3;
        font-size: 15px;
        font-weight: 700;
    }}

    .cell {{
        transform-box: fill-box;
        transform-origin: center;

        opacity: 0;

        animation:
            pop {DURATION}s ease-out both;
    }}

    @keyframes pop {{

        0% {{
            opacity: 0;
            transform: scale(0.2);
        }}

        60% {{
            opacity: 1;
            transform: scale(1.1);
        }}

        100% {{
            opacity: 1;
            transform: scale(1);
        }}

    }}

</style>


<rect
    width="{width}"
    height="{height}"
    fill="none"
/>


{"".join(labels)}


{"".join(rects)}


<text
    class="total"
    x="{LEFT}"
    y="{height - 6}"
>
    {total:,} contributions in the last year
</text>


</svg>
'''


with open(
    OUT,
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)


print(f"Created {OUT}")
print(f"{total:,} contributions")
