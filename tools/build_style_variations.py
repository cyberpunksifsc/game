#!/usr/bin/env python3
"""
Variações dos estilos escolhidos: 02 (Noir Realista), 03 (Game Boy DMG) e 04 (NES 8-bit).

Reaproveita o motor de renderização/contorno de build_character_concepts.py e gera
3 novos personagens por estilo, mantendo as regras de cada linguagem visual:
  - Noir: perfil, proporção ~1:4, paleta dessaturada + 1 cor de destaque, selout.
  - DMG: 4 tons apenas, sprite compacto, contorno no tom mais escuro.
  - NES: 3 cores + preto, cabeça grande, contorno preto.

Saída: assets/CharacterIdeas/concepts/variations/

Uso:
    app/venv/bin/python tools/build_style_variations.py
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_character_concepts import (  # noqa: E402
    CANVAS, DMG, NES, NOIR, build, internal_holes,
)

OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "CharacterIdeas" / "concepts" / "variations"

GB_PAL = {"D": "#0f380f", "d": "#306230", "l": "#8bac0f", "L": "#c4d64a"}
GB_POCKET_PAL = {"D": "#2b2b26", "d": "#6b6b5e", "l": "#a5a596", "L": "#d6d6c8"}

# ===========================================================================
# ESTILO 02 — NOIR REALISTA
# ===========================================================================
NOIR_MARA = dict(
    key="02b_noir_mara",
    title="02b. Mara",
    style="Noir | destaque: oculos neon ciano",
    desc="Cabelo chanel, sobretudo justo de gola alta e oculos-HUD ciano. Fria e precisa.",
    pal={
        "h": "#1f1a1e", "s": "#d8bfae", "V": "#38e8d8", "C": "#4a4f57",
        "c": "#6d737d", "B": "#2a2c30", "P": "#2f3036", "N": "#151517",
    },
    rows=[
        ".....hhhh.....",
        "....hhhhhh....",
        "....hhhsss....",
        "....hhVVVV....",
        "....hhssss....",
        ".....hsss.....",
        ".....CCCC.....",
        "....CCCcCC....",
        "....CCCcCCC...",
        "....CCCcCCC...",
        "....CCCcCCC...",
        "....CCCcCCs...",
        "....BBBBBB....",
        "....CCCcCC....",
        "....CCCcCCC...",
        "...CCCCcCCCC..",
        "...CCCCcCCCC..",
        "..CCCCCcCCCCC.",
        ".....PP..PP...",
        ".....PP..PP...",
        ".....PP..PP...",
        ".....PP..PP...",
        ".....PP..PP...",
        ".....PP..PP...",
        ".....NNN.NNN..",
    ],
    outline=("selout", None),
)

NOIR_OKABE = dict(
    key="02c_noir_okabe",
    title="02c. Okabe",
    style="Noir | destaque: lanterna amarela",
    desc="Veterano de barba grisalha, capa de chuva com capuz, lanterna de cabeca e corda enrolada nas costas.",
    pal={
        "K": "#3a3f3a", "k": "#5a6152", "q": "#7a826e", "s": "#c9a990",
        "E": "#1a1a1a", "W": "#9a9a9a", "Y": "#ffd23f", "R": "#7a6548",
        "r": "#a8926a", "P": "#33332f", "N": "#1b1b1a",
    },
    rows=[
        "......KKKK......",
        ".....KKKKKK.....",
        "....KKKKKKKY....",
        "....KKKkssss....",
        "....KKKksEss....",
        "....KKKksssss...",
        "....KKKkWWWW....",
        "...RRRKkWWW.....",
        "..RrrrRkkkkk....",
        "..RrRrRkkqkkk...",
        "..RrrrRkkqkkks..",
        "...RRRkkkqkkkk..",
        ".....kkkkqkkkkk.",
        "....kkkkkqkkkkk.",
        "....qqqqqqqqqqq.",
        "......PP..PP....",
        "......PP..PP....",
        "......PP..PP....",
        "......PP..PP....",
        "......PP..PP....",
        "......NNN.NNN...",
    ],
    outline=("selout", None),
)

NOIR_INES = dict(
    key="02d_noir_ines",
    title="02d. Ines",
    style="Noir | destaque: arnes laranja",
    desc="Alpinista de macacao tecnico, rabo de cavalo, arnes laranja e lancador de gancho apontado para frente.",
    pal={
        "h": "#3b2a22", "H": "#5c4334", "s": "#c99a7c", "E": "#1c1412",
        "J": "#3f4a52", "j": "#5d6a73", "O": "#e0782a", "G": "#6a6e75",
        "g": "#9aa0a8", "N": "#1a1c1f",
    },
    rows=[
        "......hhhh......",
        ".....hHHhhh.....",
        "..hhhhhhhss.....",
        ".hh..hhhsEs.....",
        ".h...hhssss.....",
        "......hsss......",
        "......JJJJ......",
        ".....JjjjJJ.....",
        ".....JOjjOJsGGGg",
        ".....JjOOjJJGG..",
        ".....JjjOjJ.....",
        ".....JjjjjJ.....",
        ".....OOOOOO.....",
        ".....JOjjOJ.....",
        ".....JJ..JJ.....",
        ".....JJ..JJ.....",
        ".....JJ..JJ.....",
        ".....JJ..JJ.....",
        ".....JJ..JJ.....",
        ".....JJ..JJ.....",
        ".....NNN.NNN....",
    ],
    outline=("selout", None),
)

# ===========================================================================
# ESTILO 03 — GAME BOY DMG
# ===========================================================================
DMG_BRICK = dict(
    key="03b_dmg_brick",
    title="03b. Brick",
    style="DMG | capacete com lanterna + balde",
    desc="Operario de capacete com lanterna acesa, macacao claro e balde de agua na mao.",
    pal=GB_PAL,
    rows=[
        ".....dddddd.....",
        "....dLLddddL....",
        "...dddddddddL...",
        ".....LLLLLL.....",
        ".....LDLLDL.....",
        ".....LLLLLL.....",
        "......LDDL......",
        "....dddddddd....",
        "...ddlddddlddL..",
        "...ddllllllddD.D",
        "...Lllllllll.dLd",
        "....llllllll.dLd",
        "....lll..lll.ddd",
        "....ddd..ddd....",
        "...DDDD..DDDD...",
    ],
    outline=("solid", "#0f380f"),
)

DMG_JUNO = dict(
    key="03c_dmg_juno",
    title="03c. Juno",
    style="DMG | bone virado + cachecol",
    desc="Jovem de bone para tras, cachecol longo ao vento e corda atravessada no peito.",
    pal=GB_PAL,
    rows=[
        ".....ddddd......",
        "..ddddddddd.....",
        ".....dLLLLL.....",
        ".....LLLDLD.....",
        ".....LLLLLL.....",
        "......LLLL......",
        ".DDDDDDDDDD.....",
        "DD...dlllld.....",
        "D...dlDDDldL....",
        "....dlllDDd.....",
        "...LdllllDd.....",
        "....dddddd......",
        "....dd..dd......",
        "....dd..dd......",
        "...DDD..DDD.....",
    ],
    outline=("solid", "#0f380f"),
)

DMG_UNIT = dict(
    key="03d_pocket_unit",
    title="03d. Unit-7 (Pocket)",
    style="Game Boy Pocket | 4 cinzas | androide",
    desc="Androide de limpeza com antena, visor de dois olhos e rodo. Mesma regra de 4 tons, paleta do GB Pocket.",
    pal=GB_POCKET_PAL,
    rows=[
        ".......D........",
        ".......d........",
        ".....ddddd......",
        "....dlllllld....",
        "....dlDDDDld....",
        "....dlLDLDld....",
        "....dlllllld....",
        ".....dddddd..DDD",
        "...ddlllllldd.d.",
        "..ddllLDDLlldLd.",
        "..dd.llDlll.....",
        "..LL.dddddd.....",
        ".....dd..dd.....",
        ".....dd..dd.....",
        "....ddd..ddd....",
        "....DDD..DDD....",
    ],
    outline=("solid", "#2b2b26"),
)

# ===========================================================================
# ESTILO 04 — NES 8-BIT
# ===========================================================================
NES_KAI = dict(
    key="04b_nes_kai",
    title="04b. Kai",
    style="NES | vermelho/laranja | ninja",
    desc="Ninja de capuz vermelho com faixa laranja esvoacante e garra de gancho na mao.",
    pal={"r": "#d82800", "o": "#fc9838", "s": "#fcbcb0", "K": "#000000"},
    rows=[
        ".....rrrrr......",
        "....rrrrrrr.....",
        "ooooooooooo.....",
        ".oo.rrsKssKs....",
        "....rrssssss....",
        "....rrrrrrr.....",
        ".....rrrrr......",
        "...rrrrrrrrr....",
        "..rrorrrrorrs...",
        "..rr.ooooo.rKK..",
        "..s..rrrrr..K.K.",
        ".....rr.rr......",
        ".....rr.rr......",
        "....rrr.rrr.....",
        "...oooo.oooo....",
    ],
    outline=("solid", "#000000"),
)

NES_SIR = dict(
    key="04c_nes_sir_mop",
    title="04c. Sir Mop",
    style="NES | verdes | cavaleiro-faxineiro",
    desc="Capacete de balde com fenda, armadura verde e esfregao erguido como lanca.",
    pal={"g": "#00a800", "G": "#b8f818", "s": "#fcbcb0", "K": "#000000"},
    rows=[
        "....gggggg......",
        "....gGgggg......",
        "...gggggggg.....",
        "....gKKKKg......",
        "....gssssg......",
        ".....gggg.......",
        "...gggggggg..G..",
        "..gGggggggggsG..",
        "..gg.gGGGg...G..",
        "..gg.ggggg...G..",
        "..ss.ggggg...G..",
        ".....gg.gg..GGG.",
        ".....gg.gg..GGG.",
        "....ggg.ggg.G.G.",
        "...GGGG.GGGG....",
    ],
    outline=("solid", "#000000"),
)

NES_LUMA = dict(
    key="04d_nes_luma",
    title="04d. Luma",
    style="NES | roxo/rosa | aventureira",
    desc="Bone com oculos de protecao, jaqueta roxa e corda rosa enrolada no ombro.",
    pal={"p": "#6844fc", "P": "#f878f8", "s": "#fcbcb0", "K": "#000000"},
    rows=[
        ".....ppppp......",
        "....pppppppp....",
        "...PPpPPpPP.....",
        "..ppssssss......",
        "..ppssKsKs......",
        "...pssssss......",
        "....sssss.......",
        "..PPPppppp......",
        ".PPpPPpppps.....",
        ".PpppPppppp.....",
        ".PPpPPpppp......",
        "..PPPspppp......",
        "....pp.pp.......",
        "....pp.pp.......",
        "...PPP.PPP......",
    ],
    outline=("solid", "#000000"),
)

GROUPS = [
    ("ESTILO 02 - NOIR REALISTA", [NOIR, NOIR_MARA, NOIR_OKABE, NOIR_INES]),
    ("ESTILO 03 - GAME BOY", [DMG, DMG_BRICK, DMG_JUNO, DMG_UNIT]),
    ("ESTILO 04 - NES 8-BIT", [NES, NES_KAI, NES_SIR, NES_LUMA]),
]


def make_showcase(groups) -> Image.Image:
    card_w, card_h, header = 270, 340, 70
    W = 4 * card_w + 30
    H = header + len(groups) * (card_h + 34) + 10
    sheet = Image.new("RGBA", (W, H), (16, 16, 24, 255))
    d = ImageDraw.Draw(sheet)
    d.rectangle([(0, 0), (W, 56)], fill=(10, 10, 16, 255))
    d.line([(0, 56), (W, 56)], fill=(0, 229, 255, 255), width=2)
    d.text((20, 12), "APEX GRAPPLER - VARIACOES DOS ESTILOS 02, 03 E 04", fill=(255, 255, 255, 255))
    d.text((20, 32), "Primeira coluna = conceito original. Demais = novas variacoes. Sprite nativo 32x32, ampliado 5x.", fill=(170, 180, 200, 255))

    y = header
    for label, items in groups:
        d.text((18, y), label, fill=(255, 140, 0, 255))
        y += 18
        for i, (c, img) in enumerate(items):
            cx = 15 + i * card_w
            d.rectangle([(cx, y), (cx + card_w - 12, y + card_h - 12)], fill=(26, 28, 40, 255),
                        outline=(255, 140, 0, 255) if i == 0 else (48, 52, 72, 255))
            bx, by = cx + (card_w - 12 - 160) // 2, y + 10
            d.rectangle([(bx, by), (bx + 159, by + 159)], fill=(30, 26, 52, 255))
            big = img.resize((160, 160), Image.Resampling.NEAREST)
            sheet.paste(big, (bx, by), big)
            d.text((cx + 10, y + 178), c["title"] + ("  (original)" if i == 0 else ""), fill=(255, 220, 40, 255))
            d.text((cx + 10, y + 194), c["style"], fill=(0, 229, 255, 255))
            words, lines, cur = c["desc"].split(), [], ""
            for w in words:
                if len(cur) + len(w) + 1 > 38:
                    lines.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            lines.append(cur)
            for j, line in enumerate(lines[:3]):
                d.text((cx + 10, y + 214 + j * 14), line, fill=(195, 200, 215, 255))
            d.text((cx + 10, y + card_h - 36), "1x:", fill=(120, 130, 150, 255))
            sheet.paste(img, (cx + 34, y + card_h - 48), img)
            x2 = img.resize((64, 64), Image.Resampling.NEAREST)
            d.text((cx + 84, y + card_h - 36), "2x:", fill=(120, 130, 150, 255))
            sheet.paste(x2, (cx + 108, y + card_h - 80), x2)
        y += card_h + 16
    return sheet


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.png"):
        old.unlink()

    rendered_groups = []
    for label, concepts in GROUPS:
        items = []
        for c in concepts:
            img = build(c)
            holes = internal_holes(img)
            if holes:
                raise RuntimeError(f"{c['key']}: pixels vazios no corpo: {holes}")
            if c not in (NOIR, DMG, NES):
                img.save(OUT_DIR / f"concept_{c['key']}.png")
                img.resize((256, 256), Image.Resampling.NEAREST).save(OUT_DIR / f"preview_8x_{c['key']}.png")
                print(f"[OK] {c['title']}")
            items.append((c, img))
        rendered_groups.append((label, items))

    strip = Image.new("RGBA", (CANVAS * 9, CANVAS), (0, 0, 0, 0))
    new_imgs = [img for _, items in rendered_groups for c, img in items[1:]]
    for i, img in enumerate(new_imgs):
        strip.paste(img, (i * CANVAS, 0))
    strip.save(OUT_DIR / "variations_strip_288x32.png")
    make_showcase(rendered_groups).save(OUT_DIR / "variations_showcase.png")
    print("Showcase das variacoes gerado.")


if __name__ == "__main__":
    main()
