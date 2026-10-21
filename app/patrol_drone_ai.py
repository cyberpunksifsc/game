import math
import pyxel
from stray_bullet import StrayBullet

DRONE_STATE_PATROL = "PATROL"
DRONE_STATE_SCANNING = "SCANNING"
DRONE_STATE_FIRING = "FIRING"
DRONE_STATE_COOLDOWN = "COOLDOWN"

DEFAULT_DRONE_ALTITUDES = [1450.0, 1100.0, 750.0, 400.0]


class PatrolDrone:
    """Drone corporativo de patrulha da fachada do arranha-céu Apex-01.

    Realiza patrulha horizontal, escaneia o alpinista com mira laser quando
    entra no raio de detecção e efetua disparo de advertência caso o alvo
    permaneça na zona de escaneamento.
    """

    def __init__(
        self,
        x: float = 160.0,
        y: float = 1100.0,
        min_x: float = 68.0,
        max_x: float = 252.0,
        speed: float = 1.2,
        direction: int = 1,
        scan_duration: int = 35,
        cooldown_duration: int = 90,
        detect_range_y: float = 55.0,
        detect_range_x: float = 160.0,
    ):
        self.x = float(x)
        self.y = float(y)
        self.base_y = float(y)
        self.min_x = float(min_x)
        self.max_x = float(max_x)
        self.speed = float(speed)
        self.direction = 1 if direction >= 0 else -1

        self.state = DRONE_STATE_PATROL
        self.scan_timer = 0
        self.scan_duration = int(scan_duration)
        self.cooldown_timer = 0
        self.cooldown_duration = int(cooldown_duration)

        self.detect_range_y = float(detect_range_y)
        self.detect_range_x = float(detect_range_x)

        self.target_x = float(x)
        self.target_y = float(y)
        self.bob_timer = 0

    def _move_horizontal(self, move_speed: float):
        """Desloca o drone horizontalmente e inverte a direção nos limites da fachada."""
        self.x += move_speed * self.direction
        if self.x <= self.min_x:
            self.x = self.min_x
            self.direction = 1
        elif self.x >= self.max_x:
            self.x = self.max_x
            self.direction = -1

    def update(self, player_x: float, player_y: float) -> StrayBullet | None:
        """Atualiza a máquina de estados do drone e retorna um StrayBullet ao disparar."""
        self.bob_timer += 1
        player_center_x = player_x + 16.0
        player_center_y = player_y + 16.0

        if self.state == DRONE_STATE_PATROL:
            self._move_horizontal(self.speed)
            if (
                abs(player_center_y - self.y) <= self.detect_range_y
                and abs(player_center_x - self.x) <= self.detect_range_x
            ):
                self.state = DRONE_STATE_SCANNING
                self.scan_timer = self.scan_duration
                self.target_x = player_center_x
                self.target_y = player_center_y
            return None

        elif self.state == DRONE_STATE_SCANNING:
            self._move_horizontal(self.speed * 0.25)
            self.target_x = player_center_x
            self.target_y = player_center_y

            # Cancela o escaneamento se o alpinista escapar verticalmente
            if abs(player_center_y - self.y) > self.detect_range_y * 1.6:
                self.state = DRONE_STATE_PATROL
                self.scan_timer = 0
                return None

            self.scan_timer -= 1
            if self.scan_timer <= 0:
                self.state = DRONE_STATE_FIRING
            return None

        elif self.state == DRONE_STATE_FIRING:
            bullet = StrayBullet(
                start_x=self.x,
                start_y=self.y,
                target_x=self.target_x,
                target_y=self.target_y,
                speed=5.6,
                telegraph_duration=10,
            )
            self.state = DRONE_STATE_COOLDOWN
            self.cooldown_timer = self.cooldown_duration
            return bullet

        elif self.state == DRONE_STATE_COOLDOWN:
            self._move_horizontal(self.speed)
            self.cooldown_timer -= 1
            if self.cooldown_timer <= 0:
                self.state = DRONE_STATE_PATROL
            return None

        return None

    def draw(self, camera_x: float, camera_y: float):
        """Renderiza o drone cyberpunk em pixel art e o feixe de escaneamento laser."""
        bob_offset = (
            int(round(math.sin(self.bob_timer * 0.15) * 1.5))
            if self.state != DRONE_STATE_SCANNING
            else 0
        )
        dx = int(self.x)
        dy = int(self.y) + bob_offset

        # Feixe laser de escaneamento e retículo de trava de mira
        if self.state == DRONE_STATE_SCANNING:
            tx = int(self.target_x)
            ty = int(self.target_y)
            beam_col = 10 if (self.scan_timer < 10 and self.scan_timer % 2 == 0) else 8
            pyxel.line(dx, dy, tx, ty, beam_col)
            pyxel.circb(tx, ty, 4, beam_col)
            pyxel.pset(tx, ty, 7)

        # Rotores duplos superiores (hélices animadas)
        blade_span = 4 if (self.bob_timer % 2 == 0) else 2
        # Suportes dos rotores
        pyxel.line(dx - 6, dy - 2, dx - 6, dy - 4, 5)
        pyxel.line(dx + 6, dy - 2, dx + 6, dy - 4, 5)
        # Pás das hélices
        pyxel.line(dx - 6 - blade_span, dy - 4, dx - 6 + blade_span, dy - 4, 6)
        pyxel.line(dx + 6 - blade_span, dy - 4, dx + 6 + blade_span, dy - 4, 6)

        # Casco metálico escuro do drone
        pyxel.rect(dx - 6, dy - 2, 13, 5, 1)
        pyxel.rectb(dx - 6, dy - 2, 13, 5, 5)
        pyxel.line(dx - 4, dy - 2, dx + 4, dy - 2, 13)

        # Olho sensor vermelho pulsante
        eye_x = dx + (2 if self.direction > 0 else -2)
        if self.state == DRONE_STATE_SCANNING:
            eye_col = 10 if (self.bob_timer % 4 < 2) else 8
        elif self.state == DRONE_STATE_COOLDOWN:
            eye_col = 4
        else:
            eye_col = 8 if (self.bob_timer % 20 < 14) else 2
        pyxel.pset(eye_x, dy, eye_col)
        pyxel.pset(dx, dy, 8)


class PatrolDroneManager:
    """Gerencia a frota de drones de patrulha posicionados em altitudes estratégicas."""

    def __init__(self, altitudes: list[float] | None = None):
        self.altitudes = (
            [float(a) for a in altitudes]
            if altitudes is not None
            else list(DEFAULT_DRONE_ALTITUDES)
        )
        self.drones: list[PatrolDrone] = []
        self.reset()

    def reset(self):
        """Recria todos os drones em suas altitudes de patrulha iniciais."""
        self.drones.clear()
        for i, altitude in enumerate(self.altitudes):
            start_x = 96.0 if (i % 2 == 0) else 224.0
            direction = 1 if (i % 2 == 0) else -1
            self.drones.append(
                PatrolDrone(
                    x=start_x,
                    y=altitude,
                    direction=direction,
                )
            )

    def update(
        self,
        player_x: float,
        player_y: float,
        is_game_over: bool = False,
    ) -> list[StrayBullet]:
        """Atualiza todos os drones e retorna a lista de projéteis disparados neste frame."""
        if is_game_over:
            return []

        fired_bullets: list[StrayBullet] = []
        for drone in self.drones:
            bullet = drone.update(player_x, player_y)
            if bullet is not None:
                fired_bullets.append(bullet)
        return fired_bullets

    def draw(self, camera_x: float, camera_y: float):
        """Renderiza todos os drones de patrulha."""
        for drone in self.drones:
            drone.draw(camera_x, camera_y)
