import json
import urllib.error
import urllib.request
from typing import Callable

# Configurações oficiais da Feira de Jogos
GOOGLE_CLIENT_ID = (
    "331191695151-ku8mdhd76pc2k36itas8lm722krn0u64.apps.googleusercontent.com"
)
CREDIT_API_URL = "https://feira-de-jogos.dev.br/api/v2/credit"
GAME_PRODUCT_ID = 92
DEFAULT_CREDIT_VALUE = 250

# Estados do fluxo de autenticação e envio de créditos na tela de vitória
STATUS_IDLE = "IDLE"
STATUS_AWAITING_LOGIN = "AWAITING_LOGIN"
STATUS_SENDING = "SENDING"
STATUS_SUCCESS = "SUCCESS"
STATUS_COOLDOWN = "COOLDOWN"
STATUS_UNAUTHORIZED = "UNAUTHORIZED"
STATUS_ERROR = "ERROR"
STATUS_UNAVAILABLE = "UNAVAILABLE"


def build_credit_payload(
    product: int = GAME_PRODUCT_ID,
    value: int = DEFAULT_CREDIT_VALUE,
) -> dict[str, int]:
    """Monta e valida o corpo JSON exigido pelo schema Joi da Feira de Jogos."""
    product_int = int(product)
    value_int = int(value)
    if product_int < 0:
        raise ValueError("O ID do produto deve ser um inteiro >= 0.")
    if value_int < 1 or value_int > 3000:
        raise ValueError("O valor de crédito deve ser um inteiro entre 1 e 3000.")
    return {
        "product": product_int,
        "value": value_int,
    }


def build_credit_headers(credential: str) -> dict[str, str]:
    """Monta os cabeçalhos HTTP com o ID Token JWT do Google One-Tap (Bearer)."""
    token = (credential or "").strip()
    if not token:
        raise ValueError("Credencial OAuth do Google ausente.")
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }


def interpret_credit_response(
    status_code: int,
    body: dict | None = None,
    credit_value: int = DEFAULT_CREDIT_VALUE,
) -> tuple[str, str, int | None]:
    """Converte o status HTTP da API `/api/v2/credit` em estado interno e mensagem de HUD."""
    op_id = None
    if isinstance(body, dict) and "operation" in body:
        try:
            op_id = int(body["operation"])
        except (TypeError, ValueError):
            op_id = None

    if status_code == 201 or (200 <= status_code < 300):
        return (
            STATUS_SUCCESS,
            f"CREDITOS RECEBIDOS: +{credit_value} TJL!",
            op_id,
        )
    if status_code == 429:
        return (
            STATUS_COOLDOWN,
            "AGUARDE COOLDOWN P/ RECEBER DE NOVO (429)",
            None,
        )
    if status_code == 401:
        return (
            STATUS_UNAUTHORIZED,
            "CONTA NAO CADASTRADA NA FEIRA (401)",
            None,
        )
    if status_code == 403:
        return (
            STATUS_UNAUTHORIZED,
            "PRODUTO OU LIMITE NAO AUTORIZADO (403)",
            None,
        )
    if status_code == 402:
        return (
            STATUS_ERROR,
            "VALOR DE CREDITO INVALIDO (402)",
            None,
        )
    if status_code == 400:
        return (
            STATUS_ERROR,
            "REQUISICAO INVALIDA NA FEIRA (400)",
            None,
        )
    return (
        STATUS_ERROR,
        f"ERRO AO CREDITAR NA FEIRA (HTTP {status_code})",
        None,
    )


class FeiraIntegration:
    """Gerencia o login Google One-Tap e o POST de créditos na tela de vitória."""

    def __init__(
        self,
        client_id: str = GOOGLE_CLIENT_ID,
        credit_url: str = CREDIT_API_URL,
        product_id: int = GAME_PRODUCT_ID,
        credit_value: int = DEFAULT_CREDIT_VALUE,
    ):
        self.client_id = client_id
        self.credit_url = credit_url
        self.product_id = int(product_id)
        self.credit_value = int(credit_value)

        self.status = STATUS_IDLE
        self.status_message = ""
        self.operation_id: int | None = None

        self._web_ready = False
        self._init_web_bridge()

    def _init_web_bridge(self):
        """Injeta o Google Identity Services (One-Tap) e a ponte DOM/Fetch no navegador via Pyodide."""
        try:
            import js  # type: ignore

            client_id_json = json.dumps(self.client_id)
            credit_url_json = json.dumps(self.credit_url)

            js.eval(
                f"""
                (() => {{
                    // 1. Garante que o script Google Identity Services (One-Tap) está carregado
                    const gsiSrc = "https://accounts.google.com/gsi/client";
                    if (!document.querySelector(`script[src="${{gsiSrc}}"]`)) {{
                        const s = document.createElement("script");
                        s.src = gsiSrc;
                        s.async = true;
                        s.defer = true;
                        document.head.appendChild(s);
                    }}

                    if (!window._apexFeira) {{
                        const state = {{
                            status: "IDLE",
                            message: "",
                            operationId: 0,
                            clientId: {client_id_json},
                            creditUrl: {credit_url_json},
                            productId: {self.product_id},
                            creditValue: {self.credit_value},
                            pollTimer: null,
                            overlay: null,
                            btnContainer: null,
                            gsiInitialized: false,
                        }};

                        const ensureOverlay = () => {{
                            if (state.overlay && document.body.contains(state.overlay)) {{
                                return state.overlay;
                            }}
                            const host = document.createElement("div");
                            host.id = "apex-feira-auth-overlay";
                            host.style.position = "fixed";
                            host.style.zIndex = "9999";
                            host.style.display = "none";
                            host.style.flexDirection = "column";
                            host.style.alignItems = "center";
                            host.style.justifyContent = "center";
                            host.style.pointerEvents = "auto";
                            host.style.transform = "translate(-50%, -50%)";

                            // Impede que cliques no botão do Google atravessem para o canvas do Pyxel
                            const stopProp = (e) => e.stopPropagation();
                            for (const evt of ["mousedown", "mouseup", "click", "touchstart", "touchend", "pointerdown", "pointerup"]) {{
                                host.addEventListener(evt, stopProp, false);
                            }}

                            const btnBox = document.createElement("div");
                            btnBox.id = "apex-feira-google-btn";
                            host.appendChild(btnBox);

                            document.body.appendChild(host);
                            state.overlay = host;
                            state.btnContainer = btnBox;
                            return host;
                        }};

                        const positionOverlay = () => {{
                            const host = state.overlay;
                            if (!host || host.style.display === "none") return;
                            const canvas = document.getElementById("canvas") || document.querySelector("canvas");
                            if (!canvas) {{
                                host.style.left = "50%";
                                host.style.top = "60%";
                                return;
                            }}
                            const rect = canvas.getBoundingClientRect();
                            const SCREEN_W = 320;
                            const SCREEN_H = 180;
                            const scale = Math.min(rect.width / SCREEN_W, rect.height / SCREEN_H);
                            const viewW = SCREEN_W * scale;
                            const viewH = SCREEN_H * scale;
                            const offsetX = rect.left + (rect.width - viewW) * 0.5;
                            const offsetY = rect.top + (rect.height - viewH) * 0.5;

                            // Posiciona exatamente na faixa reservada dentro do modal de Vitória (x=160, y=109)
                            const targetX = offsetX + (160 / SCREEN_W) * viewW;
                            const targetY = offsetY + (109 / SCREEN_H) * viewH;
                            const btnScale = Math.max(0.65, Math.min(1.15, viewH / 340));

                            host.style.left = `${{targetX}}px`;
                            host.style.top = `${{targetY}}px`;
                            host.style.transform = `translate(-50%, -50%) scale(${{btnScale}})`;
                        }};

                        window.addEventListener("resize", positionOverlay);

                        const sendCreditRequest = async (credential) => {{
                            if (state.overlay) {{
                                state.overlay.style.display = "none";
                            }}
                            state.status = "SENDING";
                            state.message = `ENVIANDO +${{state.creditValue}} CREDITOS...`;
                            state.operationId = 0;

                            try {{
                                const res = await fetch(state.creditUrl, {{
                                    method: "POST",
                                    headers: {{
                                        "Content-Type": "application/json",
                                        "Authorization": `Bearer ${{credential}}`,
                                    }},
                                    body: JSON.stringify({{
                                        product: state.productId,
                                        value: state.creditValue,
                                    }}),
                                }});

                                if (res.status === 201 || res.ok) {{
                                    let data = null;
                                    try {{
                                        data = await res.json();
                                    }} catch (_) {{}}
                                    state.status = "SUCCESS";
                                    state.operationId = (data && data.operation) ? Number(data.operation) : 0;
                                    state.message = `CREDITOS RECEBIDOS: +${{state.creditValue}} TJL!`;
                                    return;
                                }}

                                if (res.status === 429) {{
                                    state.status = "COOLDOWN";
                                    state.message = "AGUARDE COOLDOWN P/ RECEBER DE NOVO (429)";
                                    return;
                                }}

                                if (res.status === 401) {{
                                    state.status = "UNAUTHORIZED";
                                    state.message = "CONTA NAO CADASTRADA NA FEIRA (401)";
                                    // Reexibe o botão caso o jogador queira tentar outra conta Google
                                    if (state.overlay) {{
                                        state.overlay.style.display = "flex";
                                        positionOverlay();
                                    }}
                                    return;
                                }}

                                if (res.status === 403) {{
                                    state.status = "UNAUTHORIZED";
                                    state.message = "PRODUTO OU LIMITE NAO AUTORIZADO (403)";
                                    return;
                                }}

                                state.status = "ERROR";
                                state.message = `ERRO AO CREDITAR NA FEIRA (HTTP ${{res.status}})`;
                            }} catch (err) {{
                                console.error("[Feira] Erro ao enviar credito:", err);
                                state.status = "ERROR";
                                state.message = "ERRO DE CONEXAO COM A FEIRA";
                                if (state.overlay) {{
                                    state.overlay.style.display = "flex";
                                    positionOverlay();
                                }}
                            }}
                        }};

                        const mountGoogleAuth = () => {{
                            const gsi = window.google && window.google.accounts && window.google.accounts.id;
                            if (!gsi) return false;

                            const host = ensureOverlay();
                            host.style.display = "flex";
                            positionOverlay();

                            gsi.initialize({{
                                client_id: state.clientId,
                                auto_select: false,
                                cancel_on_tap_outside: false,
                                callback: (res) => {{
                                    if (!res || !res.credential) {{
                                        state.status = "ERROR";
                                        state.message = "FALHA NO LOGIN GOOGLE";
                                        return;
                                    }}
                                    sendCreditRequest(res.credential);
                                }},
                            }});

                            if (state.btnContainer) {{
                                state.btnContainer.innerHTML = "";
                                gsi.renderButton(state.btnContainer, {{
                                    type: "standard",
                                    theme: "filled_blue",
                                    size: "medium",
                                    text: "signin_with",
                                    shape: "pill",
                                    logo_alignment: "left",
                                    width: 200,
                                }});
                            }}

                            // Aciona também o prompt flutuante do Google One-Tap
                            try {{
                                gsi.prompt();
                            }} catch (e) {{
                                console.warn("[Feira] One-Tap prompt falhou:", e);
                            }}
                            return true;
                        }};

                        state.showVictoryAuth = (productId, creditValue) => {{
                            state.productId = Number(productId) || {self.product_id};
                            state.creditValue = Number(creditValue) || {self.credit_value};
                            state.status = "AWAITING_LOGIN";
                            state.message = `CONECTE O GOOGLE P/ RECEBER +${{state.creditValue}} TJL`;
                            state.operationId = 0;

                            if (state.pollTimer) {{
                                clearInterval(state.pollTimer);
                                state.pollTimer = null;
                            }}

                            if (!mountGoogleAuth()) {{
                                let attempts = 0;
                                state.pollTimer = setInterval(() => {{
                                    attempts += 1;
                                    if (state.status !== "AWAITING_LOGIN") {{
                                        clearInterval(state.pollTimer);
                                        state.pollTimer = null;
                                        return;
                                    }}
                                    if (mountGoogleAuth()) {{
                                        clearInterval(state.pollTimer);
                                        state.pollTimer = null;
                                    }} else if (attempts >= 40) {{
                                        clearInterval(state.pollTimer);
                                        state.pollTimer = null;
                                        state.status = "UNAVAILABLE";
                                        state.message = "LOGIN GOOGLE INDISPONIVEL NO NAVEGADOR";
                                    }}
                                }}, 250);
                            }}
                        }};

                        state.hideVictoryAuth = () => {{
                            if (state.pollTimer) {{
                                clearInterval(state.pollTimer);
                                state.pollTimer = null;
                            }}
                            try {{
                                if (window.google && window.google.accounts && window.google.accounts.id) {{
                                    window.google.accounts.id.cancel();
                                }}
                            }} catch (_) {{}}
                            if (state.overlay) {{
                                state.overlay.style.display = "none";
                            }}
                            state.status = "IDLE";
                            state.message = "";
                            state.operationId = 0;
                        }};

                        window._apexFeira = state;
                    }}
                }})();
                """
            )
            self._web_ready = True
        except BaseException:
            self._web_ready = False

    def start_victory_flow(self):
        """Inicia a solicitação de login Google One-Tap na tela de vitória."""
        self.operation_id = None
        if self._web_ready:
            try:
                import js  # type: ignore

                self.status = STATUS_AWAITING_LOGIN
                self.status_message = f"CONECTE O GOOGLE P/ RECEBER +{self.credit_value} TJL"
                js.window._apexFeira.showVictoryAuth(self.product_id, self.credit_value)
                return
            except BaseException:
                pass

        self.status = STATUS_AWAITING_LOGIN
        self.status_message = f"CONECTE O GOOGLE P/ RECEBER +{self.credit_value} TJL"

    def update(self):
        """Sincroniza o estado do fluxo OAuth / Fetch do navegador com o HUD do Pyxel."""
        if not self._web_ready:
            return
        try:
            import js  # type: ignore

            feira = js.window._apexFeira
            web_status = str(feira.status or STATUS_IDLE)
            web_msg = str(feira.message or "")
            web_op = int(feira.operationId or 0)
            self.status = web_status
            if web_msg:
                self.status_message = web_msg
            self.operation_id = web_op if web_op > 0 else None
        except BaseException:
            pass

    def submit_credential_sync(
        self,
        credential: str,
        sender: Callable[[str, dict[str, str], dict[str, int]], tuple[int, dict | None]] | None = None,
    ) -> tuple[str, str, int | None]:
        """Envia o POST de crédito de forma síncrona (útil para testes ou execução fora do navegador)."""
        try:
            headers = build_credit_headers(credential)
            payload = build_credit_payload(self.product_id, self.credit_value)
        except ValueError as exc:
            self.status = STATUS_ERROR
            self.status_message = str(exc)
            self.operation_id = None
            return (self.status, self.status_message, None)

        self.status = STATUS_SENDING
        self.status_message = f"ENVIANDO +{self.credit_value} CREDITOS..."
        self.operation_id = None

        try:
            if sender is not None:
                status_code, resp_body = sender(self.credit_url, headers, payload)
            else:
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    self.credit_url,
                    data=data_bytes,
                    headers=headers,
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        status_code = resp.getcode()
                        raw = resp.read().decode("utf-8", errors="replace")
                        resp_body = json.loads(raw) if raw.strip().startswith("{") else None
                except urllib.error.HTTPError as http_err:
                    status_code = http_err.code
                    resp_body = None
        except Exception:
            self.status = STATUS_ERROR
            self.status_message = "ERRO DE CONEXAO COM A FEIRA"
            self.operation_id = None
            return (self.status, self.status_message, None)

        status, message, op_id = interpret_credit_response(
            status_code,
            resp_body,
            credit_value=self.credit_value,
        )
        self.status = status
        self.status_message = message
        self.operation_id = op_id
        return (self.status, self.status_message, self.operation_id)

    def reset(self):
        """Oculta o overlay de login Google e limpa o estado ao iniciar novo turno."""
        self.status = STATUS_IDLE
        self.status_message = ""
        self.operation_id = None
        if self._web_ready:
            try:
                import js  # type: ignore

                js.window._apexFeira.hideVictoryAuth()
            except BaseException:
                pass
