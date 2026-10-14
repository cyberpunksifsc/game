import math
import random
import pyxel

PHASE_TELEGRAPH = "TELEGRAPH"
PHASE_FLYING = "FLYING"
PHASE_DEAD = "DEAD"


class StrayBullet:
    """Projétil perdido disparado de tiroteios em New Tokyo.

    Possui telegrafagem com linha laser de advertência (~0.6s) seguida por voo
    em alta velocidade na diagonal ou horizontal.
    """

    def __init__(
        self,
        start_x: float,
        start_y: float,
        target_x: float,
        target_y: float,
        speed: float = 5.2,
        telegraph_duration: int = 20,
    ):
        self.start_x = float(start_x)
        self.start_y = float(start_y)
        self.x = float(start_x)
        self.y = float(start_y)
        self.speed = float(speed)

        # Vetor de direção normalizado
        dx = target_x - start_x
        dy = target_y - start_y
        dist = math.hypot(dx, dy)
        if dist < 0.001:
            dx, dy = 1.0, 0.0
            dist = 1.0
        self.vx = (dx / dist) * self.speed
        self.vy = (dy / dist) * self.speed
        self.angle = math.atan2(dy, dx)

        # Fases do projétil
        self.phase = PHASE_TELEGRAPH
        self.telegraph_timer = telegraph_duration
        self.total_telegraph = telegraph_duration

        # Cauda do projétil traçante
        self.trail_length = 8.0

        # Limite de distância percorrida
        self.max_distance = 600.0
        self.distance_traveled = 0.0

    def update(self) -> bool:
        """Atualiza a telegrafagem e a física de voo da bala. Retorna False se o projétil deve ser removido."""
        if self.phase == PHASE_TELEGRAPH:
            self.telegraph_timer -= 1
            if self.telegraph_timer <= 0:
                self.phase = PHASE_FLYING
                # Posição de largada efetiva do voo
                self.x = self.start_x
                self.y = self.start_y
            return True

        if self.phase == PHASE_FLYING:
            self.x += self.vx
            self.y += self.vy
            step = math.hypot(self.vx, self.vy)
            self.distance_traveled += step

            if self.distance_traveled >= self.max_distance:
                self.phase = PHASE_DEAD
                return False
            return True

        return False

    def check_hit(self, px: float, py: float, pw: float = 16.0, ph: float = 20.0) -> bool:
        """Verifica se a bala colidiu com a caixa de colisão do corpo do alpinista."""
        if self.phase != PHASE_FLYING:
            return False

        # Ponta da bala e centro do traço
        head_x = self.x
        head_y = self.y
        tail_x = self.x - math.cos(self.angle) * self.trail_length
        tail_y = self.y - math.sin(self.angle) * self.trail_length

        # AABB simples do jogador
        rx1, ry1 = px, py
        rx2, ry2 = px + pw, py + ph

        # Testa se a ponta ou a cauda estão dentro da AABB
        if (rx1 <= head_x <= rx2 and ry1 <= head_y <= ry2) or (rx1 <= tail_x <= rx2 and ry1 <= tail_y <= ry2):
            self.phase = PHASE_DEAD
            return True

        return False

    def draw(self, camera_x: float, camera_y: float):
        """Renderiza a linha laser telegrafada ou o projétil traçante neon em coordenadas de mundo."""
        if self.phase == PHASE_TELEGRAPH:
            # Linha guia laser telegrafando a trajetória da bala
            # Pisca em vermelho néon (8) e nos últimos 5 frames pisca em branco (7)
            is_final_warning = self.telegraph_timer <= 5
            color = 7 if (is_final_warning and (self.telegraph_timer % 2 == 0)) else (8 if (self.telegraph_timer // 2) % 2 == 0 else 14)

            # Desenha linha pontilhada laser ao longo da trajetória
            ray_len = 380.0
            end_x = self.start_x + math.cos(self.angle) * ray_len
            end_y = self.start_y + math.sin(self.angle) * ray_len

            steps = 45
            for i in range(steps):
                if i % 3 == 0:
                    continue
                t1 = i / steps
                t2 = (i + 0.6) / steps
                x1 = int(self.start_x + (end_x - self.start_x) * t1)
                y1 = int(self.start_y + (end_y - self.start_y) * t1)
                x2 = int(self.start_x + (end_x - self.start_x) * t2)
                y2 = int(self.start_y + (end_y - self.start_y) * t2)
                pyxel.line(x1, y1, x2, y2, color)

            # Ponto de origem do disparo piscando
            pyxel.circb(int(self.start_x), int(self.start_y), 2, color)

        elif self.phase == PHASE_FLYING:
            # Projétil traçante neon: cauda laranja/amarela (9, 10) e núcleo branco/vermelho (7, 8)
            hx = int(self.x)
            hy = int(self.y)
            tx = int(self.x - math.cos(self.angle) * self.trail_length)
            ty = int(self.y - math.sin(self.angle) * self.trail_length)

            # Cauda luminosa
            pyxel.line(tx, ty, hx, hy, 9)
            # Núcleo brilhante
            mid_x = (hx + tx) // 2
            mid_y = (hy + ty) // 2
            pyxel.line(mid_x, mid_y, hx, hy, 10)
            # Cabeça da bala
            pyxel.pset(hx, hy, 7)
