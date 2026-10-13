import pyxel


class TouchControls:
    """Controlador de toque virtual na tela para dispositivos móveis (Android/celulares),

    com suporte simultâneo a Gamepads físicos (USB/Bluetooth) e teclado/mouse de Desktop.
    """

    def __init__(self, screen_w: int = 320, screen_h: int = 180):
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Visibilidade dos controles virtuais na tela
        # Ativo por padrão para suportar mobile/web imediatamente
        self.enabled = True

        # Estados contínuos de botões (segurando o toque ou botão)
        self.btn_left = False
        self.btn_right = False
        self.btn_up = False
        self.btn_down = False
        self.btn_clean = False

        # Estados de acionamento único (clique/tap apenas no frame inicial)
        self.btnp_jump = False
        self.btnp_clean = False
        self.btnp_retrieve = False

        # Histórico do frame anterior para detecção de borda de subida (btnp)
        self._prev_jump = False
        self._prev_clean = False
        self._prev_retrieve = False

        # Definição dos retângulos de toque em coordenadas de tela (320x180)
        # D-Pad (Canto inferior esquerdo: balanço horizontal e cabo vertical)
        self.rect_left = (8, 126, 24, 22)
        self.rect_right = (54, 126, 24, 22)
        self.rect_up = (31, 102, 22, 22)
        self.rect_down = (31, 150, 22, 22)

        # Botões de Ação (Canto inferior direito)
        self.rect_jump = (264, 136, 48, 28)      # Salto / Link no ar
        self.rect_clean = (212, 136, 48, 28)     # Limpar / Consertar [E]
        self.rect_retrieve = (264, 104, 48, 26)  # Recolher âncora [R]

        # Botão discreto para alternar modo touch (Canto superior direito, abaixo do placar)
        self.rect_toggle = (268, 32, 48, 11)

    def _point_in_rect(self, px: float, py: float, rect: tuple[int, int, int, int]) -> bool:
        rx, ry, rw, rh = rect
        return rx <= px <= rx + rw and ry <= py <= ry + rh

    def is_touching_ui(self, screen_x: float, screen_y: float) -> bool:
        """Verifica se as coordenadas do toque coincidem com algum botão da interface virtual.

        Se for True, o toque não deve ser interpretado como mira/disparo de âncora.
        """
        # Botão toggle permanece clicável mesmo se touch estiver desativado
        if self._point_in_rect(screen_x, screen_y, self.rect_toggle):
            return True

        if not self.enabled:
            return False

        for r in (
            self.rect_left,
            self.rect_right,
            self.rect_up,
            self.rect_down,
            self.rect_jump,
            self.rect_clean,
            self.rect_retrieve,
        ):
            if self._point_in_rect(screen_x, screen_y, r):
                return True
        return False

    def update(self):
        """Atualiza a leitura dos toques na tela e gamepads a cada frame."""
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        is_touching = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
        is_touch_down = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

        # 1. Alternância de exibição dos controles de toque (tecla T ou clique no botão [TOUCH])
        toggle_clicked = is_touch_down and self._point_in_rect(mx, my, self.rect_toggle)
        if pyxel.btnp(pyxel.KEY_T) or toggle_clicked:
            self.enabled = not self.enabled

        # Auto-reativação: se tocar nas áreas dos botões virtuais enquanto oculto, reexibe
        if not self.enabled and is_touch_down:
            for r in (self.rect_jump, self.rect_clean, self.rect_left, self.rect_right):
                if self._point_in_rect(mx, my, r):
                    self.enabled = True
                    break

        # 2. Leitura dos botões virtuais de toque na tela
        touch_left = False
        touch_right = False
        touch_up = False
        touch_down = False
        touch_jump = False
        touch_clean = False
        touch_retrieve = False

        if self.enabled and is_touching:
            touch_left = self._point_in_rect(mx, my, self.rect_left)
            touch_right = self._point_in_rect(mx, my, self.rect_right)
            touch_up = self._point_in_rect(mx, my, self.rect_up)
            touch_down = self._point_in_rect(mx, my, self.rect_down)
            touch_jump = self._point_in_rect(mx, my, self.rect_jump)
            touch_clean = self._point_in_rect(mx, my, self.rect_clean)
            touch_retrieve = self._point_in_rect(mx, my, self.rect_retrieve)

        # 3. Suporte a Gamepad físico (Android via Bluetooth/OTG e Desktop)
        pad_left = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
        pad_right = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        pad_up = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
        pad_down = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
        pad_jump = pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)
        pad_clean = pyxel.btn(pyxel.GAMEPAD1_BUTTON_X)
        pad_retrieve = pyxel.btn(pyxel.GAMEPAD1_BUTTON_Y)

        # 4. Combina toques virtuais e gamepad
        self.btn_left = touch_left or pad_left
        self.btn_right = touch_right or pad_right
        self.btn_up = touch_up or pad_up
        self.btn_down = touch_down or pad_down
        self.btn_clean = touch_clean or pad_clean

        # Detecção de pulso único (btnp)
        curr_jump = touch_jump or pad_jump
        curr_clean = touch_clean or pad_clean
        curr_retrieve = touch_retrieve or pad_retrieve

        self.btnp_jump = curr_jump and not self._prev_jump
        self.btnp_clean = curr_clean and not self._prev_clean
        self.btnp_retrieve = curr_retrieve and not self._prev_retrieve

        self._prev_jump = curr_jump
        self._prev_clean = curr_clean
        self._prev_retrieve = curr_retrieve

    def draw(self):
        """Renderiza os botões virtuais e botão de alternância no HUD."""
        # Botão de alternar modo Touch (sempre presente discretamente no topo)
        tx, ty, tw, th = self.rect_toggle
        toggle_col = 11 if self.enabled else 5
        pyxel.rect(tx, ty, tw, th, 0)
        pyxel.rectb(tx, ty, tw, th, toggle_col)
        label = "[TOUCH]" if self.enabled else "[MOUSE]"
        pyxel.text(tx + 4, ty + 3, label, toggle_col)

        if not self.enabled:
            return

        # 1. D-PAD VIRTUAL (Canto inferior esquerdo)
        # Hub central
        pyxel.rect(31, 126, 22, 22, 0)
        pyxel.rectb(31, 126, 22, 22, 5)

        # Botão ESQUERDA (Balanço Esquerdo)
        lx, ly, lw, lh = self.rect_left
        l_col = 12 if self.btn_left else 5
        pyxel.rect(lx, ly, lw, lh, 1 if self.btn_left else 0)
        pyxel.rectb(lx, ly, lw, lh, l_col)
        pyxel.tri(lx + 6, ly + 11, lx + 16, ly + 5, lx + 16, ly + 17, 7 if self.btn_left else 6)

        # Botão DIREITA (Balanço Direito)
        rx, ry, rw, rh = self.rect_right
        r_col = 12 if self.btn_right else 5
        pyxel.rect(rx, ry, rw, rh, 1 if self.btn_right else 0)
        pyxel.rectb(rx, ry, rw, rh, r_col)
        pyxel.tri(rx + 18, ry + 11, rx + 8, ry + 5, rx + 8, ry + 17, 7 if self.btn_right else 6)

        # Botão CIMA (Subir na corda)
        ux, uy, uw, uh = self.rect_up
        u_col = 12 if self.btn_up else 5
        pyxel.rect(ux, uy, uw, uh, 1 if self.btn_up else 0)
        pyxel.rectb(ux, uy, uw, uh, u_col)
        pyxel.tri(ux + 11, uy + 5, ux + 5, uy + 15, ux + 17, uy + 15, 7 if self.btn_up else 6)

        # Botão BAIXO (Descer na corda)
        dx, dy, dw, dh = self.rect_down
        d_col = 12 if self.btn_down else 5
        pyxel.rect(dx, dy, dw, dh, 1 if self.btn_down else 0)
        pyxel.rectb(dx, dy, dw, dh, d_col)
        pyxel.tri(dx + 11, dy + 17, dx + 5, dy + 7, dx + 17, dy + 7, 7 if self.btn_down else 6)

        # Rótulo de auxílio no D-Pad
        pyxel.text(lx + 2, ly - 8, "BALANCO/CABO", 5)

        # 2. BOTÕES DE AÇÃO (Canto inferior direito)
        # Botão SALTO / LINK
        jx, jy, jw, jh = self.rect_jump
        is_jump_active = self.btnp_jump or self._prev_jump
        j_col = 11 if is_jump_active else 12
        pyxel.rect(jx, jy, jw, jh, 1 if is_jump_active else 0)
        pyxel.rectb(jx, jy, jw, jh, j_col)
        pyxel.text(jx + 14, jy + 6, "SALTO", 7 if is_jump_active else 11)
        pyxel.text(jx + 16, jy + 16, "LINK", 6)

        # Botão LIMPAR / REPARAR [E]
        cx, cy, cw, ch = self.rect_clean
        c_col = 10 if self.btn_clean else 9
        pyxel.rect(cx, cy, cw, ch, 1 if self.btn_clean else 0)
        pyxel.rectb(cx, cy, cw, ch, c_col)
        pyxel.text(cx + 12, cy + 6, "LIMPAR", 7 if self.btn_clean else 10)
        pyxel.text(cx + 18, cy + 16, "[E]", 6)

        # Botão RECOLHER [R]
        rex, rey, rew, reh = self.rect_retrieve
        is_ret_active = self.btnp_retrieve or self._prev_retrieve
        re_col = 9 if is_ret_active else 5
        pyxel.rect(rex, rey, rew, reh, 1 if is_ret_active else 0)
        pyxel.rectb(rex, rey, rew, reh, re_col)
        pyxel.text(rex + 10, rey + 5, "REC [R]", 7 if is_ret_active else 9)
        pyxel.text(rex + 11, rey + 14, "ANCORA", 5)
