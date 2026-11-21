"""Make the knowit logo, icon, and social preview card.

Run from the repository root (Python 3.11 or later, for tomllib):

    uv run --no-project --with fonttools --with resvg-py python scripts/brand.py

It writes these files to docs/images/:

- logo-light.svg, logo-dark.svg, logo-light.png, logo-dark.png: the README header (GitHub light and dark mode)
- icon.svg, icon-32.png ... icon-512.png: favicon and avatar
- social.png: the GitHub social preview. Upload it by hand: Settings, General, Social preview.

The tagline below the word mark is the `description` in pyproject.toml. The README `alt` text has the same
sentence. Change both together.

The icon is a lens over a film frame. The lens shows 2 big film holes: knowit looks inside media files.
Palette "celluloid": amber film stock on a dark tile, a cream lens with a brown grip.

All text is drawn as paths from scripts/brand/Nunito.ttf (SIL Open Font License, see scripts/brand/OFL.txt).
So the output does not depend on the fonts of the computer.

The knowit name, logo, and icon are not covered by the MIT license of this repository.
"""

import math
import tomllib
from pathlib import Path

import resvg_py
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'images'
FONT = ROOT / 'scripts' / 'brand' / 'Nunito.ttf'
TAGLINE = tomllib.loads((ROOT / 'pyproject.toml').read_text(encoding='utf-8'))['project']['description']

TILE, FILM, LENS, GRIP, WHITE = '#1c1917', '#c8913a', '#f3e7cf', '#7c4a12', '#ffffff'
IT = '#b07d2a'  # contrast 3.6 on GitHub light, 5.2 on GitHub dark
LIGHT, DARK = '#1f2328', '#f0f6fc'  # GitHub text colors
GITHUB_DARK = '#0d1117'


def font(weight: int) -> TTFont:
    f = TTFont(FONT)
    return instantiateVariableFont(f, {a.axisTag: weight if a.axisTag == 'wght' else None for a in f['fvar'].axes})


def text_path(f: TTFont, text: str, height: float, ref: str) -> tuple[str, float]:
    """Return (d, width): text as SVG path data, from x=0.

    The glyph box of `ref` is `height` high, and its top is at y=0.
    """
    glyphs, cmap = f.getGlyphSet(), f.getBestCmap()
    bounds, x = BoundsPen(glyphs), 0.0
    for ch in ref:
        glyphs[cmap[ord(ch)]].draw(TransformPen(bounds, (1, 0, 0, 1, x, 0)))
        x += glyphs[cmap[ord(ch)]].width
    assert bounds.bounds is not None
    _, y_min, _, y_max = bounds.bounds
    scale = height / (y_max - y_min)
    pen, x = SVGPathPen(glyphs), 0.0
    for ch in text:
        glyph = glyphs[cmap[ord(ch)]]
        glyph.draw(TransformPen(pen, (scale, 0, 0, -scale, x, y_max * scale)))
        x += glyph.width * scale
    return pen.getCommands(), x


def film() -> str:
    """Draw a film frame at the bottom right of the tile, with 3 holes at the top and 3 at the bottom."""
    x, y, w, h, hole = 26, 32, 66, 58, 9
    holes = ''.join(
        f'<rect x="{x + hole / 2 + 1 + i * 23:.1f}" y="{hy:.1f}" width="{hole}" height="{hole * 0.8:.1f}" rx="1.5" '
        f'fill="{TILE}"/>'
        for i in range(3)
        for hy in (y + hole * 0.6, y + h - hole * 1.4)
    )
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{hole * 0.7:.1f}" fill="{FILM}"/>{holes}'


def lens() -> str:
    """Draw a lens at the top left. The glass shows the top film edge with 2 big holes, magnified.

    A gap in the tile color separates the lens from the film. The grip is drawn first, then the cream part of the
    handle with flat ends on top of it, so the joint is a clean line.
    """
    cx, cy, r, ring, handle, gap = 40, 42, 22, 8, 10, 2.5
    d, ri, hw = r + ring / 2, r - ring / 2, ring * 1.4
    x0, y0 = cx + d * 0.7, cy + d * 0.7  # handle start, on the outer edge of the ring
    x1, y1 = x0 + handle, y0 + handle  # handle end
    gx, gy = x0 + handle * 0.35, y0 + handle * 0.35  # grip start
    sx, sy = cx + d * 0.5, cy + d * 0.5  # cream part start, under the ring
    edge = cy - ri / 2
    w, h = ri * 0.6, ri * 0.48
    zoom = f'<rect x="{cx - ri - 1:.1f}" y="{edge:.1f}" width="{2 * ri + 2:.1f}" height="{cy + ri + 1 - edge:.1f}" '
    zoom += f'fill="{FILM}"/>'
    for hx in (cx - ri / 2, cx + ri / 2):
        zoom += (
            f'<rect x="{hx - w / 2:.1f}" y="{edge + ri * 0.28:.2f}" width="{w:.1f}" height="{h:.2f}" '
            f'rx="{ri * 0.1:.1f}" fill="{TILE}"/>'
        )
    hr = ri * 0.68  # highlight arc, from 200 to 250 degrees
    a0, a1 = math.radians(200), math.radians(250)
    return (
        f'<path d="M{x0:.2f} {y0:.2f} L{x1:.2f} {y1:.2f}" stroke="{TILE}" stroke-width="{hw + 2 * gap:.1f}" '
        'stroke-linecap="round"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{d + gap}" fill="{TILE}"/>'
        f'<path d="M{gx:.2f} {gy:.2f} L{x1:.2f} {y1:.2f}" stroke="{GRIP}" stroke-width="{hw:.1f}"/>'
        f'<circle cx="{x1:.2f}" cy="{y1:.2f}" r="{hw / 2:.1f}" fill="{GRIP}"/>'
        f'<path d="M{sx:.2f} {sy:.2f} L{gx:.2f} {gy:.2f}" stroke="{LENS}" stroke-width="{hw:.1f}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{TILE}"/>'
        f'<clipPath id="glass"><circle cx="{cx}" cy="{cy}" r="{ri}"/></clipPath><g clip-path="url(#glass)">{zoom}</g>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LENS}" stroke-width="{ring}"/>'
        f'<path d="M{cx + hr * math.cos(a0):.2f} {cy + hr * math.sin(a0):.2f} '
        f'A{hr:.2f} {hr:.2f} 0 0 1 {cx + hr * math.cos(a1):.2f} {cy + hr * math.sin(a1):.2f}" fill="none" '
        f'stroke="{WHITE}" stroke-opacity=".75" stroke-width="{ring * 0.45:.1f}" stroke-linecap="round"/>'
    )


def icon() -> str:
    """Draw a dark tile with a thin light border (visible on GitHub dark). The film and the lens are clipped to it."""
    return (
        f'<rect x="1" y="1" width="98" height="98" rx="21" fill="{TILE}"/>'
        '<clipPath id="tile"><rect x="1" y="1" width="98" height="98" rx="21"/></clipPath>'
        f'<g clip-path="url(#tile)">{film()}{lens()}</g>'
        '<rect x="1" y="1" width="98" height="98" rx="21" fill="none" stroke="#ffffff" stroke-opacity=".15" '
        'stroke-width="2"/>'
    )


def logo(color: str, know: tuple[str, float], it: tuple[str, float], tagline: tuple[str, float]) -> tuple[str, float]:
    """Return (SVG body, width): the icon, then the word mark ("it" in amber) with the tagline below it.

    The height is 100.
    """
    body = (
        f'<svg width="100" height="100" viewBox="0 0 100 100">{icon()}</svg>'
        f'<path transform="translate(124 0)" d="{know[0]}" fill="{color}"/>'
        f'<path transform="translate({124 + know[1]:.2f} 0)" d="{it[0]}" fill="{IT}"/>'
        f'<path transform="translate(124 74)" d="{tagline[0]}" fill="{color}" fill-opacity=".75"/>'
    )
    return body, 124 + max(know[1] + it[1], tagline[1]) + 4  # 4: margin, the 't' goes past its advance


def svg(body: str, w: float, h: float) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">'
        f'{body}</svg>'
    )


def png(name: str, content: str, w: float, h: float) -> None:
    data = resvg_py.svg_to_bytes(svg_string=content, width=round(w), height=round(h), skip_system_fonts=True)
    (OUT / name).write_bytes(bytes(data))


def main() -> None:
    heavy = font(1000)
    know = text_path(heavy, 'know', 62, 'knowit')
    it = text_path(heavy, 'it', 62, 'knowit')
    tagline = text_path(font(600), TAGLINE, 24, TAGLINE)

    for name, color in (('logo-light', LIGHT), ('logo-dark', DARK)):
        body, w = logo(color, know, it, tagline)
        (OUT / f'{name}.svg').write_text(svg(body, w, 100) + '\n', encoding='utf-8')
        png(f'{name}.png', svg(body, w, 100), w * 4, 400)

    (OUT / 'icon.svg').write_text(svg(icon(), 100, 100) + '\n', encoding='utf-8')
    for size in (32, 64, 256, 512):
        png(f'icon-{size}.png', svg(icon(), 100, 100), size, size)

    body, w = logo(DARK, know, it, tagline)
    scale = 2.6
    card = (
        f'<rect width="1280" height="640" fill="{GITHUB_DARK}"/>'
        f'<g transform="translate({(1280 - w * scale) / 2:.1f} {320 - 50 * scale:.1f}) scale({scale})">{body}</g>'
    )
    png('social.png', svg(card, 1280, 640), 1280, 640)


if __name__ == '__main__':
    main()
