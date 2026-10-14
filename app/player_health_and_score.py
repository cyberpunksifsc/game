import pyxel

# Taxa de quadros padrão do Pyxel (pyxel.init sem fps explícito)
FPS = 30

# --- Vida (HP) ---
MAX_HP = 3                      # 3 pontos de vida, cada tiro tira 1, sem regeneração
INVULNERABILITY_FRAMES = 45     # Janela de invulnerabilidade após levar dano (~1.5s)

# --- Barra de Eficiência Corporativa (0.0 a 1.0) ---
EFFICIENCY_FULL_DRAIN_SECONDS = 60.0                            # Cheia -> zero em ~60s com jogador ativo
EFFICIENCY_BASE_DRAIN = 1.0 / (EFFICIENCY_FULL_DRAIN_SECONDS * FPS)
EFFICIENCY_IDLE_MULTIPLIER = 2.0                                # Cai 2x mais rápido parado/sem trabalhar
EFFICIENCY_LOW_THRESHOLD = 0.25                                 # Abaixo disso, a barra pisca em alerta
EFFICIENCY_GAIN_CLEAN = 0.15                                    # Janela limpa: +15%
EFFICIENCY_GAIN_REPAIR = 0.30                                   # Janela consertada: +30%

# --- Pontuação ---
SCORE_CLEAN = 100
SCORE_REPAIR = 250

# --- Motivos de Game Over ---
REASON_FALL = "FALL"
REASON_HP = "HP"
REASON_EFFICIENCY = "EFFICIENCY"

GAME_OVER_TEXTS = {
    REASON_FALL: ("MOTIVO: QUEDA FATAL", "O trabalhador falhou ao se ancorar."),
    REASON_HP: ("MOTIVO: LESOES INCAPACITANTES", "O trabalhador foi atingido demais."),
    REASON_EFFICIENCY: ("MOTIVO: DESEMPENHO INSUFICIENTE", "Produtividade abaixo da meta."),
}

# Atraso antes de aceitar o comando de retentar (evita reinício acidental)
RETRY_DELAY_FRAMES = 30


class PlayerHealthAndScore:
    """Gerencia HP (dano por projétil), barra de Eficiência Corporativa (queda por
    tempo/inatividade), pontuação e condições de game over.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reinicia todas as métricas para uma nova partida (turno de trabalho)."""
        self.hp = MAX_HP
        self.invulnerable_timer = 0

        self.efficiency = 1.0

        self.score = 0
        self.windows_cleaned = 0
        self.windows_repaired = 0

        self.is_game_over = False
        self.game_over_reason = ""
        self.game_over_timer = 0

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------
    def update(self, is_idle: bool):
        """Atualiza a barra corporativa e os timers. `is_idle` indica jogador parado e sem trabalhar."""
        if self.is_game_over:
            self.game_over_timer += 1
            return

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        drain = EFFICIENCY_BASE_DRAIN
        if is_idle:
            drain *= EFFICIENCY_IDLE_MULTIPLIER
        self.efficiency = max(0.0, self.efficiency - drain)

        if self.efficiency <= 0.0:
            self.trigger_game_over(REASON_EFFICIENCY)

    # ------------------------------------------------------------------
    # Eventos de jogo
    # ------------------------------------------------------------------
    def register_window_completed(self, action_type: str) -> int:
        """Registra uma janela concluída ("CLEANING" ou "REPAIRING"). Retorna os pontos ganhos."""
        if action_type == "REPAIRING":
            points = SCORE_REPAIR
            self.windows_repaired += 1
            gain = EFFICIENCY_GAIN_REPAIR
        else:
            points = SCORE_CLEAN
            self.windows_cleaned += 1
            gain = EFFICIENCY_GAIN_CLEAN

        self.score += points
        self.efficiency = min(1.0, self.efficiency + gain)
        return points

    @property
    def is_invulnerable(self) -> bool:
        return self.invulnerable_timer > 0

    def take_damage(self, amount: int = 1) -> bool:
        """Aplica dano ao jogador. Retorna True se o dano foi efetivamente aplicado."""
        if self.is_game_over or self.is_invulnerable:
            return False

        self.hp = max(0, self.hp - amount)
        self.invulnerable_timer = INVULNERABILITY_FRAMES

        if self.hp <= 0:
            self.trigger_game_over(REASON_HP)
        return True

    def trigger_game_over(self, reason: str):
        """Encerra o turno com o motivo informado (só registra a primeira causa)."""
        if self.is_game_over:
            return
        self.is_game_over = True
        self.game_over_reason = reason
        self.game_over_timer = 0

    @property
    def can_retry(self) -> bool:
        return self.is_game_over and self.game_over_timer >= RETRY_DELAY_FRAMES

    # ------------------------------------------------------------------
    # Desenho (HUD em coordenadas de tela)
    # ------------------------------------------------------------------
    def _draw_heart(self, x: int, y: int, filled: bool):
        """Desenha um coração 7x6 em pixel art."""
        col = 8 if filled else 5
        pattern = (
            ".XX.XX.",
            "XXXXXXX",
            "XXXXXXX",
            ".XXXXX.",
            "..XXX..",
            "...X...",
        )
        for row, line in enumerate(pattern):
            for c, ch in enumerate(line):
                if ch == "X":
                    pyxel.pset(x + c, y + row, col)
        if filled:
            pyxel.pset(x + 1, y + 1, 14)  # brilho

    def draw_hud(self, screen_width: int, screen_height: int):
        # 1. Painel de Vida (abaixo das âncoras - apenas corações visuais)
        pyxel.rect(4, 21, 32, 10, 0)
        pyxel.rectb(4, 21, 32, 10, 5)
        blink_off = self.is_invulnerable and (self.invulnerable_timer // 3) % 2 == 0
        for i in range(MAX_HP):
            filled = i < self.hp
            if blink_off and i == self.hp:
                filled = True  # pisca o coração recém-perdido
            self._draw_heart(7 + i * 9, 23, filled)

        # 2. Barra de Eficiência Corporativa (topo central - compacto com % e barra)
        bx, by, bw, bh = (screen_width - 76) // 2, 4, 76, 12
        pyxel.rect(bx, by, bw, bh, 0)
        is_low = self.efficiency <= EFFICIENCY_LOW_THRESHOLD
        alert_on = is_low and (pyxel.frame_count // 8) % 2 == 0
        pyxel.rectb(bx, by, bw, bh, 8 if alert_on else 5)

        pct = int(self.efficiency * 100)
        pct_str = f"{pct:02d}%"
        pyxel.text(bx + 4, by + 4, pct_str, 8 if alert_on else 7)

        if self.efficiency > 0.5:
            fill_col = 11
        elif self.efficiency > EFFICIENCY_LOW_THRESHOLD:
            fill_col = 10
        else:
            fill_col = 8

        bar_x, bar_y, bar_w, bar_h = bx + 22, by + 4, bw - 26, 4
        pyxel.rect(bar_x, bar_y, bar_w, bar_h, 1)
        fill_w = int(bar_w * self.efficiency)
        if fill_w > 0:
            pyxel.rect(bar_x, bar_y, fill_w, bar_h, fill_col)

        # 3. Painel de Pontuação (canto superior direito - apenas o placar arcade)
        panel_w = 42
        panel_h = 12
        px = screen_width - panel_w - 4
        py = 4
        pyxel.rect(px, py, panel_w, panel_h, 0)
        pyxel.rectb(px, py, panel_w, panel_h, 5)
        score_str = f"{self.score:05d}"
        pyxel.text(px + (panel_w - len(score_str) * 4) // 2, py + 4, score_str, 10)


        # 4. Tela unificada de Game Over
        if self.is_game_over:
            self.draw_game_over(screen_width, screen_height)

    def draw_game_over(self, screen_width: int, screen_height: int):
        box_w = 220
        box_h = 72
        bx = (screen_width - box_w) // 2
        by = (screen_height - box_h) // 2

        pyxel.rect(bx, by, box_w, box_h, 0)
        pyxel.rectb(bx, by, box_w, box_h, 8)
        pyxel.rectb(bx + 2, by + 2, box_w - 4, box_h - 4, 8)

        def centered(text: str, y: int, col: int):
            pyxel.text(bx + (box_w - len(text) * 4) // 2, y, text, col)

        reason_title, reason_desc = GAME_OVER_TEXTS.get(self.game_over_reason, ("", ""))
        centered("[ RESCISAO DE CONTRATO ]", by + 8, 8)
        centered(reason_title, by + 18, 9)
        centered(reason_desc, by + 27, 7)
        centered(f"PONTUACAO FINAL: {self.score:05d}", by + 39, 10)
        centered(f"LIMPOS: {self.windows_cleaned}   REPAROS: {self.windows_repaired}", by + 48, 6)

        if self.can_retry and (pyxel.frame_count // 15) % 2 == 0:
            centered("TOQUE NA TELA OU [R]/[ESPACO] P/ RETENTAR", by + 60, 11)
