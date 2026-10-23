#!/usr/bin/env python3
"""
Gerador de 8 conceitos de personagem (IDLE) com ESTILOS DE ARTE distintos.

Cada conceito explora uma linguagem visual diferente (skill pixel-art-sprites):
proporção (chibi x realista), silhueta, paleta (Game Boy, NES, livre),
e técnica de contorno (preto, colorido, selout, rim light neon, sem contorno).

Os sprites são desenhados SEM contorno na matriz; o contorno é aplicado
automaticamente por um pós-processo de acordo com o estilo, o que garante
contorno de 1px consistente e sem falhas.

Uso:
    app/venv/bin/python tools/build_character_concepts.py
"""

from pathlib import Path
from PIL import Image, ImageDraw

CANVAS = 32
BASELINE_Y = 29  # linha onde os pés tocam o chão
CENTER_X = 16

OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "CharacterIdeas" / "concepts"


def rgb(hex_str: str) -> tuple[int, int, int, int]:
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


def darken(c, f):
    return (int(c[0] * f), int(c[1] * f), int(c[2] * f), 255)


# ---------------------------------------------------------------------------
# Renderização + contornos
# ---------------------------------------------------------------------------

def render(rows: list[str], pal: dict[str, str]) -> Image.Image:
    """Desenha a matriz centralizada horizontalmente e apoiada na BASELINE."""
    width = max(len(r) for r in rows)
    for i, r in enumerate(rows):
        for ch in r:
            if ch != "." and ch not in pal:
                raise KeyError(f"Cor '{ch}' (linha {i}) não está na paleta")
    ox = CENTER_X - width // 2
    oy = BASELINE_Y - len(rows) + 1
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                img.putpixel((ox + x, oy + y), rgb(pal[ch]))
    return img


def _neighbors4(x, y):
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


def _inside(x, y):
    return 0 <= x < CANVAS and 0 <= y < CANVAS


def outline_solid(img: Image.Image, color: str) -> Image.Image:
    """Contorno externo de 1px numa cor única (preto ou colorido)."""
    out = img.copy()
    c = rgb(color)
    for y in range(CANVAS):
        for x in range(CANVAS):
            if img.getpixel((x, y))[3]:
                continue
            if any(_inside(nx, ny) and img.getpixel((nx, ny))[3] for nx, ny in _neighbors4(x, y)):
                out.putpixel((x, y), c)
    return out


def outline_selout(img: Image.Image, factor: float = 0.42) -> Image.Image:
    """Selective outline: o contorno herda a cor vizinha escurecida."""
    out = img.copy()
    for y in range(CANVAS):
        for x in range(CANVAS):
            if img.getpixel((x, y))[3]:
                continue
            for nx, ny in _neighbors4(x, y):
                if _inside(nx, ny) and img.getpixel((nx, ny))[3]:
                    out.putpixel((x, y), darken(img.getpixel((nx, ny)), factor))
                    break
    return out


def rim_light(img: Image.Image, left: str, right: str, top: str, keep: set) -> Image.Image:
    """Silhueta escura com luz de borda neon (esquerda/direita/topo)."""
    out = img.copy()
    cl, cr, ct = rgb(left), rgb(right), rgb(top)
    for y in range(CANVAS):
        for x in range(CANVAS):
            px = img.getpixel((x, y))
            if not px[3] or px in keep:
                continue

            def empty(nx, ny):
                return not _inside(nx, ny) or not img.getpixel((nx, ny))[3]

            if empty(x, y - 1):
                out.putpixel((x, y), ct)
            elif empty(x - 1, y):
                out.putpixel((x, y), cl)
            elif empty(x + 1, y):
                out.putpixel((x, y), cr)
    return out


def internal_holes(img: Image.Image) -> list[tuple[int, int]]:
    """Pixels transparentes presos dentro do corpo (flood fill a partir da borda)."""
    seen = set()
    stack = [(x, y) for x in range(CANVAS) for y in (0, CANVAS - 1)]
    stack += [(x, y) for y in range(CANVAS) for x in (0, CANVAS - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not _inside(x, y) or img.getpixel((x, y))[3]:
            continue
        seen.add((x, y))
        stack.extend(_neighbors4(x, y))
    return [
        (x, y)
        for y in range(CANVAS)
        for x in range(CANVAS)
        if not img.getpixel((x, y))[3] and (x, y) not in seen
    ]


# ---------------------------------------------------------------------------
# 01. CHIBI MASCOTE — cabeça = ~60% da altura, contorno colorido, pastel
# ---------------------------------------------------------------------------
CHIBI = dict(
    key="01_chibi_mascot",
    title="01. Kiko - Chibi Mascote",
    style="Chibi | contorno roxo colorido | paleta pastel",
    desc="Faxineira fofa com capacete de obra gigante, oculos de protecao e rodo na mao. Leitura instantanea, ideal para mobile.",
    pal={
        "H": "#d98e04", "h": "#ffc93c", "w": "#fff4c2",
        "S": "#e0956b", "s": "#ffd3b0", "r": "#ff8fa3", "m": "#9c3a4a",
        "G": "#3d3b5c", "c": "#5ee7ff", "W": "#ffffff",
        "B": "#3a5fcd", "b": "#6b8cff", "Y": "#ffc93c",
        "N": "#6b3d2e", "g": "#9aa3b5", "x": "#e6ebf5",
    },
    rows=[
        ".....HHHHHH.....",
        "...HHhhhhhhHH...",
        "..HhwwhhhhhhhH..",
        ".HhwhhhhhhhhhhH.",
        ".HHHHHHHHHHHHHHH",
        ".Sssssssssssss..",
        ".SsGGGGGsGGGGGs.",
        ".SsGcWcGsGcWcGs.",
        ".SsGGGGGsGGGGGs.",
        ".SsrsssssssssrS.",
        "..SSsssmmsssSS..",
        "....SSSSSSSS.xxx",
        ".....BYBBYB...g.",
        "...ssBYbbYBs..g.",
        "....BBbbbbBBsSg.",
        "....BbbbbbbB..g.",
        "....BBB..BBB....",
        "...NNNN..NNNN...",
        "...NNNN..NNNN...",
    ],
    outline=("solid", "#3a2050"),
)

# ---------------------------------------------------------------------------
# 02. NOIR REALISTA — perfil, proporção 1:4, paleta dessaturada, selout
# ---------------------------------------------------------------------------
NOIR = dict(
    key="02_noir_realist",
    title="02. Vance - Noir Realista",
    style="Realista esguio | perfil | selout | paleta dessaturada",
    desc="Alpinista veterano de perfil, chapeu, sobretudo longo e cachecol vermelho ao vento. Unico ponto de cor: o vermelho.",
    pal={
        "H": "#3b3d47", "h": "#1d1e24", "s": "#d9c3ad", "E": "#2a2020",
        "R": "#c4243b", "C": "#5c5a63", "c": "#827f8a", "B": "#2e2c33",
        "P": "#34343d", "N": "#18181c",
    },
    rows=[
        ".....HHHH.....",
        ".....HHHH.....",
        "...HHHHHHHH...",
        ".....hhss.....",
        ".....hsEs.....",
        ".....hssss....",
        "......sss.....",
        ".....RRRR.....",
        "....RRCCCC....",
        "...RRCCCCCC...",
        "..RR.CCcCCC...",
        ".....CCcCCC...",
        ".....CCcCCC...",
        ".....CCcCCCs..",
        ".....BBBBBB...",
        ".....CCcCCC...",
        "....CCCcCCCC..",
        "....CCCcCCCC..",
        "...CCCCcCCCCC.",
        "...CCCPP.PPCC.",
        "......PP.PP...",
        "......PP.PP...",
        "......PP.PP...",
        "......PP.PP...",
        "......PP.PP...",
        "......NNN.NNN.",
    ],
    outline=("selout", None),
)

# ---------------------------------------------------------------------------
# 03. GAME BOY DMG — 4 tons de verde, sprite compacto e robusto
# ---------------------------------------------------------------------------
DMG = dict(
    key="03_gameboy_dmg",
    title="03. Pip - Game Boy DMG",
    style="4 cores (Game Boy) | compacto | contorno do tom mais escuro",
    desc="Limpador encapuzado com tanque de solvente nas costas e bico pulverizador. Restricao total de paleta, estilo 1989.",
    pal={"D": "#0f380f", "d": "#306230", "l": "#8bac0f", "L": "#c4d64a"},
    rows=[
        "......dddd......",
        "....ddddddd.....",
        "...dddddLLLd....",
        "...ddddLLDLLd...",
        "...ddddLLLLLd...",
        "...dddddLLLd....",
        ".llll.dddddd....",
        "lLLLllDdlllld...",
        "lLDDllDdlllldLD.",
        "lLLLllDdlllld...",
        "lLDDllDddddd....",
        "llllllDdlllld...",
        ".llll...dd.dd...",
        "........dd.dd...",
        "........dd.dd...",
        ".......DDD.DDD..",
    ],
    outline=("solid", "#0f380f"),
)

# ---------------------------------------------------------------------------
# 04. NES 8-BIT — 3 cores + preto, capacetão e canhão-gancho no braço
# ---------------------------------------------------------------------------
NES = dict(
    key="04_nes_8bit",
    title="04. Rook - NES 8-bit",
    style="3 cores + preto (NES) | capacete grande | braco-canhao",
    desc="Heroi classico estilo plataforma: capacete arredondado, lancador de gancho acoplado ao braco e botas largas.",
    pal={"B": "#0058f8", "c": "#3cbcfc", "s": "#fcbcb0", "K": "#000000"},
    rows=[
        ".....BBBBB......",
        "....BBBBBBB.....",
        "...BBcBBBBBB....",
        "...BBBssssBB....",
        "...BBssKsKsB....",
        "...BBsssssB.....",
        "....BBsKKsB.....",
        ".....BBBBB......",
        "...cBBBBBBBccc..",
        "..ccBBcBBBBcccc.",
        "..ccBBBBBBBcccK.",
        "..sBBBBBBBBccc..",
        "....cccccc......",
        "....BBB.BBB.....",
        "...BBBB.BBBB....",
        "..cccBB.BBccc...",
        "..ccccc.ccccc...",
    ],
    outline=("solid", "#000000"),
)

# ---------------------------------------------------------------------------
# 05. SILHUETA NEON — corpo escuro, rim light magenta/ciano (synthwave)
# ---------------------------------------------------------------------------
NEON = dict(
    key="05_neon_silhouette",
    title="05. Vex - Silhueta Neon",
    style="Silhueta escura | rim light magenta/ciano | sem contorno",
    desc="Corredora esguia vista quase em contraluz, rabo de cavalo de cabos, visor e nucleo brilhando. Feita para o fundo noturno.",
    pal={"X": "#141226", "V": "#5ef2ff", "G": "#ff3df2"},
    rows=[
        ".......XXX......",
        "......XXXXX.....",
        "......XXVVVV....",
        "...XXXXXXXXX....",
        "..XX...XXXX.....",
        "..X...XXXXXX....",
        "..X..XXXXXXXX...",
        "....XX.XXXXX.XX.",
        "....XX.XXXXX.XX.",
        "....XX.XXGXX.XX.",
        "....XX.XXXXX.XX.",
        "...XXX..XXX..XXX",
        ".......XXXXX....",
        "......XXXXXXX...",
        "......XXX.XXX...",
        "......XXX.XXX...",
        "......XXX.XXX...",
        "......XXX.XXX...",
        "......XXX.XXX...",
        "......XXX.XXX...",
        ".....XXXX.XXXX..",
    ],
    outline=("rim", dict(left="#ff3df2", right="#29d9ff", top="#ffb8f7", keep="VG")),
)

# ---------------------------------------------------------------------------
# 06. MECH CARTOON — piloto pequeno numa cápsula andante de mãos enormes
# ---------------------------------------------------------------------------
MECH = dict(
    key="06_mech_cartoon",
    title="06. Bolt - Mech Cartoon",
    style="Cartoon atarracado | silhueta larga | contorno preto grosso",
    desc="Piloto minusculo dentro de uma capsula de vidro, num traje-mech laranja com garras gigantes e medidor no peito.",
    pal={
        "G": "#7fd6e8", "w": "#e8fbff", "s": "#ffcc99", "K": "#1a1a1a",
        "O": "#e0601f", "o": "#ff9a3d", "Y": "#ffe14d", "T": "#1f8a8a",
        "M": "#4a4f5c",
    },
    rows=[
        ".......GGGGG........",
        "......GwGGGGG.......",
        "......GwsssGG.......",
        "......GGsKsGG.......",
        "....OOOOOOOOOOO.....",
        "...OOooooooooOOO....",
        "..TOooYYYYooooOOT...",
        ".TTOooYKKYooooOOTT..",
        ".TTOooYYYYooooOOTT..",
        "TTTOOooooooooOOOTTT.",
        "TTT.OOOOOOOOOOO.TTT.",
        "T.T...MM...MM...T.T.",
        "......MM...MM.......",
        ".....MMMM.MMMM......",
        "....OOOOO.OOOOO.....",
    ],
    outline=("solid", "#111111"),
)

# ---------------------------------------------------------------------------
# 07. ANDARILHO MINIMALISTA — cores chapadas, capa triangular, sem contorno
# ---------------------------------------------------------------------------
DRIFTER = dict(
    key="07_minimal_drifter",
    title="07. Nul - Andarilho Minimalista",
    style="Formas chapadas | 3 cores | sem contorno (Hyper Light Drifter)",
    desc="Figura encapuzada sem rosto, so um olho brilhante. Capa triangular e cachecol longo. Misterioso e elegante.",
    pal={"C": "#c23b5a", "D": "#2b1830", "t": "#3ee6c8"},
    rows=[
        "........CC........",
        ".......CCCC.......",
        "......CCDDDC......",
        "......CDDtDC......",
        "......CCDDDC......",
        "..ttt.CCCCCC......",
        "tttttCCCCCCCC.....",
        ".tt..CCCCCCCCC....",
        "....CCCCCCCCCC....",
        "....CCCCCCCCCCCt..",
        "...CCCCCCCCCCCC...",
        "...CCCCCCCCCCCCC..",
        "..CCCCCCCCCCCCCC..",
        "..CCCCCCCCCCCCCCC.",
        ".......DD.DD......",
        ".......DD.DD......",
    ],
    outline=None,
)

# ---------------------------------------------------------------------------
# 08. CYBER-GUAXINIM 16-BIT — antropomórfico, orelhas e cauda listrada
# ---------------------------------------------------------------------------
RACCOON = dict(
    key="08_cyber_raccoon",
    title="08. Rizzo - Cyber-Guaxinim 16-bit",
    style="Antropomorfico | 16-bit com hue shift | contorno roxo escuro",
    desc="Guaxinim de moletom com oculos ambar na testa, mascara natural e cauda listrada. Silhueta unica com orelhas e cauda.",
    pal={
        "G": "#4a4556", "g": "#8a8499", "l": "#c2bccf", "w": "#f2eefa",
        "M": "#231f2e", "E": "#ffffff", "N": "#1a1520", "Y": "#ffb300",
        "H": "#146b6b", "h": "#22a3a3", "i": "#6ee0d2",
        "T": "#2e2a38", "t": "#a39cb5", "P": "#3b3550", "S": "#e84a5f",
    },
    rows=[
        ".....G....G.......",
        "....GgG..GgG......",
        "....GgggggggG.....",
        "...GgYYgggYYgG....",
        "...GwwgggggwwG....",
        "...MMEMgggMEMM....",
        "...GMMwwwwwMMG....",
        "....GwwwNwwwG.....",
        ".....GwwwwwG......",
        ".....HHHHHHH......",
        "TT..HhhihhhhH.....",
        "Tt.HhhhihhhhhHl...",
        "tT.HhhhhihhhhH....",
        "Tt.HhhhhhhhhhH....",
        "tTtHHHHHHHHHHH....",
        ".tT.PPPP.PPPP.....",
        "....PPPP.PPPP.....",
        ".....PP...PP......",
        "....SSSS.SSSS.....",
    ],
    outline=("solid", "#2a1a2e"),
)

CONCEPTS = [CHIBI, NOIR, DMG, NES, NEON, MECH, DRIFTER, RACCOON]


def seal_gaps(img: Image.Image) -> Image.Image:
    """Fecha frestas de 1px presas entre partes do corpo (ex.: mão e cabo do rodo)
    pintando-as com a cor vizinha escurecida, para não sobrar pixel vazio."""
    out = img.copy()
    for x, y in internal_holes(img):
        for nx, ny in _neighbors4(x, y):
            if _inside(nx, ny) and img.getpixel((nx, ny))[3]:
                out.putpixel((x, y), darken(img.getpixel((nx, ny)), 0.6))
                break
    return out


def build(concept: dict) -> Image.Image:
    img = render(concept["rows"], concept["pal"])
    mode = concept["outline"]
    if mode is None:
        return seal_gaps(img)
    kind, arg = mode
    if kind == "solid":
        img = outline_solid(img, arg)
    elif kind == "selout":
        img = outline_selout(img)
    elif kind == "rim":
        keep = {rgb(concept["pal"][k]) for k in arg["keep"]}
        img = rim_light(img, arg["left"], arg["right"], arg["top"], keep)
    else:
        raise ValueError(kind)
    return seal_gaps(img)


def make_showcase(items: list[tuple[dict, Image.Image]]) -> Image.Image:
    cols, card_w, card_h = 4, 290, 380
    W = cols * card_w + 30
    H = 2 * card_h + 90
    sheet = Image.new("RGBA", (W, H), (16, 16, 24, 255))
    d = ImageDraw.Draw(sheet)
    d.rectangle([(0, 0), (W, 60)], fill=(10, 10, 16, 255))
    d.line([(0, 60), (W, 60)], fill=(0, 229, 255, 255), width=2)
    d.text((20, 14), "APEX GRAPPLER - 8 ESTILOS DE ARTE PARA O PROTAGONISTA (IDLE)", fill=(255, 255, 255, 255))
    d.text((20, 36), "Cada card usa proporcao, paleta e tecnica de contorno diferentes. Sprite nativo 32x32, ampliado 5x.", fill=(170, 180, 200, 255))

    for i, (c, img) in enumerate(items):
        cx = 15 + (i % cols) * card_w
        cy = 75 + (i // cols) * card_h
        d.rectangle([(cx, cy), (cx + card_w - 12, cy + card_h - 12)], fill=(26, 28, 40, 255), outline=(48, 52, 72, 255))
        # Fundo do sprite: tom da cidade noturna para avaliar contraste real
        bx, by = cx + (card_w - 12 - 160) // 2, cy + 12
        d.rectangle([(bx, by), (bx + 159, by + 159)], fill=(30, 26, 52, 255))
        big = img.resize((160, 160), Image.Resampling.NEAREST)
        sheet.paste(big, (bx, by), big)

        d.text((cx + 10, cy + 182), c["title"], fill=(255, 220, 40, 255))
        d.text((cx + 10, cy + 200), c["style"], fill=(0, 229, 255, 255))
        words, lines, cur = c["desc"].split(), [], ""
        for w in words:
            if len(cur) + len(w) + 1 > 42:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        for j, line in enumerate(lines[:4]):
            d.text((cx + 10, cy + 224 + j * 15), line, fill=(195, 200, 215, 255))
        d.text((cx + 10, cy + 330), "1x:", fill=(120, 130, 150, 255))
        sheet.paste(img, (cx + 34, cy + 318), img)
        x2 = img.resize((64, 64), Image.Resampling.NEAREST)
        d.text((cx + 80, cy + 330), "2x:", fill=(120, 130, 150, 255))
        sheet.paste(x2, (cx + 104, cy + 290), x2)
    return sheet


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Remove conceitos antigos para não deixar arquivos órfãos
    for old in OUT_DIR.glob("*.png"):
        old.unlink()

    items = []
    for c in CONCEPTS:
        img = build(c)
        holes = internal_holes(img)
        if holes:
            raise RuntimeError(f"{c['key']}: {len(holes)} pixels vazios dentro do corpo: {holes}")
        img.save(OUT_DIR / f"concept_{c['key']}.png")
        img.resize((256, 256), Image.Resampling.NEAREST).save(OUT_DIR / f"preview_8x_{c['key']}.png")
        items.append((c, img))
        print(f"[OK] {c['title']}")

    strip = Image.new("RGBA", (CANVAS * len(items), CANVAS), (0, 0, 0, 0))
    for i, (_, img) in enumerate(items):
        strip.paste(img, (i * CANVAS, 0))
    strip.save(OUT_DIR / "all_8_concepts_strip_256x32.png")
    make_showcase(items).save(OUT_DIR / "concepts_showcase_comparison.png")
    print("Showcase e spritesheet gerados.")


if __name__ == "__main__":
    main()
