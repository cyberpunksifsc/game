import math
from types import SimpleNamespace

from patrol_drone_ai import (
    DEFAULT_DRONE_ALTITUDES,
    DRONE_STATE_COOLDOWN,
    DRONE_STATE_FIRING,
    DRONE_STATE_PATROL,
    DRONE_STATE_SCANNING,
    PatrolDrone,
    PatrolDroneManager,
)
from hazard_spawner import HazardSpawner
from stray_bullet import PHASE_TELEGRAPH, StrayBullet


def test_patrol_movement_and_boundary_bounce():
    drone = PatrolDrone(x=250.0, y=1100.0, min_x=68.0, max_x=252.0, speed=1.5, direction=1)
    # Keep player far away so drone remains in PATROL
    far_player_x = 160.0
    far_player_y = 1800.0

    drone.update(far_player_x, far_player_y)
    assert drone.state == DRONE_STATE_PATROL
    assert drone.x == 251.5
    assert drone.direction == 1

    # Hit max_x boundary and bounce left
    drone.update(far_player_x, far_player_y)
    assert drone.x == 252.0
    assert drone.direction == -1

    # Move toward min_x and bounce right
    drone.x = 69.0
    drone.update(far_player_x, far_player_y)
    assert drone.x == 68.0
    assert drone.direction == 1


def test_player_detection_transitions_to_scanning():
    drone = PatrolDrone(x=150.0, y=1100.0, detect_range_y=55.0, detect_range_x=160.0)

    # Player center is (player_x + 16, player_y + 16) -> place within range
    player_x = 140.0
    player_y = 1100.0 - 16.0 + 30.0  # center_y = 1130.0 (dy = 30 <= 55)

    bullet = drone.update(player_x, player_y)
    assert bullet is None
    assert drone.state == DRONE_STATE_SCANNING
    assert drone.scan_timer == drone.scan_duration
    assert drone.target_x == player_x + 16.0
    assert drone.target_y == player_y + 16.0


def test_scan_cancellation_when_player_escapes_vertical_range():
    drone = PatrolDrone(x=150.0, y=1100.0, detect_range_y=55.0, scan_duration=35)

    # Trigger scanning
    drone.update(140.0, 1100.0 - 16.0)
    assert drone.state == DRONE_STATE_SCANNING

    # Advance a few frames while in range
    for _ in range(5):
        drone.update(140.0, 1100.0 - 16.0)
    assert drone.state == DRONE_STATE_SCANNING
    assert drone.scan_timer == 30

    # Player escapes vertically beyond detect_range_y * 1.6 (55 * 1.6 = 88.0)
    escaped_player_y = 1100.0 - 16.0 + 95.0
    bullet = drone.update(140.0, escaped_player_y)
    assert bullet is None
    assert drone.state == DRONE_STATE_PATROL
    assert drone.scan_timer == 0


def test_full_state_cycle_and_stray_bullet_firing():
    drone = PatrolDrone(
        x=120.0,
        y=750.0,
        speed=1.2,
        direction=1,
        scan_duration=10,
        cooldown_duration=15,
    )
    player_x = 180.0
    player_y = 760.0  # center = (196.0, 776.0)

    # 1. PATROL -> SCANNING
    assert drone.state == DRONE_STATE_PATROL
    assert drone.update(player_x, player_y) is None
    assert drone.state == DRONE_STATE_SCANNING
    assert drone.scan_timer == 10

    # 2. SCANNING -> FIRING (10 frames)
    for _ in range(9):
        assert drone.update(player_x, player_y) is None
        assert drone.state == DRONE_STATE_SCANNING

    assert drone.update(player_x, player_y) is None
    assert drone.state == DRONE_STATE_FIRING

    # 3. FIRING -> COOLDOWN (produces StrayBullet aimed at player center)
    expected_origin_x = drone.x
    expected_origin_y = drone.y
    bullet = drone.update(player_x, player_y)
    assert isinstance(bullet, StrayBullet)
    assert bullet.phase == PHASE_TELEGRAPH
    assert bullet.telegraph_timer == 10
    assert math.isclose(bullet.speed, 5.6)
    assert math.isclose(bullet.start_x, expected_origin_x)
    assert math.isclose(bullet.start_y, expected_origin_y)

    expected_angle = math.atan2((player_y + 16.0) - expected_origin_y, (player_x + 16.0) - expected_origin_x)
    assert math.isclose(bullet.angle, expected_angle, abs_tol=1e-5)
    assert drone.state == DRONE_STATE_COOLDOWN
    assert drone.cooldown_timer == 15

    # 4. COOLDOWN -> PATROL (15 frames)
    for _ in range(14):
        assert drone.update(player_x, player_y) is None
        assert drone.state == DRONE_STATE_COOLDOWN

    assert drone.update(player_x, player_y) is None
    assert drone.state == DRONE_STATE_PATROL


def test_hazard_spawner_integration_and_reset():
    spawner = HazardSpawner()
    assert isinstance(spawner.drone_manager, PatrolDroneManager)
    assert len(spawner.drone_manager.drones) == len(DEFAULT_DRONE_ALTITUDES)

    # Prevent random city bullets from spawning during this test
    spawner.spawn_timer = 9999

    target_drone = spawner.drone_manager.drones[0]
    target_drone.scan_duration = 3

    player = SimpleNamespace(
        x=target_drone.x - 16.0,
        y=target_drone.y - 16.0,
        anchor_system=SimpleNamespace(angular_vel=0.0, vx=0.0),
    )
    stats = SimpleNamespace(is_game_over=False, take_damage=lambda amount: False)
    cleaning_system = SimpleNamespace(interrupt_by_damage=lambda: None)

    # Frame 1: Drone detects player -> SCANNING
    spawner.update(player, stats, cleaning_system, camera_x=0.0, camera_y=1300.0)
    assert target_drone.state == DRONE_STATE_SCANNING

    # Frames 2..4: Drone finishes scanning -> FIRING
    for _ in range(3):
        spawner.update(player, stats, cleaning_system, camera_x=0.0, camera_y=1300.0)
    assert target_drone.state == DRONE_STATE_FIRING

    # Frame 5: Drone fires bullet into spawner.bullets -> COOLDOWN
    spawner.update(player, stats, cleaning_system, camera_x=0.0, camera_y=1300.0)
    assert target_drone.state == DRONE_STATE_COOLDOWN
    assert len(spawner.bullets) == 1

    # Reset restores drones and clears bullets
    spawner.reset()
    assert len(spawner.bullets) == 0
    assert all(d.state == DRONE_STATE_PATROL for d in spawner.drone_manager.drones)
