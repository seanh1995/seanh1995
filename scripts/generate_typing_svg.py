import os

LINES = [
    "Sean",
    "Go / Docker / PowerShell",
    "Learning new languages by building with AI",
    "Currently working on Forgejo Encrypt Mirror",
]

FONT_SIZE = 22
CHAR_WIDTH = FONT_SIZE * 0.6
COLOR = "#58A6FF"
WIDTH = 600
HEIGHT = 40
SPEED = 18.0  # chars per second
HOLD = 1.3
ERASE_FACTOR = 0.6


def build_slots():
    slots = []
    cursor = 0.0
    for text in LINES:
        type_dur = max(len(text) / SPEED, 0.3)
        erase_dur = type_dur * ERASE_FACTOR
        slot_dur = type_dur + HOLD + erase_dur
        full_width = round(len(text) * CHAR_WIDTH, 1)
        slots.append({
            "text": text,
            "start": cursor,
            "type_dur": type_dur,
            "erase_dur": erase_dur,
            "slot_dur": slot_dur,
            "full_width": full_width,
        })
        cursor += slot_dur
    return slots, cursor


def animate_values(slot, total):
    s = slot["start"]
    type_end = s + slot["type_dur"]
    hold_end = type_end + HOLD
    e = s + slot["slot_dur"]
    full = slot["full_width"]

    points = []
    if s > 0:
        points.append((0.0, 0))
    points.append((s / total, 0))
    points.append((type_end / total, full))
    points.append((hold_end / total, full))
    points.append((e / total, 0))
    if e < total:
        points.append((1.0, 0))

    key_times = ";".join(f"{p[0]:.5f}" for p in points)
    values = ";".join(f"{p[1]}" for p in points)
    return key_times, values


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    slots, total = build_slots()
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}">'
    ]
    for i, slot in enumerate(slots):
        key_times, values = animate_values(slot, total)
        clip_id = f"clip{i}"
        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(f'<rect x="0" y="0" width="0" height="{HEIGHT}">')
        parts.append(
            f'<animate attributeName="width" keyTimes="{key_times}" values="{values}" '
            f'dur="{total:.3f}s" begin="0s" repeatCount="indefinite" calcMode="linear" />'
        )
        parts.append("</rect>")
        parts.append("</clipPath>")
        parts.append(
            f'<text x="2" y="{HEIGHT * 0.68:.1f}" clip-path="url(#{clip_id})" '
            f'font-family="Consolas, Menlo, monospace" font-size="{FONT_SIZE}" '
            f'fill="{COLOR}">{escape(slot["text"])}</text>'
        )
    parts.append("</svg>")

    os.makedirs("assets", exist_ok=True)
    with open("assets/typing.svg", "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


if __name__ == "__main__":
    main()
