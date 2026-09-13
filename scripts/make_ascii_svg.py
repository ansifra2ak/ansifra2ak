from PIL import Image, ImageEnhance, ImageFilter
import html
import os


HERE = os.path.dirname(os.path.abspath(__file__))

SRC = os.path.join(HERE, "..", "source-prepped.png")
OUT = os.path.join(HERE, "..", "ansif-ascii.svg")


# -------------------------------------------------------
# ASCII portrait settings
# -------------------------------------------------------

COLS = 100
ROWS = 53

CELL_W = 8
CELL_H = 15

# Bright/sparse -> dark/dense
RAMP = " .`:-=+*cs#%@"

CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.18

# Anything brighter than this becomes blank space.
WHITE_FLOOR = 0.80


# -------------------------------------------------------
# Terminal panel geometry
# -------------------------------------------------------

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30

ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H

CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD


# -------------------------------------------------------
# Colors — same visual family as reference
# -------------------------------------------------------

BG = "#0d1117"
BG2 = "#111722"

FRAME = "#30363d"

TITLE_TEXT = "#7d8590"

INK = "#c9d1d9"
CURSOR = "#c9d1d9"


# -------------------------------------------------------
# Animation timing
# -------------------------------------------------------

ROW_DUR = 0.11
STAGGER = 0.11


# -------------------------------------------------------
# 1. Load prepared photo
# -------------------------------------------------------

img = Image.open(SRC).convert("L")

img = ImageEnhance.Brightness(img).enhance(
    BRIGHTNESS
)

img = ImageEnhance.Contrast(img).enhance(
    CONTRAST
)

img = img.resize(
    (COLS, ROWS),
    Image.Resampling.LANCZOS
)

pixels = img.load()


# -------------------------------------------------------
# 2. Convert image to ASCII rows
# -------------------------------------------------------

ascii_rows = []

for y in range(ROWS):

    chars = []

    for x in range(COLS):

        lum = pixels[x, y] / 255.0

        # Brighten midtones slightly.
        lum = pow(
            lum,
            GAMMA
        )

        # White background becomes blank space.
        if lum >= WHITE_FLOOR:
            chars.append(" ")
            continue

        index = int(
            (1.0 - lum)
            * (len(RAMP) - 1)
            + 0.5
        )

        index = max(
            0,
            min(
                len(RAMP) - 1,
                index
            )
        )

        chars.append(
            RAMP[index]
        )

    ascii_rows.append(
        "".join(chars)
    )


# -------------------------------------------------------
# 3. Begin SVG
# -------------------------------------------------------

art_top = (
    TITLEBAR_H
    + PAD * 0.35
)

font_size = (
    CELL_H * 0.86
)

parts = []


parts.append(

    f'''
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{CANVAS_W}"
    height="{CANVAS_H}"
    viewBox="0 0 {CANVAS_W} {CANVAS_H}"
    font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
>
'''
)


# -------------------------------------------------------
# Background gradient
# -------------------------------------------------------

parts.append(

    f'''
<defs>

    <linearGradient
        id="bg"
        x1="0"
        y1="0"
        x2="0"
        y2="1"
    >

        <stop
            offset="0"
            stop-color="{BG2}"
        />

        <stop
            offset="1"
            stop-color="{BG}"
        />

    </linearGradient>

</defs>
'''
)


# -------------------------------------------------------
# Terminal window
# -------------------------------------------------------

parts.append(

    f'''
<rect
    width="{CANVAS_W}"
    height="{CANVAS_H}"
    rx="12"
    fill="url(#bg)"
/>

<rect
    x="0.5"
    y="0.5"
    width="{CANVAS_W - 1}"
    height="{CANVAS_H - 1}"
    rx="12"
    fill="none"
    stroke="{FRAME}"
    stroke-width="1"
/>
'''
)


# -------------------------------------------------------
# Terminal title bar
# -------------------------------------------------------

parts.append(

    f'''
<line
    x1="0"
    y1="{TITLEBAR_H}"
    x2="{CANVAS_W}"
    y2="{TITLEBAR_H}"
    stroke="{FRAME}"
/>
'''
)


# macOS window dots

DOT_COLORS = [
    "#ff5f56",
    "#ffbd2e",
    "#27c93f"
]

for i, color in enumerate(
    DOT_COLORS
):

    parts.append(

        f'''
<circle
    cx="{PAD + i * 16}"
    cy="{TITLEBAR_H / 2}"
    r="5"
    fill="{color}"
/>
'''
    )


# Terminal title

parts.append(

    f'''
<text
    x="{CANVAS_W / 2}"
    y="{TITLEBAR_H / 2 + 4}"
    fill="{TITLE_TEXT}"
    font-size="12"
    text-anchor="middle"
>
    ansifra2ak@github: ~$ ./portrait.sh
</text>
'''
)


# -------------------------------------------------------
# 4. ASCII rows
#
# Each row wipes from left -> right.
# Cursor moves with the row.
# -------------------------------------------------------

for row_index, line in enumerate(
    ascii_rows
):

    y = (
        art_top
        + row_index * CELL_H
        + CELL_H * 0.74
    )

    row_y = (
        art_top
        + row_index * CELL_H
    )

    delay = (
        row_index
        * STAGGER
    )

    safe_text = html.escape(
        line
    )


    # Clip path revealing each row

    parts.append(

        f'''
<clipPath id="row-{row_index}">

    <rect
        x="{PAD}"
        y="{row_y:.1f}"
        height="{CELL_H}"
        width="0"
    >

        <animate
            attributeName="width"
            from="0"
            to="{ART_W}"
            begin="{delay:.3f}s"
            dur="{ROW_DUR:.2f}s"
            fill="freeze"
        />

    </rect>

</clipPath>
'''
    )


    # ASCII text row

    parts.append(

        f'''
<g clip-path="url(#row-{row_index})">

    <text
        xml:space="preserve"
        x="{PAD}"
        y="{y:.1f}"
        fill="{INK}"
        font-size="{font_size:.1f}"
        textLength="{ART_W}"
        lengthAdjust="spacing"
    >
        {safe_text}
    </text>

</g>
'''
    )


    # Moving typing cursor

    parts.append(

        f'''
<rect
    y="{row_y + 1:.1f}"
    width="{CELL_W}"
    height="{CELL_H - 2}"
    fill="{CURSOR}"
    opacity="0"
>

    <animate
        attributeName="x"
        from="{PAD}"
        to="{PAD + ART_W}"
        begin="{delay:.3f}s"
        dur="{ROW_DUR:.2f}s"
        fill="freeze"
    />

    <set
        attributeName="opacity"
        to="0.85"
        begin="{delay:.3f}s"
    />

    <set
        attributeName="opacity"
        to="0"
        begin="{delay + ROW_DUR:.3f}s"
    />

</rect>
'''
    )


# -------------------------------------------------------
# 5. Terminal bottom status
# -------------------------------------------------------

status_line_y = (
    TITLEBAR_H
    + ART_H
    + PAD * 0.35
)

status_y = (
    status_line_y
    + 19
)


parts.append(

    f'''
<line
    x1="0"
    y1="{status_line_y:.1f}"
    x2="{CANVAS_W}"
    y2="{status_line_y:.1f}"
    stroke="{FRAME}"
/>
'''
)


parts.append(

    f'''
<text
    x="{PAD}"
    y="{status_y:.1f}"
    fill="{TITLE_TEXT}"
    font-size="13"
>

    ansifra2ak@github:~$ whoami

    <tspan fill="{INK}">
        Ansif Rasak
    </tspan>

</text>
'''
)


# -------------------------------------------------------
# 6. Blinking terminal cursor
# -------------------------------------------------------

parts.append(

    f'''
<rect
    x="{PAD + 260}"
    y="{status_y - 12:.1f}"
    width="8"
    height="14"
    fill="{INK}"
>

    <animate
        attributeName="opacity"
        values="1;1;0;0"
        keyTimes="0;0.5;0.51;1"
        dur="1s"
        repeatCount="indefinite"
    />

</rect>
'''
)


# -------------------------------------------------------
# Finish SVG
# -------------------------------------------------------

parts.append(
    "</svg>"
)

svg = "".join(
    parts
)


with open(
    OUT,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        svg
    )


print(
    "Created:",
    OUT
)

print(
    "Canvas:",
    CANVAS_W,
    "x",
    CANVAS_H
)
