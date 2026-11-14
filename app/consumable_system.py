"""Sistema genérico de consumíveis/power-ups coletáveis que saltam das janelas concluídas."""

import math
import random
import pyxel

from player_cleaning_system import FloatingScore, Particle
from player_health_and_score import MAX_HP

# Probabilidade de 1/5 (20%) ao concluir a limpeza ou reparo de uma janela
DEFAULT_DROP_CHANCE = 0.20

# Atraso (~0.4s a 30 FPS) antes de permitir a coleta, para o item subir até o topo do pulo
PICKUP_ARM_DELAY_FRAMES = 12

# Pontuação bônus caso o jogador colete um coração já estando com a vida cheia (3/3)
FULL_HP_BONUS_SCORE = 150

# Física do salto inicial (cone de 90° para cima: -135° a -45°) e queda lenta
LAUNCH_ANGLE_MIN_DEG = -135.0
LAUNCH_ANGLE_MAX_DEG = -45.0
LAUNCH_SPEED = 2.6
UPWARD_GRAVITY = 0.14
FALL_GRAVITY = 0.035
MAX_FALL_SPEED = 0.55

SOUND_PICKUP_COLLECT = 15


class ConsumablePickup:
    """Interface/classe base para itens consumíveis ou power-ups que saltam da janela."""

    def __init__(self, x: float, y: float, launch_angle_deg: float | None = None):
        self.x = float(x)
        self.y = float(y)

        if launch_angle_deg is None:
            launch_angle_deg = random.uniform(LAUNCH_ANGLE_MIN_DEG, LAUNCH_ANGLE_MAX_DEG)
        self.launch_angle_deg = float(launch_angle_deg)
        rad = math.radians(self.launch_angle_deg)

        self.vx = math.cos(rad) * LAUNCH_SPEED
        self.vy = math.sin(rad) * LAUNCH_SPEED  # negativo = sobe
        self.age = 0
        self.collected = False

    @property
    def is_collectible(self) -> bool:
        """Só pode ser coletado após subir (~0.4s), permitindo visualizar o salto."""
        return self.age >= PICKUP_ARM_DELAY_FRAMES and not self.collected

    def update(self, min_x: float = 52.0, max_x: float = 268.0) -> bool:
        """Atualiza o arco de subida e a queda lenta subsequente."""
        if self.collected:
            return False

        self.age += 1

        if self.vy < 0.0:
            # Fase de subida: desaceleração normal até o ápice do pulo
            self.vy += UPWARD_GRAVITY
            self.vx *= 0.96
            self.x += self.vx
        else:
            # Fase de descida: cai lentamente flutuando como paraquedas
            self.vy = min(MAX_FALL_SPEED, self.vy + FALL_GRAVITY)
            self.vx *= 0.90
            sway = math.sin(self.age * 0.12) * 0.25
            self.x += self.vx + sway

        self.y += self.vy

        # Mantém dentro dos limites horizontais da fachada
        if self.x < min_x:
            self.x = min_x
            self.vx = abs(self.vx) * 0.5
        elif self.x > max_x:
            self.x = max_x
            self.vx = -abs(self.vx) * 0.5

        return True

    def check_player_collision(self, player_x: float, player_y: float) -> bool:
        """Testa colisão AABB entre o item (10x10 ao redor do centro) e o corpo do alpinista."""
        if not self.is_collectible:
            return False

        # Caixa do corpo do jogador (mesma região central do sprite 32x32)
        px1, py1 = player_x + 4, player_y + 4
        px2, py2 = player_x + 28, player_y + 28

        ix1, iy1 = self.x - 5, self.y - 5
        ix2, iy2 = self.x + 5, self.y + 5

        return not (ix2 < px1 or ix1 > px2 or iy2 < py1 or iy1 > py2)

    def apply_effect(self, player, stats) -> tuple[str, int]:
        """Aplica o efeito do consumível no jogador/stats e retorna (texto_popup, cor)."""
        raise NotImplementedError

    def draw(self):
        """Renderiza o consumível em coordenadas de mundo."""
        raise NotImplementedError


class HeartPickup(ConsumablePickup):
    """Consumível de Vida: restaura +1 coração (ou concede +150 pts se já estiver com HP cheio)."""

    def apply_effect(self, player, stats) -> tuple[str, int]:
        self.collected = True
        if stats is not None and stats.heal(1):
            return ("+1 VIDA!", 8)
        if stats is not None:
            stats.score += FULL_HP_BONUS_SCORE
        return (f"+{FULL_HP_BONUS_SCORE} HP CHEIO!", 10)

    def draw(self):
        cx = int(round(self.x))
        cy = int(round(self.y))

        # Halo pulsante quando já está pronto para coleta
        if self.is_collectible and (self.age // 4) % 2 == 0:
            pyxel.circb(cx, cy, 6, 7)

        # Coração 7x6 centralizado em (cx, cy) com contorno escuro (cor 0) para contraste
        ox = cx - 3
        oy = cy - 3
        pyxel.rect(ox - 1, oy - 1, 9, 8, 0)
        pyxel.rect(ox + 1, oy, 2, 1, 8)
        pyxel.rect(ox + 4, oy, 2, 1, 8)
        pyxel.rect(ox, oy + 1, 7, 2, 8)
        pyxel.rect(ox + 1, oy + 3, 5, 1, 8)
        pyxel.rect(ox + 2, oy + 4, 3, 1, 8)
        pyxel.pset(ox + 3, oy + 5, 8)
        # Brilho especular branco/rosa
        pyxel.pset(ox + 1, oy + 1, 7)
        pyxel.pset(ox + 2, oy + 1, 14)


class ConsumableManager:
    """Gerencia o sorteio de drop (1/5), física, coleta e desenho dos consumíveis."""

    def __init__(self, drop_chance: float = DEFAULT_DROP_CHANCE, pickup_factory=HeartPickup):
        self.drop_chance = float(drop_chance)
        self.pickup_factory = pickup_factory
        self.pickups: list[ConsumablePickup] = []
        self._init_sounds()

    def _init_sounds(self):
        try:
            # Som 15: Coleta de vida/powerup (arpejo brilhante ascendente)
            pyxel.sounds[SOUND_PICKUP_COLLECT].set("e3g3b3e4", "t", "7777", "s", 5)
        except BaseException:
            pass

    def play_collect_sound(self):
        try:
            pyxel.play(1, SOUND_PICKUP_COLLECT)
        except BaseException:
            pass

    def reset(self):
        self.pickups.clear()

    def try_spawn_from_window(self, wx: float, wy: float) -> ConsumablePickup | None:
        """Sorteia (1/5 de chance) o surgimento de um consumível saindo da janela (wx, wy)."""
        if random.random() >= self.drop_chance:
            return None
        pickup = self.pickup_factory(wx, wy)
        self.pickups.append(pickup)
        return pickup

    def update(
        self,
        player,
        stats,
        cleaning_system=None,
        camera_y: float = 0.0,
        screen_h: float = 180.0,
    ):
        if stats is not None and stats.is_game_over:
            return

        active: list[ConsumablePickup] = []
        for pickup in self.pickups:
            if not pickup.update():
                continue

            if player is not None and pickup.check_player_collision(player.x, player.y):
                label, col = pickup.apply_effect(player, stats)
                self.play_collect_sound()

                if cleaning_system is not None:
                    cleaning_system.popups.append(FloatingScore(pickup.x, pickup.y - 6, label, col))
                    for _ in range(12):
                        cleaning_system.particles.append(
                            Particle(
                                pickup.x,
                                pickup.y,
                                random.uniform(-1.8, 1.8),
                                random.uniform(-2.0, 1.0),
                                random.choice([7, 8, 10, 14]),
                                life=16,
                            )
                        )
                continue

            # Remove se cair muito abaixo da tela visível
            if pickup.y <= camera_y + screen_h + 80.0:
                active.append(pickup)

        self.pickups = active

    def draw(self):
        for pickup in self.pickups:
            pickup.draw()
