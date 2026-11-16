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
        # Coordenada (x, y) de tela de um novo toque fora da UI (para plantar âncora durante multi-touch)
        self.btnp_world_tap: tuple[float, float] | None = None

        # Histórico do frame anterior para detecção de borda de subida (btnp)
        self._prev_jump = False
        self._prev_clean = False
        self._prev_retrieve = False

        # Memória curta (grace/latch) do D-Pad para permitir salto direcional mesmo em telas
        # onde o navegador alterna o cursor único do D-Pad para o botão SALTO
        self._latched_horiz = 0       # -1 (esquerda), 0 (neutro), +1 (direita)
        self._horiz_grace_timer = 0
        self._latched_vert = 0        # -1 (cima), 0 (neutro), +1 (baixo)
        self._vert_grace_timer = 0

        # Lista opcional de toques simultâneos injetados (usado por multi-touch Web e testes)
        self.extra_touches: list[tuple[float, float]] = []

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

        self._web_multitouch_ready = False
        self._init_web_multitouch()

    def _init_web_multitouch(self):
        """Inicializa rastreador multi-touch HTML5 via Pyodide (js) quando rodando no navegador."""
        try:
            import js  # type: ignore

            js.eval(
                f"""
                if (!window._apexTouchTrackerInstalled) {{
                    window._apexTouchTrackerInstalled = true;
                    window._apexActiveTouches = [];
                    window._apexNewTouches = [];
                    const SCREEN_W = {self.screen_w};
                    const SCREEN_H = {self.screen_h};
                    const mapTouch = (t) => {{
                        const canvas = document.getElementById("canvas") || document.querySelector("canvas");
                        if (!canvas) return null;
                        const rect = canvas.getBoundingClientRect();
                        if (rect.width <= 0 || rect.height <= 0) return null;
                        const scale = Math.min(rect.width / SCREEN_W, rect.height / SCREEN_H);
                        const viewW = SCREEN_W * scale;
                        const viewH = SCREEN_H * scale;
                        const offsetX = rect.left + (rect.width - viewW) * 0.5;
                        const offsetY = rect.top + (rect.height - viewH) * 0.5;
                        const px = (t.clientX - offsetX) / scale;
                        const py = (t.clientY - offsetY) / scale;
                        if (px < -16 || px > SCREEN_W + 16 || py < -16 || py > SCREEN_H + 16) return null;
                        return [
                            Math.max(0, Math.min(SCREEN_W, px)),
                            Math.max(0, Math.min(SCREEN_H, py))
                        ];
                    }};
                    const inRect = (px, py, rx, ry, rw, rh, pad = 3) => (
                        px >= rx - pad && px <= rx + rw + pad &&
                        py >= ry - pad && py <= ry + rh + pad
                    );
                    const syncTouches = (e) => {{
                        const active = [];
                        if (e.touches) {{
                            for (let i = 0; i < e.touches.length; i++) {{
                                const pt = mapTouch(e.touches[i]);
                                if (pt) active.push(pt);
                            }}
                        }}
                        window._apexActiveTouches = active;
                        if (typeof _virtualGamepadStates !== "undefined") {{
                            let up = false, down = false, left = false, right = false;
                            let a = false, x = false, y = false;
                            for (let i = 0; i < active.length; i++) {{
                                const [px, py] = active[i];
                                if (inRect(px, py, 31, 102, 22, 22)) up = true;
                                if (inRect(px, py, 31, 150, 22, 22)) down = true;
                                if (inRect(px, py, 8, 126, 24, 22)) left = true;
                                if (inRect(px, py, 54, 126, 24, 22)) right = true;
                                if (inRect(px, py, 264, 136, 48, 28)) a = true;
                                if (inRect(px, py, 212, 136, 48, 28)) x = true;
                                if (inRect(px, py, 264, 104, 48, 26)) y = true;
                            }}
                            _virtualGamepadStates[0] = up;
                            _virtualGamepadStates[1] = down;
                            _virtualGamepadStates[2] = left;
                            _virtualGamepadStates[3] = right;
                            _virtualGamepadStates[4] = a;
                            _virtualGamepadStates[6] = x;
                            _virtualGamepadStates[7] = y;
                        }}
                        if (e.type === "touchstart" && e.changedTouches) {{
                            for (let i = 0; i < e.changedTouches.length; i++) {{
                                const pt = mapTouch(e.changedTouches[i]);
                                if (pt) window._apexNewTouches.push(pt);
                            }}
                        }}
                    }};
                    window.addEventListener("touchstart", syncTouches, {{ passive: true, capture: true }});
                    window.addEventListener("touchmove", syncTouches, {{ passive: true, capture: true }});
                    window.addEventListener("touchend", syncTouches, {{ passive: true, capture: true }});
                    window.addEventListener("touchcancel", syncTouches, {{ passive: true, capture: true }});
                }}
                """
            )
            self._web_multitouch_ready = True
        except BaseException:
            self._web_multitouch_ready = False

    def _read_web_touches(self) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
        """Lê todos os dedos ativos e novos toques registrados pelo navegador."""
        if not self._web_multitouch_ready:
            return ([], [])
        try:
            import js  # type: ignore

            raw_active = js.window._apexActiveTouches
            raw_new = js.window._apexNewTouches
            active = [(float(pt[0]), float(pt[1])) for pt in raw_active] if raw_active else []
            new_pts = [(float(pt[0]), float(pt[1])) for pt in raw_new] if raw_new else []
            if raw_new and len(new_pts) > 0:
                js.window._apexNewTouches = js.eval("[]")
            return (active, new_pts)
        except BaseException:
            return ([], [])

    @property
    def recent_horiz_dir(self) -> int:
        """Retorna a direção horizontal (-1, 0, +1) ativa ou recentemente segurada no D-Pad."""
        if self.btn_left and not self.btn_right:
            return -1
        if self.btn_right and not self.btn_left:
            return 1
        if self._horiz_grace_timer > 0:
            return self._latched_horiz
        return 0

    def _point_in_rect(self, px: float, py: float, rect: tuple[int, int, int, int], pad: float = 0.0) -> bool:
        rx, ry, rw, rh = rect
        return (rx - pad) <= px <= (rx + rw + pad) and (ry - pad) <= py <= (ry + rh + pad)

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
            if self._point_in_rect(screen_x, screen_y, r, pad=3.0):
                return True
        return False

    def update(self):
        """Atualiza a leitura dos toques na tela (incluindo multi-touch) e gamepads a cada frame."""
        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        is_touching = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
        is_touch_down = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)

        web_active, web_new = self._read_web_touches()

        # 1. Alternância de exibição dos controles de toque (tecla T ou clique no botão [TOUCH])
        toggle_clicked = is_touch_down and self._point_in_rect(mx, my, self.rect_toggle)
        if not toggle_clicked and web_new:
            toggle_clicked = any(self._point_in_rect(nx, ny, self.rect_toggle) for nx, ny in web_new)
        if pyxel.btnp(pyxel.KEY_T) or toggle_clicked:
            self.enabled = not self.enabled

        # Auto-reativação: se tocar nas áreas dos botões virtuais enquanto oculto, reexibe
        if not self.enabled and (is_touch_down or web_new):
            check_pts = [(mx, my)] if is_touch_down else []
            check_pts.extend(web_new)
            for px, py in check_pts:
                if any(
                    self._point_in_rect(px, py, r, pad=3.0)
                    for r in (self.rect_jump, self.rect_clean, self.rect_left, self.rect_right)
                ):
                    self.enabled = True
                    break

        # Detecta novos toques no mundo (fora dos botões virtuais) durante multi-touch
        self.btnp_world_tap = None
        for nx, ny in web_new:
            if not self.is_touching_ui(nx, ny):
                self.btnp_world_tap = (nx, ny)
                break

        # 2. Leitura dos botões virtuais de toque na tela (suporta múltiplos dedos simultâneos)
        touch_left = False
        touch_right = False
        touch_up = False
        touch_down = False
        touch_jump = False
        touch_clean = False
        touch_retrieve = False

        active_points: list[tuple[float, float]] = []
        if is_touching:
            active_points.append((float(mx), float(my)))
        if web_active:
            active_points.extend(web_active)
        if self.extra_touches:
            active_points.extend(self.extra_touches)

        # Também considera toques rápidos (tap de 1 frame em web_new) nos botões de ação
        tap_points = list(active_points)
        if web_new:
            tap_points.extend(web_new)

        if self.enabled and tap_points:
            for px, py in active_points:
                if self._point_in_rect(px, py, self.rect_left, pad=3.0):
                    touch_left = True
                if self._point_in_rect(px, py, self.rect_right, pad=3.0):
                    touch_right = True
                if self._point_in_rect(px, py, self.rect_up, pad=3.0):
                    touch_up = True
                if self._point_in_rect(px, py, self.rect_down, pad=3.0):
                    touch_down = True
                if self._point_in_rect(px, py, self.rect_clean, pad=3.0):
                    touch_clean = True

            for px, py in tap_points:
                if self._point_in_rect(px, py, self.rect_jump, pad=3.0):
                    touch_jump = True
                if self._point_in_rect(px, py, self.rect_clean, pad=3.0):
                    touch_clean = True
                if self._point_in_rect(px, py, self.rect_retrieve, pad=3.0):
                    touch_retrieve = True

        # Atualiza e aplica memória curta (latch/grace) do D-Pad:
        # Se o jogador estava segurando o D-Pad e o navegador/OS moveu o ponteiro único
        # para o botão SALTO/[E]/[R] ao tocar com o segundo polegar, mantém a direção ativa!
        if touch_left and not touch_right:
            self._latched_horiz = -1
            self._horiz_grace_timer = 10
        elif touch_right and not touch_left:
            self._latched_horiz = 1
            self._horiz_grace_timer = 10
        elif self._horiz_grace_timer > 0:
            self._horiz_grace_timer -= 1
            if self._horiz_grace_timer == 0:
                self._latched_horiz = 0

        if touch_up and not touch_down:
            self._latched_vert = -1
            self._vert_grace_timer = 10
        elif touch_down and not touch_up:
            self._latched_vert = 1
            self._vert_grace_timer = 10
        elif self._vert_grace_timer > 0:
            self._vert_grace_timer -= 1
            if self._vert_grace_timer == 0:
                self._latched_vert = 0

        action_touched = touch_jump or touch_clean or touch_retrieve
        if action_touched and not touch_left and not touch_right and self._horiz_grace_timer > 0:
            if self._latched_horiz < 0:
                touch_left = True
            elif self._latched_horiz > 0:
                touch_right = True
        if action_touched and not touch_up and not touch_down and self._vert_grace_timer > 0:
            if self._latched_vert < 0:
                touch_up = True
            elif self._latched_vert > 0:
                touch_down = True

        # 3. Suporte a Gamepad físico e virtual (D-Pad + Analógico Esquerdo + Botões A/B/X/Y)
        axis_x = 0
        axis_y = 0
        try:
            axis_x = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)
            axis_y = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)
        except BaseException:
            pass

        pad_left = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT) or (axis_x < -8000)
        pad_right = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT) or (axis_x > 8000)
        pad_up = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP) or (axis_y < -8000)
        pad_down = pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN) or (axis_y > 8000)
        pad_jump = pyxel.btn(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B)
        pad_clean = pyxel.btn(pyxel.GAMEPAD1_BUTTON_X)
        pad_retrieve = pyxel.btn(pyxel.GAMEPAD1_BUTTON_Y)

        if pad_left and not pad_right:
            self._latched_horiz = -1
            self._horiz_grace_timer = max(self._horiz_grace_timer, 6)
        elif pad_right and not pad_left:
            self._latched_horiz = 1
            self._horiz_grace_timer = max(self._horiz_grace_timer, 6)

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

    def draw(self, hide_controls: bool = False):
        """Renderiza os botões virtuais e botão de alternância no HUD."""
        # Durante o Game Over, oculta os controles de toque para manter a tela limpa
        if hide_controls:
            return

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

        # 2. BOTÕES DE AÇÃO (Canto inferior direito)
        # Botão SALTO
        jx, jy, jw, jh = self.rect_jump
        is_jump_active = self.btnp_jump or self._prev_jump
        j_col = 11 if is_jump_active else 12
        pyxel.rect(jx, jy, jw, jh, 1 if is_jump_active else 0)
        pyxel.rectb(jx, jy, jw, jh, j_col)
        pyxel.text(jx + 14, jy + 11, "SALTO", 7 if is_jump_active else 11)

        # Botão AÇÃO [E] (Limpar/Consertar)
        cx, cy, cw, ch = self.rect_clean
        c_col = 10 if self.btn_clean else 9
        pyxel.rect(cx, cy, cw, ch, 1 if self.btn_clean else 0)
        pyxel.rectb(cx, cy, cw, ch, c_col)
        pyxel.text(cx + 18, cy + 11, "[E]", 7 if self.btn_clean else 10)

        # Botão RECOLHER [R]
        rex, rey, rew, reh = self.rect_retrieve
        is_ret_active = self.btnp_retrieve or self._prev_retrieve
        re_col = 9 if is_ret_active else 5
        pyxel.rect(rex, rey, rew, reh, 1 if is_ret_active else 0)
        pyxel.rectb(rex, rey, rew, reh, re_col)
        pyxel.text(rex + 18, rey + 10, "[R]", 7 if is_ret_active else 9)

