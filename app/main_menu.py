import pyxel
from constants import STATE_MAIN_MENU, STATE_GAMEPLAY

class MainMenu:
    def __init__(self, app):
        self.app = app
        self.carregar_recursos()

    def carregar_recursos(self):
        pyxel.images[0].load(0, 0, "../resources.pyxres")
        
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            return STATE_GAMEPLAY
        return None
    
    def draw(self):
        pyxel.camera(0, 0)

        pyxel.blt(0, 0, 0, 0, 0, 256, 180)
        pyxel.blt(256, 0, 1, 0, 0, 64, 180)
        
        pyxel.text(self.app.WIDTH / 2 - 10, self.app.HEIGHT / 2, "Teste", 7)
    
        pyxel.text(self.app.WIDTH/2 - 28, self.app.HEIGHT/2 + 10, "Start the Game", 7)
        
        