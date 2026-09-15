from pathlib import Path
import math
import pyxel

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

class Player:
    def __init__(self, app, anchor_x=160, anchor_y=20, rope_length=65):
        self.app = app
        
        # Sistema de Ancoragem (Ponto fixado na fachada)
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.rope_length = rope_length
        
        # Ponto de fixação do cabo no sprite (arnês/mosquetão no ombro/costas)
        self.harness_offset_x = 8
        self.harness_offset_y = 10
        
        # Posição calculada do sprite (32x32)
        self.x = self.anchor_x - self.harness_offset_x
        self.y = self.anchor_y + self.rope_length - self.harness_offset_y
        
        # Timers de física e animação
        self.sway_timer = 0
        self.anim_timer = 0
        self.sway_angle = 0.0
        
        # Estado atual da animação (linha 0 = IDLE no spritesheet)
        self.state = "IDLE"
        self.anim_row = 0
        self.current_frame = 0

    def carregar_recursos(self):
        """Carrega o spritesheet do Cable-Runner no banco de imagens 2 do Pyxel."""
        sheet_path = BASE_DIR / "assets" / "CharacterIdeas" / "character_trenchcoat_sheet.png"
        if not sheet_path.exists():
            sheet_path = ROOT_DIR / "assets" / "CharacterIdeas" / "character_trenchcoat_sheet.png"
            
        if sheet_path.exists():
            pyxel.images[2].load(0, 0, str(sheet_path))

    def update(self):
        """Atualiza a física de suspensão na corda e a animação do personagem."""
        self.sway_timer += 1
        self.anim_timer += 1
        
        # Micro-balanço pendular natural de repouso (vento de alta altitude no Apex-01)
        # Amplitude suave de ~2 graus (0.035 rad), gerando ~2px de oscilação harmônica
        self.sway_angle = math.sin(self.sway_timer * 0.045) * 0.035
        
        # Posição exata do arnês baseada na física do pêndulo
        harness_x = self.anchor_x + math.sin(self.sway_angle) * self.rope_length
        harness_y = self.anchor_y + math.cos(self.sway_angle) * self.rope_length
        
        # Posição do canto superior esquerdo do sprite 32x32
        self.x = harness_x - self.harness_offset_x
        self.y = harness_y - self.harness_offset_y
        
        # Animação Idle: 4 frames a ~260ms por frame (~8 frames do Pyxel a 30 FPS)
        self.current_frame = (self.anim_timer // 8) % 4

    def draw_anchor(self):
        """Desenha o grampo mecânico da âncora fixado na fachada do prédio."""
        ax = int(self.anchor_x)
        ay = int(self.anchor_y)
        
        # Placa do grampo metálico (cor 5: cinza escuro, contorno cor 0: preto)
        pyxel.rect(ax - 3, ay - 2, 7, 4, 5)
        pyxel.rectb(ax - 3, ay - 2, 7, 4, 0)
        
        # Parafusos laterais (cor 6: cinza aço)
        pyxel.pset(ax - 2, ay, 6)
        pyxel.pset(ax + 2, ay, 6)
        
        # LED indicador de trava de ancoragem segura (cor 11: verde néon)
        pyxel.pset(ax, ay - 1, 11)
        
        # Argola/mosquetão onde a corda conecta (cor 6)
        pyxel.pset(ax, ay + 2, 6)

    def draw_cable(self):
        """Desenha a corda de aço sob tensão conectando a âncora ao arnês do alpinista."""
        ax = int(self.anchor_x)
        ay = int(self.anchor_y) + 2
        hx = int(self.x + self.harness_offset_x)
        hy = int(self.y + self.harness_offset_y)
        
        # Cabo de suspensão em aço trançado de alta resistência (cor 13: ardósia / cor 5)
        pyxel.line(ax, ay, hx, hy, 13)
        pyxel.pset(hx, hy, 6)  # Mosquetão metálico no arnês

    def draw(self):
        """Renderiza a âncora, a corda tensionada e o sprite animado do jogador."""
        # 1. Desenha a corda primeiro (passa atrás do personagem)
        self.draw_cable()
        
        # 2. Desenha o grampo da âncora na viga/fachada
        self.draw_anchor()
        
        # 3. Desenha o sprite do jogador (Banco 2, linha 0 = IDLE, transparente colkey 0)
        u = self.current_frame * 32
        v = self.anim_row * 32
        pyxel.blt(int(self.x), int(self.y), 2, u, v, 32, 32, 0)
