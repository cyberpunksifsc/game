from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
README_PATH = ROOT_DIR / "README.md"
GDD_PATH = ROOT_DIR / "gdd.md"


@pytest.fixture(scope="module")
def readme_text() -> str:
    assert README_PATH.exists(), "README.md deve existir na raiz do projeto"
    content = README_PATH.read_text(encoding="utf-8")
    assert len(content.strip()) > 0, "README.md não pode estar vazio"
    return content


@pytest.fixture(scope="module")
def gdd_text() -> str:
    assert GDD_PATH.exists(), "gdd.md deve existir na raiz do projeto"
    content = GDD_PATH.read_text(encoding="utf-8")
    assert len(content.strip()) > 0, "gdd.md não pode estar vazio"
    return content


def test_files_exist_and_non_empty(readme_text: str, gdd_text: str):
    """Verifica que README.md e gdd.md existem e possuem conteúdo substancial."""
    assert len(readme_text) > 1500
    assert len(gdd_text) > 3000


def test_no_unfinished_placeholders(readme_text: str, gdd_text: str):
    """Garante que nenhum placeholder incompleto como '(a definir' ou '(a detalhar' permaneceu."""
    placeholders = ["(a definir", "(a detalhar"]
    for placeholder in placeholders:
        assert placeholder not in readme_text.lower(), f"Placeholder '{placeholder}' encontrado no README.md"
        assert placeholder not in gdd_text.lower(), f"Placeholder '{placeholder}' encontrado no gdd.md"


def test_gdd_revision_updated(gdd_text: str):
    """Verifica que o GDD foi atualizado para a revisão 0.2.0."""
    assert "Revision: 0.2.0" in gdd_text


def test_gdd_documents_costs_powerups_and_multiplatform_controls(gdd_text: str):
    """Verifica que o GDD detalha custos/licenças, Power-Ups pré-partida e controles multiplataforma."""
    required_terms = [
        "R$ 0,00",
        "Escudo Reativo",
        "Rodo Turbo",
        "Estabilizador Corporativo",
        "Controles Multiplataforma",
        "touch_controls.py",
        "audio_manager.py",
        "powerup_system.py",
    ]
    for term in required_terms:
        assert term in gdd_text, f"Termo esperado '{term}' ausente no gdd.md"


def test_readme_documents_all_core_modules(readme_text: str):
    """Verifica que o README documenta todos os módulos Python principais em app/."""
    expected_modules = [
        "main.py",
        "main_menu.py",
        "gameplay.py",
        "player.py",
        "player_anchor_system.py",
        "player_cleaning_system.py",
        "player_health_and_score.py",
        "building_generator.py",
        "hazard_spawner.py",
        "stray_bullet.py",
        "patrol_drone_ai.py",
        "powerup_system.py",
        "audio_manager.py",
        "touch_controls.py",
    ]
    for module_name in expected_modules:
        assert module_name in readme_text, f"Módulo '{module_name}' não documentado no README.md"


def test_readme_documents_controls_testing_web_export_and_credits(readme_text: str):
    """Verifica que o README inclui controles, instruções de execução/teste/exportação Web e créditos."""
    expected_sections_and_terms = [
        "Apex-01",
        "233 d.IA",
        "Escudo Reativo",
        "Rodo Turbo",
        "Estabilizador Corporativo",
        "pip install -r app/requirements.txt",
        "python app/main.py",
        "pytest",
        "pyxel package",
        "pyxel app2html",
        "DavidKBD",
        "Electric Pulse",
        "BoldPixels",
        "MIT",
    ]
    for term in expected_sections_and_terms:
        assert term in readme_text, f"Informação obrigatória '{term}' não encontrada no README.md"


def test_readme_has_no_excessive_trailing_blank_lines(readme_text: str):
    """Garante que as dezenas de linhas em branco ao final do README.md foram removidas."""
    assert not readme_text.endswith("\n\n\n"), "README.md não deve ter múltiplas linhas vazias no final"


def test_referenced_asset_directories_exist():
    """Verifica que os diretórios de trilha sonora e fonte citados na documentação existem em assets/."""
    soundtrack_dir = ROOT_DIR / "assets" / "Audio" / "SoundTrack"
    font_dir = ROOT_DIR / "assets" / "Font" / "webfontkit-BoldPixels"

    assert soundtrack_dir.is_dir(), f"Diretório de trilha sonora não encontrado: {soundtrack_dir}"
    assert any(soundtrack_dir.iterdir()), "Diretório de trilha sonora está vazio"

    assert font_dir.is_dir(), f"Diretório da fonte BoldPixels não encontrado: {font_dir}"
    assert (font_dir / "boldpixels.ttf").exists(), "Arquivo boldpixels.ttf não encontrado"
