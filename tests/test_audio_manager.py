from pathlib import Path
from unittest.mock import MagicMock
import pytest
import pyxel

from audio_manager import (
    AudioManager,
    CHANNEL_BGM,
    DEFAULT_BGM_VOLUME,
    SECTOR_HIGH,
    SECTOR_LOW,
    SECTOR_MID,
    SOUND_BGM_HIGH,
    SOUND_BGM_LOW,
    SOUND_BGM_MENU,
    SOUND_BGM_MID,
    SOUND_GAME_OVER_STING,
    TRACK_FILES,
)


@pytest.fixture
def mocked_pyxel_audio(monkeypatch):
    """Substitui llamadas de reprodução do Pyxel por mocks para testes rápidos e determinísticos."""
    play_calls: list[tuple[int, int, bool]] = []
    stop_calls: list[int] = []
    pcm_calls: dict[int, str] = {}
    key_m_pressed = {"value": False}

    class DummySound:
        def __init__(self, slot: int):
            self.slot = slot

        def pcm(self, filename: str):
            pcm_calls[self.slot] = filename

        def set(self, *args, **kwargs):
            pass

    class DummyChannel:
        def __init__(self):
            self.gain = 0.125

    dummy_sounds = [DummySound(i) for i in range(64)]
    dummy_channels = [DummyChannel() for _ in range(4)]

    def fake_play(ch: int, snd: int, sec: float = 0, loop: bool = False, resume: bool = False):
        play_calls.append((ch, snd, bool(loop)))

    def fake_stop(ch: int | None = None):
        stop_calls.append(-1 if ch is None else ch)

    def fake_btnp(key: int, *args, **kwargs) -> bool:
        if key == pyxel.KEY_M:
            return key_m_pressed["value"]
        return False

    monkeypatch.setattr(pyxel, "sounds", dummy_sounds)
    monkeypatch.setattr(pyxel, "channels", dummy_channels)
    monkeypatch.setattr(pyxel, "play", fake_play)
    monkeypatch.setattr(pyxel, "stop", fake_stop)
    monkeypatch.setattr(pyxel, "btnp", fake_btnp)

    return {
        "play_calls": play_calls,
        "stop_calls": stop_calls,
        "pcm_calls": pcm_calls,
        "channels": dummy_channels,
        "sounds": dummy_sounds,
        "key_m_pressed": key_m_pressed,
    }


def test_all_five_audio_files_exist_and_resolve(mocked_pyxel_audio):
    """Verifica se todos os 5 arquivos da trilha sonora existem em disco e são carregados nos slots 50..54."""
    audio = AudioManager()

    expected_slots = {
        SOUND_BGM_MENU,
        SOUND_BGM_LOW,
        SOUND_BGM_MID,
        SOUND_BGM_HIGH,
        SOUND_GAME_OVER_STING,
    }
    assert set(TRACK_FILES.keys()) == expected_slots
    assert set(audio.track_paths.keys()) == expected_slots

    for slot in expected_slots:
        path = audio.get_track_path(slot)
        assert isinstance(path, Path)
        assert path.exists(), f"Arquivo de áudio ausente para o slot {slot}: {path}"
        assert path.is_file()
        assert path.stat().st_size > 0
        assert audio.tracks_loaded[slot] is True
        assert mocked_pyxel_audio["pcm_calls"][slot] == str(path)

    assert pytest.approx(mocked_pyxel_audio["channels"][CHANNEL_BGM].gain) == DEFAULT_BGM_VOLUME


@pytest.mark.parametrize(
    ("player_y", "expected_sector", "expected_slot"),
    [
        (1800.0, SECTOR_LOW, SOUND_BGM_LOW),
        (1201.0, SECTOR_LOW, SOUND_BGM_LOW),
        (1200.0, SECTOR_MID, SOUND_BGM_MID),
        (601.0, SECTOR_MID, SOUND_BGM_MID),
        (600.0, SECTOR_HIGH, SOUND_BGM_HIGH),
        (100.0, SECTOR_HIGH, SOUND_BGM_HIGH),
    ],
)
def test_get_sector_for_y_boundaries(mocked_pyxel_audio, player_y, expected_sector, expected_slot):
    """Testa os limites exatos de altitude para os três setores verticais do prédio."""
    audio = AudioManager(auto_load=False)
    sector = audio.get_sector_for_y(player_y)
    assert sector == expected_sector
    assert audio.get_track_slot_for_sector(sector) == expected_slot


def test_track_transitions_and_no_redundant_restarts(mocked_pyxel_audio):
    """Verifica transições entre Menu, Setor Baixo, Médio, Alto e Game Over sem reiniciar a mesma faixa."""
    audio = AudioManager(auto_load=False)
    play_calls = mocked_pyxel_audio["play_calls"]

    # 1. Menu Principal: toca no Canal 3 em loop; chamadas subsequentes não reiniciam a faixa
    audio.play_menu_bgm()
    audio.play_menu_bgm()
    assert play_calls == [(CHANNEL_BGM, SOUND_BGM_MENU, True)]
    assert audio.current_track_slot == SOUND_BGM_MENU

    # 2. Entrada no Gameplay na base (y=1800 -> SECTOR_LOW)
    audio.update_gameplay_bgm(1800.0, is_game_over=False)
    assert play_calls[-1] == (CHANNEL_BGM, SOUND_BGM_LOW, True)
    assert len(play_calls) == 2

    # Permanecer no mesmo setor (ex: subindo de 1800 para 1201) não reinicia a música
    audio.update_gameplay_bgm(1500.0, is_game_over=False)
    audio.update_gameplay_bgm(1201.0, is_game_over=False)
    assert len(play_calls) == 2

    # 3. Transição para o Setor Médio (y=1200 -> SECTOR_MID)
    audio.update_gameplay_bgm(1200.0, is_game_over=False)
    assert play_calls[-1] == (CHANNEL_BGM, SOUND_BGM_MID, True)
    assert len(play_calls) == 3

    # Permanecer no Setor Médio (y=900, y=601) não reinicia
    audio.update_gameplay_bgm(900.0, is_game_over=False)
    audio.update_gameplay_bgm(601.0, is_game_over=False)
    assert len(play_calls) == 3

    # 4. Transição para o Setor Alto (y=600 -> SECTOR_HIGH)
    audio.update_gameplay_bgm(600.0, is_game_over=False)
    assert play_calls[-1] == (CHANNEL_BGM, SOUND_BGM_HIGH, True)
    assert len(play_calls) == 4

    # Permanecer no Setor Alto (y=100) não reinicia
    audio.update_gameplay_bgm(100.0, is_game_over=False)
    assert len(play_calls) == 4

    # 5. Game Over dispara o sting curto sem loop apenas uma única vez
    audio.update_gameplay_bgm(100.0, is_game_over=True)
    audio.update_gameplay_bgm(100.0, is_game_over=True)
    audio.play_game_over_sting()
    assert play_calls[-1] == (CHANNEL_BGM, SOUND_GAME_OVER_STING, False)
    assert len(play_calls) == 5

    # 6. Reiniciar a partida na base (y=1800, is_game_over=False) retoma a música do Setor Baixo
    audio.update_gameplay_bgm(1800.0, is_game_over=False)
    assert play_calls[-1] == (CHANNEL_BGM, SOUND_BGM_LOW, True)
    assert len(play_calls) == 6


def test_toggle_mute_and_volume_clamping(mocked_pyxel_audio):
    """Verifica o funcionamento do mute/unmute (incluindo tecla M) e a limitação de volume [0.0, 1.0]."""
    audio = AudioManager(auto_load=False)
    play_calls = mocked_pyxel_audio["play_calls"]
    stop_calls = mocked_pyxel_audio["stop_calls"]
    bgm_channel = mocked_pyxel_audio["channels"][CHANNEL_BGM]

    # Teste de clamping de volume: -0.5 -> 0.0, 1.5 -> 1.0, 0.6 -> 0.6
    assert audio.set_volume(-0.5) == 0.0
    assert bgm_channel.gain == 0.0

    assert audio.set_volume(1.5) == 1.0
    assert bgm_channel.gain == 1.0

    assert audio.set_volume(0.6) == pytest.approx(0.6)
    assert bgm_channel.gain == pytest.approx(0.6)

    # Inicia BGM do Setor Médio
    audio.update_gameplay_bgm(1000.0, is_game_over=False)
    assert play_calls == [(CHANNEL_BGM, SOUND_BGM_MID, True)]

    # Ativa mute: interrompe imediatamente o Canal 3
    assert audio.toggle_mute() is True
    assert audio.muted is True
    assert stop_calls == [CHANNEL_BGM]

    # Enquanto estiver em mute, mudar de setor atualiza o estado mas não chama pyxel.play
    audio.update_gameplay_bgm(400.0, is_game_over=False)
    assert audio.current_sector == SECTOR_HIGH
    assert audio.current_track_slot == SOUND_BGM_HIGH
    assert len(play_calls) == 1

    # Desativa mute via tecla [M] dentro de update_gameplay_bgm: retoma a faixa atual (SECTOR_HIGH)
    mocked_pyxel_audio["key_m_pressed"]["value"] = True
    audio.update_gameplay_bgm(400.0, is_game_over=False)
    mocked_pyxel_audio["key_m_pressed"]["value"] = False

    assert audio.muted is False
    assert play_calls[-1] == (CHANNEL_BGM, SOUND_BGM_HIGH, True)
    assert len(play_calls) == 2


def test_gameplay_and_main_menu_audio_integration(mocked_pyxel_audio):
    """Verifica a integração do AudioManager com MainMenu e Gameplay."""
    from main_menu import MainMenu
    from gameplay import Gameplay

    dummy_app = MagicMock()
    dummy_app.WIDTH = 320
    dummy_app.HEIGHT = 180
    dummy_app.audio = AudioManager(auto_load=False)

    menu = MainMenu(dummy_app)
    assert dummy_app.audio.current_track_slot == SOUND_BGM_MENU
    assert mocked_pyxel_audio["play_calls"][-1] == (CHANNEL_BGM, SOUND_BGM_MENU, True)

    gameplay = Gameplay(dummy_app)
    gameplay.start_new_run()
    assert dummy_app.audio.current_sector == SECTOR_LOW
    assert dummy_app.audio.current_track_slot == SOUND_BGM_LOW
    assert mocked_pyxel_audio["play_calls"][-1] == (CHANNEL_BGM, SOUND_BGM_LOW, True)
