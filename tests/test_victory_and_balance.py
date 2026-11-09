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


def test_building_has_28_floors():
    building = BuildingGenerator()
    total_floors = int((building.base_y - 40 - building.apex_y) // building.floor_height)
    assert total_floors == 28
    assert len(building.windows) == 28 * 4
    assert building.apex_y == pytest.approx(APEX_ALTITUDE_Y)


def test_drones_all_within_28_floor_building_span():
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

    # Dreno da barra de Eficiência Corporativa 20% menor que o antigo (1 / (60 * 30))
    old_drain = 1.0 / (60.0 * FPS)
    assert EFFICIENCY_FULL_DRAIN_SECONDS == pytest.approx(75.0)
    assert EFFICIENCY_BASE_DRAIN == pytest.approx(old_drain * 0.80)


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
