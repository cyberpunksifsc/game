from player_anchor_system import (
    SHOOT_ANIM_TICKS,
    STATE_AIRBORNE,
    STATE_ANCHORED,
    STATE_FATAL_FALL,
    PlayerAnchorSystem,
)
from player_animation import (
    ACTION_ROW_CLEAN,
    ACTION_ROW_HIT,
    ACTION_ROW_PANIC,
    ACTION_ROW_REPAIR,
    ACTION_ROW_SHOOT,
    ACTIONS_U,
    AIRBORNE_V,
    HIT_ANIM_TICKS,
    MOVEMENT_U,
    PANIC_VY_THRESHOLD,
    select_frame,
)
from player_health_and_score import PlayerHealthAndScore
from powerup_system import POWERUP_SHIELD, PowerUpSystem


def test_priority_hit_overrides_everything():
    u, v = select_frame(
        state=STATE_AIRBORNE,
        action="AIRBORNE",
        vy=5.0,
        anim_timer=10,
        hit_timer=HIT_ANIM_TICKS,
        shoot_timer=SHOOT_ANIM_TICKS,
        work_action="REPAIRING",
    )
    assert u == ACTIONS_U
    assert v == ACTION_ROW_HIT * 32


def test_panic_triggers_only_above_vy_threshold():
    # Abaixo ou igual ao limiar: usa folha normal de salto aéreo (v=160)
    u_normal, v_normal = select_frame(
        state=STATE_AIRBORNE,
        action="AIRBORNE",
        vy=PANIC_VY_THRESHOLD,
        anim_timer=0,
    )
    assert u_normal == MOVEMENT_U
    assert v_normal == AIRBORNE_V

    # Acima do limiar: entra na linha PANIC da folha de ações
    u_panic, v_panic = select_frame(
        state=STATE_AIRBORNE,
        action="AIRBORNE",
        vy=PANIC_VY_THRESHOLD + 0.1,
        anim_timer=0,
    )
    assert u_panic == ACTIONS_U
    assert v_panic == ACTION_ROW_PANIC * 32

    # Queda fatal também usa PANIC
    u_fall, v_fall = select_frame(
        state=STATE_FATAL_FALL,
        action="AIRBORNE",
        vy=4.0,
        anim_timer=3,
    )
    assert u_fall == ACTIONS_U + 32
    assert v_fall == ACTION_ROW_PANIC * 32


def test_work_clean_and_repair_rows():
    u_clean, v_clean = select_frame(
        state=STATE_ANCHORED,
        action="WORKING",
        vy=0.0,
        anim_timer=5,
        work_action="CLEANING",
    )
    assert u_clean == ACTIONS_U + 32
    assert v_clean == ACTION_ROW_CLEAN * 32

    u_repair, v_repair = select_frame(
        state=STATE_ANCHORED,
        action="WORKING",
        vy=0.0,
        anim_timer=8,
        work_action="REPAIRING",
    )
    assert u_repair == ACTIONS_U + 64
    assert v_repair == ACTION_ROW_REPAIR * 32


def test_oneshot_shoot_and_hit_progress_from_f0_to_f3():
    hit_frames = [
        (select_frame(STATE_ANCHORED, "IDLE", 0.0, 0, hit_timer=t)[0] - ACTIONS_U) // 32
        for t in range(HIT_ANIM_TICKS, 0, -1)
    ]
    assert hit_frames[0] == 0
    assert hit_frames[-1] == 3
    assert hit_frames == sorted(hit_frames)
    assert set(hit_frames) == {0, 1, 2, 3}

    shoot_frames = [
        (select_frame(STATE_ANCHORED, "IDLE", 0.0, 0, shoot_timer=t)[0] - ACTIONS_U) // 32
        for t in range(SHOOT_ANIM_TICKS, 0, -1)
    ]
    assert shoot_frames[0] == 0
    assert shoot_frames[-1] == 3
    assert shoot_frames == sorted(shoot_frames)
    assert set(shoot_frames) == {0, 1, 2, 3}


def test_shield_absorption_does_not_trigger_hit_anim_timer():
    pu = PowerUpSystem(POWERUP_SHIELD)
    stats = PlayerHealthAndScore(powerup_system=pu)

    # Primeiro impacto é absorvido pelo Escudo Reativo: não deve ativar hit_anim_timer
    assert stats.take_damage(1) is False
    assert stats.hit_anim_timer == 0

    # Expira a curta invulnerabilidade do escudo e aplica dano real
    stats.invulnerable_timer = 0
    assert stats.take_damage(1) is True
    assert stats.hit_anim_timer == HIT_ANIM_TICKS


def test_plant_and_retrieve_anchor_trigger_shoot_timer():
    sys = PlayerAnchorSystem(start_anchor_x=160, start_anchor_y=1800, initial_rope_length=50)
    assert sys.shoot_timer == 0

    # Fora de alcance: falha e não dispara animação
    hx, hy = sys.get_harness_pos()
    assert sys.plant_anchor(hx + 500, hy) is False
    assert sys.shoot_timer == 0

    # Dentro do alcance: sucesso e ativa shoot_timer
    assert sys.plant_anchor(hx + 40, hy - 20) is True
    assert sys.shoot_timer == SHOOT_ANIM_TICKS

    # Zera timer e testa recolhimento
    sys.shoot_timer = 0
    assert sys.retrieve_anchor(hx + 40, hy - 20) is True
    assert sys.shoot_timer == SHOOT_ANIM_TICKS
