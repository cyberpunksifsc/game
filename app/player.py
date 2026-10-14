from pathlib import Path
import math
import pyxel
from player_anchor_system import (
    PlayerAnchorSystem,
    STATE_ANCHORED,
    STATE_AIRBORNE,
    STATE_FATAL_FALL,
    MAX_ANCHORS,
    MAX_PLANT_RANGE,
)

from touch_controls import TouchControls

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent


class Player:
    """Controlador do personagem integrado ao sistema de movimentação e ancoragem do GDD."""

    def __init__(self, app, anchor_x=160, anchor_y=1800, rope_length=50):
        self.app = app

        # Controles virtuais de toque na tela (HUD touch) e gamepad para Android/Desktop
        self.touch_controls = TouchControls(self.app.WIDTH, self.app.HEIGHT)

        # Sistema de Ancoragem e Física (conforme especificação do GDD)
        self.anchor_system = PlayerAnchorSystem(
            start_anchor_x=anchor_x,
            start_anchor_y=anchor_y,
            initial_rope_length=rope_length,
            touch_controls=self.touch_controls,
        )

        # Offsets do arnês no sprite 32x32
        self.harness_offset_x = self.anchor_system.harness_offset_x
        self.harness_offset_y = self.anchor_system.harness_offset_y

        # Timers e animação
        self.anim_timer = 0
        self.anim_row = 0
        self.current_frame = 0

        # Flag para controlar exibição do HUD de ajuda dos controles
        self.show_controls_help = True

    # Propriedades de compatibilidade para código que acesse diretamente as coordenadas
    @property
    def x(self):
        return self.anchor_system.x

    @property
    def y(self):
        return self.anchor_system.y

    @property
    def anchor_x(self):
        active = self.anchor_system.get_active_anchor()
        return active.x if active else self.anchor_system.x

    @property
    def anchor_y(self):
        active = self.anchor_system.get_active_anchor()
        return active.y if active else self.anchor_system.y

    @property
    def rope_length(self):
        return self.anchor_system.rope_length

    @property
    def state(self):
        return self.anchor_system.state

    def carregar_recursos(self):
        """Carrega os spritesheets do personagem no banco 2 do Pyxel."""
        # 1. Spritesheet principal com Trenchcoat (128x160): IDLE, CLIMB, SWING
        sheet_path = BASE_DIR / "assets" / "CharacterIdeas" / "character_trenchcoat_sheet.png"
        if not sheet_path.exists():
            sheet_path = ROOT_DIR / "assets" / "CharacterIdeas" / "character_trenchcoat_sheet.png"

        if sheet_path.exists():
            pyxel.images[2].load(0, 0, str(sheet_path))

        # 2. Spritesheet de salto/balanço livre (192x32) na linha Y=160 do mesmo banco 2
        swing_sheet_path = BASE_DIR / "assets" / "CharacterIdeas" / "character_rope_swing_sheet.png"
        if not swing_sheet_path.exists():
            swing_sheet_path = ROOT_DIR / "assets" / "CharacterIdeas" / "character_rope_swing_sheet.png"

        if swing_sheet_path.exists():
            pyxel.images[2].load(0, 160, str(swing_sheet_path))

    def update(self, camera_x: float = 0.0, camera_y: float = 0.0):
        """Atualiza a simulação física, inputs e animações."""
        self.anim_timer += 1

        # Atualiza a leitura dos botões virtuais de toque na tela e gamepads
        self.touch_controls.update()

        # Alterna exibição de ajuda com H
        if pyxel.btnp(pyxel.KEY_H):
            self.show_controls_help = not self.show_controls_help

        # Atualiza a física de ancoragem, salto e links com a câmera
        self.anchor_system.update(camera_x=camera_x, camera_y=camera_y, screen_height=self.app.HEIGHT)

        # Seleciona linha do spritesheet e frames com base na ação do sistema
        action = self.anchor_system.action
        if self.anchor_system.state == STATE_AIRBORNE:
            # Estado no ar: usa linha de voo/salto carregada em Y=160
            self.anim_row = -1  # flag indicando linha especial de salto
            self.current_frame = (self.anim_timer // 5) % 6
        elif action == "CLIMB_UP":
            self.anim_row = 1
            self.current_frame = (self.anim_timer // 6) % 4
        elif action == "CLIMB_DOWN":
            self.anim_row = 2
            self.current_frame = (self.anim_timer // 6) % 4
        elif action == "SWING_LEFT":
            self.anim_row = 3
            self.current_frame = (self.anim_timer // 6) % 4
        elif action == "SWING_RIGHT":
            self.anim_row = 4
            self.current_frame = (self.anim_timer // 6) % 4
        else:
            # IDLE (linha 0)
            self.anim_row = 0
            self.current_frame = (self.anim_timer // 8) % 4

    def draw_anchors(self, camera_x: float = 0.0, camera_y: float = 0.0):
        """Desenha todas as âncoras na fachada e destaca possíveis alvos de link."""
        world_mouse_x = camera_x + pyxel.mouse_x
        world_mouse_y = camera_y + pyxel.mouse_y
        link_target = self.anchor_system.find_link_candidate(world_mouse_x, world_mouse_y)
        is_airborne = (self.anchor_system.state == STATE_AIRBORNE)

        for a in self.anchor_system.anchors:
            is_candidate = (a == link_target)
            a.draw(is_link_candidate=is_candidate, show_guide_beam=is_airborne)

    def draw_cable(self):
        """Desenha a corda de aço sob tensão se o jogador estiver ancorado."""
        active = self.anchor_system.get_active_anchor()
        if not active or self.anchor_system.state != STATE_ANCHORED:
            return

        ax = int(active.x)
        ay = int(active.y) + 2
        hx = int(self.anchor_system.x + self.harness_offset_x)
        hy = int(self.anchor_system.y + self.harness_offset_y)

        # Cabo de suspensão em aço trançado (cor 13: ardósia / cor 5)
        pyxel.line(ax, ay, hx, hy, 13)
        # Mosquetão metálico no arnês
        pyxel.pset(hx, hy, 6)

    def draw_crosshair_and_aim(self, camera_x: float = 0.0, camera_y: float = 0.0):
        """Desenha a mira da arma de gancho no mouse e linha de alcance."""
        if self.anchor_system.state != STATE_ANCHORED:
            return

        world_mouse_x = camera_x + pyxel.mouse_x
        world_mouse_y = camera_y + pyxel.mouse_y
        hx, hy = self.anchor_system.get_harness_pos()
        dist = math.hypot(world_mouse_x - hx, world_mouse_y - hy)
        can_plant = (len(self.anchor_system.anchors) < MAX_ANCHORS) and (dist <= MAX_PLANT_RANGE)

        # Cor da mira: 11 (verde néon) se puder plantar, 8 (vermelho) se bloqueado/fora de alcance
        color = 11 if can_plant else 8

        # Linha pontilhada sutil da mira laser em coordenadas de mundo
        if dist > 10:
            steps = int(dist / 6)
            for i in range(1, steps):
                t = i / steps
                lx = int(hx + (world_mouse_x - hx) * t)
                ly = int(hy + (world_mouse_y - hy) * t)
                if i % 2 == 0:
                    pyxel.pset(lx, ly, 12 if can_plant else 8)

        # Retículo da mira no cursor do mouse em coordenadas de mundo
        mx, my = int(world_mouse_x), int(world_mouse_y)
        pyxel.line(mx - 4, my, mx + 4, my, color)
        pyxel.line(mx, my - 4, mx, my + 4, color)
        pyxel.circb(mx, my, 3, color)

    def draw_hud(self, game_over: bool = False):
        """Desenha o display de status das âncoras e notificações corporativas."""
        # 1. Painel de Âncoras (canto superior esquerdo - 3 slots visuais compactos)
        # Mostra os 3 slots com o status: Ativa (Verde), Em Espera (Laranja), Livre (Cinza)
        panel_w = 44
        panel_h = 15
        pyxel.rect(4, 4, panel_w, panel_h, 0)
        pyxel.rectb(4, 4, panel_w, panel_h, 5)

        for i in range(MAX_ANCHORS):
            box_x = 7 + i * 12
            box_y = 6
            if i < len(self.anchor_system.anchors):
                anc = self.anchor_system.anchors[i]
                if anc.is_active:
                    # Ativa: verde néon
                    pyxel.rect(box_x, box_y, 9, 11, 11)
                    pyxel.text(box_x + 3, box_y + 3, "A", 0)
                else:
                    # Inativa plantada: laranja néon
                    pyxel.rect(box_x, box_y, 9, 11, 9)
                    pyxel.text(box_x + 3, box_y + 3, "P", 0)
            else:
                # Slot disponível
                pyxel.rectb(box_x, box_y, 9, 11, 5)
                pyxel.pset(box_x + 4, box_y + 5, 5)

        # 2. Mensagens de feedback de erro impeditivo (ocultas durante Game Over)
        if self.anchor_system.feedback_timer > 0 and not game_over:
            msg = self.anchor_system.feedback_msg
            color = self.anchor_system.feedback_color
            tw = len(msg) * 4
            x = (self.app.WIDTH - tw) // 2
            pyxel.rect(x - 4, 24, tw + 8, 11, 0)
            pyxel.rectb(x - 4, 24, tw + 8, 11, color)
            pyxel.text(x, 27, msg, color)

        # 3. Dicas de Controles de rodapé removidas para desobstruir a tela


    def draw(self, camera_x: float = None, camera_y: float = None, game_over: bool = False, is_invulnerable: bool = False):
        """Renderiza corda, âncoras, mira, sprite do alpinista e HUD."""
        if camera_x is None:
            camera_x = self.anchor_system.camera_x
        if camera_y is None:
            camera_y = self.anchor_system.camera_y

        # 1. Elementos em coordenadas de mundo (ativa a câmera do Pyxel)
        pyxel.camera(int(camera_x), int(camera_y))
        self.draw_anchors(camera_x, camera_y)
        if not game_over:
            self.draw_crosshair_and_aim(camera_x, camera_y)
        self.draw_cable()

        # Sprite do Alpinista com efeito de piscar durante invulnerabilidade
        px = int(self.anchor_system.x)
        py = int(self.anchor_system.y)
        blink_hidden = is_invulnerable and ((pyxel.frame_count // 2) % 2 == 0)

        if self.anchor_system.state != STATE_FATAL_FALL and not blink_hidden:
            if self.anim_row == -1:
                # Spritesheet de salto/voo no ar (em Y=160 no Banco 2)
                u = self.current_frame * 32
                v = 160
                pyxel.blt(px, py, 2, u, v, 32, 32, 0)
            else:
                # Spritesheet do trenchcoat (IDLE, CLIMB, SWING)
                u = self.current_frame * 32
                v = self.anim_row * 32
                pyxel.blt(px, py, 2, u, v, 32, 32, 0)

        # 2. Interface HUD (fixa na tela com câmera resetada em (0, 0))
        pyxel.camera(0, 0)
        self.draw_hud(game_over)
        self.touch_controls.draw(hide_controls=game_over)
