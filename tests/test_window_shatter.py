import pytest

import hazard_spawner as hs
from building_generator import (
    BuildingGenerator,
    Window,
    SHATTER_ANIM_FRAMES,
    WINDOW_STATE_BROKEN,
    WINDOW_STATE_CLEAN,
    WINDOW_STATE_DIRTY,
)
from hazard_spawner import HazardSpawner
from stray_bullet import PHASE_FLYING, StrayBullet


class DummyAnchorSystem:
    def __init__(self):
        self.angular_vel = 0.0
        self.vx = 0.0


class DummyPlayer:
    """Jogador posicionado longe da trajetória das balas de teste."""

    def __init__(self, x: float = -500.0, y: float = -500.0):
        self.x = x
        self.y = y
        self.anchor_system = DummyAnchorSystem()


class DummyStats:
    is_game_over = False

    def take_damage(self, amount: int) -> bool:
        return True


class DummyCleaningSystem:
    def __init__(self):
        self.popups = []

    def interrupt_by_damage(self):
        pass


def _clean_window(x=60.0, y=100.0) -> Window:
    return Window(x=x, y=y, w=32, h=24, col=0, floor=5, initial_state=WINDOW_STATE_CLEAN)


def _flying_bullet_at(x: float, y: float) -> StrayBullet:
    bullet = StrayBullet(start_x=x, start_y=y, target_x=x + 100, target_y=y, telegraph_duration=0)
    bullet.phase = PHASE_FLYING
    return bullet


def _spawner_with_one_window(win: Window):
    spawner = HazardSpawner()
    spawner.spawn_timer = 10_000  # sem novas balas aleatórias
    spawner.drone_manager.drones.clear()
    building = BuildingGenerator()
    building.windows = [win]
    return spawner, building


# ---------------------------------------------------------------- Window


def test_shatter_turns_clean_window_into_broken():
    win = _clean_window()
    assert win.shatter() is True
    assert win.state == WINDOW_STATE_BROKEN
    assert win.work_frames == 0.0
    assert win.shatter_timer == SHATTER_ANIM_FRAMES


@pytest.mark.parametrize("state", [WINDOW_STATE_DIRTY, WINDOW_STATE_BROKEN])
def test_shatter_ignores_non_clean_windows(state):
    win = Window(x=0, y=0, w=32, h=24, col=0, floor=0, initial_state=state)
    win.work_frames = 10.0
    assert win.shatter() is False
    assert win.state == state
    assert win.work_frames == 10.0
    assert win.shatter_timer == 0


def test_find_window_at():
    building = BuildingGenerator()
    win = building.windows[10]
    assert building.find_window_at(win.x + 5, win.y + 5) is win
    assert building.find_window_at(-100.0, -100.0) is None


# ---------------------------------------------------------------- Spawner


def test_bullet_shatters_clean_window_when_chance_hits(monkeypatch):
    monkeypatch.setattr(hs, "BULLET_WINDOW_BREAK_CHANCE", 1.0)
    win = _clean_window()
    spawner, building = _spawner_with_one_window(win)
    cleaning = DummyCleaningSystem()
    spawner.bullets = [_flying_bullet_at(win.x + 2, win.y + 12)]

    spawner.update(DummyPlayer(), DummyStats(), cleaning, 0.0, 0.0, building=building)

    assert win.state == WINDOW_STATE_BROKEN
    assert len(spawner.sparks) >= 10
    assert any(p.text == "VIDRO!" for p in cleaning.popups)
    # A bala continua voando após estilhaçar o vidro
    assert len(spawner.bullets) == 1


def test_bullet_rolls_only_once_and_misses_when_chance_zero(monkeypatch):
    monkeypatch.setattr(hs, "BULLET_WINDOW_BREAK_CHANCE", 0.0)
    win = _clean_window()
    spawner, building = _spawner_with_one_window(win)
    bullet = _flying_bullet_at(win.x + 2, win.y + 12)
    spawner.bullets = [bullet]

    spawner.update(DummyPlayer(), DummyStats(), DummyCleaningSystem(), 0.0, 0.0, building=building)

    assert win.state == WINDOW_STATE_CLEAN
    assert bullet.glass_rolled is True


def test_bullet_that_already_rolled_never_shatters(monkeypatch):
    monkeypatch.setattr(hs, "BULLET_WINDOW_BREAK_CHANCE", 1.0)
    win = _clean_window()
    spawner, building = _spawner_with_one_window(win)
    bullet = _flying_bullet_at(win.x + 2, win.y + 12)
    bullet.glass_rolled = True
    spawner.bullets = [bullet]

    spawner.update(DummyPlayer(), DummyStats(), DummyCleaningSystem(), 0.0, 0.0, building=building)

    assert win.state == WINDOW_STATE_CLEAN


def test_update_without_building_is_backwards_compatible():
    spawner = HazardSpawner()
    spawner.bullets = [_flying_bullet_at(100.0, 100.0)]
    spawner.update(DummyPlayer(), DummyStats(), DummyCleaningSystem(), 0.0, 0.0)
    assert spawner.bullets[0].glass_rolled is False


def test_break_chance_is_low():
    assert 0.0 < hs.BULLET_WINDOW_BREAK_CHANCE <= 0.10
