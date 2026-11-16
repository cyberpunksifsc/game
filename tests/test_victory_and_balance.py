import pytest

from building_generator import BuildingGenerator
from hazard_spawner import (
    APEX_ALTITUDE_Y,
    BASE_MIN_INTERVAL,
    BASE_SPEED_MAX,
    BASE_SPEED_MIN,
    MAX_SPEED_MAX,
    MIN_ALLOWED_INTERVAL,
)
from patrol_drone_ai import DEFAULT_DRONE_ALTITUDES
from player_health_and_score import (
    BONUS_MAX_EFFICIENCY,
    BONUS_PER_HP,
    EFFICIENCY_BASE_DRAIN,
    EFFICIENCY_FULL_DRAIN_SECONDS,
    FPS,
    REASON_HP,
    REASON_VICTORY,
    PlayerHealthAndScore,
)


def test_building_has_18_floors():
    building = BuildingGenerator()
    total_floors = int((building.base_y - 40 - building.apex_y) // building.floor_height)
    assert total_floors == 18
    assert len(building.windows) == 18 * 4
    assert building.apex_y == pytest.approx(APEX_ALTITUDE_Y)


def test_drones_all_within_18_floor_building_span():
    building = BuildingGenerator()
    for alt in DEFAULT_DRONE_ALTITUDES:
        assert building.apex_y < alt < 1800.0


def test_bullet_final_caps_match_balance_spec():
    # Início permanece igual ao original
    assert BASE_MIN_INTERVAL == 110
    assert (BASE_SPEED_MIN, BASE_SPEED_MAX) == (4.8, 6.0)

    # Teto final travado em 6.2 de velocidade máxima e 2.5s (75 frames) de cooldown mínimo
    assert MAX_SPEED_MAX == pytest.approx(6.2)
    assert MIN_ALLOWED_INTERVAL == 75

    # Dreno da barra de Eficiência Corporativa (1 / (60 * 30))
    assert EFFICIENCY_FULL_DRAIN_SECONDS == pytest.approx(60.0)
    assert EFFICIENCY_BASE_DRAIN == pytest.approx(1.0 / (EFFICIENCY_FULL_DRAIN_SECONDS * FPS))


def test_trigger_victory_calculates_bonuses_and_resets_cleanly():
    stats = PlayerHealthAndScore()
    stats.score = 1000
    stats.hp = 2
    stats.efficiency = 0.80

    stats.trigger_victory()

    assert stats.is_game_over is True
    assert stats.is_victory is True
    assert stats.game_over_reason == REASON_VICTORY
    assert stats.hp_bonus == 2 * BONUS_PER_HP
    assert stats.efficiency_bonus == int(round(0.80 * BONUS_MAX_EFFICIENCY))
    assert stats.score == 1000 + stats.hp_bonus + stats.efficiency_bonus

    # Chamadas subsequentes a trigger_victory ou trigger_game_over são ignoradas
    stats.trigger_game_over(REASON_HP)
    assert stats.is_victory is True
    assert stats.game_over_reason == REASON_VICTORY

    # Reset limpa estado de vitória e bônus
    stats.reset()
    assert stats.is_game_over is False
    assert stats.is_victory is False
    assert stats.hp_bonus == 0
    assert stats.efficiency_bonus == 0
    assert stats.score == 0


def test_multitouch_and_single_pointer_dpad_plus_jump(monkeypatch):
    import pyxel
    from touch_controls import TouchControls
    from player_anchor_system import (
        DIRECTIONAL_JUMP_VX,
        STATE_AIRBORNE,
        PlayerAnchorSystem,
    )

    state = {"mx": 0, "my": 0, "down": False, "pressed": False}
    monkeypatch.setattr(pyxel, "mouse_x", 0, raising=False)
    monkeypatch.setattr(pyxel, "mouse_y", 0, raising=False)
    monkeypatch.setattr(
        pyxel,
        "btn",
        lambda k: state["down"] if k == pyxel.MOUSE_BUTTON_LEFT else False,
    )
    monkeypatch.setattr(
        pyxel,
        "btnp",
        lambda k, *a, **kw: state["pressed"] if k == pyxel.MOUSE_BUTTON_LEFT else False,
    )
    monkeypatch.setattr(pyxel, "btnv", lambda k: 0)

    tc = TouchControls()
    sys = PlayerAnchorSystem(touch_controls=tc)

    # Caso 1: Multi-touch real (Dedo 1 segurando D-Pad Direita + Dedo 2 tocando SALTO)
    state["down"] = True
    state["pressed"] = False
    monkeypatch.setattr(pyxel, "mouse_x", 64, raising=False)   # dentro de rect_right
    monkeypatch.setattr(pyxel, "mouse_y", 136, raising=False)
    tc.extra_touches = [(280.0, 150.0)]  # segundo dedo dentro de rect_jump

    tc.update()
    assert tc.btn_right is True
    assert tc.btnp_jump is True

    sys.update()
    assert sys.state == STATE_AIRBORNE
    assert sys.vx >= DIRECTIONAL_JUMP_VX

    # Caso 2: Mesmo quando o navegador move o ponteiro único do D-Pad Esquerda para SALTO
    tc.extra_touches = []
    tc._prev_jump = False
    sys.reset()

    # Frame 1: Segurando D-Pad Esquerda
    monkeypatch.setattr(pyxel, "mouse_x", 18, raising=False)   # dentro de rect_left
    monkeypatch.setattr(pyxel, "mouse_y", 136, raising=False)
    state["down"] = True
    tc.update()
    sys.update()
    assert tc.btn_left is True

    # Frame 2: Segundo polegar toca em SALTO e o navegador desloca mouse_x/mouse_y para rect_jump
    monkeypatch.setattr(pyxel, "mouse_x", 280, raising=False)  # dentro de rect_jump
    monkeypatch.setattr(pyxel, "mouse_y", 150, raising=False)
    tc.update()
    assert tc.btn_left is True
    assert tc.btnp_jump is True

    # Mesmo que angular_vel tenha zerado no pico do balanço, saltar segurando esquerda impulsiona para a esquerda
    sys.angular_vel = 0.0
    sys.update()
    assert sys.state == STATE_AIRBORNE
    assert sys.vx <= -DIRECTIONAL_JUMP_VX

