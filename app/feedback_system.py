import json
import webbrowser
from typing import Callable
import pyxel

FEEDBACK_FORM_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSeeleFRJ3PbTeX9nmxFtfqF_3VMD6bBGixNGFODEtqjbHGK9A/"
    "viewform?entry.52413313=ApexGrappler"
)

# Matriz QR Code ISO/IEC 18004 (Versão 6, 41x41, ECC L) pré-computada para FEEDBACK_FORM_URL
FEEDBACK_QR_MATRIX = (
    "#######.....#.#.#.#.#.##..#.#####.#######",
    "#.....#.#.#...###.#...#..####.#...#.....#",
    "#.###.#..###..###..#.#..#..##.#.#.#.###.#",
    "#.###.#.#.#..##..#.....####....#..#.###.#",
    "#.###.#..##..##.##..#####...#.#.#.#.###.#",
    "#.....#.#.##...#.##.##...#.##.....#.....#",
    "#######.#.#.#.#.#.#.#.#.#.#.#.#.#.#######",
    "...............##.#.##..#.#.#..#.........",
    "#####.####..#.#..#########.#.##..#.#.#.#.",
    "##.###.##.#.#...#...###..#..#.########.##",
    "..#...#...#.##.#..#..##..###.#..#..#.....",
    "#.#.#..###......#.#####.#.#....#####.#.##",
    "##....###.###....#..#....####.......###..",
    "..####..........#.##.###.##.######.##...#",
    ".#.#.##....#####.##.##..######...#.#..#..",
    "#.####...#.#...#...#.####.###.##..####.#.",
    "#...#.###.##.###.....##.######.#.........",
    "#...##.#.#...##.#...##......#####.###...#",
    "...######.#..####...#...##.####.#.#.#..#.",
    ".###.#.#..####.#....##.#....#..##.####.#.",
    ".####.#.#.....#.##..#....##..###....###..",
    ".#.....##.#.#...#..#..##....#..###.##...#",
    ".###.######...##..#.###.#.#####.##....#..",
    "...###..###.#..#..#..#.....#......##.#.#.",
    "....###.###..#####...##.##...#...#.....##",
    "####....#.###....######..#..#########..#.",
    "#.##..###.#....#..#..##...##..#.#..#.##..",
    "#.......####..##..#.##..#.#.#..###.#.....",
    "#.#...##...##...#..##....#.#...##...###.#",
    "#.#.#..#.#....#.#.##.###.##.######.###.##",
    "#.##.###..#########.#...####.#....#.###..",
    "#.##...#...#...#..##.###..#.#...###..#..#",
    "#.....#.#..#.####.....##.###.#..#####.#.#",
    "........###..####..###.###..#.#.#...#.##.",
    "#######.###.######..##...####.###.#.#.#..",
    "#.....#..#.#.#.##...####..#.#..##...#..##",
    "#.###.#.##....##.#..#..####.###.#####.#..",
    "#.###.#.###.#...#..#.###....#####.....#.#",
    "#.###.#.#.#....#....###...###..#.##.##...",
    "#.....#.#.#.#.#...##.##...#.#..##..#.#.#.",
    "#######.###.#.##.#....#.##...###...#.##..",
)

QR_QUIET_ZONE = 2
QR_MODULES = len(FEEDBACK_QR_MATRIX)
QR_TOTAL_SIZE = QR_MODULES + QR_QUIET_ZONE * 2  # 45x45 px


def draw_feedback_qr(x: int, y: int, quiet_zone: int = QR_QUIET_ZONE) -> None:
    """Desenha o QR Code de feedback em pixel art (fundo branco + módulos pretos via runs horizontais)."""
    total = QR_MODULES + quiet_zone * 2
    pyxel.rect(x, y, total, total, 7)
    for row_idx, row in enumerate(FEEDBACK_QR_MATRIX):
        py = y + quiet_zone + row_idx
        col_idx = 0
        while col_idx < QR_MODULES:
            if row[col_idx] == "#":
                start = col_idx
                while col_idx < QR_MODULES and row[col_idx] == "#":
                    col_idx += 1
                pyxel.rect(x + quiet_zone + start, py, col_idx - start, 1, 0)
            else:
                col_idx += 1


class FeedbackSystem:
    """Gerencia abertura do formulário de feedback exclusivamente na tela de vitória."""

    def __init__(self, url: str = FEEDBACK_FORM_URL):
        self.url = url
        self.victory_active = False
        self.feedback_rect: tuple[int, int, int, int] = (22, 130, 78, 14)
        self.qr_rect: tuple[int, int, int, int] = (250, 60, QR_TOTAL_SIZE, QR_TOTAL_SIZE)
        self._web_ready = False
        self._init_web_bridge()

    def _init_web_bridge(self) -> None:
        """Instala listeners síncronos no DOM (Pyxel Web) para abrir a URL sem bloqueio de pop-up."""
        try:
            import js  # type: ignore

            url_json = json.dumps(self.url)
            js.eval(
                f"""
                (() => {{
                    if (!window._apexFeedback) {{
                        const fb = {{
                            url: {url_json},
                            victoryActive: false,
                            feedbackRect: [22, 130, 78, 14],
                            qrRect: [250, 60, {QR_TOTAL_SIZE}, {QR_TOTAL_SIZE}],
                            lastOpenMs: 0,
                        }};

                        const mapClientPoint = (clientX, clientY) => {{
                            const canvas = document.getElementById("canvas") || document.querySelector("canvas");
                            if (!canvas) return null;
                            const rect = canvas.getBoundingClientRect();
                            if (rect.width <= 0 || rect.height <= 0) return null;
                            const scale = Math.min(rect.width / 320, rect.height / 180);
                            const viewW = 320 * scale;
                            const viewH = 180 * scale;
                            const offsetX = rect.left + (rect.width - viewW) * 0.5;
                            const offsetY = rect.top + (rect.height - viewH) * 0.5;
                            const px = (clientX - offsetX) / scale;
                            const py = (clientY - offsetY) / scale;
                            if (px < 0 || px > 320 || py < 0 || py > 180) return null;
                            return [px, py];
                        }};

                        const inRect = (px, py, r, pad = 2) => (
                            px >= r[0] - pad && px <= r[0] + r[2] + pad &&
                            py >= r[1] - pad && py <= r[1] + r[3] + pad
                        );

                        const openForm = () => {{
                            const now = Date.now();
                            if (now - fb.lastOpenMs < 400) return;
                            fb.lastOpenMs = now;
                            window.open(fb.url, "_blank", "noopener,noreferrer");
                        }};

                        window.addEventListener("keydown", (e) => {{
                            if (!fb.victoryActive || e.repeat) return;
                            if (e.key === "f" || e.key === "F") {{
                                openForm();
                            }}
                        }}, true);

                        window.addEventListener("click", (e) => {{
                            if (!fb.victoryActive) return;
                            const pt = mapClientPoint(e.clientX, e.clientY);
                            if (!pt) return;
                            if (inRect(pt[0], pt[1], fb.feedbackRect) || inRect(pt[0], pt[1], fb.qrRect)) {{
                                openForm();
                            }}
                        }}, true);

                        window.addEventListener("touchend", (e) => {{
                            if (!fb.victoryActive || !e.changedTouches || e.changedTouches.length === 0) return;
                            const t = e.changedTouches[0];
                            const pt = mapClientPoint(t.clientX, t.clientY);
                            if (!pt) return;
                            if (inRect(pt[0], pt[1], fb.feedbackRect, 4) || inRect(pt[0], pt[1], fb.qrRect, 4)) {{
                                openForm();
                            }}
                        }}, true);

                        window._apexFeedback = fb;
                    }}
                }})();
                """
            )
            self._web_ready = True
        except BaseException:
            self._web_ready = False

    def set_victory_active(
        self,
        active: bool,
        feedback_rect: tuple[int, int, int, int] | None = None,
        qr_rect: tuple[int, int, int, int] | None = None,
    ) -> None:
        """Ativa ou desativa a captura de clique/tecla do feedback conforme a tela de vitória."""
        self.victory_active = bool(active)
        if feedback_rect is not None:
            self.feedback_rect = feedback_rect
        if qr_rect is not None:
            self.qr_rect = qr_rect

        if self._web_ready:
            try:
                import js  # type: ignore

                fb = js.window._apexFeedback
                fb.victoryActive = self.victory_active
                fb.feedbackRect = list(self.feedback_rect)
                fb.qrRect = list(self.qr_rect)
            except BaseException:
                pass

    def open_feedback(self, opener: Callable[[str], object] | None = None) -> bool:
        """Abre o formulário de feedback apenas se a tela de vitória estiver ativa."""
        if not self.victory_active:
            return False
        if opener is not None:
            opener(self.url)
            return True
        if self._web_ready:
            try:
                import js  # type: ignore

                js.window.open(self.url, "_blank", "noopener,noreferrer")
                return True
            except BaseException:
                pass
        return bool(webbrowser.open(self.url))

    def update_desktop_input(self, clicked_feedback: bool = False) -> bool:
        """No modo Desktop Python, trata atalho [F] ou clique na área de feedback."""
        if not self.victory_active or self._web_ready:
            return False
        if pyxel.btnp(pyxel.KEY_F) or clicked_feedback:
            return self.open_feedback()
        return False
