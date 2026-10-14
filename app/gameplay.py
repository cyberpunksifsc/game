from pathlib import Path
import pyxel
from player import Player
from building_generator import BuildingGenerator
from player_cleaning_system import PlayerCleaningSystem
from player_anchor_system import STATE_FATAL_FALL
from player_health_and_score import PlayerHealthAndScore, REASON_FALL

STATE_PLAYING = "PLAYING"
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Som de alarme corporativo (definido em PlayerAnchorSystem.init_sounds)
SOUND_GAME_OVER_ALARM = 5


class Gameplay:
    def __init__(self, app):
        self.app = app
        self.camera_x = 0.0
        self.camera_y = 0.0

        # Gerador da fachada do arranha-céu Apex-01
        self.building = BuildingGenerator()

        # Jogador inicia na base térrea (meio da base: x=160, y=1800)
        self.player = Player(self.app, anchor_x=160, anchor_y=1800, rope_length=50)

        # HP, barra de Eficiência Corporativa, pontuação e condições de game over
        self.stats = PlayerHealthAndScore()

        # Sistema de limpeza e conserto de janelas (acionado com [E])
        self.cleaning_system = PlayerCleaningSystem(self.player, self.building, self.stats)

    def enter(self):
        """Chamado toda vez que o app entra no estado GAMEPLAY."""
        self.carregar_recursos()
        self.start_new_run()

    def start_new_run(self):
        """Reinicia a partida inteira: posição, pontuação, HP, barra e janelas do prédio."""
        self.player.anchor_system.reset()
        self.building.generate()
        self.cleaning_system.reset()
        self.stats.reset()
        self.recenter_camera()

    def recenter_camera(self):
        """Centraliza a câmera na posição do jogador."""
        self.camera_x = (self.player.x + 16) - self.app.WIDTH / 2
        self.camera_y = (self.player.y + 16) - self.app.HEIGHT / 2

    def carregar_recursos(self):
        resource_file = BASE_DIR / "resources.pyxres"
        if resource_file.exists():
            pyxel.load(str(resource_file))

        bg_image = ROOT_DIR / "assets" / "BackGround" / "city1" / "1.png"
        if bg_image.exists():
            pyxel.images[1].load(0, 0, str(bg_image))

        # Carrega o spritesheet do personagem no banco 2
        self.player.carregar_recursos()

    def _retry_pressed(self) -> bool:
        """Comando de retentar após Game Over (teclado, toque, mouse ou gamepad)."""
        touch = self.player.touch_controls
        touch_on_ui = touch.is_touching_ui(pyxel.mouse_x, pyxel.mouse_y)
        return (
            pyxel.btnp(pyxel.KEY_R)
            or pyxel.btnp(pyxel.KEY_SPACE)
            or (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and not touch_on_ui)
            or touch.btnp_jump
            or touch.btnp_clean
            or touch.btnp_retrieve
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)
        )

    def update(self):
        # Game Over: congela a simulação e aguarda o comando de retentar
        if self.stats.is_game_over:
            self.stats.update(is_idle=False)
            self.player.touch_controls.update()
            if self.stats.can_retry and self._retry_pressed():
                self.start_new_run()
            return

        # Atualiza o sistema de limpeza e reparo de janelas
        self.cleaning_system.update()

        # Estabiliza o alpinista se estiver ativamente limpando/reparando
        self.player.anchor_system.is_working = self.cleaning_system.is_cleaning

        # Atualiza a movimentação e âncoras considerando a posição atual da câmera
        self.player.update(self.camera_x, self.camera_y)

        # Condição 1 de Game Over: queda fatal (o alarme já é tocado pelo sistema de âncoras)
        if self.player.state == STATE_FATAL_FALL:
            self.stats.trigger_game_over(REASON_FALL)
            return

        # Barra corporativa cai mais rápido se o jogador estiver parado e sem trabalhar.
        # Condições 2 (HP) e 3 (desempenho) são disparadas dentro do sistema de stats.
        is_idle = self.player.anchor_system.is_idle and not self.cleaning_system.is_cleaning
        self.stats.update(is_idle=is_idle)
        if self.stats.is_game_over:
            try:
                pyxel.play(0, SOUND_GAME_OVER_ALARM)
            except BaseException:
                pass
            self.cleaning_system.is_cleaning = False
            return

        # Acompanhamento suave da câmera (lerp)
        target_x = (self.player.x + 16) - self.app.WIDTH / 2
        target_y = (self.player.y + 16) - self.app.HEIGHT / 2
        self.camera_x += (target_x - self.camera_x) * 0.12
        self.camera_y += (target_y - self.camera_y) * 0.12

    def draw_background(self):
        """Desenha o skyline de New Tokyo no fundo com efeito de paralaxe."""
        offset_x = int(-self.camera_x * 0.15) % 256
        offset_y = int(-self.camera_y * 0.15) % 180

        pyxel.camera(0, 0)
        for bx in (-256, 0, 256):
            for by in (-180, 0, 180):
                x = offset_x + bx
                y = offset_y + by
                if x < self.app.WIDTH and x + 256 > 0 and y < self.app.HEIGHT and y + 180 > 0:
                    pyxel.blt(x, y, 1, 0, 0, 256, 180)

    def draw(self):
        pyxel.cls(0)

        # 1. Fundo da cidade com paralaxe
        self.draw_background()

        # 2. Fachada do prédio com vigas, janelas e base (coordenadas de mundo)
        pyxel.camera(int(self.camera_x), int(self.camera_y))
        self.building.draw(self.camera_x, self.camera_y, target_window=self.cleaning_system.target_window)

        # 3. Partículas e feixes de limpeza/solda
        self.cleaning_system.draw_world(self.camera_x, self.camera_y)

        # 4. Jogador, âncoras, mira e HUD de movimentação
        self.player.draw(self.camera_x, self.camera_y, game_over=self.stats.is_game_over)

        # 5. HUD de limpeza e prompts de ação
        pyxel.camera(0, 0)
        self.cleaning_system.draw_hud(self.app.WIDTH, self.app.HEIGHT)

        # 6. HUD de vida, barra de desempenho corporativo e tela de game over
        self.stats.draw_hud(self.app.WIDTH, self.app.HEIGHT)
