import pytest

from audio_manager import (
    AudioManager,
    SOUND_BGM_LOW,
    SOUND_BGM_MENU,
    SOUND_GAME_OVER_STING,
)
from building_generator import BuildingGenerator, SHATTER_ANIM_FRAMES
from player_anchor_system import (
    FACADE_APEX_Y,
    FACADE_BASE_Y,
    FACADE_MAX_X,
    FACADE_MIN_X,
    FATAL_FALL_BELOW_ANCHOR,
    PlayerAnchorSystem,
    STATE_AIRBORNE,
    STATE_FATAL_FALL,
)


def test_lazy_audio_loads_only_requested_slot_on_demand(monkeypatch):
    import pyxel

    pcm_loaded = []

    class DummySound:
        def __init__(self, slot):
            self.slot = slot

        def pcm(self, path):
            pcm_loaded.append(self.slot)

    class DummyChannel:
        gain = 0.45

    monkeypatch.setattr(pyxel, "sounds", [DummySound(i) for i in range(64)])
    monkeypatch.setattr(pyxel, "channels", [DummyChannel() for _ in range(4)])
    monkeypatch.setattr(pyxel, "play", lambda *a, **k: None)
    monkeypatch.setattr(pyxel, "btnp", lambda *a, **k: False)

    audio = AudioManager(auto_load=False, lazy_load=True)
    assert pcm_loaded == []

    # Tocar música do menu carrega apenas o slot 50
    audio.play_menu_bgm()
    assert pcm_loaded == [SOUND_BGM_MENU]

    # Entrar no setor baixo carrega apenas o slot 51
    audio.update_gameplay_bgm(1800.0, is_game_over=False)
    assert pcm_loaded == [SOUND_BGM_MENU, SOUND_BGM_LOW]

    # Game Over sting é .ogg enxuto (< 100 KB)
    sting_path = audio.get_track_path(SOUND_GAME_OVER_STING)
    assert sting_path.suffix == ".ogg"
    assert sting_path.stat().st_size < 100_000


def test_building_spatial_lookup_and_update_timers():
    building = BuildingGenerator()
    for win in building.windows:
        cx = win.x + win.w / 2
        cy = win.y + win.h / 2
        assert building.find_window_at(cx, cy) is win

    # Verifica que shatter_timer avança no update() sem depender de draw()
    clean_win = next(w for w in building.windows if w.state == "CLEAN")
    assert clean_win.shatter() is True
    assert clean_win.shatter_timer == SHATTER_ANIM_FRAMES
    building.update(target_window=clean_win)
    assert clean_win.shatter_timer == SHATTER_ANIM_FRAMES - 1


def test_plant_anchor_rejects_points_outside_facade():
    sys = PlayerAnchorSystem(start_anchor_x=60, start_anchor_y=680, initial_rope_length=30)
    # No céu à esquerda da fachada (x < FACADE_MIN_X) Within range
    assert sys.plant_anchor(FACADE_MIN_X - 10, 690) is False
    # Acima do teto Apex (y < FACADE_APEX_Y) Within range
    assert sys.plant_anchor(60, FACADE_APEX_Y - 15) is False
    # Dentro da fachada e dentro do alcance: válido
    assert sys.plant_anchor(90, 680) is True
    assert sys.is_valid_facade_point(FACADE_MAX_X, FACADE_BASE_Y) is True


def test_fatal_fall_triggers_promptly_below_lowest_anchor(monkeypatch):
    import pyxel

    monkeypatch.setattr(pyxel, "btn", lambda k: False)
    monkeypatch.setattr(pyxel, "btnp", lambda k: False)
    monkeypatch.setattr(pyxel, "mouse_x", 160, raising=False)
    monkeypatch.setattr(pyxel, "mouse_y", 90, raising=False)

    sys = PlayerAnchorSystem(start_anchor_x=160, start_anchor_y=1200, initial_rope_length=50)
    sys.jump()
    assert sys.state == STATE_AIRBORNE

    # Mesmo que a câmera acompanhe o jogador na queda, passar de lowest_anchor_y + FATAL_FALL_BELOW_ANCHOR dispara queda fatal
    sys.y = 1200.0 + FATAL_FALL_BELOW_ANCHOR + 5.0
    sys.update(camera_x=0.0, camera_y=sys.y - 90.0, screen_height=180.0)
    assert sys.state == STATE_FATAL_FALL
