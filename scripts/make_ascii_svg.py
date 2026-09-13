from PIL import Image, ImageEnhance

INPUT_IMAGE = "source-prepped.png"
OUTPUT_SVG = "ansif-ascii.svg"

ASCII_CHARS = "@%#*+=-:. "
WIDTH = 62


def image_to_ascii(image_path):
    img = Image.open(image_path).convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.4)

    aspect_ratio = img.height / img.width
    height = int(WIDTH * aspect_ratio * 0.48)

    img = img.resize((WIDTH, height))

    pixels = list(img.getdata())
    lines = []

    for y in range(height):
        line = ""

        for x in range(WIDTH):
            pixel = pixels[y * WIDTH + x]
            index = int(pixel / 255 * (len(ASCII_CHARS) - 1))
            line += ASCII_CHARS[index]

        lines.append(line)

    return lines


def create_svg(lines):
    font_size = 10
    line_height = 11

    svg_width = WIDTH * 6.1
    svg_height = len(lines) * line_height + 40

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{svg_width}"
    height="{svg_height}"
    viewBox="0 0 {svg_width} {svg_height}">

    <rect width="100%" height="100%" fill="#0d1117" rx="8"/>

    <style>
        .ascii-line {{
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: {font_size}px;
            fill: #c9d1d9;
            opacity: 0;
            animation: reveal 0.08s forwards;
        }}

        @keyframes reveal {{
            from {{
                opacity: 0;
                transform: translateY(2px);
            }}

            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .cursor {{
            fill: #c9d1d9;
            animation: blink 1s steps(1) infinite;
        }}

        @keyframes blink {{
            50% {{
                opacity: 0;
            }}
        }}
    </style>

    <text
        x="14"
        y="18"
        font-family="monospace"
        font-size="10"
        fill="#8b949e">
        ansifra2ak@github:~$ ./whoami
    </text>
'''

    start_y = 35

    for i, line in enumerate(lines):
        escaped = (
            line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

        y = start_y + (i * line_height)
        delay = i * 0.035

        svg += f'''
    <text
        class="ascii-line"
        x="10"
        y="{y}"
        xml:space="preserve"
        style="animation-delay:{delay:.3f}s">
        {escaped}
    </text>
'''

    cursor_y = start_y + len(lines) * line_height + 4

    svg += f'''
    <rect
        class="cursor"
        x="10"
        y="{cursor_y}"
        width="7"
        height="2"
    />

</svg>
'''

    return svg


ascii_lines = image_to_ascii(INPUT_IMAGE)
svg_content = create_svg(ascii_lines)

with open(OUTPUT_SVG, "w", encoding="utf-8") as file:
    file.write(svg_content)

print(f"Created {OUTPUT_SVG}")
