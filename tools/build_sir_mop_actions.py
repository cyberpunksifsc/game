#!/usr/bin/env python3
"""
Gerador da Spritesheet de Ações do 'Sir Mop' para o Pyxel (128x160 px = 4 colunas x 5 linhas de 32x32).

Carregada em (128, 0) no banco de imagem 2 do Pyxel:
- Linha 0: CLEAN (4 frames — esfregando janela com movimento vertical/diagonal e espuma)
- Linha 1: REPAIR (4 frames — esfregão invertido como lança-solda a laser com faíscas)
- Linha 2: SHOOT (4 frames — antecipação, disparo do gancho com clarão, coice e recuperação)
- Linha 3: HIT (4 frames — flash de impacto, tranco para trás na corda e recuperação)
- Linha 4: PANIC (4 frames — queda livre descontrolada com braços erguidos e pernas pedalando)
"""

from pathlib import Path
from PIL import Image, ImageDraw

from adapt_sir_mop_pyxel import (
    CANVAS,
    PYXEL_PALETTE,
    render_sir_mop,
)
from build_sir_mop_spritesheets import (
    APP_ASSETS_CHAR_DIR,
    ASSETS_CHAR_DIR,
    SIR_MOP_DIR,
    compose_pose,
    save_gif,
     set_pixels,
    validate_frames,
)


def rows_to_grid(rows: list[str]) -> list[list[str]]:
    return [list(r) for r in rows]


def grid_to_rows(grid: list[list[str]]) -> list[str]:
    return ["".join(r) for r in grid]


def clear_default_mop(grid: list[list[str]]):
    """Remove o esfregão padrão à direita do tronco (X=18..26, Y=10..22) para desenhar poses customizadas."""
    for y in range(10, 23):
        for x in range(18, 27):
            grid[y][x] = "."


def draw_mop_scrub(
    grid: list[list[str]],
    hand_y: int,
    head_x: int,
    head_y: int,
    style: str = "normal",
):
    """Desenha o braço direito e o esfregão esfregando o painel de vidro à frente."""
    clear_default_mop(grid)

    # Mão direita segurando o cabo (X=18)
    set_pixels(grid, [(18, hand_y, "E"), (19, hand_y, "9")])

    # Haste laranja conectando a mão até a base das cerdas (head_x, head_y)
    steps = max(abs(head_x - 19), abs(head_y - hand_y), 1)
    for i in range(steps + 1):
        sx = int(round(19 + (head_x - 19) * (i / steps)))
        sy = int(round(hand_y + (head_y - hand_y) * (i / steps)))
        set_pixels(grid, [(sx, sy, "9")])

    if style == "high":
        # Cerdas no alto contra o vidro + brilho de espuma branca
        set_pixels(
            grid,
            [
                (head_x, head_y - 1, "A"), (head_x + 1, head_y - 1, "A"), (head_x + 2, head_y - 1, "7"),
                (head_x, head_y, "A"),     (head_x + 1, head_y, "A"),     (head_x + 2, head_y, "A"),
                (head_x, head_y + 1, "3"), (head_x + 1, head_y + 1, "A"), (head_x + 2, head_y + 1, "7"),
            ],
        )
    elif style == "mid_press":
        # Cerdas comprimidas no meio da janela + gotas de espuma
        set_pixels(
            grid,
            [
                (head_x, head_y - 1, "A"), (head_x + 1, head_y - 1, "7"),
                (head_x, head_y, "A"),     (head_x + 1, head_y, "A"),     (head_x + 2, head_y, "7"),
                (head_x, head_y + 1, "3"), (head_x + 1, head_y + 1, "A"), (head_x + 2, head_y + 1, "A"),
                (head_x + 1, head_y + 2, "7"),
            ],
        )
    elif style == "low_flat":
        # Cerdas achatadas na base do movimento + espuma espalhada
        set_pixels(
            grid,
            [
                (head_x - 1, head_y, "A"), (head_x, head_y, "A"), (head_x + 1, head_y, "A"), (head_x + 2, head_y, "7"),
                (head_x - 1, head_y + 1, "3"), (head_x, head_y + 1, "A"), (head_x + 1, head_y + 1, "7"), (head_x + 2, head_y + 1, "A"),
            ],
        )
    else:  # "flare_up"
        # Cerdas abertas subindo de volta na diagonal
        set_pixels(
            grid,
            [
                (head_x, head_y - 1, "7"), (head_x + 2, head_y - 1, "A"),
                (head_x, head_y, "A"),     (head_x + 1, head_y, "A"),     (head_x + 2, head_y, "A"),
                (head_x, head_y + 1, "A"), (head_x + 1, head_y + 1, "3"), (head_x + 2, head_y + 1, "7"),
            ],
        )


def draw_inverted_torch_mop(
    grid: list[list[str]],
    recoil_dx: int = 0,
    tip_color: str = "A",
    spark_pattern: int = 0,
):
    """Desenha o esfregão invertido como lança-solda: cerdas para trás/baixo e ponta incandescente à frente."""
    clear_default_mop(grid)
    mx = 18 + recoil_dx
    my = 13

    # Cerdas amarelas viradas para trás/baixo (logo abaixo da mão direita)
    set_pixels(
        grid,
        [
            (mx, my + 2, "A"), (mx + 1, my + 2, "A"),
            (mx - 1, my + 3, "3"), (mx, my + 3, "A"), (mx + 1, my + 3, "3"),
        ],
    )

    # Mão direita firme e haste da lança-solda apontada horizontalmente à frente
    set_pixels(
        grid,
        [
            (mx, my, "E"),
            (mx + 1, my, "9"),
            (mx + 2, my, "9"),
            (mx + 3, my, "9"),
            (mx + 4, my, "5"),
            (mx + 5, my, "6"),  # bocal metálico de solda na ponta do cabo
            (mx + 6, my, tip_color),
        ],
    )

    tx, ty = mx + 6, my
    if spark_pattern == 1:
        # Clarão branco intenso + faíscas diagonais abertas
        set_pixels(
            grid,
            [
                (tx, ty - 1, "A"),
                (tx + 1, ty, "7"),
                (tx, ty + 1, "A"),
                (tx + 2, ty - 2, "7"),
                (tx + 2, ty + 2, "9"),
            ],
        )
    elif spark_pattern == 2:
        # Arco de solda alternado em X
        set_pixels(
            grid,
            [
                (tx - 1, ty - 2, "7"),
                (tx + 1, ty - 1, "7"),
                (tx + 1, ty, "A"),
                (tx + 1, ty + 1, "7"),
                (tx + 2, ty - 1, "9"),
                (tx - 1, ty + 2, "A"),
            ],
        )
    elif spark_pattern == 3:
        # Fagulha residual de recuo
        set_pixels(
            grid,
            [
                (tx + 1, ty, "A"),
                (tx + 2, ty - 1, "9"),
                (tx + 1, ty + 2, "9"),
            ],
        )


def draw_launcher_arm(grid: list[list[str]], phase: str):
    """Desenha o braço esquerdo estendendo o lançador de gancho para a diagonal superior esquerda."""
    # Limpa o braço esquerdo padrão (X=9..10, Y=13..16) para redesenhar a pose
    for y in range(13, 17):
        for x in range(9, 11):
            grid[y][x] = "."

    if phase == "windup":
        # F0: Antecipação — braço esquerdo encolhido puxando o lançador junto ao peito
        set_pixels(
            grid,
            [
                (9, 13, "3"), (10, 13, "B"),
                (8, 14, "E"), (9, 14, "5"), (10, 14, "6"),
                (8, 10, "6"),
            ],
        )
    elif phase == "fire":
        # F1: Ação — braço esquerdo estendido para a esquerda/cima disparando o gancho com clarão!
        set_pixels(
            grid,
            [
                # Ombro e braço esquerdo estendidos à esquerda (Y=12..13)
                (8, 12, "B"), (9, 12, "B"), (10, 12, "3"),
                (7, 12, "E"),
                # Pistola lançadora metálica apontada para cima/esquerda (X=4..6, Y=11..12)
                (5, 11, "6"), (6, 11, "6"), (6, 12, "5"),
                # Clarão de disparo na boca (X=3..5, Y=8..10) + gancho disparado
                (4, 9, "7"), (5, 9, "A"), (4, 10, "A"),
                (3, 7, "6"), (3, 8, "9"), (4, 7, "6"),
                (8, 10, "6"),
            ],
        )
    elif phase == "recoil":
        # F2: Contato / Coice — lançador sobe em recuo com fumaça/faísca
        set_pixels(
            grid,
            [
                (8, 11, "B"), (9, 12, "B"),
                (7, 11, "E"),
                (5, 9, "6"), (6, 10, "5"), (6, 9, "6"),
                (4, 8, "9"), (5, 7, "A"),
                (8, 10, "6"),
            ],
        )
    elif phase == "recover":
        # F3: Recuperação — braço abaixando o lançador de volta ao coldre
        set_pixels(
            grid,
            [
                (9, 13, "B"), (10, 13, "3"),
                (8, 14, "E"), (7, 14, "5"), (7, 13, "6"),
                (8, 10, "6"),
            ],
        )


def apply_hit_flash(grid: list[list[str]], intense: bool = True):
    """Substitui parte do verde da armadura por branco/amarelo para destacar o impacto do tiro."""
    for y in range(7, 20):
        for x in range(9, 20):
            if grid[y][x] == "B" and (x + y) % 2 == 0:
                grid[y][x] = "7" if intense else "A"


# ---------------------------------------------------------------------------
# Construção das 5 linhas (4 frames cada)
# ---------------------------------------------------------------------------

def build_clean_frames() -> list[Image.Image]:
    """Linha 0: CLEAN (4 frames) — Sir Mop esfregando o painel de vidro com o esfregão."""
    # F0: Esfregão no alto à direita
    g0 = rows_to_grid(compose_pose(head_dy=0, visor_glint=True))
    draw_mop_scrub(g0, hand_y=12, head_x=22, head_y=10, style="high")

    # F1: Esfregão descendo com pressão no centro do vidro, tronco inclina 1px à frente
    g1 = rows_to_grid(compose_pose(head_dx=1, torso_dx=1))
    draw_mop_scrub(g1, hand_y=13, head_x=23, head_y=14, style="mid_press")

    # F2: Esfregão na base do vidro, cerdas achatadas espalhando espuma, joelhos flexionam
    g2 = rows_to_grid(
        compose_pose(
            head_dx=1,
            head_dy=1,
            torso_dx=1,
            left_leg_pose="bend_right_soft",
            right_leg_pose="bend_right_soft",
        )
    )
    draw_mop_scrub(g2, hand_y=14, head_x=22, head_y=18, style="low_flat")

    # F3: Esfregão subindo de volta na diagonal com cerdas abertas
    g3 = rows_to_grid(compose_pose(head_dy=-1, visor_glint=True))
    draw_mop_scrub(g3, hand_y=12, head_x=21, head_y=12, style="flare_up")

    return [render_sir_mop(grid_to_rows(g)) for g in (g0, g1, g2, g3)]


def build_repair_frames() -> list[Image.Image]:
    """Linha 1: REPAIR (4 frames) — Esfregão invertido usado como lança-solda com faíscas."""
    # F0: Posiciona a lança-solda, ponta amarela aquecendo
    g0 = rows_to_grid(compose_pose(visor_glint=True))
    draw_inverted_torch_mop(g0, recoil_dx=0, tip_color="A", spark_pattern=0)

    # F1: Contato forte de solda (ponta branca + faíscas abertas)
    g1 = rows_to_grid(compose_pose(visor_glint=True))
    draw_inverted_torch_mop(g1, recoil_dx=0, tip_color="7", spark_pattern=1)

    # F2: Pulso contínuo de solda (arco alternado em X + leve flexão de joelho)
    g2 = rows_to_grid(compose_pose(right_leg_pose="bend_right_soft"))
    draw_inverted_torch_mop(g2, recoil_dx=0, tip_color="A", spark_pattern=2)

    # F3: Leve recuo do braço e elmo pela vibração da solda
    g3 = rows_to_grid(compose_pose(head_dx=-1, visor_glint=True))
    draw_inverted_torch_mop(g3, recoil_dx=-1, tip_color="9", spark_pattern=3)
    set_pixels(g3, [(8, 10, "6")])

    return [render_sir_mop(grid_to_rows(g)) for g in (g0, g1, g2, g3)]


def build_shoot_frames() -> list[Image.Image]:
    """Linha 2: SHOOT (4 frames) — Antecipação, disparo do lançador de gancho, coice e recuperação."""
    # F0: Antecipação (leve squash)
    g0 = rows_to_grid(compose_pose(head_dy=1, torso_dy=1, mop_dy=1))
    draw_launcher_arm(g0, "windup")

    # F1: Disparo com braço erguido e clarão na boca do lançador
    g1 = rows_to_grid(compose_pose(head_dy=0, torso_dy=0, mop_dx=1, visor_glint=True))
    draw_launcher_arm(g1, "fire")

    # F2: Coice (recoil) — cabeça e tronco recuam 1px
    g2 = rows_to_grid(compose_pose(head_dx=-1, torso_dx=-1, left_leg_pose="bend_left_soft", mop_dx=1, mop_dy=-1))
    draw_launcher_arm(g2, "recoil")
    set_pixels(g2, [(8, 10, "6")])  # garante mosquetão intacto

    # F3: Recuperação voltando à pose neutra
    g3 = rows_to_grid(compose_pose(head_dy=0, torso_dy=0))
    draw_launcher_arm(g3, "recover")

    return [render_sir_mop(grid_to_rows(g)) for g in (g0, g1, g2, g3)]


def build_hit_frames() -> list[Image.Image]:
    """Linha 3: HIT (4 frames) — Flash de impacto, tranco para trás na corda e recuperação."""
    # F0: Flash branco de impacto no peitoral
    g0 = rows_to_grid(compose_pose(head_dx=-1, torso_dx=-1, mop_dx=1, mop_dy=-1))
    apply_hit_flash(g0, intense=True)
    set_pixels(g0, [(8, 10, "6")])

    # F1: Pico do tranco (corpo arqueado para trás, joelhos dobrados, esfregão jogado para cima)
    g1 = rows_to_grid(
        compose_pose(
            head_dx=-1,
            head_dy=-1,
            torso_dx=-1,
            left_leg_pose="bend_left_deep",
            right_leg_pose="bend_right_soft",
            mop_dx=2,
            mop_dy=-3,
            bristles_flare_up=True,
        )
    )
    apply_hit_flash(g1, intense=False)
    set_pixels(g1, [(8, 10, "6")])

    # F2: Balanço de atordoamento
    g2 = rows_to_grid(
        compose_pose(
            head_dx=-1,
            torso_dx=0,
            left_leg_pose="bend_left_soft",
            right_leg_pose="bend_left_soft",
            mop_dx=1,
            mop_dy=-1,
        )
    )
    set_pixels(g2, [(8, 10, "6")])

    # F3: Recuperando postura
    g3 = rows_to_grid(compose_pose(head_dy=1, mop_dy=0))
    set_pixels(g3, [(8, 10, "6")])

    return [render_sir_mop(grid_to_rows(g)) for g in (g0, g1, g2, g3)]


def draw_panic_flail_arms(grid: list[list[str]], frame_idx: int):
    """Desenha ambos os braços erguidos agitando no ar e o esfregão com cerdas para cima."""
    clear_default_mop(grid)
    for y in range(12, 17):
        for x in range(8, 11):
            grid[y][x] = "."

    # Braço esquerdo agitando para cima/esquerda
    if frame_idx in (0, 2):
        set_pixels(grid, [(9, 11, "B"), (8, 10, "B"), (7, 9, "E"), (7, 8, "E")])
    else:
        set_pixels(grid, [(9, 12, "B"), (8, 11, "B"), (7, 11, "E"), (6, 10, "E")])

    # Braço direito erguido segurando o esfregão de cabeça para cima (cerdas esvoaçando no topo!)
    shift_x = 0 if frame_idx % 2 == 0 else 1
    hx = 19 + shift_x
    hy = 10 if frame_idx in (0, 2) else 11
    set_pixels(
        grid,
        [
            (18, 12, "B"),
            (hx, hy + 1, "E"),
            (hx, hy, "9"),
            (hx, hy - 1, "9"),
            (hx, hy - 2, "9"),
            # Cerdas abertas no alto pela força do vento na queda
            (hx - 1, hy - 3, "A"), (hx, hy - 3, "3"), (hx + 1, hy - 3, "A"),
            (hx - 2, hy - 4, "A"), (hx, hy - 4, "A"), (hx + 2, hy - 4, "A"),
        ],
    )


def build_panic_frames() -> list[Image.Image]:
    """Linha 4: PANIC (4 frames) — Queda livre descontrolada com braços no alto e pernas pedalando."""
    # F0: Perna esquerda chuta alto, direita esticada, braços e esfregão erguidos
    g0 = rows_to_grid(
        compose_pose(
            head_dy=-1,
            torso_dy=-1,
            left_leg_pose="kick_left",
            right_leg_pose="straight",
            keep_harness_fixed=False,
        )
    )
    draw_panic_flail_arms(g0, 0)

    # F1: Troca a pedalada (perna esquerda esticada, perna direita chuta alto), elmo inclina à esquerda
    g1 = rows_to_grid(
        compose_pose(
            head_dx=-1,
            head_dy=-2,
            torso_dy=-1,
            left_leg_pose="straight",
            right_leg_pose="kick_right",
            keep_harness_fixed=False,
        )
    )
    draw_panic_flail_arms(g1, 1)

    # F2: Ambas as pernas encolhidas em pânico (< >), elmo inclina à direita
    g2 = rows_to_grid(
        compose_pose(
            head_dx=1,
            head_dy=-1,
            torso_dy=0,
            left_leg_pose="bend_left_deep",
            right_leg_pose="bend_right_deep",
            keep_harness_fixed=False,
        )
    )
    draw_panic_flail_arms(g2, 2)

    # F3: Pernas abertas em X (kick_left + kick_right), olhando para cima
    g3 = rows_to_grid(
        compose_pose(
            head_dx=0,
            head_dy=-2,
            torso_dy=-1,
            left_leg_pose="kick_left",
            right_leg_pose="kick_right",
            keep_harness_fixed=False,
        )
    )
    draw_panic_flail_arms(g3, 3)

    return [render_sir_mop(grid_to_rows(g)) for g in (g0, g1, g2, g3)]


def make_actions_showcase(rows_data: list[tuple[str, str, list[Image.Image], bool]]) -> Image.Image:
    scale = 4  # 32 * 4 = 128px por frame
    fw = CANVAS * scale
    W = 1040
    H = 80 + len(rows_data) * 165
    sheet = Image.new("RGBA", (W, H), (16, 16, 24, 255))
    d = ImageDraw.Draw(sheet)

    d.rectangle([(0, 0), (W, 56)], fill=(10, 10, 16, 255))
    d.line([(0, 56), (W, 56)], fill=(255, 163, 0, 255), width=2)
    d.text((20, 12), "SIR MOP - SPRITESHEET DE ACOES (BANCO 2 U=128, V=0 | 128x160)", fill=(255, 255, 255, 255))
    d.text((20, 32), "5 animacoes de acao (4 frames cada): LIMPAR, CONSERTAR, DISPARAR, DANO e PANICO/QUEDA", fill=(170, 180, 200, 255))

    y = 70
    for row_idx, (name, desc, frames, anchored) in enumerate(rows_data):
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
            if anchored:
                ax, ay = bx + 8 * scale + scale // 2, by + 10 * scale + scale // 2
                d.line([(bx + 16 * scale, by + 4), (ax, ay)], fill=(131, 118, 156, 255), width=2)
            big = fr.resize((fw, fw), Image.Resampling.NEAREST)
            sheet.paste(big, (bx, by), big)
            d.text((bx + 4, by + fw - 14), f"F{i}", fill=(200, 205, 220, 255))
        y += 165

    return sheet


def main():
    SIR_MOP_DIR.mkdir(parents=True, exist_ok=True)

    rows_data = [
        ("CLEAN", "Esfregando janela com espuma nas cerdas (4 frames, loop)", build_clean_frames(), True),
        ("REPAIR", "Esfregao invertido como lanca-solda com faiscas (4 frames, loop)", build_repair_frames(), True),
        ("SHOOT", "Disparo/recolhimento do lancador de gancho com coice (4 frames, 1x)", build_shoot_frames(), True),
        ("HIT", "Impacto de projetil com flash e tranco na corda (4 frames, 1x)", build_hit_frames(), True),
        ("PANIC", "Queda livre descontrolada com bracos no alto (4 frames, loop)", build_panic_frames(), False),
    ]

    for name, _, frames, anchored in rows_data:
        validate_frames(frames, name, check_harness=anchored)

    actions_sheet = Image.new("RGBA", (CANVAS * 4, CANVAS * 5), (0, 0, 0, 0))
    for r_idx, (_, _, frames, _) in enumerate(rows_data):
        for c_idx, fr in enumerate(frames):
            actions_sheet.paste(fr, (c_idx * CANVAS, r_idx * CANVAS))

    actions_sheet.save(SIR_MOP_DIR / "sir_mop_actions_sheet.png")
    actions_sheet.resize((128 * 8, 160 * 8), Image.Resampling.NEAREST).save(
        SIR_MOP_DIR / "sir_mop_actions_sheet_preview_8x.png"
    )

    for name, _, frames, _ in rows_data:
        save_gif(frames, SIR_MOP_DIR / f"sir_mop_{name.lower()}.gif", duration_ms=130)

    for target_dir in (ASSETS_CHAR_DIR, APP_ASSETS_CHAR_DIR):
        if target_dir.exists():
            actions_sheet.save(target_dir / "character_actions_sheet.png")
            actions_sheet.resize((128 * 8, 160 * 8), Image.Resampling.NEAREST).save(
                target_dir / "character_actions_sheet_preview_8x.png"
            )

    showcase = make_actions_showcase(rows_data)
    showcase.save(SIR_MOP_DIR / "sir_mop_actions_showcase.png")
    print("[OK] Spritesheet de ações do Sir Mop (128x160) gerada e validada com sucesso!")


if __name__ == "__main__":
    main()
