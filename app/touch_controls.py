import math
import pyxel


class TouchControls:
    """Controlador de toque virtual na tela para dispositivos móveis (Android/celulares),

    com Joystick Virtual analógico circular arrastável, suporte multi-touch simultâneo
    a botões de ação e compatibilidade com Gamepads físicos e teclado/mouse de Desktop.
    """

    def __init__(self, screen_w: int = 320, screen_h: int = 180):
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Visibilidade dos controles virtuais na tela
        # Ativo por padrão para suportar mobile/web imediatamente
        self.enabled = True

        # Estados contínuos de direção e ação (segurando o joystick ou botão)
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

        # Memória curta (grace/latch) do joystick para permitir salto direcional mesmo em telas
        # onde o navegador alterna o ponteiro único do joystick para o botão SALTO
        self._latched_horiz = 0       # -1 (esquerda), 0 (neutro), +1 (direita)
        self._horiz_grace_timer = 0
        self._latched_vert = 0        # -1 (cima), 0 (neutro), +1 (baixo)
        self._vert_grace_timer = 0

        # Lista opcional de toques simultâneos injetados (usado por multi-touch Web e testes)
        self.extra_touches: list[tuple[float, float]] = []

        # Configuração do Joystick Virtual circular (canto inferior esquerdo)
        self.joy_cx = 42
        self.joy_cy = 138
        self.joy_radius = 26          # Raio visual da base circular e curso máximo do stick
        self.joy_grab_radius = 36     # Raio de captura inicial do toque no joystick
        self.joy_drag_radius = 72     # Raio máximo mantendo o arraste ativo sem escapar
        self.joy_deadzone = 6.0       # Zona morta central antes de acionar direção
        self.joy_knob_radius = 9      # Raio da alavanca/cabeça móvel do joystick

        self.joy_active = False
        self.joy_knob_x = float(self.joy_cx)
        self.joy_knob_y = float(self.joy_cy)
        self.joy_dx = 0.0             # Vetor normalizado [-1.0, 1.0]
        self.joy_dy = 0.0

        # Retângulos equivalentes às zonas do joystick (mantidos por compatibilidade)
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
        """Inicializa rastreador multi-touch HTML5 via Pyodide (js) e oculta botões nativos do Pyxel."""
        try:
            import js  # type: ignore

            js.eval(
                f"""
                (() => {{
                    // Remove/oculta qualquer gamepad virtual nativo do Pyxel Web e restaura o canvas a 100%
                    const hideNativePyxelGamepad = () => {{
                        for (const id of ["pyxel-gamepad-cross", "pyxel-gamepad-button", "pyxel-gamepad-menu"]) {{
                            const el = document.getElementById(id);
                            if (el) el.style.display = "none";
                        }}
                        const c = document.getElementById("canvas");
                        if (c && c.style.height === "80%") c.style.height = "100%";
                    }};
                    hideNativePyxelGamepad();
                    setTimeout(hideNativePyxelGamepad, 200);
                    setTimeout(hideNativePyxelGamepad, 1000);

                    if (!window._apexTouchTrackerInstalled) {{
                        window._apexTouchTrackerInstalled = true;
                        window._apexActiveTouches = [];
                        window._apexNewTouches = [];
                        const SCREEN_W = {self.screen_w};
                        const SCREEN_H = {self.screen_h};
                        const JOY_CX = {self.joy_cx};
                        const JOY_CY = {self.joy_cy};
                        const JOY_GRAB_R = {self.joy_drag_radius};
                        const JOY_DEADZONE = {self.joy_deadzone};
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
                            if (px < -24 || px > SCREEN_W + 24 || py < -24 || py > SCREEN_H + 24) return null;
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
                            hideNativePyxelGamepad();
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
                                    const dx = px - JOY_CX;
                                    const dy = py - JOY_CY;
                                    if (Math.hypot(dx, dy) <= JOY_GRAB_R && px < 140) {{
                                        if (dy <= -JOY_DEADZONE) up = true;
                                        if (dy >= JOY_DEADZONE) down = true;
                                        if (dx <= -JOY_DEADZONE) left = true;
                                        if (dx >= JOY_DEADZONE) right = true;
                                    }}
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
                }})();
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
        """Retorna a direção horizontal (-1, 0, +1) ativa ou recentemente segurada no joystick."""
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

    def _point_in_joystick(self, px: float, py: float, allow_drag_zone: bool = False) -> bool:
        max_r = self.joy_drag_radius if allow_drag_zone else self.joy_grab_radius
        return px < 140.0 and math.hypot(px - self.joy_cx, py - self.joy_cy) <= max_r

    def is_touching_ui(self, screen_x: float, screen_y: float) -> bool:
        """Verifica se as coordenadas do toque coincidem com o joystick ou algum botão virtual.

        Se for True, o toque não deve ser interpretado como mira/disparo de âncora.
        """
        # Botão toggle permanece clicável mesmo se touch estiver desativado
        if self._point_in_rect(screen_x, screen_y, self.rect_toggle):
            return True

        if not self.enabled:
            return False

        if self._point_in_joystick(screen_x, screen_y, allow_drag_zone=self.joy_active):
            return True

        for r in (
            self.rect_jump,
            self.rect_clean,
            self.rect_retrieve,
        ):
            if self._point_in_rect(screen_x, screen_y, r, pad=3.0):
                return True
        return False

    def update(self):
        """Atualiza a leitura do joystick virtual, botões de toque (multi-touch) e gamepads."""
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

        # Auto-reativação: se tocar no joystick ou botões virtuais enquanto oculto, reexibe
        if not self.enabled and (is_touch_down or web_new):
            check_pts = [(float(mx), float(my))] if is_touch_down else []
            check_pts.extend(web_new)
            for px, py in check_pts:
                if self._point_in_joystick(px, py) or any(
                    self._point_in_rect(px, py, r, pad=3.0)
                    for r in (self.rect_jump, self.rect_clean)
                ):
                    self.enabled = True
                    break

        # Detecta novos toques no mundo (fora do joystick e dos botões) durante multi-touch
        self.btnp_world_tap = None
        for nx, ny in web_new:
            if not self.is_touching_ui(nx, ny):
                self.btnp_world_tap = (nx, ny)
                break

        # 2. Leitura do Joystick Virtual e Botões de Ação (suporta múltiplos dedos simultâneos)
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

        tap_points = list(active_points)
        if web_new:
            tap_points.extend(web_new)

        joy_point: tuple[float, float] | None = None

        if self.enabled and tap_points:
            # Procura dedo que está controlando o joystick (mais próximo do centro do joystick)
            best_joy_dist = 9999.0
            for px, py in active_points:
                # Ignora dedos que estão claramente nos botões de ação da direita
                if px >= 180.0:
                    continue
                if self._point_in_joystick(px, py, allow_drag_zone=self.joy_active):
                    d = math.hypot(px - self.joy_cx, py - self.joy_cy)
                    if d < best_joy_dist:
                        best_joy_dist = d
                        joy_point = (px, py)

            for px, py in active_points:
                if self._point_in_rect(px, py, self.rect_clean, pad=3.0):
                    touch_clean = True

            for px, py in tap_points:
                if self._point_in_rect(px, py, self.rect_jump, pad=3.0):
                    touch_jump = True
                if self._point_in_rect(px, py, self.rect_clean, pad=3.0):
                    touch_clean = True
                if self._point_in_rect(px, py, self.rect_retrieve, pad=3.0):
                    touch_retrieve = True

        # Atualiza estado e posição da alavanca do Joystick Virtual
        if joy_point is not None:
            self.joy_active = True
            dx = joy_point[0] - self.joy_cx
            dy = joy_point[1] - self.joy_cy
            dist = math.hypot(dx, dy)
            if dist > self.joy_radius and dist > 0.0:
                scale = self.joy_radius / dist
                self.joy_knob_x = self.joy_cx + dx * scale
                self.joy_knob_y = self.joy_cy + dy * scale
            else:
                self.joy_knob_x = joy_point[0]
                self.joy_knob_y = joy_point[1]

            self.joy_dx = max(-1.0, min(1.0, dx / float(self.joy_radius)))
            self.joy_dy = max(-1.0, min(1.0, dy / float(self.joy_radius)))

            if dx <= -self.joy_deadzone:
                touch_left = True
            elif dx >= self.joy_deadzone:
                touch_right = True

            if dy <= -self.joy_deadzone:
                touch_up = True
            elif dy >= self.joy_deadzone:
                touch_down = True
        else:
            self.joy_active = False
            self.joy_knob_x = float(self.joy_cx)
            self.joy_knob_y = float(self.joy_cy)
            self.joy_dx = 0.0
            self.joy_dy = 0.0

        # Memória curta (latch/grace) do Joystick:
        # Se o jogador estava segurando o joystick e o navegador moveu o ponteiro único
        # para o botão SALTO/[E]/[R] ao tocar com o outro polegar, mantém a direção ativa!
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
                self.joy_knob_x = float(self.joy_cx - self.joy_radius * 0.75)
            elif self._latched_horiz > 0:
                touch_right = True
                self.joy_knob_x = float(self.joy_cx + self.joy_radius * 0.75)
        if action_touched and not touch_up and not touch_down and self._vert_grace_timer > 0:
            if self._latched_vert < 0:
                touch_up = True
                self.joy_knob_y = float(self.joy_cy - self.joy_radius * 0.75)
            elif self._latched_vert > 0:
                touch_down = True
                self.joy_knob_y = float(self.joy_cy + self.joy_radius * 0.75)

        # 3. Suporte a Gamepad físico (D-Pad + Analógico Esquerdo + Botões A/B/X/Y)
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

        # Se controlado por teclado/gamepad sem toque no joystick, move visualmente a alavanca
        if not self.joy_active:
            if self.btn_left and not self.btn_right:
                self.joy_knob_x = float(self.joy_cx - self.joy_radius * 0.7)
            elif self.btn_right and not self.btn_left:
                self.joy_knob_x = float(self.joy_cx + self.joy_radius * 0.7)
            if self.btn_up and not self.btn_down:
                self.joy_knob_y = float(self.joy_cy - self.joy_radius * 0.7)
            elif self.btn_down and not self.btn_up:
                self.joy_knob_y = float(self.joy_cy + self.joy_radius * 0.7)

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
        """Renderiza o Joystick Virtual circular, botões de ação e botão de alternância no HUD."""
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

        # 1. JOYSTICK VIRTUAL ANALÓGICO (Canto inferior esquerdo)
        cx = self.joy_cx
        cy = self.joy_cy
        r = self.joy_radius
        kx = int(round(self.joy_knob_x))
        ky = int(round(self.joy_knob_y))
        is_deflected = (
            self.joy_active
            or self.btn_left
            or self.btn_right
            or self.btn_up
            or self.btn_down
        )

        # Base circular escura com anel duplo e marcações de eixo
        pyxel.circ(cx, cy, r, 0)
        pyxel.circb(cx, cy, r, 12 if is_deflected else 5)
        pyxel.circb(cx, cy, r - 2, 1)
        pyxel.line(cx - r + 4, cy, cx + r - 4, cy, 1)
        pyxel.line(cx, cy - r + 4, cx, cy + r - 4, 1)
        pyxel.circb(cx, cy, int(self.joy_deadzone), 5)

        # Haste central ligando a base à cabeça da alavanca
        if kx != cx or ky != cy:
            pyxel.line(cx, cy, kx, ky, 6)

        # Cabeça móvel (thumbstick) do joystick
        kr = self.joy_knob_radius
        pyxel.circ(kx, ky, kr, 12 if is_deflected else 5)
        pyxel.circb(kx, ky, kr, 7 if is_deflected else 6)
        pyxel.pset(kx - 2, ky - 2, 7)

        # 2. BOTÕES DE AÇÃO (Canto inferior direito)
        # Botão SALTO
        jx, jy, jw, jh = self.rect_jump
        is_jump_active = self.btnp_jump or self._prev_jump
        j_col = 11 if is_jump_active else 12
        pyxel.rect(jx, jy, jw, jh, 1 if is_jump_active else 0)
        pyxel.rectb(jx, jy, jw, jh, j_col)
        pyxel.text(jx + 14, jy + 11, "SALTO", 7 if is_jump_active else 11)

        # Botão AÇÃO [E] (Limpar/Consertar)
        acx, acy, acw, ach = self.rect_clean
        c_col = 10 if self.btn_clean else 9
        pyxel.rect(acx, acy, acw, ach, 1 if self.btn_clean else 0)
        pyxel.rectb(acx, acy, acw, ach, c_col)
        pyxel.text(acx + 18, acy + 11, "[E]", 7 if self.btn_clean else 10)

        # Botão RECOLHER [R]
        rex, rey, rew, reh = self.rect_retrieve
        is_ret_active = self.btnp_retrieve or self._prev_retrieve
        re_col = 9 if is_ret_active else 5
        pyxel.rect(rex, rey, rew, reh, 1 if is_ret_active else 0)
        pyxel.rectb(rex, rey, rew, reh, re_col)
        pyxel.text(rex + 18, rey + 10, "[R]", 7 if is_ret_active else 9)
