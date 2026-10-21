import pytest
import pyxel
from powerup_system import (
    PowerUpSystem,
    POWERUP_NONE,
    POWERUP_SHIELD,
    POWERUP_TURBO,
    POWERUP_STABILIZER,
    POWERUP_ORDER,
)
from building_generator import (
    Window,
    BuildingGenerator,
    WINDOW_STATE_CLEAN,
    WINDOW_STATE_DIRTY,
    WINDOW_STATE_BROKEN,
)
from player_health_and_score import PlayerHealthAndScore
from player_cleaning_system import PlayerCleaningSystem
from player_anchor_system import STATE_ANCHORED
from main_menu import MainMenu
from constants import STATE_GAMEPLAY


class DummyAnchorSystem:
    def __init__(self, hx=120.0, hy=1820.0):
        self.hx = hx
        self.hy = hy
        self.state = STATE_ANCHORED
        self.angular_vel = 0.0
        self.angle = 0.0
        self.camera_x = 0.0
        self.camera_y = 0.0

    def get_harness_pos(self):
        return self.hx, self.hy


class DummyPlayer:
    def __init__(self, hx=120.0, hy=1820.0):
        self.anchor_system = DummyAnchorSystem(hx, hy)
        self.touch_controls = None


def test_powerup_selection_and_cycling():
    ps = PowerUpSystem()
    assert ps.selected_powerup == POWERUP_NONE
    assert ps.work_speed_multiplier == 1.0
    assert ps.efficiency_drain_multiplier == 1.0
    assert ps.score_multiplier == 1.0
    assert not ps.has_active_shield

    # Cycle forward through all 4 options
    assert ps.cycle_selection(1) == POWERUP_SHIELD
    assert ps.has_active_shield
    assert ps.cycle_selection(1) == POWERUP_TURBO
    assert not ps.has_active_shield
    assert ps.work_speed_multiplier == 1.5
    assert ps.cycle_selection(1) == POWERUP_STABILIZER
    assert ps.efficiency_drain_multiplier == 0.70
    assert ps.score_multiplier == 1.25
    assert ps.cycle_selection(1) == POWERUP_NONE

    # Cycle backward
    assert ps.cycle_selection(-1) == POWERUP_STABILIZER

    # Direct selection
    for pid in POWERUP_ORDER:
        assert ps.select_powerup(pid) == pid
        assert ps.selected_powerup == pid


def test_shield_absorbs_first_hit_and_recharges_on_reset():
    ps = PowerUpSystem(POWERUP_SHIELD)
    stats = PlayerHealthAndScore(powerup_system=ps)

    assert stats.hp == 3
    assert ps.has_active_shield

    # First hit is absorbed by the shield: returns False so cleaning isn't interrupted, HP stays 3
    damage_applied = stats.take_damage(1)
    assert damage_applied is False
    assert stats.hp == 3
    assert not ps.has_active_shield
    assert stats.invulnerable_timer == 20

    # Wait out brief shield invulnerability (20 frames)
    for _ in range(20):
        stats.update(is_idle=False)
    assert not stats.is_invulnerable

    # Second hit reduces HP to 2 and returns True
    damage_applied_2 = stats.take_damage(1)
    assert damage_applied_2 is True
    assert stats.hp == 2

    # Resetting stats for a new shift recharges the shield
    stats.reset()
    assert stats.hp == 3
    assert ps.has_active_shield


def test_turbo_squeegee_cleans_in_30_frames_and_repairs_in_70_frames(monkeypatch):
    monkeypatch.setattr(pyxel, "btn", lambda key: key == pyxel.KEY_E)
    monkeypatch.setattr(pyxel, "frame_count", 1, raising=False)

    ps = PowerUpSystem(POWERUP_TURBO)
    stats = PlayerHealthAndScore(powerup_system=ps)
    building = BuildingGenerator()

    # Locate a dirty window and place player over it
    dirty_win = next(w for w in building.windows if w.state == WINDOW_STATE_DIRTY)
    player = DummyPlayer(dirty_win.x + dirty_win.w / 2, dirty_win.y + dirty_win.h / 2)
    cleaning = PlayerCleaningSystem(player, building, stats)

    # After 29 frames (29 * 1.5 = 43.5 < 45), window is still dirty
    for _ in range(29):
        cleaning.update()
    assert dirty_win.state == WINDOW_STATE_DIRTY

    # Frame 30 completes cleaning (30 * 1.5 = 45.0)
    cleaning.update()
    assert dirty_win.state == WINDOW_STATE_CLEAN
    assert stats.windows_cleaned == 1

    # Now test repairing a broken window (105 frames required -> 70 frames at 1.5x speed)
    broken_win = next(w for w in building.windows if w.state == WINDOW_STATE_BROKEN)
    player.anchor_system.hx = broken_win.x + broken_win.w / 2
    player.anchor_system.hy = broken_win.y + broken_win.h / 2

    for _ in range(69):
        cleaning.update()
    assert broken_win.state == WINDOW_STATE_BROKEN

    cleaning.update()
    assert broken_win.state == WINDOW_STATE_CLEAN
    assert stats.windows_repaired == 1


def test_corp_stabilizer_reduces_drain_and_boosts_score():
    ps_none = PowerUpSystem(POWERUP_NONE)
    stats_none = PlayerHealthAndScore(powerup_system=ps_none)

    ps_stab = PowerUpSystem(POWERUP_STABILIZER)
    stats_stab = PlayerHealthAndScore(powerup_system=ps_stab)

    for _ in range(300):
        stats_none.update(is_idle=False)
        stats_stab.update(is_idle=False)

    drain_none = 1.0 - stats_none.efficiency
    drain_stab = 1.0 - stats_stab.efficiency
    assert pytest.approx(drain_stab, rel=1e-5) == drain_none * 0.70

    # Score multiplier: 100 * 1.25 = 125 for cleaning, int(250 * 1.25) = 312 for repairing
    pts_clean = stats_stab.register_window_completed("CLEANING")
    assert pts_clean == 125
    assert stats_stab.score == 125

    pts_repair = stats_stab.register_window_completed("REPAIRING")
    assert pts_repair == 312
    assert stats_stab.score == 125 + 312


def test_main_menu_powerup_card_click_does_not_start_game(monkeypatch):
    class DummyApp:
        WIDTH = 320
        HEIGHT = 180

    app = DummyApp()
    monkeypatch.setattr(MainMenu, "carregar_recursos", lambda self: None)
    menu = MainMenu(app)

    # Click inside the 2nd card (POWERUP_SHIELD)
    cards = menu.powerup_system.get_card_rects(app.WIDTH, app.HEIGHT)
    shield_pid, cx, cy, cw, ch = cards[1]
    assert shield_pid == POWERUP_SHIELD

    monkeypatch.setattr(pyxel, "mouse_x", cx + cw // 2, raising=False)
    monkeypatch.setattr(pyxel, "mouse_y", cy + ch // 2, raising=False)
    monkeypatch.setattr(pyxel, "btnp", lambda key: key == pyxel.MOUSE_BUTTON_LEFT)

    new_state = menu.update()
    assert new_state is None
    assert menu.powerup_system.selected_powerup == POWERUP_SHIELD

    # Clicking outside the cards (e.g., on the Start button) starts gameplay
    monkeypatch.setattr(pyxel, "mouse_x", 160, raising=False)
    monkeypatch.setattr(pyxel, "mouse_y", 90, raising=False)
    assert menu.update() == STATE_GAMEPLAY
