from pathlib import Path
import pyxel
from constants import STATE_MAIN_MENU, STATE_GAMEPLAY
from audio_manager import AudioManager
from powerup_system import PowerUpSystem

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

class MainMenu:
    def __init__(self, app):
        self.app = app
        if not hasattr(self.app, "powerup_system") or self.app.powerup_system is None:
            self.app.powerup_system = PowerUpSystem()
        self.powerup_system = self.app.powerup_system
        self.audio = getattr(app, "audio", None) or AudioManager()
        self.show_tutorial = True
        self.carregar_recursos()
        self.audio.play_menu_bgm()

    def enter(self):
        self.carregar_recursos()
        self.audio.play_menu_bgm()

    @staticmethod
    def get_tutorial_open_button_rect(screen_w: int = 320, screen_h: int = 180) -> tuple[int, int, int, int]:
        """Retorna o retângulo (x, y, w, h) do botão de abrir o tutorial no Menu Principal."""
        bw = 144
        bh = 14
        bx = (screen_w - bw) // 2
        by = (screen_h // 2 - 6) + 22 + 4
        return (bx, by, bw, bh)

    @staticmethod
    def get_tutorial_close_button_rect(screen_w: int = 320, screen_h: int = 180) -> tuple[int, int, int, int]:
        """Retorna o retângulo (x, y, w, h) do botão de fechar a tela de tutorial."""
        bw = 212
        bh = 16
        bx = (screen_w - bw) // 2
        by = screen_h - 27
        return (bx, by, bw, bh)

    def is_tutorial_open_click(self, mx: float, my: float, screen_w: int = 320, screen_h: int = 180) -> bool:
        bx, by, bw, bh = self.get_tutorial_open_button_rect(screen_w, screen_h)
        return bx <= mx <= (bx + bw) and by <= my <= (by + bh)

    def is_tutorial_close_click(self, mx: float, my: float, screen_w: int = 320, screen_h: int = 180) -> bool:
        bx, by, bw, bh = self.get_tutorial_close_button_rect(screen_w, screen_h)
        return bx <= mx <= (bx + bw) and by <= my <= (by + bh)

    def carregar_recursos(self):
        try:
            for bg_left in (
                Path("assets/BackGround/city1/bg_left.png"),
                BASE_DIR / "assets" / "BackGround" / "city1" / "bg_left.png",
                ROOT_DIR / "assets" / "BackGround" / "city1" / "bg_left.png",
            ):
                if bg_left.exists():
                    pyxel.images[0].load(0, 0, str(bg_left))
                    break
            for bg_right in (
                Path("assets/BackGround/city1/bg_right.png"),
                BASE_DIR / "assets" / "BackGround" / "city1" / "bg_right.png",
                ROOT_DIR / "assets" / "BackGround" / "city1" / "bg_right.png",
            ):
                if bg_right.exists():
                    pyxel.images[1].load(0, 0, str(bg_right))
                    break
        except BaseException:
            pass
        
    def update(self):
        try:
            if pyxel.btnp(pyxel.KEY_M):
                self.audio.toggle_mute()
        except BaseException:
            pass

        self.audio.play_menu_bgm()

        if self.show_tutorial:
            if (
                pyxel.btnp(pyxel.KEY_SPACE)
                or pyxel.btnp(pyxel.KEY_RETURN)
                or pyxel.btnp(pyxel.KEY_ESCAPE)
                or pyxel.btnp(pyxel.KEY_H)
                or pyxel.btnp(pyxel.KEY_Q)
                or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
                or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START)
            ):
                self.show_tutorial = False
            return None

        if pyxel.btnp(pyxel.KEY_H):
            self.show_tutorial = True
            return None

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.is_tutorial_open_click(
            pyxel.mouse_x, pyxel.mouse_y, self.app.WIDTH, self.app.HEIGHT
        ):
            self.show_tutorial = True
            return None

        consumed_click = self.powerup_system.handle_menu_input(self.app.WIDTH, self.app.HEIGHT)
        if consumed_click:
            return None

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

    def draw_tutorial(self):
        w = self.app.WIDTH
        h = self.app.HEIGHT
        bx, by, bw, bh = 6, 4, w - 12, h - 8

        pyxel.rect(bx, by, bw, bh, 0)
        pyxel.rectb(bx, by, bw, bh, 12)
        pyxel.rectb(bx + 2, by + 2, bw - 4, bh - 4, 5)

        # Cabeçalho do Manual
        pyxel.rect(bx + 3, by + 3, bw - 6, 11, 1)
        title = "[ TUTORIAL - MANUAL DE OPERACAO APEX-01 ]"
        pyxel.text(bx + (bw - len(title) * 4) // 2, by + 6, title, 11)
        pyxel.line(bx + 3, by + 14, bx + bw - 4, by + 14, 12)

        tx = bx + 8

        # 1. Como Ganhar
        pyxel.text(tx, 21, "1. COMO GANHAR (UNICO OBJETIVO DE VITORIA)", 11)
        pyxel.text(tx, 28, "- Escale a fachada ate chegar ao topo do predio (APEX) para vencer!", 7)
        pyxel.text(tx, 35, "- So limpar vidros NAO vence o jogo: voce precisa alcancar o topo!", 10)
        pyxel.line(bx + 6, 43, bx + bw - 7, 43, 5)

        # 2. Como Sobreviver
        pyxel.text(tx, 46, "2. COMO SOBREVIVER (MANTENHA-SE VIVO NA SUBIDA)", 8)
        pyxel.text(tx, 53, "- EFICIENCIA (TOPO): Cai sem parar! Limpe (+15%) e repare (+30%)", 7)
        pyxel.text(tx, 60, "  janelas no caminho p/ nao zerar a barra (em 0% voce e demitido!).", 10)
        pyxel.text(tx, 67, "- TIROS E DRONES (3 VIDAS): Desvie do laser! Janelas dropam +1 Vida.", 7)
        pyxel.text(tx, 74, "- QUEDA FATAL: Ao saltar, conecte (Link) em outra ancora alinhada.", 9)
        pyxel.line(bx + 6, 82, bx + bw - 7, 82, 5)

        # 3. Mecânicas e Controles
        pyxel.text(tx, 85, "3. MECANICAS E CONTROLES (PC / TOUCH / GAMEPAD)", 12)
        pyxel.text(tx, 93, "- PLANTAR ANCORA (MAX 3): Clique Esq. ou Toque na fachada (mira verde)", 7)
        pyxel.text(tx, 101, "- MOVER / BALANCAR: W,A,S,D / Setas / Joystick Virtual na corda ativa", 7)
        pyxel.text(tx, 109, "- SALTAR E LINK NO AR: [ESPACO] / Botao [SALTO] / Clique no apoio", 7)
        pyxel.text(tx, 117, "- LIMPAR / REPARAR: Segure [E] na janela (progresso salvo se parar!)", 10)
        pyxel.text(tx, 125, "- RECOLHER ANCORA: Clique Dir. ou [R] p/ liberar slot e continuar", 6)
        pyxel.text(tx, 133, "- POWER-UPS: Escolha 1 equipamento no menu antes de iniciar [1-4]", 11)

        # Botão para fechar o tutorial e voltar ao Menu Principal
        cbx, cby, cbw, cbh = self.get_tutorial_close_button_rect(w, h)
        pulse = (pyxel.frame_count // 15) % 2
        border_col = 11 if pulse else 12
        pyxel.rect(cbx, cby, cbw, cbh, 1)
        pyxel.rectb(cbx, cby, cbw, cbh, border_col)
        close_label = "[ ENTENDI / IR AO MENU (ESPACO / TOQUE) ]"
        pyxel.text(
            cbx + (cbw - len(close_label) * 4) // 2,
            cby + 5,
            close_label,
            11 if pulse else 7,
        )

    def draw(self):
        pyxel.camera(0, 0)

        pyxel.blt(0, 0, 0, 0, 0, 256, 180)
        pyxel.blt(256, 0, 1, 0, 0, 64, 180)

        if self.show_tutorial:
            self.draw_tutorial()
            return

        # Letreiro do Título
        pyxel.text(self.app.WIDTH // 2 - 26, self.app.HEIGHT // 2 - 36, "APEX GRAPPLER", 11)
        pyxel.text(self.app.WIDTH // 2 - 40, self.app.HEIGHT // 2 - 26, "OPERACAO VERTICAL", 7)

        # Botão / Caixa de Início adaptada para Touch (celulares) e Teclado/Mouse (Desktop)
        bw = 144
        bh = 22
        bx = (self.app.WIDTH - bw) // 2
        by = self.app.HEIGHT // 2 - 6

        pulse = (pyxel.frame_count // 15) % 2
        border_col = 11 if pulse else 12

        pyxel.rect(bx, by, bw, bh, 0)
        pyxel.rectb(bx, by, bw, bh, border_col)
        pyxel.text(bx + 14, by + 5, "[ TOQUE PARA INICIAR ]", 11 if pulse else 7)
        pyxel.text(bx + 10, by + 13, "OU ESPACO / ENTER / CLIQUE", 6)

        # Botão para reabrir a tela de Tutorial / Instruções
        tbx, tby, tbw, tbh = self.get_tutorial_open_button_rect(self.app.WIDTH, self.app.HEIGHT)
        pyxel.rect(tbx, tby, tbw, tbh, 0)
        pyxel.rectb(tbx, tby, tbw, tbh, 12)
        tut_label = "[ COMO JOGAR / TUTORIAL (H) ]"
        pyxel.text(tbx + (tbw - len(tut_label) * 4) // 2, tby + 4, tut_label, 12)

        # Seletor de Power-Ups Pré-Partida
        self.powerup_system.draw_menu_selector(self.app.WIDTH, self.app.HEIGHT)
        
        