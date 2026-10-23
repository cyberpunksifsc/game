"""
Visualizador Interativo Pyxel para os 8 Conceitos de Sprite do Alpinista
Permite inspecionar cada conceito em tempo real com o motor Pyxel,
testar contra os fundos reais do jogo e verificar a conexao do arnês do gancho.

Controles:
  [1] a [8] ou [Esquerda]/[Direita]: Alternar entre os 8 personagens
  [B]: Alternar fundo (Grid Escuro, Skyline Noturno, Fachada com Janelas)
  [Z]: Alternar Zoom (1x nativo, 2x, 4x)
  [C]: Alternar exibição do cabo de ancoragem no arnês (8, 10)
  [Q] ou [Esc]: Sair
"""

from pathlib import Path
import math
import pyxel

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
CONCEPTS_DIR = ROOT_DIR / "assets" / "CharacterIdeas" / "concepts"
STRIP_PATH = CONCEPTS_DIR / "all_8_concepts_strip_256x32.png"

CHARACTERS_INFO = [
    {
        "id": 1,
        "name": "Trenchcoat Drifter",
        "archetype": "Cyberpunk Noir Alpinist",
        "tagline": "Sobretudo marrom clássico, visor ciano e coldre tático",
    },
    {
        "id": 2,
        "name": "Exo-Rig Heavy",
        "archetype": "Industrial Welder & Loader",
        "tagline": "Exoesqueleto amarelo, pistões hidráulicos e botijas de resina",
    },
    {
        "id": 3,
        "name": "Cyber-Ninja",
        "archetype": "Stealth Infiltrator & Recon",
        "tagline": "Nanofibra esguia preta/roxa, óticas duplas e cachecol digital",
    },
    {
        "id": 4,
        "name": "Hazmat Bio-Cleaner",
        "archetype": "Toxic Smog & Acid Specialist",
        "tagline": "Traje hermético amarelo, visor esférico e tanque químico",
    },
    {
        "id": 5,
        "name": "Street Punk",
        "archetype": "Underground Neon Rebel",
        "tagline": "Moicano rosa neon, colete jeans e braço cibernético cromado",
    },
    {
        "id": 6,
        "name": "Apex Security Enforcer",
        "archetype": "Corporate Tactical Guard",
        "tagline": "Placas cerâmicas brancas, sensor vermelho e insígnia corporativa",
    },
    {
        "id": 7,
        "name": "Synth Unit Model-04",
        "archetype": "Autonomous Maintenance Android",
        "tagline": "Chassi robótico ardósia, três lentes óticas e linhas de energia",
    },
    {
        "id": 8,
        "name": "Aero-Courier",
        "archetype": "High-Altitude Rooftop Acrobat",
        "tagline": "Jaqueta bomber neon laranja, propulsor iônico e óculos retrô",
    },
]


class CharacterPreviewApp:
    def __init__(self):
        pyxel.init(320, 180, title="Apex Grappler — 8 Character Concepts Preview", fps=30)
        pyxel.mouse(True)

        self.selected_index = 0
        self.bg_mode = 1  # 0: Grid escuro, 1: Skyline city1, 2: Fachada com janela
        self.zoom = 2     # 1: 1x, 2: 2x, 4: 4x
        self.show_cable = True
        self.anim_timer = 0

        # Carrega a fita de 8 sprites no Banco 0 (256x32)
        if STRIP_PATH.exists():
            pyxel.images[0].load(0, 0, str(STRIP_PATH))

        # Carrega o background city1 no Banco 1
        bg_file = ROOT_DIR / "assets" / "BackGround" / "city1" / "1.png"
        if bg_file.exists():
            pyxel.images[1].load(0, 0, str(bg_file))

        pyxel.run(self.update, self.draw)

    def update(self):
        self.anim_timer += 1

        # Teclas numéricas 1 a 8
        for i in range(8):
            key = getattr(pyxel, f"KEY_{i + 1}", None)
            if key and pyxel.btnp(key):
                self.selected_index = i

        # Navegação com setas
        if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            self.selected_index = (self.selected_index - 1) % 8
        if pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            self.selected_index = (self.selected_index + 1) % 8

        # Alternar fundo com B
        if pyxel.btnp(pyxel.KEY_B):
            self.bg_mode = (self.bg_mode + 1) % 3

        # Alternar Zoom com Z
        if pyxel.btnp(pyxel.KEY_Z):
            if self.zoom == 1:
                self.zoom = 2
            elif self.zoom == 2:
                self.zoom = 4
            else:
                self.zoom = 1

        # Alternar cabo com C
        if pyxel.btnp(pyxel.KEY_C):
            self.show_cable = not self.show_cable

        # Sair com Q ou Escape
        if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

    def draw_background(self):
        if self.bg_mode == 0:
            # Grid escuro de desenvolvimento
            pyxel.cls(0)
            for x in range(0, 320, 16):
                pyxel.line(x, 0, x, 180, 1)
            for y in range(0, 180, 16):
                pyxel.line(0, y, 320, y, 1)

        elif self.bg_mode == 1:
            # Skyline de New Tokyo (city1)
            pyxel.cls(0)
            pyxel.blt(32, 0, 1, 0, 0, 256, 180)

        elif self.bg_mode == 2:
            # Fachada do edifício com janelas
            pyxel.cls(1)
            pyxel.rect(44, 0, 232, 180, 0)
            pyxel.rectb(44, 0, 232, 180, 5)
            # Janelas simuladas
            for fy in (20, 68, 116):
                for fx in (58, 102, 146, 190, 234):
                    pyxel.rect(fx, fy, 32, 24, 1)
                    pyxel.rectb(fx, fy, 32, 24, 5)
                    pyxel.line(fx, fy + 12, fx + 32, fy + 12, 5)

    def draw(self):
        self.draw_background()

        # Balanço sutil de respiração idle
        bob_y = math.sin(self.anim_timer * 0.1) * 1.5

        # Posição central do personagem
        center_x = 144
        center_y = 66 + int(bob_y)

        # 1. Simulação da corda de ancoragem presa no ponto do arnês (x + 8, y + 10)
        if self.show_cable:
            anchor_x = center_x + 8 + 40
            anchor_y = 16
            harness_x = center_x + 8
            harness_y = center_y + 10

            pyxel.line(anchor_x, anchor_y, harness_x, harness_y, 13)
            # Ponto de fixação da âncora
            pyxel.circ(anchor_x, anchor_y, 2, 11)
            pyxel.pset(anchor_x, anchor_y, 7)
            # Mosquetão
            pyxel.pset(harness_x, harness_y, 6)

        # 2. Desenho do sprite selecionado em escala nativa (1x)
        u = self.selected_index * 32
        pyxel.blt(center_x, center_y, 0, u, 0, 32, 32, 0)

        # 3. Caixa de Destaque Ampliada à Direita (Zoom 2x ou 4x)
        info = CHARACTERS_INFO[self.selected_index]
        zoom_box_x = 224
        zoom_box_y = 44
        zoom_size = 32 * self.zoom

        # Painel do Zoom
        pyxel.rect(zoom_box_x - 6, zoom_box_y - 18, zoom_size + 12, zoom_size + 30, 0)
        pyxel.rectb(zoom_box_x - 6, zoom_box_y - 18, zoom_size + 12, zoom_size + 30, 5)
        pyxel.text(zoom_box_x, zoom_box_y - 12, f"ZOOM {self.zoom}x", 10)

        # Sprite com zoom (blt escalado através de passos)
        for py in range(32):
            for px in range(32):
                col = pyxel.images[0].pget(u + px, py)
                if col != 0:
                    pyxel.rect(
                        zoom_box_x + px * self.zoom,
                        zoom_box_y + py * self.zoom,
                        self.zoom,
                        self.zoom,
                        col,
                    )

        # 4. Fita inferior com os 8 ícones para seleção rápida
        strip_y = 148
        pyxel.rect(0, strip_y - 4, 320, 36, 0)
        pyxel.line(0, strip_y - 4, 320, strip_y - 4, 5)

        for i in range(8):
            slot_x = 12 + i * 38
            is_active = (i == self.selected_index)
            border_col = 10 if is_active else 5

            # Borda do slot
            pyxel.rect(slot_x - 2, strip_y - 1, 36, 26, 1 if is_active else 0)
            pyxel.rectb(slot_x - 2, strip_y - 1, 36, 26, border_col)
            # Sprite em miniatura
            pyxel.blt(slot_x, strip_y, 0, i * 32, 0, 32, 24, 0)
            # Número do atalho
            pyxel.text(slot_x + 14, strip_y + 20, str(i + 1), 10 if is_active else 6)

        # 5. HUD Superior com informações do arquétipo
        pyxel.rect(0, 0, 320, 32, 0)
        pyxel.line(0, 32, 320, 32, 12)

        pyxel.text(10, 5, f"[{info['id']}/8] {info['name'].upper()}", 10)
        pyxel.text(10, 14, f"Arquetipo: {info['archetype']}", 12)
        pyxel.text(10, 23, info["tagline"], 7)

        # Dicas de atalhos à direita
        pyxel.text(205, 5, "1-8 / Setas: Trocar", 6)
        pyxel.text(205, 14, f"B: Fundo (Modo {self.bg_mode})", 6)
        pyxel.text(205, 23, f"Z: Zoom ({self.zoom}x) | C: Cabo", 6)


if __name__ == "__main__":
    CharacterPreviewApp()
