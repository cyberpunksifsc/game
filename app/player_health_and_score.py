import pyxel
from feedback_system import FeedbackSystem, QR_TOTAL_SIZE, draw_feedback_qr
from feira_integration import (
    FeiraIntegration,
    STATUS_COOLDOWN,
    STATUS_ERROR,
    STATUS_SENDING,
    STATUS_SUCCESS,
    STATUS_UNAUTHORIZED,
    STATUS_UNAVAILABLE,
)

# Taxa de quadros padrão do Pyxel (pyxel.init sem fps explícito)
FPS = 30

# --- Vida (HP) ---
MAX_HP = 3                      # 3 pontos de vida, cada tiro tira 1, sem regeneração
INVULNERABILITY_FRAMES = 45     # Janela de invulnerabilidade após levar dano (~1.5s)
HIT_ANIM_TICKS = 15             # Duração da animação de reação a dano (~0.5s)

# --- Barra de Eficiência Corporativa (0.0 a 1.0) ---
EFFICIENCY_FULL_DRAIN_SECONDS = 60.0
EFFICIENCY_BASE_DRAIN = 1.0 / (EFFICIENCY_FULL_DRAIN_SECONDS * FPS)
EFFICIENCY_IDLE_MULTIPLIER = 2.0                                # Cai 2x mais rápido parado/sem trabalhar
EFFICIENCY_LOW_THRESHOLD = 0.25                                 # Abaixo disso, a barra pisca em alerta
EFFICIENCY_GAIN_CLEAN = 0.15                                    # Janela limpa: +15%
EFFICIENCY_GAIN_REPAIR = 0.30                                   # Janela consertada: +30%

# --- Pontuação ---
SCORE_CLEAN = 100
SCORE_REPAIR = 250
BONUS_PER_HP = 300
BONUS_MAX_EFFICIENCY = 500
SOUND_VICTORY_FANFARE = 14

# --- Motivos de Encerramento (Game Over / Vitória) ---
REASON_FALL = "FALL"
REASON_HP = "HP"
REASON_EFFICIENCY = "EFFICIENCY"
REASON_VICTORY = "VICTORY"

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

    def __init__(self, powerup_system=None, feira_integration=None, feedback_system=None):
        self.powerup_system = powerup_system
        self.feira = feira_integration if feira_integration is not None else FeiraIntegration()
        self.feedback = feedback_system if feedback_system is not None else FeedbackSystem()
        self._init_sounds()
        self.reset()

    def _init_sounds(self):
        try:
            # Som 14: Fanfarra corporativa de vitória ao concluir o expediente no Apex
            pyxel.sounds[SOUND_VICTORY_FANFARE].set("c3e3g3c4g3c4", "t", "777767", "v", 6)
        except BaseException:
            pass

    def reset(self):
        """Reinicia todas as métricas para uma nova partida (turno de trabalho)."""
        self.hp = MAX_HP
        self.invulnerable_timer = 0
        self.hit_anim_timer = 0

        self.efficiency = 1.0

        self.score = 0
        self.windows_cleaned = 0
        self.windows_repaired = 0
        self.hp_bonus = 0
        self.efficiency_bonus = 0

        self.is_game_over = False
        self.is_victory = False
        self.game_over_reason = ""
        self.game_over_timer = 0

        if self.powerup_system is not None:
            self.powerup_system.activate_for_shift()

        if self.feira is not None:
            self.feira.reset()

        if self.feedback is not None:
            self.feedback.set_victory_active(False)

    # ------------------------------------------------------------------
    # Atualização
    # ------------------------------------------------------------------
    def update(self, is_idle: bool):
        """Atualiza a barra corporativa e os timers. `is_idle` indica jogador parado e sem trabalhar."""
        if self.is_game_over:
            self.game_over_timer += 1
            if self.is_victory:
                if self.feira is not None:
                    self.feira.update()
                if self.feedback is not None:
                    clicked_fb = False
                    try:
                        clicked_fb = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.is_victory_feedback_click(
                            pyxel.mouse_x,
                            pyxel.mouse_y,
                        )
                    except BaseException:
                        clicked_fb = False
                    self.feedback.update_desktop_input(clicked_feedback=clicked_fb)
            return

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        if self.hit_anim_timer > 0:
            self.hit_anim_timer -= 1

        drain = EFFICIENCY_BASE_DRAIN
        if is_idle:
            drain *= EFFICIENCY_IDLE_MULTIPLIER
        if self.powerup_system is not None:
            drain *= self.powerup_system.efficiency_drain_multiplier
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

        if self.powerup_system is not None:
            points = int(points * self.powerup_system.score_multiplier)

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

        if self.powerup_system and self.powerup_system.try_absorb_hit():
            self.invulnerable_timer = 20
            return False

        self.hp = max(0, self.hp - amount)
        self.invulnerable_timer = INVULNERABILITY_FRAMES
        self.hit_anim_timer = HIT_ANIM_TICKS

        if self.hp <= 0:
            self.trigger_game_over(REASON_HP)
        return True

    def heal(self, amount: int = 1) -> bool:
        """Cura o jogador até MAX_HP. Retorna True se curou pelo menos 1 coração."""
        if self.is_game_over or self.hp >= MAX_HP or amount <= 0:
            return False
        self.hp = min(MAX_HP, self.hp + amount)
        return True

    def trigger_game_over(self, reason: str):
        """Encerra o turno com o motivo informado (só registra a primeira causa)."""
        if self.is_game_over:
            return
        self.is_game_over = True
        self.is_victory = (reason == REASON_VICTORY)
        self.game_over_reason = reason
        self.game_over_timer = 0
        if not self.is_victory and self.feedback is not None:
            self.feedback.set_victory_active(False)

    def trigger_victory(self):
        """Encerra o expediente com vitória ao alcançar o topo (Apex), somando bônus finais."""
        if self.is_game_over:
            return
        self.hp_bonus = max(0, self.hp) * BONUS_PER_HP
        self.efficiency_bonus = int(round(max(0.0, self.efficiency) * BONUS_MAX_EFFICIENCY))
        self.score += self.hp_bonus + self.efficiency_bonus
        self.trigger_game_over(REASON_VICTORY)
        if self.feira is not None:
            self.feira.start_victory_flow()
        if self.feedback is not None:
            self.feedback.set_victory_active(
                True,
                feedback_rect=self.get_victory_feedback_rect(),
                qr_rect=self.get_victory_qr_rect(),
            )
        try:
            pyxel.play(0, SOUND_VICTORY_FANFARE)
        except BaseException:
            pass

    @staticmethod
    def _get_victory_box(screen_width: int = 320, screen_height: int = 180) -> tuple[int, int, int, int]:
        box_w = 292
        box_h = 128
        bx = (screen_width - box_w) // 2
        by = (screen_height - box_h) // 2
        return (bx, by, box_w, box_h)

    @staticmethod
    def get_victory_feedback_rect(screen_width: int = 320, screen_height: int = 180) -> tuple[int, int, int, int]:
        """Retorna o retângulo (x, y, w, h) do botão de Feedback na tela de vitória."""
        bx, by, _, _ = PlayerHealthAndScore._get_victory_box(screen_width, screen_height)
        return (bx + 8, by + 104, 78, 14)

    @staticmethod
    def get_victory_qr_rect(screen_width: int = 320, screen_height: int = 180) -> tuple[int, int, int, int]:
        """Retorna o retângulo (x, y, w, h) do QR Code de Feedback na tela de vitória."""
        bx, by, _, _ = PlayerHealthAndScore._get_victory_box(screen_width, screen_height)
        qr_area_x = bx + 230
        qr_area_w = 58
        qr_x = qr_area_x + (qr_area_w - QR_TOTAL_SIZE) // 2
        qr_y = by + 30
        return (qr_x, qr_y, QR_TOTAL_SIZE, QR_TOTAL_SIZE)

    @staticmethod
    def get_victory_retry_rect(screen_width: int = 320, screen_height: int = 180) -> tuple[int, int, int, int]:
        """Retorna o retângulo (x, y, w, h) do botão de Novo Turno na tela de vitória."""
        bx, by, _, _ = PlayerHealthAndScore._get_victory_box(screen_width, screen_height)
        return (bx + 90, by + 104, 118, 14)

    def is_victory_feedback_click(
        self,
        mx: float,
        my: float,
        screen_width: int = 320,
        screen_height: int = 180,
    ) -> bool:
        """Verifica se um clique/toque na tela de vitória ocorreu sobre o botão ou QR de Feedback."""
        fx, fy, fw, fh = self.get_victory_feedback_rect(screen_width, screen_height)
        if fx <= mx <= (fx + fw) and fy <= my <= (fy + fh):
            return True
        qx, qy, qw, qh = self.get_victory_qr_rect(screen_width, screen_height)
        return qx <= mx <= (qx + qw) and qy <= my <= (qy + qh)

    def is_victory_retry_click(
        self,
        mx: float,
        my: float,
        screen_width: int = 320,
        screen_height: int = 180,
    ) -> bool:
        """Verifica se um clique/toque na tela de vitória ocorreu sobre o botão de Novo Turno."""
        rx, ry, rw, rh = self.get_victory_retry_rect(screen_width, screen_height)
        return rx <= mx <= (rx + rw) and ry <= my <= (ry + rh)

    @property
    def can_retry(self) -> bool:
        return self.is_game_over and self.game_over_timer >= RETRY_DELAY_FRAMES

    # ------------------------------------------------------------------
    # Desenho (HUD em coordenadas de tela)
    # ------------------------------------------------------------------
    def _draw_heart(self, x: int, y: int, filled: bool):
        """Desenha um coração 7x6 em pixel art usando linhas horizontais rápidas."""
        col = 8 if filled else 5
        pyxel.rect(x + 1, y, 2, 1, col)
        pyxel.rect(x + 4, y, 2, 1, col)
        pyxel.rect(x, y + 1, 7, 2, col)
        pyxel.rect(x + 1, y + 3, 5, 1, col)
        pyxel.rect(x + 2, y + 4, 3, 1, col)
        pyxel.pset(x + 3, y + 5, col)
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

        # 3b. Badge de Power-Up equipado (abaixo dos corações)
        if self.powerup_system is not None:
            self.powerup_system.draw_hud_badge(screen_width, screen_height)

        # 4. Tela unificada de Game Over
        if self.is_game_over:
            self.draw_game_over(screen_width, screen_height)

    def draw_game_over(self, screen_width: int, screen_height: int):
        if self.is_victory:
            bx, by, box_w, box_h = self._get_victory_box(screen_width, screen_height)
        else:
            box_w = 220
            box_h = 72
            bx = (screen_width - box_w) // 2
            by = (screen_height - box_h) // 2

        border_col = 11 if self.is_victory else 8
        inner_col = 10 if self.is_victory else 8

        pyxel.rect(bx, by, box_w, box_h, 0)
        pyxel.rectb(bx, by, box_w, box_h, border_col)
        pyxel.rectb(bx + 2, by + 2, box_w - 4, box_h - 4, inner_col)

        def centered(text: str, y: int, col: int, area_x: int = bx, area_w: int = box_w):
            pyxel.text(area_x + (area_w - len(text) * 4) // 2, y, text, col)

        if self.is_victory:
            col_x = bx + 4
            col_w = 222
            centered("[ EXPEDIENTE CONCLUIDO! ]", by + 6, 11, col_x, col_w)
            centered("META CORPORATIVA ATINGIDA NO APEX", by + 15, 10, col_x, col_w)
            centered(f"BONUS HP: +{self.hp_bonus}   EFIC: +{self.efficiency_bonus}", by + 24, 12, col_x, col_w)
            centered(f"PONTUACAO FINAL: {self.score:05d}", by + 33, 10, col_x, col_w)
            centered(f"LIMPOS: {self.windows_cleaned}   REPAROS: {self.windows_repaired}", by + 42, 7, col_x, col_w)

            # Seção Feira de Jogos (Google One-Tap OAuth + POST de créditos)
            pyxel.line(col_x + 4, by + 50, col_x + col_w - 5, by + 50, 5)
            feira_status = self.feira.status if self.feira is not None else ""
            feira_msg = (
                self.feira.status_message
                if (self.feira is not None and self.feira.status_message)
                else "CONECTE O GOOGLE P/ RECEBER +250 TJL"
            )
            if feira_status == STATUS_SUCCESS:
                msg_col = 11
            elif feira_status == STATUS_SENDING:
                msg_col = 12
            elif feira_status == STATUS_COOLDOWN:
                msg_col = 9
            elif feira_status in (STATUS_UNAUTHORIZED, STATUS_ERROR):
                msg_col = 8
            else:
                msg_col = 10
            centered(feira_msg, by + 54, msg_col, col_x, col_w)

            # Área de status / slot do botão Google One-Tap
            slot_x = col_x + 12
            slot_y = by + 66
            slot_w = col_w - 24
            slot_h = 24
            pyxel.rect(slot_x, slot_y, slot_w, slot_h, 1)
            if feira_status == STATUS_SUCCESS:
                pyxel.rectb(slot_x, slot_y, slot_w, slot_h, 11)
                centered("CREDITO ENVIADO P/ SUA CONTA GOOGLE!", slot_y + 9, 11, col_x, col_w)
            elif feira_status == STATUS_SENDING:
                pyxel.rectb(slot_x, slot_y, slot_w, slot_h, 12)
                centered("AUTENTICADO! PROCESSANDO CREDITO...", slot_y + 9, 12, col_x, col_w)
            elif feira_status == STATUS_COOLDOWN:
                pyxel.rectb(slot_x, slot_y, slot_w, slot_h, 9)
                centered("LIMITE DE 1 MINUTO POR TENTATIVA", slot_y + 9, 9, col_x, col_w)
            elif feira_status == STATUS_UNAVAILABLE:
                pyxel.rectb(slot_x, slot_y, slot_w, slot_h, 6)
                centered("LOGIN GOOGLE INDISPONIVEL", slot_y + 9, 6, col_x, col_w)
            else:
                pyxel.rectb(slot_x, slot_y, slot_w, slot_h, 12)
                centered("ENTRAR COM GOOGLE (ONE-TAP)", slot_y + 9, 7, col_x, col_w)

            # Botão de Feedback (sempre visível na vitória)
            fx, fy, fw, fh = self.get_victory_feedback_rect(screen_width, screen_height)
            pyxel.rect(fx, fy, fw, fh, 1)
            pyxel.rectb(fx, fy, fw, fh, 12)
            centered("[ FEEDBACK (F) ]", fy + 4, 10, fx, fw)

            if self.can_retry:
                rx, ry, rw, rh = self.get_victory_retry_rect(screen_width, screen_height)
                pyxel.rect(rx, ry, rw, rh, 1)
                btn_border = 11 if (pyxel.frame_count // 15) % 2 == 0 else 5
                pyxel.rectb(rx, ry, rw, rh, btn_border)
                centered("[ NOVO TURNO (R / ESPACO) ]", ry + 4, 11, rx, rw)

            # Coluna direita: QR Code para feedback rápido por celular
            pyxel.line(bx + 228, by + 6, bx + 228, by + box_h - 7, 5)
            qr_area_x = bx + 230
            qr_area_w = 58
            centered("AVALIE O", by + 12, 10, qr_area_x, qr_area_w)
            centered("JOGO!", by + 20, 10, qr_area_x, qr_area_w)
            qx, qy, _, _ = self.get_victory_qr_rect(screen_width, screen_height)
            draw_feedback_qr(qx, qy)
            centered("[F] OU QR", by + 82, 12, qr_area_x, qr_area_w)
            centered("FORMULARIO", by + 91, 7, qr_area_x, qr_area_w)
            return

        reason_title, reason_desc = GAME_OVER_TEXTS.get(self.game_over_reason, ("", ""))
        centered("[ RESCISAO DE CONTRATO ]", by + 8, 8)
        centered(reason_title, by + 18, 9)
        centered(reason_desc, by + 27, 7)
        centered(f"PONTUACAO FINAL: {self.score:05d}", by + 39, 10)
        centered(f"LIMPOS: {self.windows_cleaned}   REPAROS: {self.windows_repaired}", by + 48, 6)

        if self.can_retry and (pyxel.frame_count // 15) % 2 == 0:
            centered("TOQUE NA TELA OU [R]/[ESPACO] P/ RETENTAR", by + 60, 11)
