import pyxel

STATE_INTRO = "INTRO"
STATE_PLAYING = "PLAYING"  # renomeado pra não colidir mentalmente com o STATE_GAMEPLAY do app

class Gameplay:
    def __init__(self, app):
        self.app = app
        self.state = STATE_INTRO
        self.camera_y = 0

    def enter(self):
        """Chamado toda vez que o app entra no estado GAMEPLAY."""
        self.state = STATE_INTRO
        self.camera_y = 0

    def update(self):
        if self.state == STATE_INTRO:
            self.camera_y += 2
            if self.camera_y >= 160:
                self.camera_y = 160
                self.state = STATE_PLAYING
        elif self.state == STATE_PLAYING:
            pass  # aqui entra a lógica real do jogo

        return None  # gameplay ainda não devolve nenhuma troca de STATE do app

    def draw(self):
        pyxel.cls(0)
        pyxel.camera(0, self.camera_y)
        pyxel.blt(0, 0, 0, 0, 0, 256, 256)     # topo do prédio (banco 0)
        pyxel.blt(0, 256, 1, 0, 0, 256, 68)    # continuação embaixo (banco 1)