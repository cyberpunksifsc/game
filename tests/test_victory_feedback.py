import pyxel

from feedback_system import (
    FEEDBACK_FORM_URL,
    FEEDBACK_QR_MATRIX,
    QR_TOTAL_SIZE,
    FeedbackSystem,
    draw_feedback_qr,
)
from player_health_and_score import REASON_HP, PlayerHealthAndScore


def test_feedback_url_and_qr_matrix_dimensions():
    assert FEEDBACK_FORM_URL == (
        "https://docs.google.com/forms/d/e/1FAIpQLSeeleFRJ3PbTeX9nmxFtfqF_3VMD6bBGixNGFODEtqjbHGK9A/"
        "viewform?entry.52413313=ApexGrappler"
    )
    assert len(FEEDBACK_QR_MATRIX) == 41
    assert all(len(row) == 41 and set(row) <= {"#", "."} for row in FEEDBACK_QR_MATRIX)
    assert QR_TOTAL_SIZE == 45


def test_victory_rects_do_not_overlap_and_stay_inside_screen():
    stats = PlayerHealthAndScore()
    fb = stats.get_victory_feedback_rect(320, 180)
    retry = stats.get_victory_retry_rect(320, 180)
    qr = stats.get_victory_qr_rect(320, 180)

    for rx, ry, rw, rh in (fb, retry, qr):
        assert 0 <= rx and rx + rw <= 320
        assert 0 <= ry and ry + rh <= 180

    # Feedback button e Retry button não se sobrepõem
    assert fb[0] + fb[2] < retry[0]
    # QR Code não invade o botão de feedback nem o de retry
    assert qr[0] > retry[0] + retry[2]

    # Clicar no botão de feedback ou QR NÃO dispara retry
    assert stats.is_victory_feedback_click(fb[0] + 5, fb[1] + 5, 320, 180) is True
    assert stats.is_victory_retry_click(fb[0] + 5, fb[1] + 5, 320, 180) is False
    assert stats.is_victory_feedback_click(qr[0] + 5, qr[1] + 5, 320, 180) is True
    assert stats.is_victory_retry_click(qr[0] + 5, qr[1] + 5, 320, 180) is False


def test_feedback_only_active_and_rendered_on_victory(monkeypatch):
    texts_drawn = []
    rects_drawn = []
    monkeypatch.setattr(pyxel, "rect", lambda x, y, w, h, c: rects_drawn.append((x, y, w, h, c)))
    monkeypatch.setattr(pyxel, "rectb", lambda *a, **k: None)
    monkeypatch.setattr(pyxel, "line", lambda *a, **k: None)
    monkeypatch.setattr(pyxel, "text", lambda x, y, s, c: texts_drawn.append((s, c)))
    monkeypatch.setattr(pyxel, "frame_count", 0, raising=False)

    opened_urls = []
    fb = FeedbackSystem()
    stats = PlayerHealthAndScore(feedback_system=fb)

    # Fora da vitória (inclusive na derrota), feedback não abre e não é desenhado
    assert fb.victory_active is False
    assert fb.open_feedback(opener=opened_urls.append) is False

    stats.trigger_game_over(REASON_HP)
    assert fb.victory_active is False
    assert fb.open_feedback(opener=opened_urls.append) is False
    stats.draw_game_over(320, 180)
    assert "[ FEEDBACK (F) ]" not in [t[0] for t in texts_drawn]
    assert not any(w == 45 and h == 45 and c == 7 for _, _, w, h, c in rects_drawn)

    # Ao vencer, feedback ativa, aparece na tela e abre a URL quando acionado
    stats.reset()
    texts_drawn.clear()
    rects_drawn.clear()
    stats.trigger_victory()
    assert fb.victory_active is True

    stats.draw_game_over(320, 180)
    rendered = [t[0] for t in texts_drawn]
    assert "[ FEEDBACK (F) ]" in rendered
    assert "AVALIE O" in rendered
    assert any(w == 45 and h == 45 and c == 7 for _, _, w, h, c in rects_drawn)

    assert fb.open_feedback(opener=opened_urls.append) is True
    assert opened_urls == [FEEDBACK_FORM_URL]

    # Ao reiniciar turno, desativa novamente
    stats.reset()
    assert fb.victory_active is False


def test_draw_feedback_qr_draws_quiet_zone_and_modules(monkeypatch):
    rects = []
    monkeypatch.setattr(pyxel, "rect", lambda x, y, w, h, c: rects.append((x, y, w, h, c)))

    draw_feedback_qr(10, 20)
    assert rects[0] == (10, 20, 45, 45, 7)
    module_rects = rects[1:]
    assert len(module_rects) > 0
    assert all(c == 0 and h == 1 for _, _, _, h, c in module_rects)
    assert all(12 <= x and x + w <= 53 and 22 <= y < 63 for x, y, w, _, _ in module_rects)


def test_desktop_key_f_opens_feedback_only_on_victory(monkeypatch):
    opened = []
    fb = FeedbackSystem()
    stats = PlayerHealthAndScore(feedback_system=fb)

    monkeypatch.setattr(pyxel, "btnp", lambda k: k == pyxel.KEY_F)
    monkeypatch.setattr(pyxel, "mouse_x", 0, raising=False)
    monkeypatch.setattr(pyxel, "mouse_y", 0, raising=False)
    monkeypatch.setattr("feedback_system.webbrowser.open", lambda u: opened.append(u) or True)

    stats.trigger_game_over(REASON_HP)
    stats.update(is_idle=False)
    assert opened == []

    stats.reset()
    stats.trigger_victory()
    stats.update(is_idle=False)
    assert opened == [FEEDBACK_FORM_URL]
