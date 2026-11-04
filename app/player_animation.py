"""Seleção pura de frames de animação do Sir Mop (movimento + ações)."""

from player_anchor_system import STATE_AIRBORNE, STATE_FATAL_FALL

TILE_SIZE = 32
MOVEMENT_U = 0
ACTIONS_U = 128
AIRBORNE_V = 160

# Linhas da folha de ações (em u=128)
ACTION_ROW_CLEAN = 0
ACTION_ROW_REPAIR = 1
ACTION_ROW_SHOOT = 2
ACTION_ROW_HIT = 3
ACTION_ROW_PANIC = 4

# Durações totais das animações one-shot (a 30 FPS)
SHOOT_ANIM_TICKS = 14  # F0(3) + F1(3) + F2(4) + F3(4)
HIT_ANIM_TICKS = 15    # F0(3) + F1(4) + F2(4) + F3(4)

# Limiar de velocidade vertical para entrar em pânico na queda livre
PANIC_VY_THRESHOLD = 3.0


def _oneshot_frame(timer: int, total_ticks: int, thresholds: tuple[int, int, int]) -> int:
    """Mapeia um timer decrescente [total_ticks..1] para o índice de frame 0..3."""
    elapsed = max(0, total_ticks - timer)
    if elapsed < thresholds[0]:
        return 0
    if elapsed < thresholds[1]:
        return 1
    if elapsed < thresholds[2]:
        return 2
    return 3


def select_frame(
    state: str,
    action: str,
    vy: float,
    anim_timer: int,
    hit_timer: int = 0,
    shoot_timer: int = 0,
    work_action: str = "",
) -> tuple[int, int]:
    """Retorna as coordenadas (u, v) do frame 32x32 no banco de imagem 2 do Pyxel."""
    # 1. Reação a dano tem prioridade máxima
    if hit_timer > 0:
        frame = _oneshot_frame(hit_timer, HIT_ANIM_TICKS, (3, 7, 11))
        return (ACTIONS_U + frame * TILE_SIZE, ACTION_ROW_HIT * TILE_SIZE)

    # 2. Queda livre em alta velocidade (pânico) ou queda fatal
    if (state == STATE_AIRBORNE and vy > PANIC_VY_THRESHOLD) or state == STATE_FATAL_FALL:
        frame = (anim_timer // 3) % 4
        return (ACTIONS_U + frame * TILE_SIZE, ACTION_ROW_PANIC * TILE_SIZE)

    # 3. Salto acrobático normal no ar
    if state == STATE_AIRBORNE:
        frame = (anim_timer // 5) % 6
        return (MOVEMENT_U + frame * TILE_SIZE, AIRBORNE_V)

    # 4. Disparo ou recolhimento do lançador de gancho
    if shoot_timer > 0:
        frame = _oneshot_frame(shoot_timer, SHOOT_ANIM_TICKS, (3, 6, 10))
        return (ACTIONS_U + frame * TILE_SIZE, ACTION_ROW_SHOOT * TILE_SIZE)

    # 5. Trabalho contextual na janela (Limpeza com esfregão ou Conserto com lança-solda)
    if action == "WORKING" or work_action in ("CLEANING", "REPAIRING"):
        if work_action == "REPAIRING":
            frame = (anim_timer // 4) % 4
            return (ACTIONS_U + frame * TILE_SIZE, ACTION_ROW_REPAIR * TILE_SIZE)
        frame = (anim_timer // 5) % 4
        return (ACTIONS_U + frame * TILE_SIZE, ACTION_ROW_CLEAN * TILE_SIZE)

    # 6. Movimentação ancorada na corda
    if action == "CLIMB_UP":
        row = 1
        frame = (anim_timer // 6) % 4
    elif action == "CLIMB_DOWN":
        row = 2
        frame = (anim_timer // 6) % 4
    elif action == "SWING_LEFT":
        row = 3
        frame = (anim_timer // 6) % 4
    elif action == "SWING_RIGHT":
        row = 4
        frame = (anim_timer // 6) % 4
    else:
        row = 0
        frame = (anim_timer // 8) % 4

    return (MOVEMENT_U + frame * TILE_SIZE, row * TILE_SIZE)
