import math
import random
import pytest

from hazard_spawner import (
    APEX_ALTITUDE_Y,
    BASE_MAX_INTERVAL,
    BASE_MIN_INTERVAL,
    BASE_SPEED_MAX,
    BASE_SPEED_MIN,
    BASE_TELEGRAPH_FRAMES,
    MAX_ALLOWED_INTERVAL,
    MAX_SPEED_MAX,
    MAX_SPEED_MIN,
    MAX_TIME_FRAMES,
    MIN_ALLOWED_INTERVAL,
    MIN_TELEGRAPH_FRAMES,
    START_ALTITUDE_Y,
    HazardSpawner,
)


class DummyAnchorSystem:
    def __init__(self):
        self.angular_vel = 0.0
        self.vx = 0.0


class DummyPlayer:
    def __init__(self, x: float = 160.0, y: float = START_ALTITUDE_Y):
        self.x = x
        self.y = y
        self.anchor_system = DummyAnchorSystem()


class DummyStats:
    def __init__(self, is_game_over: bool = False):
        self.is_game_over = is_game_over

    def take_damage(self, amount: int) -> bool:
        return True


class DummyCleaningSystem:
    def interrupt_by_damage(self):
        pass


def test_difficulty_factor_start_is_zero():
    spawner = HazardSpawner()
    assert spawner.elapsed_frames == 0
    assert spawner.get_difficulty_factor(START_ALTITUDE_Y) == pytest.approx(0.0)


def test_difficulty_factor_mid_game_and_altitude_weights():
    spawner = HazardSpawner()
    # Half time (1800 frames -> time_factor = 0.5), base altitude (altitude_factor = 0.0)
    spawner.elapsed_frames = MAX_TIME_FRAMES // 2
    assert spawner.get_difficulty_factor(START_ALTITUDE_Y) == pytest.approx(0.55 * 0.5)

    # Zero time, apex altitude (altitude_factor = 1.0)
    spawner.elapsed_frames = 0
    assert spawner.get_difficulty_factor(APEX_ALTITUDE_Y) == pytest.approx(0.45)

    # Half time (0.5) + midpoint altitude (0.5) => 0.55*0.5 + 0.45*0.5 = 0.5
    spawner.elapsed_frames = MAX_TIME_FRAMES // 2
    mid_y = (START_ALTITUDE_Y + APEX_ALTITUDE_Y) / 2.0
    assert spawner.get_difficulty_factor(mid_y) == pytest.approx(0.5)


def test_difficulty_factor_clamped_within_zero_and_one():
    spawner = HazardSpawner()
    # Below start altitude and negative frames (edge check)
    spawner.elapsed_frames = -100
    assert spawner.get_difficulty_factor(2500.0) == 0.0

    # Long survival (beyond MAX_TIME_FRAMES) and above apex altitude
    spawner.elapsed_frames = MAX_TIME_FRAMES * 3
    assert spawner.get_difficulty_factor(-500.0) == 1.0
    assert spawner.get_difficulty_factor(APEX_ALTITUDE_Y) == 1.0


def test_current_intervals_decrease_monotonically_and_respect_floor():
    spawner = HazardSpawner()
    prev_min, prev_max = spawner.get_current_intervals(START_ALTITUDE_Y)
    assert (prev_min, prev_max) == (BASE_MIN_INTERVAL, BASE_MAX_INTERVAL)

    steps = 20
    for step in range(1, steps + 1):
        ratio = step / float(steps)
        spawner.elapsed_frames = int(MAX_TIME_FRAMES * ratio)
        player_y = START_ALTITUDE_Y - ratio * (START_ALTITUDE_Y - APEX_ALTITUDE_Y)
        cur_min, cur_max = spawner.get_current_intervals(player_y)

        assert cur_min <= prev_min
        assert cur_max <= prev_max
        assert cur_min >= MIN_ALLOWED_INTERVAL
        assert cur_max >= MAX_ALLOWED_INTERVAL
        assert cur_min <= cur_max
        assert spawner.min_interval == cur_min
        assert spawner.max_interval == cur_max
        prev_min, prev_max = cur_min, cur_max

    # At maximum difficulty, intervals reach the exact floor
    spawner.elapsed_frames = MAX_TIME_FRAMES * 2
    assert spawner.get_current_intervals(APEX_ALTITUDE_Y) == (
        MIN_ALLOWED_INTERVAL,
        MAX_ALLOWED_INTERVAL,
    )


def test_bullet_speed_range_increases_monotonically():
    spawner = HazardSpawner()
    prev_smin, prev_smax = spawner.get_bullet_speed_range(START_ALTITUDE_Y)
    assert (prev_smin, prev_smax) == pytest.approx((BASE_SPEED_MIN, BASE_SPEED_MAX))

    for step in range(1, 11):
        ratio = step / 10.0
        spawner.elapsed_frames = int(MAX_TIME_FRAMES * ratio)
        player_y = START_ALTITUDE_Y - ratio * (START_ALTITUDE_Y - APEX_ALTITUDE_Y)
        smin, smax = spawner.get_bullet_speed_range(player_y)
        assert smin > prev_smin
        assert smax > prev_smax
        assert smin < smax
        prev_smin, prev_smax = smin, smax

    assert (prev_smin, prev_smax) == pytest.approx((MAX_SPEED_MIN, MAX_SPEED_MAX))


def test_telegraph_duration_scales_from_20_down_to_12():
    spawner = HazardSpawner()
    assert spawner.get_telegraph_duration(START_ALTITUDE_Y) == BASE_TELEGRAPH_FRAMES

    prev_telegraph = BASE_TELEGRAPH_FRAMES
    for step in range(1, 11):
        ratio = step / 10.0
        spawner.elapsed_frames = int(MAX_TIME_FRAMES * ratio)
        player_y = START_ALTITUDE_Y - ratio * (START_ALTITUDE_Y - APEX_ALTITUDE_Y)
        t_frames = spawner.get_telegraph_duration(player_y)
        assert MIN_TELEGRAPH_FRAMES <= t_frames <= prev_telegraph
        prev_telegraph = t_frames

    assert prev_telegraph == MIN_TELEGRAPH_FRAMES


def test_double_burst_spawns_only_at_high_difficulty():
    random.seed(42)
    spawner = HazardSpawner()

    # At maximum difficulty, double_burst has 20% probability per spawn
    spawner.elapsed_frames = MAX_TIME_FRAMES
    burst_occurrences = 0
    for _ in range(100):
        spawner.bullets.clear()
        spawner.spawn_bullet(160.0, APEX_ALTITUDE_Y, 0.0, 0.0, 320.0, 180.0)
        if len(spawner.bullets) == 2:
            burst_occurrences += 1
            b1, b2 = spawner.bullets
            assert b1.total_telegraph == MIN_TELEGRAPH_FRAMES
            assert b2.total_telegraph == MIN_TELEGRAPH_FRAMES + 8
            assert abs(b2.start_y - b1.start_y) == pytest.approx(28.0)

    assert burst_occurrences > 5


def test_simulation_over_1000_frames_and_reset():
    random.seed(12345)

    # Low difficulty simulation (start of game, low altitude)
    low_spawner = HazardSpawner()
    low_player = DummyPlayer(y=START_ALTITUDE_Y)
    stats = DummyStats()
    cleaning = DummyCleaningSystem()

    low_spawn_events = 0
    for _ in range(1200):
        prev_timer = low_spawner.spawn_timer
        low_spawner.update(low_player, stats, cleaning, 0.0, 1600.0)
        if prev_timer == 1:
            low_spawn_events += 1

    assert low_spawner.elapsed_frames == 1200

    # High difficulty simulation (late game, high altitude)
    high_spawner = HazardSpawner()
    high_spawner.elapsed_frames = MAX_TIME_FRAMES
    high_player = DummyPlayer(y=APEX_ALTITUDE_Y)

    high_spawn_events = 0
    for _ in range(1200):
        prev_timer = high_spawner.spawn_timer
        high_spawner.update(high_player, stats, cleaning, 0.0, 100.0)
        if prev_timer == 1:
            high_spawn_events += 1

    assert high_spawner.elapsed_frames == MAX_TIME_FRAMES + 1200
    assert high_spawn_events > low_spawn_events * 1.5

    # Verify reset restores initial state
    high_spawner.reset()
    assert high_spawner.elapsed_frames == 0
    assert high_spawner.spawn_timer == 90
    assert high_spawner.min_interval == BASE_MIN_INTERVAL
    assert high_spawner.max_interval == BASE_MAX_INTERVAL
    assert len(high_spawner.bullets) == 0
    assert len(high_spawner.sparks) == 0
