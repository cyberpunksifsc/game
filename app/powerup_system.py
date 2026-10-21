import pyxel

# Constantes de Power-Ups Pré-Partida (conforme GDD: Power-Ups Pré-Partida)
POWERUP_NONE = "NONE"
POWERUP_SHIELD = "SHIELD"
POWERUP_TURBO = "TURBO_SQUEEGEE"
POWERUP_STABILIZER = "CORP_STABILIZER"

POWERUP_ORDER = [
    POWERUP_NONE,
    POWERUP_SHIELD,
    POWERUP_TURBO,
    POWERUP_STABILIZER,
]

POWERUP_METADATA = {
    POWERUP_NONE: {
        "name": "SEM ITEM",
        "short": "[1] SEM ITEM",
        "hud_label": "PADRAO",
        "desc": "Turno padrao sem equipamento extra",
        "color": 6,
    },
    POWERUP_SHIELD: {
        "name": "ESCUDO REATIVO",
        "short": "[2] ESCUDO",
        "hud_label": "ESCUDO",
        "desc": "Absorve 1 tiro sem perder vida",
        "color": 12,
    },
    POWERUP_TURBO: {
        "name": "RODO TURBO",
        "short": "[3] RODO TURBO",
        "hud_label": "RODO TURBO",
        "desc": "+50% veloc. limpeza e reparo",
        "color": 11,
    },
    POWERUP_STABILIZER: {
        "name": "ESTABILIZADOR",
        "short": "[4] ESTABILIZADOR",
        "hud_label": "ESTABILIZ.",
        "desc": "-30% queda meta / +25% pts",
        "color": 10,
    },
}


class PowerUpSystem:
    """Gerencia a seleção pré-partida de Power-Ups no Menu Principal e seus
    efeitos passivos/ativos durante o turno de trabalho na fachada do Apex-01.
    """

    def __init__(self, initial_powerup: str = POWERUP_NONE):
        self.selected_powerup = POWERUP_NONE
        self.shield_charges = 0
        self.select_powerup(initial_powerup)

    def select_powerup(self, powerup_id: str) -> str:
        """Define o power-up selecionado para o próximo turno, se válido."""
        if powerup_id in POWERUP_METADATA:
            self.selected_powerup = powerup_id
        self.activate_for_shift()
        return self.selected_powerup

    def cycle_selection(self, step: int = 1) -> str:
        """Alterna ciclicamente entre as 4 opções de Power-Up pré-partida."""
        idx = POWERUP_ORDER.index(self.selected_powerup)
        next_idx = (idx + step) % len(POWERUP_ORDER)
        self.selected_powerup = POWERUP_ORDER[next_idx]
        self.activate_for_shift()
        return self.selected_powerup

    def activate_for_shift(self):
        """Inicializa/recarrega as cargas do equipamento selecionado no início do turno."""
        self.shield_charges = 1 if self.selected_powerup == POWERUP_SHIELD else 0

    def reset(self):
        """Alias para recarregar o power-up selecionado ao reiniciar a partida."""
        self.activate_for_shift()

    # ------------------------------------------------------------------
    # Multiplicadores e Estado Passivo/Ativo
    # ------------------------------------------------------------------
    @property
    def work_speed_multiplier(self) -> float:
        if self.selected_powerup == POWERUP_TURBO:
            return 1.5
        return 1.0

    @property
    def efficiency_drain_multiplier(self) -> float:
        if self.selected_powerup == POWERUP_STABILIZER:
            return 0.70
        return 1.0

    @property
    def score_multiplier(self) -> float:
        if self.selected_powerup == POWERUP_STABILIZER:
            return 1.25
        return 1.0

    @property
    def has_active_shield(self) -> bool:
        return self.shield_charges > 0

    def try_absorb_hit(self) -> bool:
        """Tenta absorver o impacto de um projétil com o Escudo Reativo.
        Retorna True se o tiro foi absorvido sem perda de HP.
        """
        if self.shield_charges > 0:
            self.shield_charges -= 1
            return True
        return False

    # ------------------------------------------------------------------
    # Interface do Menu Principal (Seleção Pré-Partida)
    # ------------------------------------------------------------------
    def get_card_rects(self, screen_w: int = 320, screen_h: int = 180) -> list[tuple[str, int, int, int, int]]:
        """Retorna a lista (powerup_id, x, y, w, h) dos 4 cartões no Menu Principal."""
        card_w = 74
        card_h = 16
        gap = 3
        total_w = len(POWERUP_ORDER) * card_w + (len(POWERUP_ORDER) - 1) * gap
        start_x = (screen_w - total_w) // 2
        card_y = screen_h - 38

        rects = []
        for i, pid in enumerate(POWERUP_ORDER):
            cx = start_x + i * (card_w + gap)
            rects.append((pid, cx, card_y, card_w, card_h))
        return rects

    def handle_menu_input(self, screen_w: int = 320, screen_h: int = 180) -> bool:
        """Processa teclas (1-4, setas, A/D) e cliques nos cartões de Power-Up.
        Retorna True se um clique do mouse foi consumido pela barra de seleção.
        """
        if pyxel.btnp(pyxel.KEY_1):
            self.select_powerup(POWERUP_NONE)
        elif pyxel.btnp(pyxel.KEY_2):
            self.select_powerup(POWERUP_SHIELD)
        elif pyxel.btnp(pyxel.KEY_3):
            self.select_powerup(POWERUP_TURBO)
        elif pyxel.btnp(pyxel.KEY_4):
            self.select_powerup(POWERUP_STABILIZER)
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.cycle_selection(-1)
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.cycle_selection(1)

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            for pid, cx, cy, cw, ch in self.get_card_rects(screen_w, screen_h):
                if cx <= mx <= cx + cw and cy <= my <= cy + ch:
                    self.select_powerup(pid)
                    return True

        return False

    def draw_menu_selector(self, screen_w: int = 320, screen_h: int = 180):
        """Desenha a barra cyberpunk de Power-Ups Pré-Partida na base do Menu Principal."""
        panel_x = 4
        panel_y = screen_h - 50
        panel_w = screen_w - 8
        panel_h = 46

        pyxel.rect(panel_x, panel_y, panel_w, panel_h, 0)
        pyxel.rectb(panel_x, panel_y, panel_w, panel_h, 5)

        header = "POWER-UP PRE-PARTIDA [1-4 / SETAS / TOQUE]"
        pyxel.text((screen_w - len(header) * 4) // 2, panel_y + 4, header, 7)

        for pid, cx, cy, cw, ch in self.get_card_rects(screen_w, screen_h):
            meta = POWERUP_METADATA[pid]
            is_selected = (pid == self.selected_powerup)
            border_col = meta["color"] if is_selected else 5
            bg_col = 1 if is_selected else 0

            pyxel.rect(cx, cy, cw, ch, bg_col)
            pyxel.rectb(cx, cy, cw, ch, border_col)

            label = meta["short"]
            lx = cx + (cw - len(label) * 4) // 2
            ly = cy + 5
            pyxel.text(lx, ly, label, meta["color"] if is_selected else 6)

        active_meta = POWERUP_METADATA[self.selected_powerup]
        desc_line = f"{active_meta['name']}: {active_meta['desc']}"
        pyxel.text(
            (screen_w - len(desc_line) * 4) // 2,
            panel_y + panel_h - 8,
            desc_line,
            active_meta["color"],
        )

    # ------------------------------------------------------------------
    # HUD e Efeitos Visuais na Partida
    # ------------------------------------------------------------------
    def draw_hud_badge(self, screen_w: int = 320, screen_h: int = 180):
        """Desenha o badge compacto do Power-Up equipado abaixo dos corações de HP."""
        if self.selected_powerup == POWERUP_NONE:
            return

        meta = POWERUP_METADATA[self.selected_powerup]
        if self.selected_powerup == POWERUP_SHIELD:
            if self.has_active_shield:
                label = "ESCUDO OK"
                col = 12
            else:
                label = "ESCUDO USADO"
                col = 5
        else:
            label = meta["hud_label"]
            col = meta["color"]

        bx = 4
        by = 33
        bw = len(label) * 4 + 6
        bh = 9
        pyxel.rect(bx, by, bw, bh, 0)
        pyxel.rectb(bx, by, bw, bh, col)
        pyxel.text(bx + 3, by + 2, label, col)

    def draw_player_shield(self, player_x: float, player_y: float):
        """Desenha uma bolha de energia ciano pulsante ao redor do alpinista quando o escudo está ativo."""
        if not self.has_active_shield:
            return

        cx = int(player_x + 15)
        cy = int(player_y + 16)
        pulse = (pyxel.frame_count // 6) % 2
        radius = 13 + pulse
        pyxel.circb(cx, cy, radius, 12)
        if pulse == 0:
            pyxel.circb(cx, cy, radius - 2, 11)
