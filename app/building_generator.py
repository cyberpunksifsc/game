import random
import pyxel

# Constantes de Estado das Janelas (conforme GDD)
WINDOW_STATE_CLEAN = "CLEAN"
WINDOW_STATE_DIRTY = "DIRTY"
WINDOW_STATE_BROKEN = "BROKEN"

# Tempos de execução a 30 FPS (conforme GDD: 1.5s limpeza, 3.5s conserto)
CLEAN_FRAMES_REQUIRED = 45   # 1.5s * 30 FPS
REPAIR_FRAMES_REQUIRED = 105 # 3.5s * 30 FPS


class Window:
    """Representa um painel de vidro na fachada do arranha-céu Apex-01."""

    def __init__(self, x: float, y: float, w: int, h: int, col: int, floor: int, initial_state: str = WINDOW_STATE_CLEAN):
        self.x = float(x)
        self.y = float(y)
        self.w = int(w)
        self.h = int(h)
        self.col = col
        self.floor = floor

        self.state = initial_state
        self.work_frames = 0
        self.pulse_timer = random.randint(0, 60)

    @property
    def max_frames(self) -> int:
        if self.state == WINDOW_STATE_DIRTY:
            return CLEAN_FRAMES_REQUIRED
        elif self.state == WINDOW_STATE_BROKEN:
            return REPAIR_FRAMES_REQUIRED
        return 1

    @property
    def progress(self) -> float:
        if self.state == WINDOW_STATE_CLEAN or self.work_frames <= 0:
            return 0.0
        return min(1.0, self.work_frames / float(self.max_frames))

    def advance_work(self, amount_frames: int = 1) -> bool:
        """Avança o progresso da ação contextual. Retorna True se o trabalho foi concluído."""
        if self.state == WINDOW_STATE_CLEAN:
            return False

        self.work_frames += amount_frames
        if self.work_frames >= self.max_frames:
            self.work_frames = 0
            self.state = WINDOW_STATE_CLEAN
            return True
        return False

    def draw(self, camera_x: float, camera_y: float, is_target: bool = False):
        """Desenha a janela e seu estado visual com tiles e texturas."""
        wx = int(self.x)
        wy = int(self.y)

        # Fundo do interior do escritório (visível através do vidro)
        # Cor 1 (azul marinho escuro)
        pyxel.rect(wx, wy, self.w, self.h, 1)

        # Desenho dos painéis de vidro usando os tiles do banco 0
        # Cada janela 32x24 é montada com 2 blocos de 16px de largura
        if self.state == WINDOW_STATE_CLEAN:
            # Vidro Limpo: reflexo translúcido ciano (tile 0, 0 no banco 0)
            pyxel.blt(wx, wy, 0, 0, 0, 16, 16)
            pyxel.blt(wx + 16, wy, 0, 0, 0, 16, 16)
            pyxel.blt(wx, wy + 16, 0, 0, 0, 16, self.h - 16)
            pyxel.blt(wx + 16, wy + 16, 0, 0, 0, 16, self.h - 16)
            # Brilho sutil do vidro limpo
            pyxel.line(wx + 2, wy + 2, wx + 10, wy + 2, 12)
        elif self.state == WINDOW_STATE_DIRTY:
            # Vidro Sujo: poeira e fuligem industrial (tile 16, 0 no banco 0)
            pyxel.blt(wx, wy, 0, 16, 0, 16, 16)
            pyxel.blt(wx + 16, wy, 0, 16, 0, 16, 16)
            pyxel.blt(wx, wy + 16, 0, 16, 0, 16, self.h - 16)
            pyxel.blt(wx + 16, wy + 16, 0, 16, 0, 16, self.h - 16)
            # Manchas amarelas de fuligem
            pyxel.pset(wx + 8, wy + 12, 4)
            pyxel.pset(wx + 22, wy + 8, 4)
            pyxel.pset(wx + 14, wy + 18, 9)
        elif self.state == WINDOW_STATE_BROKEN:
            # Vidro Quebrado: rachaduras e estilhaços por tiros (tile 96, 0 no banco 0)
            pyxel.blt(wx, wy, 0, 96, 0, 16, 16)
            pyxel.blt(wx + 16, wy, 0, 112, 0, 16, 16)
            pyxel.blt(wx, wy + 16, 0, 96, 0, 16, self.h - 16)
            pyxel.blt(wx + 16, wy + 16, 0, 112, 0, 16, self.h - 16)
            # Linhas de rachadura aguda em branco/cinza
            pyxel.line(wx + 6, wy + 4, wx + 14, wy + 14, 7)
            pyxel.line(wx + 14, wy + 14, wx + 26, wy + 10, 7)
            pyxel.line(wx + 14, wy + 14, wx + 10, wy + 22, 6)
            pyxel.pset(wx + 14, wy + 14, 8)  # furo central do projétil

        # Moldura metálica da janela (cor 5: cinza escuro, contorno preto 0)
        pyxel.rectb(wx, wy, self.w, self.h, 0)
        pyxel.rectb(wx + 1, wy + 1, self.w - 2, self.h - 2, 5)

        # Se for o alvo em foco do alpinista, exibe retículo néon pulsante
        if is_target and self.state != WINDOW_STATE_CLEAN:
            self.pulse_timer = (self.pulse_timer + 1) % 60
            glow_col = 11 if (self.pulse_timer // 6) % 2 == 0 else 12
            if self.state == WINDOW_STATE_BROKEN:
                glow_col = 9 if (self.pulse_timer // 6) % 2 == 0 else 8
            pyxel.rectb(wx - 1, wy - 1, self.w + 2, self.h + 2, glow_col)

        # Barra de progresso do trabalho atual (se pausado ou em andamento)
        if self.progress > 0.0 and self.state != WINDOW_STATE_CLEAN:
            bar_w = self.w - 4
            bar_h = 4
            bx = wx + 2
            by = wy + self.h - 6

            # Fundo da barra
            pyxel.rect(bx, by, bar_w, bar_h, 0)
            pyxel.rectb(bx, by, bar_w, bar_h, 5)

            # Preenchimento néon (ciano se limpeza, laranja/amarelo se reparo)
            fill_col = 12 if self.state == WINDOW_STATE_DIRTY else 10
            fill_w = int((bar_w - 2) * self.progress)
            if fill_w > 0:
                pyxel.rect(bx + 1, by + 1, fill_w, bar_h - 2, fill_col)


class BuildingGenerator:
    """Gera e gerencia a fachada estrutural do arranha-céu Apex-01.

    Compreende a base térrea (Setores Baixos, y ≈ 1850), os andares de janelas
    com vigas metálicas e o topo corporativo (Apex, y ≈ 40).
    """

    def __init__(self):
        # Limites da fachada
        self.building_left = 44
        self.building_right = 276
        self.building_width = self.building_right - self.building_left
        self.building_center_x = (self.building_left + self.building_right) // 2

        # Alturas do mundo
        self.base_y = 1880.0     # Nível térreo da calçada/fundação
        self.apex_y = 40.0       # Topo do arranha-céu (Apex)
        self.floor_height = 42   # Distância vertical entre pavimentos

        # Colunas de janelas (4 colunas na fachada)
        self.window_w = 32
        self.window_h = 24
        self.column_xs = [60, 114, 174, 228]

        # Lista de todas as janelas geradas
        self.windows: list[Window] = []

        # Gerar toda a estrutura do edifício
        self.generate()

    def generate(self):
        """Gera todos os pavimentos de janelas da base até o topo."""
        self.windows.clear()

        # Determina o número de andares
        total_floors = int((self.base_y - 40 - self.apex_y) // self.floor_height)

        # Semente aleatória reprodutível para a fachada
        rnd = random.Random(42)

        for floor in range(total_floors):
            # Altura Y do chão deste andar (da base para cima)
            floor_y = self.base_y - 45 - (floor * self.floor_height)

            for col_idx, col_x in enumerate(self.column_xs):
                win_y = floor_y - self.window_h

                # Distribuição contextual dos estados de janela (quantidade reduzida e equilibrada)
                if floor == 0:
                    # Andar 0 (Base inicial do jogador): apenas 1 janela suja próxima para teste imediato
                    if col_idx == 1:
                        state = WINDOW_STATE_DIRTY   # Teste imediato de limpeza com E
                    else:
                        state = WINDOW_STATE_CLEAN
                elif floor == 1:
                    # Andar 1: apenas 1 janela quebrada para teste do reparo
                    if col_idx == 2:
                        state = WINDOW_STATE_BROKEN  # Teste imediato de reparo com E
                    else:
                        state = WINDOW_STATE_CLEAN
                else:
                    # Andares superiores: distribuição mais esparsa (maioria limpa)
                    roll = rnd.random()
                    if roll < 0.12:
                        state = WINDOW_STATE_DIRTY
                    elif roll < 0.18:
                        state = WINDOW_STATE_BROKEN
                    else:
                        state = WINDOW_STATE_CLEAN

                win = Window(
                    x=col_x,
                    y=win_y,
                    w=self.window_w,
                    h=self.window_h,
                    col=col_idx,
                    floor=floor,
                    initial_state=state,
                )
                self.windows.append(win)

    def find_target_window(self, harness_x: float, harness_y: float) -> Window | None:
        """Encontra a janela mais próxima sob o alcance de trabalho do alpinista."""
        best_win = None
        best_dist = 9999.0

        for win in self.windows:
            # Janelas limpas não precisam de trabalho
            if win.state == WINDOW_STATE_CLEAN:
                continue

            # Centro da janela
            cx = win.x + win.w / 2
            cy = win.y + win.h / 2

            # Distância até o arnês do alpinista
            dx = abs(harness_x - cx)
            dy = abs(harness_y - cy)

            # Alcance máximo para conseguir trabalhar na janela (confortável para ancoragem)
            if dx <= (win.w / 2 + 18) and dy <= (win.h / 2 + 18):
                dist = dx * dx + dy * dy
                if dist < best_dist:
                    best_dist = dist
                    best_win = win

        return best_win

    def draw_facade_beams(self, camera_y: float, screen_height: float):
        """Desenha as vigas metálicas horizontais e colunas de sustentação visíveis."""
        min_y = camera_y - 40
        max_y = camera_y + screen_height + 40

        # 1. Parede de fundo do edifício (concreto reforçado/placas de titânio escuro)
        # Cor 1 (azul noite/preto industrial)
        visible_top = max(int(self.apex_y), int(camera_y - 20))
        visible_bottom = min(int(self.base_y + 60), int(camera_y + screen_height + 20))
        if visible_bottom > visible_top:
            pyxel.rect(self.building_left, visible_top, self.building_width, visible_bottom - visible_top, 0)
            pyxel.rectb(self.building_left, visible_top, self.building_width, visible_bottom - visible_top, 5)

        # 2. Vigas verticais da estrutura metálica externa
        v_beam_xs = [self.building_left, 96, 150, 210, self.building_right - 12]
        for vx in v_beam_xs:
            if visible_bottom > visible_top:
                # Coluna vertical cinza escuro com rebites
                pyxel.rect(vx, visible_top, 12, visible_bottom - visible_top, 5)
                pyxel.line(vx, visible_top, vx, visible_bottom, 0)
                pyxel.line(vx + 11, visible_top, vx + 11, visible_bottom, 0)
                # Rebites espaçados
                for ry in range(visible_top + (visible_top % 16), visible_bottom, 16):
                    pyxel.pset(vx + 5, ry, 6)

        # 3. Vigas horizontais entre os pavimentos (onde âncoras se fixam perfeitamente)
        total_floors = int((self.base_y - 40 - self.apex_y) // self.floor_height)
        for floor in range(total_floors + 1):
            beam_y = self.base_y - 45 - (floor * self.floor_height)
            if min_y <= beam_y <= max_y:
                by = int(beam_y)
                # Viga de aço de 8px de altura com rebites metálicos (tile 112, 16 do banco 0)
                for bx in range(self.building_left, self.building_right, 16):
                    w = min(16, self.building_right - bx)
                    pyxel.blt(bx, by, 0, 112, 16, w, 8)
                # Faixa sutil de neon sob cada viga de andar
                if floor % 3 == 0:
                    pyxel.line(self.building_left + 2, by + 8, self.building_right - 2, by + 8, 12)
                elif floor % 3 == 1:
                    pyxel.line(self.building_left + 2, by + 8, self.building_right - 2, by + 8, 8)

    def draw_base_foundation(self, camera_y: float, screen_height: float):
        """Desenha a fundação térrea dos andares inferiores (Setor 01 / Calçada industrial)."""
        by = int(self.base_y)
        if camera_y + screen_height < by - 50:
            return

        # Bloco maciço de concreto da fundação
        pyxel.rect(self.building_left - 16, by, self.building_width + 32, 120, 5)
        pyxel.rectb(self.building_left - 16, by, self.building_width + 32, 120, 0)

        # Viga pesada de base com rebites duplos
        for bx in range(self.building_left - 16, self.building_right + 16, 16):
            pyxel.blt(bx, by - 8, 0, 112, 16, 16, 16)

        # Portão industrial / Entrada de serviço dos trabalhadores
        gx = self.building_center_x - 36
        pyxel.rect(gx, by + 12, 72, 48, 0)
        pyxel.rectb(gx, by + 12, 72, 48, 6)

        # Listras diagonais de alerta industrial amarelo/preto
        for s in range(0, 72, 8):
            pyxel.line(gx + s, by + 12, gx + s + 4, by + 20, 9)

        # Letreiro holográfico neon na base
        pyxel.text(gx - 20, by + 2, "[ SETOR 01: MANUTENCAO INDUSTRIAL APEX ]", 11)
        pyxel.text(gx + 6, by + 28, "PORTAO APEX-01", 7)
        pyxel.text(gx - 4, by + 40, "ACESSO ALPINISTAS", 10)

        # Luzes de sinalização térrea piscando
        pulse = (pyxel.frame_count // 15) % 2
        pyxel.circ(self.building_left - 4, by + 6, 3, 8 if pulse else 9)
        pyxel.circ(self.building_right + 4, by + 6, 3, 8 if pulse else 9)

    def draw_apex_roof(self, camera_y: float):
        """Desenha a cobertura corporativa no topo (Apex-01)."""
        ay = int(self.apex_y)
        if camera_y > ay + 150:
            return

        # Viga mestre do topo
        pyxel.rect(self.building_left - 24, ay - 20, self.building_width + 48, 24, 5)
        pyxel.rectb(self.building_left - 24, ay - 20, self.building_width + 48, 24, 0)

        # Antena de transmissão corporativa
        ax = self.building_center_x
        pyxel.line(ax, ay - 20, ax, ay - 55, 6)
        pyxel.line(ax - 6, ay - 20, ax + 6, ay - 20, 6)
        # Luz vermelha de advertência de tráfego aéreo no topo da antena
        alert_col = 8 if (pyxel.frame_count // 12) % 2 == 0 else 7
        pyxel.circ(ax, ay - 55, 2, alert_col)

        # Letreiro Apex no topo
        pyxel.text(ax - 22, ay - 14, "NEO-APEX CORP", 12)

    def draw(self, camera_x: float, camera_y: float, target_window: Window | None = None):
        """Renderiza todo o edifício visível em coordenadas de mundo."""
        screen_height = 180.0

        # 1. Vigas e paredes da fachada
        self.draw_facade_beams(camera_y, screen_height)

        # 2. Janelas visíveis na tela
        for win in self.windows:
            if camera_y - 30 <= win.y <= camera_y + screen_height + 30:
                is_target = (win == target_window)
                win.draw(camera_x, camera_y, is_target=is_target)

        # 3. Base térrea
        self.draw_base_foundation(camera_y, screen_height)

        # 4. Topo corporativo (Apex)
        self.draw_apex_roof(camera_y)
