from pathlib import Path

LINES = [
    "Hi, I'm Sean",
    "Open source contributor: winutil & linutil",
    "Python / Java / SQL / Docker",
    "HTML and CSS, written by hand",
    "Always building something new",
]

FONT_SIZE = 22
CHAR_WIDTH = FONT_SIZE * 0.6
COLOR_DARK = "#58A6FF"
COLOR_LIGHT = "#0969DA"
PADDING = 20
LEFT_X = 2
MIN_WIDTH = 600
HEIGHT = 40
SPEED = 16.0  # chars per second
HOLD = 1.6
ERASE_SPEED = 30.0  # chars per second
GAP = 0.3  # pause between lines
CURSOR_WIDTH = 2
BLINK = 0.6  # seconds per blink cycle

OUTPUT = Path(__file__).resolve().parent.parent / "assets" / "typing.svg"


def text_width(text):
    return round(len(text) * CHAR_WIDTH, 1)


def build_slots(origin_for):
    slots = []
    cursor = 0.0
    for text in LINES:
        type_dur = max(len(text) / SPEED, 0.3)
        erase_dur = max(len(text) / ERASE_SPEED, 0.2)
        slot_dur = type_dur + HOLD + erase_dur + GAP
        full_width = text_width(text)
        slots.append({
            "text": text,
            "start": cursor,
            "type_dur": type_dur,
            "erase_dur": erase_dur,
            "slot_dur": slot_dur,
            "full_width": full_width,
            "x": origin_for(full_width),
        })
        cursor += slot_dur
    return slots, cursor


def animate_values(slot, total):
    """Keyframes of the revealed width: 0 -> full (typing) -> full (hold) -> 0 (erase)."""
    s = slot["start"]
    type_end = s + slot["type_dur"]
    hold_end = type_end + HOLD
    erase_end = hold_end + slot["erase_dur"]
    full = slot["full_width"]

    points = []
    if s > 0:
        points.append((0.0, 0))
    points.append((s / total, 0))
    points.append((type_end / total, full))
    points.append((hold_end / total, full))
    points.append((erase_end / total, 0))
    if erase_end < total:
        points.append((1.0, 0))
    return points


def join(points, index, fmt):
    return ";".join(fmt(p[index]) for p in points)


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    longest = max(text_width(t) for t in LINES)
    width = max(MIN_WIDTH, int(longest + PADDING * 2))
    slots, total = build_slots(lambda w: LEFT_X)
    baseline = round(HEIGHT * 0.68, 1)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" '
        f'viewBox="0 0 {width} {HEIGHT}" role="img" aria-label="{escape(" | ".join(LINES))}">',
        "<style>"
        f".t,.c{{fill:{COLOR_DARK}}}"
        f"@media (prefers-color-scheme:light){{.t,.c{{fill:{COLOR_LIGHT}}}}}"
        "</style>",
    ]

    for i, slot in enumerate(slots):
        points = animate_values(slot, total)
        key_times = join(points, 0, lambda v: f"{v:.5f}")
        widths = join(points, 1, str)
        cursor_x = ";".join(f"{slot['x'] + p[1] + CHAR_WIDTH:.1f}" for p in points)
        visible_from = slot["start"] / total
        visible_to = (slot["start"] + slot["slot_dur"] - GAP) / total
        clip_id = f"clip{i}"

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(f'<rect x="{slot["x"]}" y="0" width="0" height="{HEIGHT}">')
        parts.append(
            f'<animate attributeName="width" keyTimes="{key_times}" values="{widths}" '
            f'dur="{total:.3f}s" repeatCount="indefinite" calcMode="linear" />'
        )
        parts.append("</rect>")
        parts.append("</clipPath>")
        parts.append(
            f'<text class="t" x="{slot["x"]}" y="{baseline}" clip-path="url(#{clip_id})" '
            f'textLength="{slot["full_width"]}" lengthAdjust="spacing" '
            f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}">'
            f'{escape(slot["text"])}</text>'
        )

        # Cursor: follows the text edge, only shown during its own line, blinks while idle.
        parts.append('<g opacity="0">')
        parts.append(
            f'<animate attributeName="opacity" calcMode="discrete" '
            f'keyTimes="0;{visible_from:.5f};{visible_to:.5f}" values="0;1;0" '
            f'dur="{total:.3f}s" repeatCount="indefinite" />'
        )
        parts.append(
            f'<rect class="c" x="{slot["x"] + CHAR_WIDTH:.1f}" y="{HEIGHT * 0.2:.1f}" '
            f'width="{CURSOR_WIDTH}" height="{HEIGHT * 0.6:.1f}">'
        )
        parts.append(
            f'<animate attributeName="x" keyTimes="{key_times}" values="{cursor_x}" '
            f'dur="{total:.3f}s" repeatCount="indefinite" calcMode="linear" />'
        )
        parts.append(
            f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" '
            f'dur="{BLINK}s" repeatCount="indefinite" calcMode="discrete" />'
        )
        parts.append("</rect>")
        parts.append("</g>")

    parts.append("</svg>")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(parts), encoding="utf-8")


if __name__ == "__main__":
    main()
