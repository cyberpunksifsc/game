#!/usr/bin/env python3
"""
Adaptação do sprite 'Sir Mop' (04c) para o motor Pyxel (32x32 nativo).

Ajustes realizados:
1. Paleta convertida 1:1 para os RGBs exatos da paleta padrão de 16 cores do Pyxel:
   - Cor 0 (transparente): (0, 0, 0, 0) -> colkey=0 no pyxel.blt()
   - Cor 1 (#2B2B45): Contorno externo de 1px e fenda do elmo (substitui #000000 para não sumir com colkey=0)
   - Cor 3 (#008751): Verde-escuro (sombra da armadura e elmo)
   - Cor 11 (#00E436): Verde-vivo (armadura principal)
   - Cor 10 (#FFEC27): Amarelo (cerdas do esfregão, botas e brilho da armadura)
   - Cor 9 (#FFA300): Laranja (cabo do esfregão / detalhes)
   - Cor 14 (#FFCCAA): Pêssego (rosto e mãos)
   - Cor 6 (#C2C3C7) e Cor 5 (#5F574F): Argola metálica do arnês em (8, 10)
2. Reposicionamento no canvas 32x32 (Y=5..23, X=7..24):
   - Engate do cabo exatamente em (8, 10)
   - Corpo centralizado dentro da hitbox (X=6..22, Y=6..26) e do escudo (centro 15,16, raio 13).
"""

from pathlib import Path
from PIL import Image, ImageDraw

CANVAS = 32
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "CharacterIdeas" / "sir_mop"

# Paleta oficial de 16 cores do Pyxel (RGBA)
PYXEL_PALETTE = {
    ".": (0, 0, 0, 0),          # 0: Transparente (colkey=0)
    "1": (43, 43, 69, 255),     # 1: #2B2B45 Azul-marinho escuro (contorno e fenda)
    "3": (0, 135, 81, 255),     # 3: #008751 Verde-escuro (sombra da armadura)
    "5": (95, 87, 79, 255),     # 5: #5F574F Cinza-escuro (base do arnês)
    "6": (194, 195, 199, 255),  # 6: #C2C3C7 Cinza-claro (argola metálica do mosquetão)
    "7": (255, 241, 232, 255),  # 7: #FFF1E8 Branco (brilho especular)
    "9": (255, 163, 0, 255),    # 9: #FFA300 Laranja (haste do esfregão / detalhe)
    "A": (255, 236, 39, 255),   # 10: #FFEC27 Amarelo (cerdas do esfregão / botas / brasão)
    "B": (0, 228, 54, 255),     # 11: #00E436 Verde-claro (armadura principal)
    "E": (255, 204, 170, 255),  # 14: #FFCCAA Pêssego (rosto e mãos)
}

# Matriz 32x32 do Sir Mop adaptado (sem o contorno externo de 1px, que é gerado automaticamente com a cor '1')
# Nota: (8, 10) é a argola metálica '6' do arnês nas costas!
SIR_MOP_INNER_32 = [
    "................................",  # 00
    "................................",  # 01
    "................................",  # 02
    "................................",  # 03
    "................................",  # 04
    "................................",  # 05
    "................................",  # 06 (contorno superior ficará aqui)
    "...........BBBBBB...............",  # 07 Topo do elmo-balde
    "...........BAABBB...............",  # 08 Brilho no elmo
    "..........3BBBBBBB..............",  # 09 Aba do elmo
    "........65.31111B...............",  # 10 (8,10) = '6' Mosquetão no topo da mochila + Fenda do visor!
    "........5553EEEEB...............",  # 11 Mochila/arnês conectada ao pescoço + Rosto
    "........553BBBBBBB...9..........",  # 12 Mochila acoplada ao ombro + Topo do cabo
    ".........3ABBBBBBBBE99..........",  # 13 Ombreira iluminada + Mão segurando o cabo
    ".........3B.BAAA3...9...........",  # 14 Peitoral com brasão dourado + Cabo
    ".........3B.3BBBB...9...........",  # 15 Armadura abdominal + Cabo
    ".........EE.33333...9...........",  # 16 Mão esquerda + Cinto + Cabo
    "............3B.3B..AAA..........",  # 17 Coxas + Base do esfregão
    "............3B.3B..AAA..........",  # 18 Joelhos + Cerdas do esfregão
    "...........3BB.3BB.A3A..........",  # 19 Caneleiras + Pontas do esfregão
    "..........AAAA.AAAA.............",  # 20 Botas amarelas de cavaleiro
    "..........99AA.99AA.............",  # 21 Solado reforçado das botas
    "................................",  # 22 (contorno inferior ficará aqui)
    "................................",  # 23
    "................................",  # 24
    "................................",  # 25
    "................................",  # 26
    "................................",  # 27
    "................................",  # 28
    "................................",  # 29
    "................................",  # 30
    "................................",  # 31
]


def render_sir_mop(inner_rows: list[str]) -> Image.Image:
    assert len(inner_rows) == CANVAS, f"Esperado {CANVAS} linhas, recebido {len(inner_rows)}"
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    for y, row in enumerate(inner_rows):
        assert len(row) == CANVAS, f"Linha {y} tem {len(row)} colunas, esperado {CANVAS}"
        for x, ch in enumerate(row):
            if ch != ".":
                img.putpixel((x, y), PYXEL_PALETTE[ch])

    # Aplica contorno externo de 1px usando Cor 1 do Pyxel (#2B2B45)
    out = img.copy()
    outline_col = PYXEL_PALETTE["1"]
    for y in range(CANVAS):
        for x in range(CANVAS):
            if img.getpixel((x, y))[3] > 0:
                continue
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < CANVAS and 0 <= ny < CANVAS and img.getpixel((nx, ny))[3] > 0:
                    out.putpixel((x, y), outline_col)
                    break

    # Preenche eventuais frestas internas de 1px (entre braço/corpo ou arnês/corpo) com Cor 1
    seen = set()
    stack = [(x, y) for x in range(CANVAS) for y in (0, CANVAS - 1)]
    stack += [(x, y) for y in range(CANVAS) for x in (0, CANVAS - 1)]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or not (0 <= x < CANVAS and 0 <= y < CANVAS) or out.getpixel((x, y))[3] > 0:
            continue
        seen.add((x, y))
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    for y in range(CANVAS):
        for x in range(CANVAS):
            if out.getpixel((x, y))[3] == 0 and (x, y) not in seen:
                out.putpixel((x, y), outline_col)

    return out


def make_comparison_sheet(original_img: Image.Image, adapted_img: Image.Image) -> Image.Image:
    W, H = 920, 400
    sheet = Image.new("RGBA", (W, H), (16, 16, 24, 255))
    d = ImageDraw.Draw(sheet)

    d.rectangle([(0, 0), (W, 56)], fill=(10, 10, 16, 255))
    d.line([(0, 56), (W, 56)], fill=(0, 228, 54, 255), width=2)
    d.text((20, 12), "SIR MOP - ADAPTACAO TECNICA PARA O MOTOR PYXEL (32x32)", fill=(255, 255, 255, 255))
    d.text((20, 32), "Comparativo: Conceito NES Original vs. Versao Nativa Pyxel + Alinhamento de Sistemas", fill=(170, 180, 200, 255))

    scale = 6  # 32 * 6 = 192x192
    box_size = 32 * scale

    panels = [
        ("1. CONCEITO NES ORIGINAL", "Contorno #000000 (some no colkey=0) | Base Y=30", original_img, False, False),
        ("2. SIMULACAO DO BUG NO PYXEL", "O que acontece ao desenhar o original com colkey=0", original_img, True, False),
        ("3. SIR MOP ADAPTADO (PYXEL)", "Paleta nativa Pyxel | Contorno Cor 1 | Cabo em (8,10)", adapted_img, False, True),
    ]

    for idx, (title, subtitle, src_img, simulate_colkey_bug, show_overlays) in enumerate(panels):
        px = 20 + idx * 300
        py = 72
        d.rectangle([(px, py), (px + 280, py + 310)], fill=(26, 28, 40, 255), outline=(48, 52, 72, 255))
        bx = px + (280 - box_size) // 2
        by = py + 12

        # Fundo noturno do jogo
        d.rectangle([(bx, by), (bx + box_size - 1, by + box_size - 1)], fill=(30, 26, 52, 255), outline=(60, 65, 90, 255))

        img_to_draw = src_img.copy()
        if simulate_colkey_bug:
            # Remove pixels #000000 como o pyxel.blt(..., colkey=0) faz
            for y in range(32):
                for x in range(32):
                    r, g, b, a = img_to_draw.getpixel((x, y))
                    if a > 0 and (r, g, b) == (0, 0, 0):
                        img_to_draw.putpixel((x, y), (0, 0, 0, 0))

        big = img_to_draw.resize((box_size, box_size), Image.Resampling.NEAREST)
        sheet.paste(big, (bx, by), big)

        if show_overlays:
            # 1. Hitbox de balas: (6, 6) com w=16, h=20 -> X=6..22, Y=6..26
            hx0, hy0 = bx + 6 * scale, by + 6 * scale
            hx1, hy1 = bx + 22 * scale, by + 26 * scale
            d.rectangle([(hx0, hy0), (hx1, hy1)], outline=(255, 0, 77, 180), width=1)

            # 2. Bolha de Escudo Reativo: centro (15, 16), raio 13
            scx, scy = bx + 15 * scale + scale // 2, by + 16 * scale + scale // 2
            sr = 13 * scale
            d.ellipse([(scx - sr, scy - sr), (scx + sr, scy + sr)], outline=(41, 173, 255, 180), width=1)

            # 3. Cabo e ponto do arnês em (8, 10)
            ax, ay = bx + 8 * scale + scale // 2, by + 10 * scale + scale // 2
            d.line([(bx + 18 * scale, by + 2 * scale), (ax, ay)], fill=(131, 118, 156, 255), width=2)
            d.ellipse([(ax - 4, ay - 4), (ax + 4, ay + 4)], fill=(0, 228, 54, 255), outline=(255, 255, 255, 255))

        d.text((px + 10, py + 214), title, fill=(255, 220, 40, 255))
        d.text((px + 10, py + 232), subtitle, fill=(0, 229, 255, 255))

        # Escala 1x e 2x
        d.text((px + 10, py + 276), "1x:", fill=(140, 150, 170, 255))
        sheet.paste(img_to_draw, (px + 34, py + 264), img_to_draw)
        x2 = img_to_draw.resize((64, 64), Image.Resampling.NEAREST)
        d.text((px + 82, py + 276), "2x:", fill=(140, 150, 170, 255))
        sheet.paste(x2, (px + 106, py + 240), x2)

    if True:
        # Legenda dos overlays no painel 3
        px3 = 20 + 2 * 300
        d.text((px3 + 178, 72 + 254), "Legenda:", fill=(200, 205, 220, 255))
        d.text((px3 + 178, 72 + 268), "- Ponto verde: Cabo (8,10)", fill=(0, 228, 54, 255))
        d.text((px3 + 178, 72 + 281), "- Caixa verm.: Hitbox", fill=(255, 0, 77, 255))
        d.text((px3 + 178, 72 + 294), "- Circ. azul: Escudo", fill=(41, 173, 255, 255))

    return sheet


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    adapted = render_sir_mop(SIR_MOP_INNER_32)

    # Verificações técnicas estritas
    allowed_rgbs = set(PYXEL_PALETTE.values())
    for y in range(CANVAS):
        for x in range(CANVAS):
            px = adapted.getpixel((x, y))
            assert px in allowed_rgbs, f"Cor fora da paleta Pyxel em ({x},{y}): {px}"
            assert px != (0, 0, 0, 255), f"Pixel #000000 proibido em ({x},{y}) (conflita com colkey=0)"

    assert adapted.getpixel((8, 10)) == PYXEL_PALETTE["6"], (
        f"Esperado argola do arnês na posição (8, 10), encontrado: {adapted.getpixel((8, 10))}"
    )

    adapted.save(OUT_DIR / "sir_mop_idle_pyxel_32x32.png")
    adapted.resize((256, 256), Image.Resampling.NEAREST).save(OUT_DIR / "sir_mop_idle_pyxel_8x.png")

    orig_path = Path(__file__).resolve().parent.parent / "assets" / "CharacterIdeas" / "concepts" / "variations" / "concept_04c_nes_sir_mop.png"
    orig_img = Image.open(orig_path)
    sheet = make_comparison_sheet(orig_img, adapted)
    sheet.save(OUT_DIR / "sir_mop_pyxel_adaptation_comparison.png")
    print("[OK] Sir Mop adaptado e validado para o Pyxel com sucesso!")


if __name__ == "__main__":
    main()
