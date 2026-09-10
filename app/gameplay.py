import pyxel

STATE_PLAYING = "PLAYING"  # renomeado pra não colidir mentalmente com o STATE_GAMEPLAY do app

class Gameplay:
    def __init__(self, app):
        self.app = app
        self.camera_y = 0

        self.carregar_recursos()

        print(self.app.WIDTH)
        print(self.app.HEIGHT)

    def enter(self):
        """Chamado toda vez que o app entra no estado GAMEPLAY."""
        self.camera_y = 0

    def carregar_recursos(self):
        pyxel.images[1].load(0, 0, "../assets/BackGround/city1/1.png")
        pyxel.load("../resources.pyxres")

    def update(self):
        pass

    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, 40, 25)