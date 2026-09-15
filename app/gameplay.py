from pathlib import Path
import pyxel
from player import Player

STATE_PLAYING = "PLAYING"  # renomeado pra não colidir mentalmente com o STATE_GAMEPLAY do app
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

class Gameplay:
    def __init__(self, app):
        self.app = app
        self.camera_y = 0
        self.player = Player(self.app)

        print(self.app.WIDTH)
        print(self.app.HEIGHT)

    def enter(self):
        """Chamado toda vez que o app entra no estado GAMEPLAY."""
        self.camera_y = 0
        self.carregar_recursos()

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
        self.player.update()

    def draw(self):
        pyxel.cls(0)
        pyxel.camera(0, 0)
        pyxel.bltm(0, 0, 0, 0, 0, self.app.WIDTH, self.app.HEIGHT)
        self.player.draw()

