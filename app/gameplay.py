from pathlib import Path
import pyxel
from player import Player
from building_generator import BuildingGenerator
from player_cleaning_system import PlayerCleaningSystem

STATE_PLAYING = "PLAYING"
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent


class Gameplay:
    def __init__(self, app):
        self.app = app
        self.camera_x = 0.0
        self.camera_y = 0.0

        # Gerador da fachada do arranha-céu Apex-01
        self.building = BuildingGenerator()

        # Jogador inicia na base térrea (meio da base: x=160, y=1800)
        self.player = Player(self.app, anchor_x=160, anchor_y=1800, rope_length=50)

        # Sistema de limpeza e conserto de janelas (acionado com [E])
        self.cleaning_system = PlayerCleaningSystem(self.player, self.building)

    def enter(self):
        """Chamado toda vez que o app entra no estado GAMEPLAY."""
        self.carregar_recursos()
        self.player.anchor_system.reset()
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

    def update(self):
        was_fatal = (self.player.state == "FATAL_FALL")

        # Atualiza o sistema de limpeza e reparo de janelas
        self.cleaning_system.update()

        # Estabiliza o alpinista se estiver ativamente limpando/reparando
        self.player.anchor_system.is_working = self.cleaning_system.is_cleaning

        # Atualiza a movimentação e âncoras considerando a posição atual da câmera
        self.player.update(self.camera_x, self.camera_y)

        # Se reiniciou após uma queda fatal, recentraliza a câmera imediatamente
        if was_fatal and self.player.state != "FATAL_FALL":
            self.recenter_camera()
            return

        # Acompanhamento suave da câmera (lerp)
        if self.player.state != "FATAL_FALL":
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
        self.player.draw(self.camera_x, self.camera_y)

        # 5. HUD de limpeza e pontuação corporativa
        pyxel.camera(0, 0)
        self.cleaning_system.draw_hud(self.app.WIDTH, self.app.HEIGHT)
