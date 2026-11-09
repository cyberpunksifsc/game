import types
import pytest
import pyxel

from building_generator import BuildingGenerator, WINDOW_STATE_DIRTY
from consumable_system import (
    DEFAULT_DROP_CHANCE,
    FULL_HP_BONUS_SCORE,
    LAUNCH_ANGLE_MAX_DEG,
    LAUNCH_ANGLE_MIN_DEG,
    MAX_FALL_SPEED,
    PICKUP_ARM_DELAY_FRAMES,
    ConsumableManager,
    ConsumablePickup,
    HeartPickup,
)
from player_anchor_system import STATE_ANCHORED
from player_cleaning_system import PlayerCleaningSystem
from player_health_and_score import MAX_HP, PlayerHealthAndScore


def test_drop_chance_is_one_in_five(monkeypatch):
    assert DEFAULT_DROP_CHANCE == pytest.approx(0.20)
    mgr = ConsumableManager()

    # Abaixo de 0.20 -> gera o consumível
    monkeypatch.setattr("consumable_system.random.random", lambda: 0.19)
    pickup = mgr.try_spawn_from_window(120.0, 900.0)
    assert isinstance(pickup, HeartPickup)
    assert len(mgr.pickups) == 1

    # Igual ou acima de 0.20 -> não gera
    monkeypatch.setattr("consumable_system.random.random", lambda: 0.20)
    assert mgr.try_spawn_from_window(120.0, 900.0) is None
    assert len(mgr.pickups) == 1


def test_upward_90_degree_cone_and_slow_descent():
    for _ in range(30):
        p = HeartPickup(160.0, 1000.0)
        assert LAUNCH_ANGLE_MIN_DEG <= p.launch_angle_deg <= LAUNCH_ANGLE_MAX_DEG
        assert p.vy < 0.0  # Salta sempre para cima inicialmente

    # Simula subida até o ápice e depois queda lenta
    p = HeartPickup(160.0, 1000.0, launch_angle_deg=-90.0)
    initial_y = p.y
    for _ in range(15):
        p.update()
    peak_y = p.y
    assert peak_y < initial_y  # Subiu

    # Continua atualizando durante a queda e verifica limite de velocidade lenta
    for _ in range(60):
        p.update()
        if p.vy > 0:
            assert p.vy <= MAX_FALL_SPEED + 1e-6


def test_arm_delay_prevents_instant_collection_until_peak():
    p = HeartPickup(116.0, 516.0, launch_angle_deg=-90.0)
    # Jogador exatamente em cima da posição inicial do item
    px, py = 100.0, 500.0

    for frame in range(PICKUP_ARM_DELAY_FRAMES - 1):
        p.update()
        assert p.is_collectible is False
        assert p.check_player_collision(px, py) is False

    # No frame PICKUP_ARM_DELAY_FRAMES (12 = ~0.4s), torna-se coletável
    p.update()
    assert p.is_collectible is True
    # Reposiciona perto do jogador para validar colisão ativa
    p.x, p.y = 116.0, 516.0
    assert p.check_player_collision(px, py) is True


def test_heart_pickup_heals_missing_hp_or_grants_full_hp_bonus():
    stats = PlayerHealthAndScore()
    stats.hp = 2
    stats.score = 500

    heart1 = HeartPickup(100.0, 500.0)
    label1, _ = heart1.apply_effect(None, stats)
    assert stats.hp == 3
    assert stats.score == 500
    assert "+1 VIDA" in label1

    # Já com 3/3 corações: mantém 3 corações e soma bônus de +150 pontos
    assert stats.hp == MAX_HP
    heart2 = HeartPickup(100.0, 500.0)
    label2, _ = heart2.apply_effect(None, stats)
    assert stats.hp == MAX_HP
    assert stats.score == 500 + FULL_HP_BONUS_SCORE
    assert str(FULL_HP_BONUS_SCORE) in label2


def test_cleaning_system_triggers_consumable_spawn_on_completion(monkeypatch):
    building = BuildingGenerator()
    target_win = building.windows[0]
    target_win.state = WINDOW_STATE_DIRTY
    target_win.work_frames = target_win.max_frames - 1

    wx = target_win.x + target_win.w / 2
    wy = target_win.y + target_win.h / 2

    anchor_stub = types.SimpleNamespace(
        state=STATE_ANCHORED,
        angular_vel=0.0,
        angle=0.0,
        camera_x=0.0,
        camera_y=0.0,
        get_harness_pos=lambda: (wx, wy),
    )
    player_stub = types.SimpleNamespace(anchor_system=anchor_stub, touch_controls=None)
    stats = PlayerHealthAndScore()
    mgr = ConsumableManager(drop_chance=1.0)
    cleaning = PlayerCleaningSystem(player_stub, building, stats=stats, consumable_manager=mgr)

    monkeypatch.setattr(pyxel, "btn", lambda key: key == pyxel.KEY_E)
    monkeypatch.setattr(pyxel, "frame_count", 1, raising=False)

    cleaning.update()
    assert len(mgr.pickups) == 1
    assert mgr.pickups[0].x == pytest.approx(wx)
    assert mgr.pickups[0].y == pytest.approx(wy)
