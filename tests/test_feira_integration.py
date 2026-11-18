import pytest

from feira_integration import (
    CREDIT_API_URL,
    DEFAULT_CREDIT_VALUE,
    GAME_PRODUCT_ID,
    GOOGLE_CLIENT_ID,
    STATUS_AWAITING_LOGIN,
    STATUS_COOLDOWN,
    STATUS_ERROR,
    STATUS_IDLE,
    STATUS_SUCCESS,
    STATUS_UNAUTHORIZED,
    FeiraIntegration,
    build_credit_headers,
    build_credit_payload,
    interpret_credit_response,
)
from player_health_and_score import PlayerHealthAndScore


def test_default_constants_match_feira_spec():
    assert GOOGLE_CLIENT_ID == (
        "331191695151-ku8mdhd76pc2k36itas8lm722krn0u64.apps.googleusercontent.com"
    )
    assert CREDIT_API_URL == "https://feira-de-jogos.dev.br/api/v2/credit"
    assert GAME_PRODUCT_ID == 92
    assert DEFAULT_CREDIT_VALUE == 250


def test_build_credit_payload_matches_joi_transfer_schema():
    payload = build_credit_payload()
    # transferSchema aceita exclusivamente { product, value } sem chaves extras
    assert set(payload.keys()) == {"product", "value"}
    assert payload["product"] == 92
    assert payload["value"] == 250

    with pytest.raises(ValueError):
        build_credit_payload(product=-1, value=250)
    with pytest.raises(ValueError):
        build_credit_payload(product=92, value=0)
    with pytest.raises(ValueError):
        build_credit_payload(product=92, value=3001)


def test_build_credit_headers_sets_bearer_token():
    headers = build_credit_headers("eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test")
    assert headers == {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test",
    }

    with pytest.raises(ValueError):
        build_credit_headers("   ")


def test_interpret_credit_response_for_all_backend_statuses():
    status, msg, op_id = interpret_credit_response(201, {"operation": 42}, credit_value=250)
    assert status == STATUS_SUCCESS
    assert "+250" in msg
    assert op_id == 42

    status, _, op_id = interpret_credit_response(429, None)
    assert status == STATUS_COOLDOWN
    assert op_id is None

    status, _, _ = interpret_credit_response(401, None)
    assert status == STATUS_UNAUTHORIZED

    status, _, _ = interpret_credit_response(403, None)
    assert status == STATUS_UNAUTHORIZED

    status, _, _ = interpret_credit_response(402, None)
    assert status == STATUS_ERROR

    status, _, _ = interpret_credit_response(400, {"error": '"value" is required'})
    assert status == STATUS_ERROR

    status, _, _ = interpret_credit_response(500, None)
    assert status == STATUS_ERROR


def test_victory_triggers_feira_login_flow_and_submit():
    feira = FeiraIntegration()
    stats = PlayerHealthAndScore(feira_integration=feira)

    assert feira.status == STATUS_IDLE

    stats.trigger_victory()
    assert stats.is_victory is True
    assert feira.status == STATUS_AWAITING_LOGIN

    captured = {}

    def fake_sender(url, headers, payload):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = payload
        return (201, {"operation": 777})

    status, msg, op_id = feira.submit_credential_sync("jwt-token-google", sender=fake_sender)
    assert status == STATUS_SUCCESS
    assert op_id == 777
    assert "+250" in msg
    assert captured["url"] == "https://feira-de-jogos.dev.br/api/v2/credit"
    assert captured["headers"]["Authorization"] == "Bearer jwt-token-google"
    assert captured["payload"] == {"product": 92, "value": 250}

    # Reiniciar partida reseta o estado da integração
    stats.reset()
    assert feira.status == STATUS_IDLE
    assert feira.operation_id is None


def test_victory_retry_button_rect_prevents_accidental_click_outside():
    stats = PlayerHealthAndScore()
    rx, ry, rw, rh = stats.get_victory_retry_rect(320, 180)

    # Clique na área do botão do Google (centro y=109) NÃO dispara reinício acidental
    assert stats.is_victory_retry_click(160, 109, 320, 180) is False

    # Clique dentro do botão [ NOVO TURNO ] dispara reinício
    assert stats.is_victory_retry_click(rx + rw / 2, ry + rh / 2, 320, 180) is True


def test_draw_game_over_victory_renders_all_feira_states(monkeypatch):
    import pyxel
    from feira_integration import STATUS_SENDING

    texts_drawn = []
    monkeypatch.setattr(pyxel, "rect", lambda *a, **k: None)
    monkeypatch.setattr(pyxel, "rectb", lambda *a, **k: None)
    monkeypatch.setattr(pyxel, "line", lambda *a, **k: None)
    monkeypatch.setattr(pyxel, "text", lambda x, y, s, c: texts_drawn.append((s, c)))
    monkeypatch.setattr(pyxel, "frame_count", 0, raising=False)

    feira = FeiraIntegration()
    stats = PlayerHealthAndScore(feira_integration=feira)
    stats.trigger_victory()
    stats.game_over_timer = 40  # habilita can_retry

    for st, msg in (
        (STATUS_AWAITING_LOGIN, "CONECTE O GOOGLE P/ RECEBER +250 TJL"),
        (STATUS_SENDING, "ENVIANDO +250 CREDITOS..."),
        (STATUS_SUCCESS, "CREDITOS RECEBIDOS: +250 TJL!"),
        (STATUS_COOLDOWN, "AGUARDE COOLDOWN P/ RECEBER DE NOVO (429)"),
        (STATUS_UNAUTHORIZED, "CONTA NAO CADASTRADA NA FEIRA (401)"),
        (STATUS_ERROR, "ERRO DE CONEXAO COM A FEIRA"),
    ):
        texts_drawn.clear()
        feira.status = st
        feira.status_message = msg
        stats.draw_game_over(320, 180)
        rendered_strings = [t[0] for t in texts_drawn]
        assert "[ EXPEDIENTE CONCLUIDO! ]" in rendered_strings
        assert msg in rendered_strings
        assert "[ NOVO TURNO (R / ESPACO) ]" in rendered_strings


def test_web_bridge_has_no_domain_restriction_and_includes_button_fallback(monkeypatch):
    import sys
    import types

    captured_js = []
    fake_js = types.ModuleType("js")
    fake_js.eval = lambda code: captured_js.append(code)
    monkeypatch.setitem(sys.modules, "js", fake_js)

    feira = FeiraIntegration()
    assert feira._web_ready is True
    assert len(captured_js) == 1

    js_code = captured_js[0]
    assert "REQUER DOMINIO" not in js_code
    assert "ONE-TAP ATIVO APENAS" not in js_code
    assert "unregistered_origin" not in js_code
    assert "gsi.renderButton" in js_code
    assert "gsi.prompt" in js_code
    assert "state.gsiInitialized" in js_code
    assert "itp_support: true" in js_code

