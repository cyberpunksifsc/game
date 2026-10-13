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
        if (
            pyxel.btnp(pyxel.KEY_Q)
            or pyxel.btnp(pyxel.KEY_SPACE)
            or pyxel.btnp(pyxel.KEY_RETURN)
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
            or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)
        ):
            return STATE_GAMEPLAY
        return None

    def draw(self):
        pyxel.camera(0, 0)

        pyxel.blt(0, 0, 0, 0, 0, 256, 180)
        pyxel.blt(256, 0, 1, 0, 0, 64, 180)

        # Letreiro do Título
        pyxel.text(self.app.WIDTH // 2 - 26, self.app.HEIGHT // 2 - 24, "APEX GRAPPLER", 11)
        pyxel.text(self.app.WIDTH // 2 - 40, self.app.HEIGHT // 2 - 14, "OPERACAO VERTICAL", 7)

        # Botão / Caixa de Início adaptada para Touch (celulares) e Teclado/Mouse (Desktop)
        bw = 144
        bh = 22
        bx = (self.app.WIDTH - bw) // 2
        by = self.app.HEIGHT // 2 + 10

        pulse = (pyxel.frame_count // 15) % 2
        border_col = 11 if pulse else 12

        pyxel.rect(bx, by, bw, bh, 0)
        pyxel.rectb(bx, by, bw, bh, border_col)
        pyxel.text(bx + 14, by + 5, "[ TOQUE PARA INICIAR ]", 11 if pulse else 7)
        pyxel.text(bx + 10, by + 13, "OU ESPACO / ENTER / CLIQUE", 6)
        
        