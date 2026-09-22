import math
import pyxel

# Constantes do Sistema de Ancoragem (conforme GDD)
MAX_ANCHORS = 3
MAX_PLANT_RANGE = 145.0       # Alcance máximo para disparar nova âncora
MIN_ROPE_LENGTH = 28.0        # Comprimento mínimo da corda (subir)
MAX_ROPE_LENGTH = 82.0       # Comprimento máximo da corda (descer)

# Regras de Atracamento / Link no ar:
# Menos livre horizontalmente (player deve estar na coluna do apoio)
# Mais livre verticalmente (faixa vertical ampla de suspensão abaixo do apoio)
LINK_X_TOLERANCE = 55.0       # Tolerância horizontal (+/- pixels em relação ao eixo X do apoio)
LINK_Y_MIN = 15.0             # Distância vertical mínima abaixo do apoio
LINK_Y_MAX = 75.0            # Distância vertical máxima abaixo do apoio (alcance do cabo)

# Estados do Jogador
STATE_ANCHORED = "ANCHORED"   # Conectado à corda ativa
STATE_AIRBORNE = "AIRBORNE"   # Em salto / queda livre após desconexão
STATE_FATAL_FALL = "FATAL_FALL"  # Game over por queda


class Anchor:
    """Representa um ponto de ancoragem fixado na fachada do arranha-céu."""

    def __init__(self, x: float, y: float, is_active: bool = False):
        self.x = float(x)
        self.y = float(y)
        self.is_active = is_active
        self.pulse_timer = 0

    def update(self):
        self.pulse_timer = (self.pulse_timer + 1) % 60

    def draw(self, is_link_candidate: bool = False, show_guide_beam: bool = False):
        ax = int(self.x)
        ay = int(self.y)

        # Base metálica do grampo (cor 5: cinza escuro, contorno 0: preto)
        pyxel.rect(ax - 3, ay - 2, 7, 4, 5)
        pyxel.rectb(ax - 3, ay - 2, 7, 4, 0)

        # Parafusos industriais laterais (cor 6: cinza aço)
        pyxel.pset(ax - 2, ay, 6)
        pyxel.pset(ax + 2, ay, 6)

        # LED Indicador de status:
        # - Ativa: Verde néon (11)
        # - Candidata a link: Ciano pulsante (12 / 7)
        # - Inativa à espera: Laranja néon (9)
        if self.is_active:
            led_color = 11
        elif is_link_candidate:
            led_color = 12 if (self.pulse_timer // 5) % 2 == 0 else 7
        else:
            led_color = 9

        pyxel.pset(ax, ay - 1, led_color)

        # Argola/mosquetão onde a corda engata
        pyxel.pset(ax, ay + 2, 6)

        # Feixe guia holográfico da coluna vertical quando o player está no ar
        if not self.is_active and show_guide_beam:
            beam_color = 12 if is_link_candidate else 5
            for gy in range(ay + int(LINK_Y_MIN), ay + int(LINK_Y_MAX), 8):
                pyxel.pset(ax, gy, beam_color)

        # Se for candidata a link no ar ou pronta para salto, exibe retículo holográfico
        if is_link_candidate:
            radius = 5 + (self.pulse_timer % 4)
            pyxel.circb(ax, ay, radius, 12)
            pyxel.text(ax - 14, ay - 10, "LINK OK", 11)


class PlayerAnchorSystem:
    """Gerencia as 3 âncoras, física pendular na corda ativa, salto com momentum,

    verificação de alinhamento no eixo Y para link e condição de queda fatal.
    """

    def __init__(self, start_anchor_x=160, start_anchor_y=25, initial_rope_length=65):
        self.initial_anchor_x = float(start_anchor_x)
        self.initial_anchor_y = float(start_anchor_y)
        self.initial_rope_length = float(initial_rope_length)

        # Configurações de fixação no arnês do personagem (sprite 32x32)
        self.harness_offset_x = 8
        self.harness_offset_y = 10

        # Inicializa o estado do sistema
        self.reset()

        # Configuração de áudio chiptune Pyxel
        self.init_sounds()

    def init_sounds(self):
        """Configura os efeitos sonoros chiptune do sistema de ancoragem."""
        try:
            # Som 0: Fixação de nova âncora (trava metálica)
            pyxel.sounds[0].set("g2c3", "p", "64", "f", 4)
            # Som 1: Recolher âncora
            pyxel.sounds[1].set("c3g2", "p", "53", "f", 4)
            # Som 2: Salto (impulso de vento)
            pyxel.sounds[2].set("c2e2g2", "s", "432", "s", 3)
            # Som 3: Reconexão de Link bem-sucedida (trava firme)
            pyxel.sounds[3].set("e2g2c3", "t", "667", "v", 5)
            # Som 4: Falha no link / desalinhado (zumbido de erro)
            pyxel.sounds[4].set("f1d1", "n", "64", "f", 6)
            # Som 5: Queda fatal (alarme corporativo)
            pyxel.sounds[5].set("c2r1c2r1c2", "p", "70707", "v", 8)
        except BaseException:
            pass

    def play_sound(self, sound_id: int):
        try:
            pyxel.play(0, sound_id)
        except BaseException:
            pass

    def reset(self):
        """Reinicia o jogador na âncora padrão inicial."""
        self.anchors = [Anchor(self.initial_anchor_x, self.initial_anchor_y, is_active=True)]
        self.state = STATE_ANCHORED

        self.rope_length = float(self.initial_rope_length)
        self.angle = 0.0
        self.angular_vel = 0.0
        self.sway_timer = 0

        # Posição do sprite
        self.x = self.initial_anchor_x - self.harness_offset_x
        self.y = self.initial_anchor_y + self.rope_length - self.harness_offset_y

        self.vx = 0.0
        self.vy = 0.0
        self.source_anchor = None
        self.source_anchor_y = self.initial_anchor_y
        self.camera_x = 0.0
        self.camera_y = 0.0

        self.action = "IDLE"
        self.feedback_msg = ""
        self.feedback_timer = 0
        self.feedback_color = 7

    def set_feedback(self, msg: str, duration: int = 45, color: int = 7):
        self.feedback_msg = msg
        self.feedback_timer = duration
        self.feedback_color = color

    def get_active_anchor(self) -> Anchor | None:
        for a in self.anchors:
            if a.is_active:
                return a
        return None

    def get_harness_pos(self) -> tuple[float, float]:
        return (self.x + self.harness_offset_x, self.y + self.harness_offset_y)

    def find_link_candidate(self, cursor_x: float = None, cursor_y: float = None) -> Anchor | None:
        """Encontra uma âncora inativa plantada onde o jogador, durante o salto,

        possui o alinhamento vertical com o apoio (coluna horizontal do apoio e faixa Y de suspensão).
        """
        hx, hy = self.get_harness_pos()
        best_anchor = None
        best_dist = 9999.0

        for a in self.anchors:
            # Não conecta a âncora ativa ou à âncora da qual acabou de saltar
            if a.is_active or (self.state == STATE_AIRBORNE and a == self.source_anchor):
                continue

            # 1. Alinhamento horizontal com a coluna do apoio (menos livre horizontalmente)
            dx = abs(hx - a.x)
            if dx > LINK_X_TOLERANCE:
                continue

            # 2. Faixa vertical Y abaixo do apoio (mais livre verticalmente, dentro do alcance do cabo)
            dy = hy - a.y
            if dy < LINK_Y_MIN or dy > LINK_Y_MAX:
                continue

            # Se estiver na área válida, seleciona o apoio (priorizando mira do cursor se informada)
            if cursor_x is not None and cursor_y is not None:
                dist = math.hypot(cursor_x - a.x, cursor_y - a.y)
            else:
                dist = math.hypot(dx, dy)

            if dist < best_dist:
                best_dist = dist
                best_anchor = a

        return best_anchor

    def plant_anchor(self, target_x: float, target_y: float) -> bool:
        """Planta uma nova âncora na fachada, caso haja menos de 3 no total."""
        if len(self.anchors) >= MAX_ANCHORS:
            self.set_feedback("LIMITE: 3 ANCORAS! RECOLHA UMA [DIR/R]", 60, 8)
            return False

        hx, hy = self.get_harness_pos()
        dist = math.hypot(target_x - hx, target_y - hy)
        if dist > MAX_PLANT_RANGE:
            self.set_feedback("FORA DE ALCANCE DA ARMA", 45, 9)
            return False

        # Evita plantar exatamente em cima de outra âncora
        for a in self.anchors:
            if math.hypot(target_x - a.x, target_y - a.y) < 12.0:
                self.set_feedback("LOCAL JA OCUPADO", 45, 9)
                return False

        new_anchor = Anchor(target_x, target_y, is_active=False)
        self.anchors.append(new_anchor)
        self.play_sound(0)
        self.set_feedback(f"ANCORA PLANTADA ({len(self.anchors)}/3)", 45, 11)
        return True

    def retrieve_anchor(self, cursor_x: float = None, cursor_y: float = None) -> bool:
        """Recolhe uma âncora já plantada inativa, liberando slot."""
        inactive_anchors = [a for a in self.anchors if not a.is_active]
        if not inactive_anchors:
            self.set_feedback("NENHUMA ANCORA INATIVA PARA RECOLHER", 45, 9)
            return False

        target = None
        if cursor_x is not None and cursor_y is not None:
            # Procura primeiro se há alguma próxima do cursor (até 30px)
            for a in inactive_anchors:
                if math.hypot(cursor_x - a.x, cursor_y - a.y) < 30.0:
                    target = a
                    break

        if target is None:
            # Pega a mais próxima do jogador
            hx, hy = self.get_harness_pos()
            target = min(inactive_anchors, key=lambda a: math.hypot(hx - a.x, hy - a.y))

        self.anchors.remove(target)
        self.play_sound(1)
        self.set_feedback(f"ANCORA RECOLHIDA ({len(self.anchors)}/3)", 45, 10)
        return True

    def jump(self):
        """Executa o salto a partir da corda ativa, desconectando o cabo

        e transferindo o momentum angular para queda livre.
        """
        active = self.get_active_anchor()
        if not active or self.state != STATE_ANCHORED:
            return

        self.source_anchor = active
        self.source_anchor_y = active.y
        active.is_active = False
        self.state = STATE_AIRBORNE

        # Conservação do momento linear tangencial do pêndulo
        # v_x = omega * L * cos(theta), v_y = -omega * L * sin(theta)
        tangential_speed = self.angular_vel * self.rope_length
        self.vx = tangential_speed * math.cos(self.angle)
        self.vy = -tangential_speed * math.sin(self.angle) - 2.0  # Impulso para cima

        self.play_sound(2)
        self.set_feedback("SALTO! PRESSIONE [ESPACO] PARA LINK", 60, 10)

    def try_link(self, cursor_x: float = None, cursor_y: float = None) -> bool:
        """Tenta reconectar a uma âncora já plantada enquanto no ar."""
        if self.state != STATE_AIRBORNE:
            return False

        candidate = self.find_link_candidate(cursor_x, cursor_y)
        if candidate:
            # Conexão bem-sucedida!
            candidate.is_active = True
            self.source_anchor = None
            self.state = STATE_ANCHORED

            hx, hy = self.get_harness_pos()
            dx = hx - candidate.x
            dy = hy - candidate.y
            dist = math.hypot(dx, dy)

            self.rope_length = max(MIN_ROPE_LENGTH, min(MAX_ROPE_LENGTH, dist))
            self.angle = math.atan2(dx, dy)

            # Projeção da velocidade linear no movimento pendular da nova âncora
            tangential_v = self.vx * math.cos(self.angle) - self.vy * math.sin(self.angle)
            self.angular_vel = tangential_v / self.rope_length

            self.play_sound(3)
            self.set_feedback("LINK COM SUCESSO!", 45, 11)
            return True
        else:
            # Falha de link com feedback contextual
            self.play_sound(4)
            hx, hy = self.get_harness_pos()
            inactives = [a for a in self.anchors if not a.is_active and a != self.source_anchor]
            if not inactives:
                self.set_feedback("NENHUM APOIO PLANTADO!", 45, 8)
            else:
                nearest = min(inactives, key=lambda a: math.hypot(hx - a.x, hy - a.y))
                dx = abs(hx - nearest.x)
                dy = hy - nearest.y
                if dx > LINK_X_TOLERANCE:
                    self.set_feedback("FORA DA COLUNA DO APOIO!", 45, 8)
                elif dy < LINK_Y_MIN:
                    self.set_feedback("MUITO ALTO P/ ATRACAR!", 45, 8)
                elif dy > LINK_Y_MAX:
                    self.set_feedback("MUITO BAIXO P/ ATRACAR!", 45, 8)
                else:
                    self.set_feedback("SEM ALINHAMENTO COM O APOIO!", 45, 8)
            return False

    def update(self, camera_x: float = 0.0, camera_y: float = 0.0, screen_height: float = 180.0):
        """Atualiza a simulação física do jogador e o gerenciador de âncoras."""
        self.camera_x = camera_x
        self.camera_y = camera_y

        for a in self.anchors:
            a.update()

        if self.feedback_timer > 0:
            self.feedback_timer -= 1

        if self.state == STATE_ANCHORED:
            self._update_anchored(camera_x, camera_y)
        elif self.state == STATE_AIRBORNE:
            self._update_airborne(camera_x, camera_y, screen_height)
        elif self.state == STATE_FATAL_FALL:
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset()

    def _update_anchored(self, camera_x: float = 0.0, camera_y: float = 0.0):
        active = self.get_active_anchor()
        if not active:
            # Se não houver âncora ativa, entra em queda livre
            self.state = STATE_AIRBORNE
            return

        self.source_anchor_y = active.y
        is_moving_horiz = False
        is_moving_vert = False

        # 1. Controles de balanço no pêndulo (A/D ou setas)
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
            self.angular_vel -= 0.004
            self.action = "SWING_LEFT"
            is_moving_horiz = True
        elif pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
            self.angular_vel += 0.004
            self.action = "SWING_RIGHT"
            is_moving_horiz = True

        # 2. Controles de subida e descida na corda (W/S ou setas)
        if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP):
            self.rope_length = max(MIN_ROPE_LENGTH, self.rope_length - 1.2)
            if not is_moving_horiz:
                self.action = "CLIMB_UP"
            is_moving_vert = True
        elif pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
            self.rope_length = min(MAX_ROPE_LENGTH, self.rope_length + 1.2)
            if not is_moving_horiz:
                self.action = "CLIMB_DOWN"
            is_moving_vert = True

        # 3. Física de pêndulo simples
        # Aceleração da gravidade tangencial
        gravity_acc = -(0.22 / self.rope_length) * math.sin(self.angle)
        self.angular_vel += gravity_acc
        self.angular_vel *= 0.993  # Amortecimento natural do ar/cabo
        self.angular_vel = max(-0.085, min(0.085, self.angular_vel))
        self.angle += self.angular_vel

        # Se em repouso absoluto sem inputs, aplica micro-balanço atmosférico do Apex-01
        effective_angle = self.angle
        if not is_moving_horiz and not is_moving_vert and abs(self.angular_vel) < 0.003 and abs(self.angle) < 0.05:
            self.action = "IDLE"
            self.sway_timer += 1
            effective_angle += math.sin(self.sway_timer * 0.045) * 0.035

        # Posição calculada do arnês e do sprite
        hx = active.x + math.sin(effective_angle) * self.rope_length
        hy = active.y + math.cos(effective_angle) * self.rope_length
        self.x = hx - self.harness_offset_x
        self.y = hy - self.harness_offset_y

        # Mantém velocidade tangencial calculada para salto imediato
        tangential = self.angular_vel * self.rope_length
        self.vx = tangential * math.cos(effective_angle)
        self.vy = -tangential * math.sin(effective_angle)

        # 4. Salto (ESPAÇO)
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.jump()

        # Coordenadas do mouse no espaço de mundo
        world_mouse_x = camera_x + pyxel.mouse_x
        world_mouse_y = camera_y + pyxel.mouse_y

        # 5. Ação de plantar âncora (Mouse Esq)
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.plant_anchor(world_mouse_x, world_mouse_y)

        # 6. Ação de recolher âncora (Mouse Dir ou R)
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT) or pyxel.btnp(pyxel.KEY_R):
            self.retrieve_anchor(world_mouse_x, world_mouse_y)

    def _update_airborne(self, camera_x: float = 0.0, camera_y: float = 0.0, screen_height: float = 180.0):
        self.action = "AIRBORNE"

        # Gravidade linear e resistência do ar
        self.vy += 0.16
        self.vx *= 0.992

        # Controle direcional leve no ar
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
            self.vx -= 0.08
        if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
            self.vx += 0.08

        self.x += self.vx
        self.y += self.vy

        world_mouse_x = camera_x + pyxel.mouse_x
        world_mouse_y = camera_y + pyxel.mouse_y

        # Tentativa de Link no ar (ESPAÇO, E ou Clique do mouse)
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_E) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.try_link(world_mouse_x, world_mouse_y)

        # Condição de Queda Fatal (caiu abaixo do limite visível da tela)
        if self.y > camera_y + screen_height + 35:
            self.state = STATE_FATAL_FALL
            self.play_sound(5)
            self.set_feedback("CONTRATO RESCINDIDO: QUEDA FATAL", 9999, 8)
