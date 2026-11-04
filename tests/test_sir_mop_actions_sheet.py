from pathlib import Path
from PIL import Image

from player_animation import ACTIONS_U, AIRBORNE_V, MOVEMENT_U

ROOT_DIR = Path(__file__).resolve().parent.parent
APP_SHEET_PATH = ROOT_DIR / "app" / "assets" / "CharacterIdeas" / "character_actions_sheet.png"
ASSETS_SHEET_PATH = ROOT_DIR / "assets" / "CharacterIdeas" / "character_actions_sheet.png"

ALLOWED_PALETTE_RGBS = {
    (0, 0, 0, 0),
    (43, 43, 69, 255),
    (0, 135, 81, 255),
    (95, 87, 79, 255),
    (194, 195, 199, 255),
    (255, 241, 232, 255),
    (255, 163, 0, 255),
    (255, 236, 39, 255),
    (0, 228, 54, 255),
    (255, 204, 170, 255),
}
HARNESS_RING_RGBA = (194, 195, 199, 255)


def test_actions_sheet_exists_and_fits_bank_2():
    assert APP_SHEET_PATH.exists()
    assert ASSETS_SHEET_PATH.exists()

    img = Image.open(APP_SHEET_PATH)
    assert img.size == (128, 160)
    # Folha de movimento ocupa [0..127, 0..159], ações ocupa [128..255, 0..159] e salto ocupa [0..191, 160..191]
    assert MOVEMENT_U + 128 <= ACTIONS_U
    assert ACTIONS_U + img.width <= 256
    assert img.height <= AIRBORNE_V


def test_actions_sheet_palette_and_no_pure_black():
    img = Image.open(APP_SHEET_PATH)
    for y in range(img.height):
        for x in range(img.width):
            px = img.getpixel((x, y))
            assert px in ALLOWED_PALETTE_RGBS, f"Cor fora da paleta em ({x},{y}): {px}"
            assert px != (0, 0, 0, 255), f"#000000 proibido em ({x},{y})"


def test_anchored_rows_preserve_harness_at_8_10():
    img = Image.open(APP_SHEET_PATH)
    # Linhas 0..3 (CLEAN, REPAIR, SHOOT, HIT) são ancoradas e mantêm o mosquetão fixo em (8, 10)
    for row in range(4):
        for col in range(4):
            fx = col * 32 + 8
            fy = row * 32 + 10
            assert img.getpixel((fx, fy)) == HARNESS_RING_RGBA, (
                f"Mosquetão desalinhado na linha {row}, frame {col}"
            )


def test_every_row_has_distinct_non_empty_frames():
    img = Image.open(APP_SHEET_PATH)
    for row in range(5):
        frames_bytes = []
        for col in range(4):
            crop = img.crop((col * 32, row * 32, (col + 1) * 32, (row + 1) * 32))
            non_transparent = sum(
                1
                for y in range(32)
                for x in range(32)
                if crop.getpixel((x, y))[3] > 0
            )
            assert non_transparent >= 80, f"Frame vazio/muito pequeno na linha {row}, F{col}"
            frames_bytes.append(crop.tobytes())

        # Garante que frames consecutivos mudam (animação real)
        for i in range(3):
            assert frames_bytes[i] != frames_bytes[i + 1], (
                f"Frames consecutivos F{i} e F{i+1} idênticos na linha {row}"
            )
