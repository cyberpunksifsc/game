import math
import random
import pyxel
from stray_bullet import StrayBullet, PHASE_FLYING, PHASE_TELEGRAPH
from player_cleaning_system import Particle

SOUND_LASER_WARN = 10
SOUND_BULLET_FIRE = 11
SOUND_BULLET_HIT = 12


class HazardSpawner:
    """Gerencia o ciclo de geração de perigos da cidade (balas perdidas vindas de
    conflitos urbanos nos setores inferiores e tráfego aéreo).
    """

    def __init__(self):
        self.bullets: list[StrayBullet] = []
        self.sparks: list[Particle] = []

        # Temporizador de spawn (frames)
        self.spawn_timer = 90  # 3 segundos de respiro antes da primeira bala
        self.min_interval = 110  # ~3.6s
        self.max_interval = 170  # ~5.6s

        self.init_sounds()

    def init_sounds(self):
        """Inicializa efeitos sonoros das balas e impactos chiptune nos canais 10 a 12."""
        try:
            # Som 10: Bipe laser agudo de advertência (trava de mira)
            pyxel.sounds[10].set("b3r1b3", "p", "707", "f", 4)
            # Som 11: Disparo de arma automática distante (estampido metálico rápido)
            pyxel.sounds[11].set("f2c2a1", "n", "753", "s", 3)
            # Som 12: Impacto de projétil / ricochete perfurante no traje
            pyxel.sounds[12].set("c1d1c1d1", "n", "7641", "f", 5)
        except BaseException:
            pass

    def play_sound(self, sound_id: int):
        try:
            pyxel.play(2, sound_id)
        except BaseException:
            pass

    def reset(self):
        """Reinicia o spawner para uma nova partida."""
        self.bullets.clear()
        self.sparks.clear()
        self.spawn_timer = 90

    def spawn_bullet(self, player_x: float, player_y: float, camera_x: float, camera_y: float, screen_w: float, screen_h: float):
        """Cria um disparo vindo dos flancos da cidade na direção da área do jogador."""
        from_left = random.random() < 0.5

        if from_left:
            start_x = camera_x - 20
            target_x = camera_x + screen_w + 40
        else:
            start_x = camera_x + screen_w + 20
            target_x = camera_x - 40

        # Altura de origem: flutua em relação ao jogador
        start_y = player_y + random.uniform(-40, 50)

        # Destino calculado para cruzar na vizinhança do alpinista (com dispersão aleatória)
        target_y = player_y + random.uniform(-35, 35)

        bullet = StrayBullet(
            start_x=start_x,
            start_y=start_y,
            target_x=target_x,
            target_y=target_y,
            speed=random.uniform(4.8, 6.0),
            telegraph_duration=20,  # ~0.66s de aviso prévio
        )
        self.bullets.append(bullet)
        self.play_sound(SOUND_LASER_WARN)

    def update(
        self,
        player,
        stats,
        cleaning_system,
        camera_x: float,
        camera_y: float,
        screen_w: float = 320.0,
        screen_h: float = 180.0,
    ):
        """Atualiza disparos, colisões e partículas de impacto."""
        # Atualiza partículas de faíscas existentes
        self.sparks = [s for s in self.sparks if s.update()]

        if stats.is_game_over:
            return

        # 1. Temporizador de geração de novos disparos
        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_bullet(player.x, player.y, camera_x, camera_y, screen_w, screen_h)
            self.spawn_timer = random.randint(self.min_interval, self.max_interval)

        # 2. Caixa de colisão do corpo do alpinista (centralizada no torso)
        # O sprite é 32x32 com arnês em offset (8, 10). O tronco fica entre x+6 e x+22.
        hitbox_x = player.x + 6
        hitbox_y = player.y + 6
        hitbox_w = 16
        hitbox_h = 20

        # 3. Atualiza cada bala e testa colisão
        remaining_bullets = []
        for bullet in self.bullets:
            prev_phase = bullet.phase
            is_alive = bullet.update()

            # Se acabou a telegrafagem e começou a voar, toca o estampido do disparo
            if prev_phase == PHASE_TELEGRAPH and bullet.phase == PHASE_FLYING:
                self.play_sound(SOUND_BULLET_FIRE)

            if not is_alive:
                continue

            # Testa colisão se estiver na fase de voo
            if bullet.phase == PHASE_FLYING:
                hit = bullet.check_hit(hitbox_x, hitbox_y, hitbox_w, hitbox_h)
                if hit:
                    # Aplica dano ao jogador se ele não for invulnerável
                    damage_applied = stats.take_damage(1)
                    if damage_applied:
                        # Interrompe limpeza/reparo imediatamente
                        if hasattr(cleaning_system, "interrupt_by_damage"):
                            cleaning_system.interrupt_by_damage()

                        # Aplica empurrão físico/recuo do impacto no balanço do jogador
                        knockback_dir = 1.0 if bullet.vx > 0 else -1.0
                        if hasattr(player.anchor_system, "angular_vel"):
                            player.anchor_system.angular_vel += knockback_dir * 0.025
                        if hasattr(player.anchor_system, "vx"):
                            player.anchor_system.vx += knockback_dir * 0.8

                        # Efeito sonoro de impacto no traje/arnês
                        self.play_sound(SOUND_BULLET_HIT)

                        # Gera faíscas de ricochete metálico
                        for _ in range(12):
                            self.sparks.append(Particle(
                                x=bullet.x,
                                y=bullet.y,
                                vx=random.uniform(-2.5, 2.5) + knockback_dir * 1.0,
                                vy=random.uniform(-2.0, 1.0),
                                color=random.choice([7, 8, 9, 10]),
                                life=14,
                            ))

                    # A bala foi destruída pelo impacto
                    continue

            remaining_bullets.append(bullet)

        self.bullets = remaining_bullets

    def draw(self, camera_x: float, camera_y: float):
        """Renderiza todas as miras laser, balas e faíscas em coordenadas de mundo."""
        # Partículas de faíscas metálicas
        for s in self.sparks:
            s.draw()

        # Projéteis e lasers de mira
        for bullet in self.bullets:
            bullet.draw(camera_x, camera_y)
