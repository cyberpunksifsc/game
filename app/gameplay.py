from pathlib import Path
import pyxel
from player import Player

STATE_PLAYING = "PLAYING"  # renomeado pra não colidir mentalmente com o STATE_GAMEPLAY do app
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

class Gameplay:
    def __init__(self, app):
        self.app = app
        self.camera_x = 0.0
        self.camera_y = 0.0
        self.player = Player(self.app)

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

        # 2. Fachada do prédio / Tilemap (em coordenadas de mundo)
        pyxel.camera(int(self.camera_x), int(self.camera_y))
        pyxel.bltm(0, 0, 0, 0, 0, 2048, 2048, 0)

        # 3. Jogador, âncoras, mira e HUD
        self.player.draw(self.camera_x, self.camera_y)


