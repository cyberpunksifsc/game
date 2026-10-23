#!/usr/bin/env python3
"""
Gerador das Spritesheets Completas de Animação do 'Sir Mop' para o Pyxel.

Gera:
1. Main Sheet (128x160 px = 4 colunas x 5 linhas de 32x32):
   - Linha 0: IDLE (4 frames — respiração de cavaleiro, brilho no elmo e oscilação do esfregão)
   - Linha 1: CLIMB_UP (4 frames — escalando o cabo com passadas alternadas de joelho e puxada de braço)
   - Linha 2: CLIMB_DOWN (4 frames — rapel controlado deslizando pelo cabo, cerdas do esfregão subindo com o vento)
   - Linha 3: SWING_LEFT (4 frames — impulso pendular para a esquerda, pernas projetadas à esquerda)
   - Linha 4: SWING_RIGHT (4 frames — impulso pendular para a direita, esfregão em riste como lança de justa)
2. Rope Swing / Airborne Sheet (192x32 px = 6 colunas x 1 linha de 32x32):
   - Linha única (carregada em Y=160 no banco 2): Salto acrobático no ar entre âncoras (6 frames).
3. Painel de Visualização (Showcase) e GIFs animados de todas as ações.
"""

from pathlib import Path
from PIL import Image, ImageDraw

from adapt_sir_mop_pyxel import (
    CANVAS,
    PYXEL_PALETTE,
    SIR_MOP_INNER_32,
    render_sir_mop,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
SIR_MOP_DIR = ROOT_DIR / "assets" / "CharacterIdeas" / "sir_mop"
ASSETS_CHAR_DIR = ROOT_DIR / "assets" / "CharacterIdeas"
APP_ASSETS_CHAR_DIR = ROOT_DIR / "app" / "assets" / "CharacterIdeas"


# ---------------------------------------------------------------------------
# Utilitários de transformação de partes do corpo em 32x32
# ---------------------------------------------------------------------------

def empty_grid() -> list[list[str]]:
    return [["." for _ in range(CANVAS)] for _ in range(CANVAS)]


def grid_to_rows(g: list[list[str]]) -> list[str]:
    return ["".join(r) for r in g]


def blit_region(
    src_rows: list[str],
    dst: list[list[str]],
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    dx: int = 0,
    dy: int = 0,
):
    """Copia a região retangular [x0..x1, y0..y1] de src_rows para dst com deslocamento (dx, dy)."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            ch = src_rows[y][x]
            if ch != ".":
                nx, ny = x + dx, y + dy
                if 0 <= nx < CANVAS and 0 <= ny < CANVAS:
                    dst[ny][nx] = ch


def set_pixels(dst: list[list[str]], coords: list[tuple[int, int, str]]):
    for x, y, ch in coords:
        if 0 <= x < CANVAS and 0 <= y < CANVAS:
            if ch == ".":
                dst[y][x] = "."
            else:
                dst[y][x] = ch


def compose_pose(
    head_dx: int = 0,
    head_dy: int = 0,
    torso_dx: int = 0,
    torso_dy: int = 0,
    left_arm_dy: int = 0,
    left_leg_dx: int = 0,
    left_leg_dy: int = 0,
    right_leg_dx: int = 0,
    right_leg_dy: int = 0,
    mop_dx: int = 0,
    mop_dy: int = 0,
    keep_harness_fixed: bool = True,
    bristles_flare_up: bool = False,
    visor_glint: bool = False,
    lance_forward: bool = False,
) -> list[str]:
    """Compõe um frame 32x32 do Sir Mop articulando cabeça, tronco, braços, pernas e esfregão."""
    g = empty_grid()
    base = SIR_MOP_INNER_32

    # 1. Pernas (Y=17..21): perna esquerda X=10..13, perna direita X=15..18
    blit_region(base, g, 10, 17, 13, 21, dx=left_leg_dx, dy=left_leg_dy)
    blit_region(base, g, 15, 17, 18, 21, dx=right_leg_dx, dy=right_leg_dy)

    # Preenche conexão da coxa se a perna desceu 1px
    if left_leg_dy > 0:
        set_pixels(g, [(12 + left_leg_dx, 17, "3"), (13 + left_leg_dx, 17, "B")])
    if right_leg_dy > 0:
        set_pixels(g, [(15 + right_leg_dx, 17, "3"), (16 + right_leg_dx, 17, "B")])

    # 2. Tronco central (X=11..17, Y=12..16)
    blit_region(base, g, 11, 12, 17, 16, dx=torso_dx, dy=torso_dy)

    # 3. Braço esquerdo (X=9..10, Y=13..16)
    blit_region(base, g, 9, 13, 10, 16, dx=torso_dx, dy=torso_dy + left_arm_dy)

    # 4. Cabeça / Elmo-balde (X=10..17, Y=7..11)
    blit_region(base, g, 10, 7, 17, 11, dx=head_dx, dy=head_dy)
    if visor_glint:
        # Brilho dourado passando na viseira/elmo
        set_pixels(g, [(14 + head_dx, 8 + head_dy, "A"), (15 + head_dx, 8 + head_dy, "7")])

    # 5. Mochila e mosquetão do arnês (X=8..10, Y=10..12)
    # Mantém (8, 10) fixo quando ancorado para o cabo nunca desgrudar!
    h_dx = 0 if keep_harness_fixed else torso_dx
    h_dy = 0 if keep_harness_fixed else torso_dy
    blit_region(base, g, 8, 10, 10, 12, dx=h_dx, dy=h_dy)
    # Garante ponte sólida entre mochila e tronco mesmo quando o tronco inclina
    set_pixels(g, [(10 + h_dx, 11 + h_dy, "5"), (10 + h_dx, 12 + h_dy, "3")])

    # 6. Braço direito + Esfregão (X=18..22, Y=12..19)
    if lance_forward:
        # Esfregão inclinado à frente como lança de justa (SWING_RIGHT)
        mx = 18 + mop_dx
        my = 13 + mop_dy
        set_pixels(
            g,
            [
                (mx, my, "E"),
                (mx + 1, my, "9"),
                (mx + 2, my, "9"),
                (mx + 3, my, "9"),
                (mx + 4, my, "9"),
                (mx + 5, my - 1, "A"),
                (mx + 5, my, "A"),
                (mx + 5, my + 1, "A"),
                (mx + 6, my - 1, "A"),
                (mx + 6, my, "3"),
                (mx + 6, my + 1, "A"),
            ],
        )
    else:
        blit_region(base, g, 18, 12, 22, 19, dx=mop_dx, dy=mop_dy)
        if bristles_flare_up:
            # Cerdas do esfregão abertas pela corrente de ar (CLIMB_DOWN / AIRBORNE)
            bx = 19 + mop_dx
            by = 17 + mop_dy
            set_pixels(
                g,
                [
                    (bx, by - 1, "A"),
                    (bx + 2, by - 1, "A"),
                    (bx, by + 2, "A"),
                    (bx + 1, by + 2, "3"),
                    (bx + 2, by + 2, "A"),
                ],
            )

    return grid_to_rows(g)


# ---------------------------------------------------------------------------
# Definição das 5 linhas da Spritesheet Principal (4 frames cada)
# ---------------------------------------------------------------------------

def build_idle_frames() -> list[Image.Image]:
    """Linha 0: IDLE (4 frames) — respiração sutil, brilho no elmo e leve pulso do esfregão."""
    poses = [
        compose_pose(),  # Frame 0: Neutro
        compose_pose(head_dy=-1, mop_dy=-1, visor_glint=True),  # Frame 1: Inspira / ergue elmo e esfregão
        compose_pose(visor_glint=True),  # Frame 2: Neutro com reflexo no elmo
        compose_pose(head_dy=1, torso_dy=1, left_arm_dy=0, mop_dy=0),  # Frame 3: Expira / assenta na corda
    ]
    return [render_sir_mop(p) for p in poses]


def build_climb_up_frames() -> list[Image.Image]:
    """Linha 1: CLIMB_UP (4 frames) — escalada vigorosa alternando joelhos e braços."""
    poses = [
        # Frame 0: Joelho direito alto, braço esquerdo puxando no alto, esfregão erguido
        compose_pose(head_dy=-1, left_arm_dy=-2, left_leg_dy=1, right_leg_dy=-2, mop_dy=-2),
        # Frame 1: Passagem subindo
        compose_pose(head_dy=0, left_arm_dy=-1, left_leg_dy=0, right_leg_dy=-1, mop_dy=-1),
        # Frame 2: Joelho esquerdo alto, perna direita esticada, esfregão firme
        compose_pose(head_dy=-1, left_arm_dy=1, left_leg_dy=-2, right_leg_dy=1, mop_dy=0),
        # Frame 3: Passagem completando ciclo
        compose_pose(head_dy=0, left_arm_dy=0, left_leg_dy=-1, right_leg_dy=0, mop_dy=-1),
    ]
    return [render_sir_mop(p) for p in poses]


def build_climb_down_frames() -> list[Image.Image]:
    """Linha 2: CLIMB_DOWN (4 frames) — descida de rapel com cerdas esvoaçando para cima."""
    poses = [
        compose_pose(head_dy=1, left_leg_dy=-1, right_leg_dy=0, mop_dy=-1, bristles_flare_up=True),
        compose_pose(head_dy=1, torso_dy=1, left_leg_dy=0, right_leg_dy=-1, mop_dy=-2, bristles_flare_up=True),
        compose_pose(head_dy=1, left_leg_dy=-1, right_leg_dy=-1, mop_dy=-1, bristles_flare_up=True),
        compose_pose(head_dy=0, left_leg_dy=0, right_leg_dy=0, mop_dy=-1, bristles_flare_up=True),
    ]
    return [render_sir_mop(p) for p in poses]


def build_swing_left_frames() -> list[Image.Image]:
    """Linha 3: SWING_LEFT (4 frames) — impulso pendular para a esquerda."""
    poses = [
        compose_pose(head_dx=-1, left_leg_dx=-1, right_leg_dx=-1, mop_dx=0),
        compose_pose(head_dx=-1, torso_dx=-1, left_leg_dx=-2, left_leg_dy=-1, right_leg_dx=-1, mop_dx=0, mop_dy=-1),
        compose_pose(head_dx=-1, torso_dx=-1, left_leg_dx=-2, right_leg_dx=-2, right_leg_dy=-1, mop_dx=0),
        compose_pose(head_dx=0, left_leg_dx=-1, right_leg_dx=-1, mop_dx=0),
    ]
    return [render_sir_mop(p) for p in poses]


def build_swing_right_frames() -> list[Image.Image]:
    """Linha 4: SWING_RIGHT (4 frames) — impulso pendular para a direita com esfregão em riste!"""
    poses = [
        compose_pose(head_dx=1, left_leg_dx=1, right_leg_dx=1, mop_dx=1, mop_dy=-1),
        compose_pose(head_dx=1, torso_dx=1, left_leg_dx=1, right_leg_dx=2, right_leg_dy=-1, mop_dx=1, mop_dy=-1, lance_forward=True),
        compose_pose(head_dx=1, torso_dx=1, left_leg_dx=2, left_leg_dy=-1, right_leg_dx=2, mop_dx=1, lance_forward=True),
        compose_pose(head_dx=1, left_leg_dx=1, right_leg_dx=1, mop_dx=1),
    ]
    return [render_sir_mop(p) for p in poses]


def build_airborne_frames() -> list[Image.Image]:
    """Folha de Salto / Voo Livre (6 frames, 192x32) — salto acrobático entre âncoras."""
    poses = [
        # Frame 0: Impulso de decolagem
        compose_pose(head_dy=-1, torso_dy=-1, left_leg_dy=-1, right_leg_dy=-2, mop_dy=-2, keep_harness_fixed=False),
        # Frame 1: Subida no ar com lança-esfregão em riste
        compose_pose(head_dx=1, head_dy=-2, torso_dy=-2, left_leg_dx=-1, left_leg_dy=-2, right_leg_dx=1, right_leg_dy=-3, mop_dx=1, mop_dy=-2, keep_harness_fixed=False, lance_forward=True),
        # Frame 2: Ápice do salto (pose heroica)
        compose_pose(head_dx=1, head_dy=-2, torso_dy=-2, left_leg_dx=-1, left_leg_dy=-3, right_leg_dx=1, right_leg_dy=-2, mop_dx=1, mop_dy=-3, keep_harness_fixed=False, lance_forward=True, visor_glint=True),
        # Frame 3: Início da descida aérea, esfregão erguido
        compose_pose(head_dx=1, head_dy=-1, torso_dy=-1, left_leg_dy=-2, right_leg_dx=1, right_leg_dy=-1, mop_dx=1, mop_dy=-2, keep_harness_fixed=False, bristles_flare_up=True),
        # Frame 4: Preparando reconexão (perna estendida à frente)
        compose_pose(head_dy=-1, left_leg_dx=-1, left_leg_dy=-1, right_leg_dx=1, right_leg_dy=0, mop_dy=-1, keep_harness_fixed=False, bristles_flare_up=True),
        # Frame 5: Amortecendo encaixe no link
        compose_pose(head_dy=0, left_leg_dy=0, right_leg_dy=-1, mop_dy=0, keep_harness_fixed=False),
    ]
    return [render_sir_mop(p) for p in poses]


def validate_frames(frames: list[Image.Image], label: str, check_harness: bool = True):
    allowed = set(PYXEL_PALETTE.values())
    for i, img in enumerate(frames):
        for y in range(CANVAS):
            for x in range(CANVAS):
                px = img.getpixel((x, y))
                assert px in allowed, f"[{label} F{i}] Cor inválida em ({x},{y}): {px}"
                assert px != (0, 0, 0, 255), f"[{label} F{i}] #000000 proibido em ({x},{y})"
        if check_harness:
            assert img.getpixel((8, 10)) == PYXEL_PALETTE["6"], (
                f"[{label} F{i}] Mosquetão (8,10) desalinhado: {img.getpixel((8, 10))}"
            )


def make_full_showcase(rows_dict: list[tuple[str, str, list[Image.Image]]], airborne: list[Image.Image]) -> Image.Image:
    scale = 4  # 32 * 4 = 128px por frame
    fw = CANVAS * scale
    W = 1040
    H = 80 + len(rows_dict) * 165 + 185
    sheet = Image.new("RGBA", (W, H), (16, 16, 24, 255))
    d = ImageDraw.Draw(sheet)

    d.rectangle([(0, 0), (W, 56)], fill=(10, 10, 16, 255))
    d.line([(0, 56), (W, 56)], fill=(0, 228, 54, 255), width=2)
    d.text((20, 12), "SIR MOP - SPRITESHEETS COMPLETAS DE ANIMACAO (PYXEL 32x32)", fill=(255, 255, 255, 255))
    d.text((20, 32), "5 animacoes ancoradas (4 frames cada, cabo fixo em 8,10) + 1 animacao de salto aereo (6 frames)", fill=(170, 180, 200, 255))

    y = 70
    for row_idx, (name, desc, frames) in enumerate(rows_dict):
        d.rectangle([(16, y), (W - 16, y + 152)], fill=(24, 26, 38, 255), outline=(48, 52, 72, 255))
        d.text((28, y + 12), f"LINHA {row_idx}: {name}", fill=(255, 220, 40, 255))
        d.text((28, y + 30), desc, fill=(0, 229, 255, 255))
        d.text((28, y + 54), "Escala 1x:", fill=(140, 150, 170, 255))
        for i, fr in enumerate(frames):
            sheet.paste(fr, (100 + i * 38, y + 44), fr)

        for i, fr in enumerate(frames):
            bx = 340 + i * (fw + 24)
            by = y + 12
            d.rectangle([(bx, by), (bx + fw - 1, by + fw - 1)], fill=(30, 26, 52, 255), outline=(60, 65, 90, 255))
            # Linha do cabo de aço presa em (8, 10)
            ax, ay = bx + 8 * scale + scale // 2, by + 10 * scale + scale // 2
            d.line([(bx + 16 * scale, by + 4), (ax, ay)], fill=(131, 118, 156, 255), width=2)
            big = fr.resize((fw, fw), Image.Resampling.NEAREST)
            sheet.paste(big, (bx, by), big)
            d.text((bx + 4, by + fw - 14), f"F{i}", fill=(200, 205, 220, 255))
        y += 165

    # Bloco final: AIRBORNE (6 frames)
    d.rectangle([(16, y), (W - 16, y + 170)], fill=(24, 26, 38, 255), outline=(255, 163, 0, 255))
    d.text((28, y + 10), "LINHA ESPECIAL (Y=160): STATE_AIRBORNE (6 FRAMES - SALTO ENTRE ANCORAS)", fill=(255, 220, 40, 255))
    for i, fr in enumerate(airborne):
        bx = 28 + i * (fw + 36)
        by = y + 32
        d.rectangle([(bx, by), (bx + fw - 1, by + fw - 1)], fill=(30, 26, 52, 255), outline=(60, 65, 90, 255))
        big = fr.resize((fw, fw), Image.Resampling.NEAREST)
        sheet.paste(big, (bx, by), big)
        d.text((bx + 4, by + fw - 14), f"AR F{i}", fill=(255, 220, 40, 255))

    return sheet


def save_gif(frames: list[Image.Image], path: Path, duration_ms: int = 160, scale: int = 6):
    scaled = []
    for fr in frames:
        bg = Image.new("RGBA", (CANVAS * scale, CANVAS * scale), (30, 26, 52, 255))
        big = fr.resize((CANVAS * scale, CANVAS * scale), Image.Resampling.NEAREST)
        bg.paste(big, (0, 0), big)
        scaled.append(bg.convert("RGB"))
    scaled[0].save(path, save_all=True, append_images=scaled[1:], duration=duration_ms, loop=0)


def main():
    SIR_MOP_DIR.mkdir(parents=True, exist_ok=True)

    rows_data = [
        ("IDLE", "Respiracao sutil na corda e brilho no elmo (4 frames)", build_idle_frames()),
        ("CLIMB_UP", "Subindo pela corda com joelhos e bracos alternados (4 frames)", build_climb_up_frames()),
        ("CLIMB_DOWN", "Descida de rapel com cerdas subindo pelo vento (4 frames)", build_climb_down_frames()),
        ("SWING_LEFT", "Impulso pendular para a esquerda (4 frames)", build_swing_left_frames()),
        ("SWING_RIGHT", "Impulso pendular para a direita com esfregao em riste (4 frames)", build_swing_right_frames()),
    ]
    airborne_frames = build_airborne_frames()

    for name, _, frames in rows_data:
        validate_frames(frames, name, check_harness=True)
    validate_frames(airborne_frames, "AIRBORNE", check_harness=False)

    # 1. Monta a Spritesheet Principal (128x160)
    main_sheet = Image.new("RGBA", (CANVAS * 4, CANVAS * 5), (0, 0, 0, 0))
    for r_idx, (_, _, frames) in enumerate(rows_data):
        for c_idx, fr in enumerate(frames):
            main_sheet.paste(fr, (c_idx * CANVAS, r_idx * CANVAS))

    # 2. Monta a Spritesheet de Salto / Balanço Livre (192x32)
    swing_sheet = Image.new("RGBA", (CANVAS * 6, CANVAS), (0, 0, 0, 0))
    for c_idx, fr in enumerate(airborne_frames):
        swing_sheet.paste(fr, (c_idx * CANVAS, 0))

    # Salva em assets/CharacterIdeas/sir_mop/
    main_sheet.save(SIR_MOP_DIR / "sir_mop_sheet.png")
    main_sheet.resize((128 * 8, 160 * 8), Image.Resampling.NEAREST).save(SIR_MOP_DIR / "sir_mop_sheet_preview_8x.png")
    swing_sheet.save(SIR_MOP_DIR / "sir_mop_rope_swing_sheet.png")
    swing_sheet.resize((192 * 8, 32 * 8), Image.Resampling.NEAREST).save(SIR_MOP_DIR / "sir_mop_rope_swing_sheet_preview_8x.png")

    # Salva GIFs de preview
    for name, _, frames in rows_data:
        save_gif(frames, SIR_MOP_DIR / f"sir_mop_{name.lower()}.gif")
    save_gif(airborne_frames, SIR_MOP_DIR / "sir_mop_airborne.gif", duration_ms=110)

    # Atualiza os arquivos carregados pelo jogo (em assets/CharacterIdeas e app/assets/CharacterIdeas)
    for target_dir in (ASSETS_CHAR_DIR, APP_ASSETS_CHAR_DIR):
        if target_dir.exists():
            rows_data[0][2][0].save(target_dir / "character_trenchcoat_32x32.png")
            rows_data[0][2][0].resize((256, 256), Image.Resampling.NEAREST).save(target_dir / "character_trenchcoat_preview_8x.png")
            main_sheet.save(target_dir / "character_trenchcoat_sheet.png")
            main_sheet.resize((128 * 8, 160 * 8), Image.Resampling.NEAREST).save(target_dir / "character_trenchcoat_sheet_preview_8x.png")
            swing_sheet.save(target_dir / "character_rope_swing_sheet.png")
            swing_sheet.resize((192 * 8, 32 * 8), Image.Resampling.NEAREST).save(target_dir / "character_rope_swing_sheet_preview_8x.png")

    showcase = make_full_showcase(rows_data, airborne_frames)
    showcase.save(SIR_MOP_DIR / "sir_mop_animations_showcase.png")
    print("[OK] Todas as animações do Sir Mop geradas, validadas e integradas ao jogo!")


if __name__ == "__main__":
    main()
