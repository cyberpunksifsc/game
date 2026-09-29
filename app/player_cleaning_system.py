import random
import pyxel
from building_generator import (
    Window,
    WINDOW_STATE_CLEAN,
    WINDOW_STATE_DIRTY,
    WINDOW_STATE_BROKEN,
    CLEAN_FRAMES_REQUIRED,
    REPAIR_FRAMES_REQUIRED,
)
from player_anchor_system import STATE_ANCHORED


class Particle:
    """Partícula visual para água/espuma de limpeza ou faíscas de laser."""

    def __init__(self, x: float, y: float, vx: float, vy: float, color: int, life: int = 15):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # gravidade leve
        self.life -= 1
        return self.life > 0

    def draw(self):
        pyxel.pset(int(self.x), int(self.y), self.color)


class FloatingScore:
    """Texto flutuante indicador de pontuação e feedback corporativo."""

    def __init__(self, x: float, y: float, text: str, color: int):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 40

    def update(self) -> bool:
        self.y -= 0.5
        self.life -= 1
        return self.life > 0

    def draw(self):
        tw = len(self.text) * 4
        pyxel.text(int(self.x - tw / 2), int(self.y), self.text, self.color)


class PlayerCleaningSystem:
    """Gerencia a detecção de janelas sujas/quebradas, controle de tempo de limpeza (1.5s)

    e conserto (3.5s) com a tecla [E], pausa e retomada sem perda de progresso,
    efeitos visuais, pontuação e feedback corporativo.
    """

    def __init__(self, player, building):
        self.player = player
        self.building = building

        # Janela atualmente em foco/alcance do alpinista
        self.target_window: Window | None = None

        # Estado da ação
        self.is_cleaning = False
        self.current_action_type = ""  # "CLEANING" ou "REPAIRING"

        # Pontuação acumulada no turno
        self.score = 0
        self.windows_cleaned = 0
        self.windows_repaired = 0

        # Partículas e popups
        self.particles: list[Particle] = []
        self.popups: list[FloatingScore] = []

        # Configuração de sons chiptune para limpeza e solda
        self.init_sounds()

    def init_sounds(self):
        """Inicializa os sons chiptune dos equipamentos nos slots 6 a 9 do Pyxel."""
        try:
            # Som 6: Rodo / Spray de limpeza (chiado/spray abrasivo)
            pyxel.sounds[6].set("c1e1g1c2", "n", "3210", "f", 4)
            # Som 7: Selamento a laser / resina térmica (zumbido de alta frequência)
            pyxel.sounds[7].set("g2b2d3f3", "t", "7564", "v", 3)
            # Som 8: Conclusão Limpeza (acorde alegre brilhante)
            pyxel.sounds[8].set("c3e3g3c4", "t", "6677", "s", 6)
            # Som 9: Conclusão Reparo (fanfarra tecnológica)
            pyxel.sounds[9].set("d3f#3a3d4", "p", "7777", "v", 7)
        except BaseException:
            pass

    def play_sound(self, sound_id: int, channel: int = 1):
        try:
            pyxel.play(channel, sound_id)
        except BaseException:
            pass

    def update(self):
        """Atualiza a detecção de janelas próximas, o progresso da ação com [E] e partículas."""
        # 1. Atualiza partículas e popups existentes
        self.particles = [p for p in self.particles if p.update()]
        self.popups = [pop for pop in self.popups if pop.update()]

        # 2. Localiza a posição atual do arnês do alpinista
        hx, hy = self.player.anchor_system.get_harness_pos()

        # 3. Identifica a janela sob alcance
        self.target_window = self.building.find_target_window(hx, hy)

        # Se não estiver ancorado ou não tiver janela acionável sob alcance, desativa ação
        if self.player.anchor_system.state != STATE_ANCHORED or self.target_window is None:
            self.is_cleaning = False
            return

        # 4. Verifica o acionamento contextual da Tecla [E]
        holding_e = pyxel.btn(pyxel.KEY_E)

        if holding_e and self.target_window.state != WINDOW_STATE_CLEAN:
            self.is_cleaning = True
            action_type = "CLEANING" if self.target_window.state == WINDOW_STATE_DIRTY else "REPAIRING"
            self.current_action_type = action_type

            # Estabiliza o balanço pendular para que o alpinista fique firme contra a fachada
            self.player.anchor_system.angular_vel *= 0.75
            self.player.anchor_system.angle *= 0.90

            # Gera partículas contextuais
            wx = self.target_window.x + self.target_window.w / 2
            wy = self.target_window.y + self.target_window.h / 2

            if action_type == "CLEANING":
                # Partículas de água e espuma néon (ciano 12, branco 7, azul 1)
                if random.random() < 0.65:
                    vx = random.uniform(-1.2, 1.2)
                    vy = random.uniform(-0.8, 1.5)
                    col = random.choice([12, 7, 6, 11])
                    self.particles.append(Particle(hx + random.uniform(-6, 6), hy + random.uniform(-4, 4), vx, vy, col, life=12))

                # Efeito sonoro contínuo de limpeza a cada 5 frames
                if pyxel.frame_count % 5 == 0:
                    self.play_sound(6, channel=1)
            else:
                # Partículas de solda a laser (laranja 9, amarelo 10, rosa néon 8, branco 7)
                if random.random() < 0.8:
                    vx = random.uniform(-2.0, 2.0)
                    vy = random.uniform(-1.5, 0.5)
                    col = random.choice([10, 9, 8, 7])
                    self.particles.append(Particle(hx + random.uniform(-4, 4), hy + random.uniform(-4, 4), vx, vy, col, life=16))

                # Efeito sonoro de solda a laser
                if pyxel.frame_count % 4 == 0:
                    self.play_sound(7, channel=1)

            # Avança o progresso da janela (1 frame de trabalho)
            completed = self.target_window.advance_work(1.0)

            if completed:
                self.is_cleaning = False
                if action_type == "CLEANING":
                    self.score += 100
                    self.windows_cleaned += 1
                    self.play_sound(8, channel=1)
                    self.popups.append(FloatingScore(wx, wy - 8, "+100 LIMPO!", 11))
                    self.player.anchor_system.set_feedback("+100 VIDRO LIMPO!", 45, 11)
                else:
                    self.score += 250
                    self.windows_repaired += 1
                    self.play_sound(9, channel=1)
                    self.popups.append(FloatingScore(wx, wy - 8, "+250 CONSERTADO!", 10))
                    self.player.anchor_system.set_feedback("+250 VIDRO REPARADO!", 45, 10)

                # Flash com faíscas de celebração
                for _ in range(16):
                    self.particles.append(Particle(
                        wx, wy,
                        random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5),
                        random.choice([7, 10, 11, 12]),
                        life=20,
                    ))
        else:
            # Jogador soltou a tecla [E] ou terminou: ação pausa imediatamente,
            # conservando o progresso salvo na janela sem nenhuma perda!
            self.is_cleaning = False

    def draw_world(self, camera_x: float, camera_y: float):
        """Desenha partículas, efeitos e popups de texto em coordenadas de mundo."""
        # 1. Partículas de spray e solda
        for p in self.particles:
            p.draw()

        # 2. Textos flutuantes de pontuação
        for pop in self.popups:
            pop.draw()

        # 3. Ferramenta de trabalho nas mãos do alpinista durante a ação
        if self.is_cleaning and self.target_window:
            hx, hy = self.player.anchor_system.get_harness_pos()
            wx = self.target_window.x + self.target_window.w / 2
            wy = self.target_window.y + self.target_window.h / 2

            # Raio laser ou rodo conectando a mão do alpinista à superfície do vidro
            if self.current_action_type == "REPAIRING":
                # Feixe de laser térmico azul/ciano ou amarelo
                laser_col = 10 if (pyxel.frame_count // 2) % 2 == 0 else 7
                pyxel.line(int(hx), int(hy), int(wx + random.uniform(-4, 4)), int(wy + random.uniform(-4, 4)), laser_col)
                pyxel.circb(int(wx), int(wy), 3, laser_col)
            else:
                # Spray/rodo de limpeza
                pyxel.line(int(hx), int(hy), int(wx), int(wy), 12)
                pyxel.rect(int(wx - 4), int(wy - 1), 8, 2, 7)

    def draw_hud(self, screen_width: int, screen_height: int):
        """Desenha a dica de ação contextual [E] e o placar corporativo no HUD."""
        # 1. Prompt de ação contextual quando o alpinista está sobre uma janela
        if self.target_window and self.target_window.state != WINDOW_STATE_CLEAN:
            hx, hy = self.player.anchor_system.get_harness_pos()
            screen_wx = int(self.target_window.x + self.target_window.w / 2 - self.player.anchor_system.camera_x)
            screen_wy = int(self.target_window.y - self.player.anchor_system.camera_y - 12)

            if self.target_window.state == WINDOW_STATE_DIRTY:
                label = "[E] LIMPAR (1.5s)"
                color = 11
            else:
                label = "[E] CONSERTAR (3.5s)"
                color = 10

            tw = len(label) * 4
            bx = screen_wx - tw // 2
            by = screen_wy

            # Caixa do prompt
            pyxel.rect(bx - 3, by - 2, tw + 6, 9, 0)
            pyxel.rectb(bx - 3, by - 2, tw + 6, 9, color)
            pyxel.text(bx, by, label, color)

            # Barra de porcentagem visível em cima se estiver em andamento
            if self.target_window.progress > 0:
                pct = int(self.target_window.progress * 100)
                pct_str = f"{pct}%"
                pyxel.text(bx + tw + 6, by, pct_str, 7)

        # 2. Painel de Desempenho e Pontuação (canto superior direito da tela)
        panel_w = 110
        panel_h = 24
        px = screen_width - panel_w - 4
        py = 4

        pyxel.rect(px, py, panel_w, panel_h, 0)
        pyxel.rectb(px, py, panel_w, panel_h, 5)

        pyxel.text(px + 4, py + 3, f"PONTOS: {self.score:05d}", 10)
        pyxel.text(px + 4, py + 11, f"LIMPOS: {self.windows_cleaned}", 11)
        pyxel.text(px + 56, py + 11, f"REPAROS: {self.windows_repaired}", 12)
