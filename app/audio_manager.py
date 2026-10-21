from pathlib import Path
import pyxel

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
SOUNDTRACK_DIR = ROOT_DIR / "assets" / "Audio" / "SoundTrack"

# Canal dedicado exclusivamente à trilha sonora (canais 0, 1 e 2 ficam livres para SFX)
CHANNEL_BGM = 3
DEFAULT_BGM_VOLUME = 0.45

# Setores verticais da fachada do arranha-céu Apex-01
SECTOR_LOW = "SECTOR_LOW"    # Setor Baixo (Submundo/Base): player_y > 1200.0
SECTOR_MID = "SECTOR_MID"    # Setor Médio (Zona Industrial/Corporativa): 600.0 < player_y <= 1200.0
SECTOR_HIGH = "SECTOR_HIGH"  # Setor Alto (Ápice da Torre): player_y <= 600.0

SECTOR_LOW_THRESHOLD = 1200.0
SECTOR_MID_THRESHOLD = 600.0

# Slots de som Pyxel reservados para áudio PCM (50 a 54)
SOUND_BGM_MENU = 50
SOUND_BGM_LOW = 51
SOUND_BGM_MID = 52
SOUND_BGM_HIGH = 53
SOUND_GAME_OVER_STING = 54

TRACK_FILES: dict[int, str] = {
    SOUND_BGM_MENU: "DavidKBD - Electric Pulse - 01 - Electric Pulse-full.ogg",
    SOUND_BGM_LOW: "DavidKBD - Electric Pulse - 03 - Cyber Lights-full.ogg",
    SOUND_BGM_MID: "DavidKBD - Electric Pulse - 04 - Retrochrome Nights-full.ogg",
    SOUND_BGM_HIGH: "DavidKBD - Electric Pulse - 05 - Neon Arcadia Awakening-full.ogg",
    SOUND_GAME_OVER_STING: "DavidKBD - Electric Pulse - 10 - Synthetic Power Surge-short.wav",
}

SECTOR_TO_TRACK_SLOT: dict[str, int] = {
    SECTOR_LOW: SOUND_BGM_LOW,
    SECTOR_MID: SOUND_BGM_MID,
    SECTOR_HIGH: SOUND_BGM_HIGH,
}


class AudioManager:
    """Gerencia a trilha sonora dinâmica por setor de altitude usando o suporte
    nativo a PCM (OGG/WAV) do Pyxel 2.9.9 no Canal 3, preservando os canais 0, 1 e 2
    para os efeitos sonoros procedurais (SFX).
    """

    def __init__(
        self,
        volume: float = DEFAULT_BGM_VOLUME,
        soundtrack_dir: Path | None = None,
        auto_load: bool = True,
    ):
        self.soundtrack_dir: Path = Path(soundtrack_dir) if soundtrack_dir is not None else SOUNDTRACK_DIR
        self.track_paths: dict[int, Path] = {
            slot: self.soundtrack_dir / filename
            for slot, filename in TRACK_FILES.items()
        }

        self.muted: bool = False
        self.volume: float = max(0.0, min(1.0, float(volume)))

        self.current_sector: str | None = None
        self.current_track_slot: int | None = None
        self.current_loop: bool = True
        self.game_over_sting_played: bool = False
        self.tracks_loaded: dict[int, bool] = {}

        if auto_load:
            self.load_tracks()

    def get_track_path(self, slot: int) -> Path:
        """Retorna o caminho completo do arquivo de áudio associado ao slot."""
        return self.track_paths[slot]

    def load_tracks(self) -> dict[int, bool]:
        """Carrega os arquivos OGG/WAV nos slots PCM do Pyxel (50 a 54) e ajusta
        o ganho do canal de BGM. Captura BaseException caso o Pyxel não esteja
        inicializado.
        """
        try:
            pyxel.channels[CHANNEL_BGM].gain = self.volume
        except BaseException:
            pass

        loaded: dict[int, bool] = {}
        for slot, filepath in self.track_paths.items():
            if not filepath.exists():
                loaded[slot] = False
                continue
            try:
                pyxel.sounds[slot].pcm(str(filepath))
                loaded[slot] = True
            except BaseException:
                loaded[slot] = False

        self.tracks_loaded = dict(loaded)
        return loaded

    def get_sector_for_y(self, player_y: float) -> str:
        """Determina o setor vertical do arranha-céu com base na coordenada Y do jogador."""
        y = float(player_y)
        if y > SECTOR_LOW_THRESHOLD:
            return SECTOR_LOW
        if y > SECTOR_MID_THRESHOLD:
            return SECTOR_MID
        return SECTOR_HIGH

    def get_track_slot_for_sector(self, sector: str) -> int:
        """Retorna o slot de som correspondente ao setor informado."""
        return SECTOR_TO_TRACK_SLOT.get(sector, SOUND_BGM_LOW)

    def _play_on_bgm_channel(self, slot: int, loop: bool) -> None:
        """Executa o slot informado no Canal 3 caso não esteja em mute."""
        if self.muted:
            return
        try:
            pyxel.channels[CHANNEL_BGM].gain = self.volume
        except BaseException:
            pass
        try:
            pyxel.play(CHANNEL_BGM, slot, loop=loop)
        except BaseException:
            pass

    def play_menu_bgm(self) -> None:
        """Inicia a música tema do Menu Principal em loop se ainda não estiver tocando."""
        self.current_sector = None
        self.game_over_sting_played = False

        if self.current_track_slot == SOUND_BGM_MENU:
            return

        self.current_track_slot = SOUND_BGM_MENU
        self.current_loop = True
        self._play_on_bgm_channel(SOUND_BGM_MENU, loop=True)

    def play_game_over_sting(self) -> None:
        """Dispara o sting curto de Game Over (sem loop) apenas uma vez por derrota."""
        if self.game_over_sting_played:
            return

        self.game_over_sting_played = True
        self.current_sector = None
        self.current_track_slot = SOUND_GAME_OVER_STING
        self.current_loop = False
        self._play_on_bgm_channel(SOUND_GAME_OVER_STING, loop=False)

    def update_gameplay_bgm(self, player_y: float, is_game_over: bool = False) -> None:
        """Atualiza a trilha sonora durante a partida conforme a altitude do alpinista,
        o estado de Game Over e o comando de mute [M].
        """
        mute_pressed = False
        try:
            mute_pressed = bool(pyxel.btnp(pyxel.KEY_M))
        except BaseException:
            mute_pressed = False

        if mute_pressed:
            self.toggle_mute()

        if is_game_over:
            self.play_game_over_sting()
            return

        # Se uma nova partida começou após um Game Over, libera o sting para o futuro
        self.game_over_sting_played = False

        sector = self.get_sector_for_y(player_y)
        slot = self.get_track_slot_for_sector(sector)

        if sector != self.current_sector or self.current_track_slot != slot:
            self.current_sector = sector
            self.current_track_slot = slot
            self.current_loop = True
            self._play_on_bgm_channel(slot, loop=True)

    def toggle_mute(self) -> bool:
        """Alterna o estado de mute da trilha sonora, interrompendo ou retomando o Canal 3."""
        self.muted = not self.muted
        if self.muted:
            try:
                pyxel.stop(CHANNEL_BGM)
            except BaseException:
                pass
        else:
            try:
                pyxel.channels[CHANNEL_BGM].gain = self.volume
            except BaseException:
                pass
            if self.current_track_slot is not None:
                try:
                    pyxel.play(CHANNEL_BGM, self.current_track_slot, loop=self.current_loop)
                except BaseException:
                    pass
        return self.muted

    def set_volume(self, gain: float) -> float:
        """Define o volume (gain) do canal de BGM limitado ao intervalo [0.0, 1.0]."""
        self.volume = max(0.0, min(1.0, float(gain)))
        try:
            pyxel.channels[CHANNEL_BGM].gain = self.volume
        except BaseException:
            pass
        return self.volume
