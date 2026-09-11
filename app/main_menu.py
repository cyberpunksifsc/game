from pathlib import Path
import pyxel
from constants import STATE_MAIN_MENU, STATE_GAMEPLAY

ROOT_DIR = Path(__file__).resolve().parent.parent

class MainMenu:
    def __init__(self, app):
        self.app = app
        self.carregar_recursos()

    def enter(self):
        self.carregar_recursos()

    def carregar_recursos(self):
        bg_left = ROOT_DIR / "assets" / "BackGround" / "city1" / "bg_left.png"
        bg_right = ROOT_DIR / "assets" / "BackGround" / "city1" / "bg_right.png"
        if bg_left.exists():
            pyxel.images[0].load(0, 0, str(bg_left))
        if bg_right.exists():
            pyxel.images[1].load(0, 0, str(bg_right))
        
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
        
        