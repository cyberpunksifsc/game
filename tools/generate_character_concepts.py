#!/usr/bin/env python3
"""
Generator of 8 Distinct Cyberpunk Player Character Concepts (IDLE State)
Conforms to the Pixel Art Skill guidelines:
- 32x32 native canvas resolution
- Pyxel 16 default color palette with directional top-left lighting
- Distinct silhouettes and archetype personalities
- Harness connection point at (8, 10) for grapple cable consistency
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Pyxel 16-color Default Palette (RGBA)
PYXEL_PALETTE = {
    0: (0, 0, 0, 0),          # 0: Transparent
    1: (43, 43, 69, 255),     # 1: Navy / Dark Blue
    2: (146, 43, 87, 255),    # 2: Dark Purple / Magenta
    3: (0, 135, 81, 255),     # 3: Dark Green
    4: (171, 82, 54, 255),    # 4: Brown
    5: (95, 87, 79, 255),     # 5: Dark Gray
    6: (194, 195, 199, 255),  # 6: Light Gray
    7: (255, 241, 232, 255),  # 7: White
    8: (255, 0, 77, 255),     # 8: Red / Hot Pink
    9: (255, 163, 0, 255),    # 9: Orange
    10: (255, 236, 39, 255),  # 10: Yellow
    11: (0, 228, 54, 255),    # 11: Green
    12: (41, 173, 255, 255),  # 12: Cyan / Neon Blue
    13: (131, 118, 156, 255), # 13: Indigo / Slate
    14: (255, 204, 170, 255), # 14: Peach / Skin
    15: (255, 119, 168, 255), # 15: Pink
}


def parse_ascii_grid(lines: list[str]) -> list[list[int]]:
    """Converts 32 lines of 32 hex/symbol characters into a 32x32 integer matrix."""
    grid = []
    # Symbol mapping: '.' or ' ' = 0, '0'..'9' = 0..9, 'A'..'F' = 10..15
    char_map = {
        '.': 0, ' ': 0,
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
        '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
        'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15,
    }
    for y, line in enumerate(lines[:32]):
        row = []
        for x, ch in enumerate(line[:32]):
            row.append(char_map.get(ch, 0))
        # Pad row to 32 if needed
        while len(row) < 32:
            row.append(0)
        grid.append(row)
    while len(grid) < 32:
        grid.append([0] * 32)
    return grid


def grid_to_image(grid: list[list[int]]) -> Image.Image:
    """Converts 32x32 palette matrix to a PIL RGBA Image."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    for y in range(32):
        for x in range(32):
            col_idx = grid[y][x]
            img.putpixel((x, y), PYXEL_PALETTE.get(col_idx, (0, 0, 0, 0)))
    return img


# ==============================================================================
# 8 CONCEPTS DEFINITIONS (32x32 each)
# ==============================================================================

CONCEPTS_DATA = {}

# ------------------------------------------------------------------------------
# 1. Trenchcoat Drifter (Refined classic noir climber)
# Wide collar duster, glowing cyan HUD visor, harness with carabiner
# ------------------------------------------------------------------------------
CONCEPTS_DATA["01_trenchcoat_drifter"] = {
    "title": "01. Trenchcoat Drifter",
    "subtitle": "Classic Cyberpunk Noir Alpinist",
    "desc": "Sobretudo de couro desgastado, gola alta corta-vento, visor HUD retangular ciano e coldre de gancho.",
    "grid": parse_ascii_grid([
        "................................", # 00
        "................................", # 01
        "................................", # 02
        "...........111111...............", # 03 Chapéu/Gola topo
        ".........1111111111.............", # 04
        ".........9911CCCCCCA............", # 05 Visor ciano
        ".........9911CCCCCCA............", # 06
        ".........44144444449............", # 07 Rosto/lenço
        "......55.44144444EE49...........", # 08 Arnês no ombro
        "....5B55449944444444............", # 09 Mosquetão LED verde
        "....5B5544999A1111..4...........", # 10 (8,10) CARABINER!
        "....5B5544999AA444444...........", # 11
        "....55554494AA99441155..........", # 12 Peitoral do sobretudo
        "....111144944499141155666.......", # 13
        "....444499944499141155676166....", # 14 Braço e luva
        "...4444999111111111111566..6....", # 15 Cinto de utilidades
        "..444499111CCCCCC11111..........", # 16 Fivela néon
        "...4441..11111111.1111..........", # 17 Fendas do sobretudo
        ".........111111...1551..........", # 18 Pernas
        ".........111111...1551..........", # 19
        ".........155111...1551..........", # 20
        ".........111111...1551..........", # 21
        ".........155556...15556.........", # 22 Botas pesadas
        ".........111556...11156.........", # 23
        "................................", # 24
        "................................", # 25
        "................................", # 26
        "................................", # 27
        "................................", # 28
        "................................", # 29
        "................................", # 30
        "................................", # 31
    ])
}

# ------------------------------------------------------------------------------
# 2. Exo-Rig Heavy (Industrial Welder & Builder)
# Bulky yellow/black hydraulic loader shoulders, heavy mask, resin tank
# ------------------------------------------------------------------------------
CONCEPTS_DATA["02_exorig_heavy"] = {
    "title": "02. Exo-Rig Heavy",
    "subtitle": "Industrial Welder & Heavy Loader",
    "desc": "Exoesqueleto hidráulico amarelo de alto torque, capacete industrial reforçado e botijas de resina nas costas.",
    "grid": parse_ascii_grid([
        "................................", # 00
        "..........AAAAAA................", # 01 Topo do capacete
        ".........AA9999AA...............", # 02
        "........AA9911119A..............", # 03 Viseira de solda
        "........AA9199991A..............", # 04
        "........AA9199991A..............", # 05
        "........5599555595..............", # 06 Filtro de ar duplo
        "......55AAAA5555AAAA55..........", # 07 Ombreiras largas de exoesqueleto
        "....5566AA995555AA996655........", # 08 Articulações hidráulicas
        "...55B36AA991111AA996655........", # 09 Cilindro traseiro
        "...55B36AA1AA1AA1AA9665.........", # 10 Listras de perigo (8,10)
        "...55B36551AA1AA1AA955..........", # 11
        "....5566551111111155655.........", # 12 Peitoral reforçado
        "....5566556677665555665.........", # 13 Braço com atuador
        "....11115566666611556655........", # 14 Luvas de soldagem
        "....55551111111111115555........", # 15 Cinto de ancoragem pesada
        "....55..AA555555AA..55..........", # 16 Coxas com vigas exo
        "........AA551155AA..............", # 17
        "........AA551155AA..............", # 18 Pistões pneumáticos
        "........5566115566..............", # 19
        "........5566115566..............", # 20 Joelheiras blindadas
        "........AA5511AA55..............", # 21
        ".......5AA5565AA556.............", # 22 Botas com trava magnética
        ".......555556555556.............", # 23
        "................................", # 24
        "................................", # 25
        "................................", # 26
        "................................", # 27
        "................................", # 28
        "................................", # 29
        "................................", # 30
        "................................", # 31
    ])
}

# ------------------------------------------------------------------------------
# 3. Cyber-Ninja (Shadow Infiltrator / Ghost Recon)
# Sleek dark suit, dual magenta optics, high-tech fluttering scarf
# ------------------------------------------------------------------------------
CONCEPTS_DATA["03_cyber_ninja"] = {
    "title": "03. Cyber-Ninja",
    "subtitle": "Stealth Infiltrator & Recon Ghost",
    "desc": "Traje de nanofibra esguio preto e roxo, óticas duplas magenta, cachecol cibernético esvoaçante e garras magnéticas.",
    "grid": parse_ascii_grid([
        "................................", # 00
        "................................", # 01
        "................................", # 02
        "............1111................", # 03 Capuz aerodinâmico
        "...........111111...............", # 04
        "...........181181...............", # 05 Olhos cibernéticos duplos
        "...........1F11F1...............", # 06 Brilho magenta
        "...........111111...............", # 07 Máscara angular
        ".........22.1111..22............", # 08 Gola do cachecol
        "....22FF222211112222............", # 09 Cachecol flutuando à esquerda
        "...22FF222221CC1222.............", # 10 Conduíte cyan / (8,10)
        "..22FF22....1111................", # 11 Ponta do cachecol
        "....22......15511666............", # 12 Peitoral leve
        "............15511676............", # 13 Braçadeira com garras
        "............11111666............", # 14
        "...........11221111.............", # 15 Cinto de kunais/âncoras
        "...........11221111.............", # 16
        "...........1111.111.............", # 17 Pernas ágeis
        "...........1111.111.............", # 18
        "...........1221.1221............", # 19 Detalhe roxo nas coxas
        "...........1111.1111............", # 20
        "...........1551.1551............", # 21 Tabi com solado aderente
        "...........1556.1556............", # 22
        "...........1116.1116............", # 23
        "................................", # 24
        "................................", # 25
        "................................", # 26
        "................................", # 27
        "................................", # 28
        "................................", # 29
        "................................", # 30
        "................................", # 31
    ])
}

# ------------------------------------------------------------------------------
# 4. Hazmat Bio-Cleaner (Corrosive Smog & Acid Specialist)
# Rounded toxic-yellow pressurized hood, convex green visor, chemical backpack
# ------------------------------------------------------------------------------
CONCEPTS_DATA["04_hazmat_cleaner"] = {
    "title": "04. Hazmat Bio-Cleaner",
    "subtitle": "Toxic Smog & Acid Specialist",
    "desc": "Traje hermético amarelo radioativo contra chuva ácida, visor panorâmico esférico e tanque de solvente nas costas.",
    "grid": parse_ascii_grid([
        "................................", # 00
        "...........AAAAA................", # 01 Capuz esférico
        "..........AAAAAAA...............", # 02
        ".........AA11111AA..............", # 03 Moldura do visor
        ".........A1BB7BBB1A.............", # 04 Visor espelhado verde/ciano
        ".........A1BBBBBB1A.............", # 05
        ".........AA11111AA..............", # 06
        "..........A55665A...............", # 07 Respirador frontal
        "......55.AAA5555AAA.............", # 08 Ombro pressurizado
        "....55335AA955559AA.............", # 09 Tanque químico
        "...553B35AA911119AA5............", # 10 Líquido radioativo (8,10)
        "...553335AA91CC19AA5............", # 11
        "....55555AA999999AA556..........", # 12 Avental espesso
        ".....55..555555555555676........", # 13
        ".........555555555555566........", # 14 Luvas de borracha
        ".........AAAA11AAAA.............", # 15 Cinto de vedação
        ".........AAAA..AAAA.............", # 16 Calças largas
        ".........AA99..AA99.............", # 17
        ".........AA99..AA99.............", # 18
        ".........AA55..AA55.............", # 19
        ".........AA55..AA55.............", # 20
        ".........1111..1111.............", # 21 Botas pesadas de descontaminação
        ".........1551..1551.............", # 22
        ".........1556..1556.............", # 23
        "................................", # 24
        "................................", # 25
        "................................", # 26
        "................................", # 27
        "................................", # 28
        "................................", # 29
        "................................", # 30
        "................................", # 31
    ])
}

# ------------------------------------------------------------------------------
# 5. Street Punk / Scavenger (Underground Neon Rebel)
# Punk mohawk, cybernetic eye, denim vest, chrome cyber-arm, ripped knees
# ------------------------------------------------------------------------------
CONCEPTS_DATA["05_street_punk"] = {
    "title": "05. Street Punk Climber",
    "subtitle": "Underground Scavenger & Rebel",
    "desc": "Moicano rosa neon, jaqueta jeans rasgada, braço esquerdo cibernético de cromo e remendos de sucata.",
    "grid": parse_ascii_grid([
        "................................", # 00
        "............8888................", # 01 Moicano punk
        "...........88FF88...............", # 02
        "...........11EE11...............", # 03 Rosto
        "...........1EECCE...............", # 04 Olho cibernético cyan
        "...........1EE1EE...............", # 05 Máscara de pano
        "...........118811...............", # 06 Bandana no pescoço
        ".........CCCC11CCCC.............", # 07 Colete jeans rasgado
        "......55.CC111111CC.666.........", # 08 Ombro de cromo à direita
        "....55885CC81EE18CC6766.........", # 09 Braço cibernético
        "...558885CC111111CC.666.........", # 10 (8,10) Mosquetão
        "....55555CC119911CC.666.........", # 11
        ".........CC111111CC.666.........", # 12
        ".........1111111111.666.........", # 13 Punho de metal
        ".........1155555511.666.........", # 14
        ".........1111111111.............", # 15 Cinto com correntes
        ".........5551..1555.............", # 16 Calça cargo surrada
        ".........5551..1555.............", # 17
        ".........55EE..1555.............", # 18 Rasgo no joelho (pele)
        ".........5551..1555.............", # 19
        ".........5551..1555.............", # 20
        ".........8881..8881.............", # 21 Tênis de cano alto neon
        ".........8887..8887.............", # 22
        ".........1117..1117.............", # 23
        "................................", # 24
        "................................", # 25
        "................................", # 26
        "................................", # 27
        "................................", # 28
        "................................", # 29
        "................................", # 30
        "................................", # 31
    ])
}

# ------------------------------------------------------------------------------
# 6. Neo-Apex Corporate Enforcer (High-Tech Security Shocktrooper)
# Angular white ceramic armor, red visor line, sleek ballistic shell
# ------------------------------------------------------------------------------
CONCEPTS_DATA["06_corporate_enforcer"] = {
    "title": "06. Apex Security Enforcer",
    "subtitle": "Privatized Corporate Shocktrooper",
    "desc": "Blindagem tática de cerâmica branca, visor visor monocular vermelho corporativo e placa peitoral com LED Neo-Apex.",
    "grid": parse_ascii_grid([
        "................................", # 00
        "..........777777................", # 01 Topo do capacete branco
        ".........77666677...............", # 02
        "........77666666775.............", # 03 Antena lateral
        "........77188881775.............", # 04 Sensor visor vermelho
        "........7718888177..............", # 05
        "........7766666677..............", # 06 Placa mandibular
        "......55.77777777.55............", # 07 Ombreiras de cerâmica
        "....558857766116677.............", # 08
        "...55888577661C6677.666.........", # 09 Logo corporativo cyan
        "...55888577661C6677.676.........", # 10 (8,10) Ancoragem tática
        "....555557766116677.666.........", # 11
        ".........7766666677.666.........", # 12 Peitoral blindado
        ".........5577667755.666.........", # 13
        ".........1111111111.111.........", # 14 Luva tática
        ".........5577777755.............", # 15 Cinto de serviço
        ".........7766..7766.............", # 16 Placas de coxa
        ".........7766..7766.............", # 17
        ".........1111..1111.............", # 18 Articulação em kevlar
        ".........7766..7766.............", # 19 Caneleiras brancas
        ".........7766..7766.............", # 20
        ".........1111..1111.............", # 21 Botas magnéticas
        ".........55556.55556............", # 22
        ".........11116.11116............", # 23
        "................................", # 24
        "................................", # 25
        "................................", # 26
        "................................", # 27
        "................................", # 28
        "................................", # 29
        "................................", # 30
        "................................", # 31
    ])
}

# ------------------------------------------------------------------------------
# 7. Synth Unit Model-04 (Autonomous Maintenance Android)
# Robotic chassis in slate/navy, triad of cyan camera lenses, digitigrade joints
# ------------------------------------------------------------------------------
CONCEPTS_DATA["07_synth_android"] = {
    "title": "07. Synth Unit Model-04",
    "subtitle": "Autonomous Maintenance Android",
    "desc": "Chassi robótico em ardósia e azul escuro, trio de lentes óticas ciano e condutores de energia expostos.",
    "grid": parse_ascii_grid([
        "................................", # 00
        "................................", # 01
        "...........DDDDDD...............", # 02 Cabeça robótica chassi
        "..........DDDDDDDD..............", # 03
        "..........DD1C1CDD..............", # 04 Lentes óticas superiores
        "..........DD11C1DD..............", # 05 Lente ótica inferior
        "..........DD5555DD..............", # 06 Ventilação de refrigeração
        "..........55666655..............", # 07 Junta de pescoço
        "......55.DDDDDDDDDD.............", # 08 Ombreiras sintéticas
        "....55BB5DD1CCCC1DD.............", # 09 Linha de pulso cyan
        "...55BB55DD1C77C1DD.66..........", # 10 Núcleo de energia (8,10)
        "....55555DD1CCCC1DD6766.........", # 11
        ".........5511CC1155.666.........", # 12 Eixo de cintura estreito
        ".........5566116655.666.........", # 13
        ".........5566116655.555.........", # 14 Garras articuladas
        ".........DDDDDDDDDD.............", # 15 Bacia mecânica
        ".........DD55..55DD.............", # 16 Pernas mecânicas
        ".........DD55..55DD.............", # 17
        ".........6655..5566.............", # 18 Juntas esféricas
        "..........55....55..............", # 19 Hastes amortecedoras
        "..........55....55..............", # 20
        ".........6655..5566.............", # 21 Pés articulados tripés
        ".........6611..1166.............", # 22
        ".........6611..1166.............", # 23
        "................................", # 24
        "................................", # 25
        "................................", # 26
        "................................", # 27
        "................................", # 28
        "................................", # 29
        "................................", # 30
        "................................", # 31
    ])
}

# ------------------------------------------------------------------------------
# 8. Aero-Courier / Sky-Runner (High-Altitude Acrobat)
# Puffy orange bomber jacket, twin mini thrusters on back, runner tights
# ------------------------------------------------------------------------------
CONCEPTS_DATA["08_aero_courier"] = {
    "title": "08. Aero-Courier Sky-Runner",
    "subtitle": "High-Altitude Rooftop Acrobat",
    "desc": "Jaqueta bomber inflada neon laranja, mini-propulsor iônico nas costas e óculos de aviador retrô-futurista.",
    "grid": parse_ascii_grid([
        "................................", # 00
        "...........555555...............", # 01 Capacete leve de aviador
        "..........55555555..............", # 02
        ".........5599..9955.............", # 03 Óculos de lente âmbar dupla
        ".........55AA..AA55.............", # 04
        ".........5511EE1155.............", # 05 Rosto / máscara
        "..........55999955..............", # 06 Gola da bomber
        "......55.9999999999.............", # 07 Jaqueta bomber laranja volumosa
        "....55CC599999999999............", # 08
        "...55CC759911CC11999666.........", # 09 Mini-propulsor cyan (8,10)
        "....555559911CC11999676.........", # 10
        ".........99999999999666.........", # 11
        ".........99999999999666.........", # 12 Volume da jaqueta
        ".........1111111111.111.........", # 13 Luvas de escalada
        ".........1111111111.............", # 14 Cintura justa
        ".........11AA..AA11.............", # 15 Faixa de perigo lateral
        ".........11AA..AA11.............", # 16 Calça de corrida colada
        ".........1111..1111.............", # 17
        ".........5555..5555.............", # 18 Joelheiras acolchoadas
        ".........1111..1111.............", # 19
        ".........9999..9999.............", # 20 Tênis com mola pneumática
        ".........9977..9977.............", # 21
        ".........5577..5577.............", # 22 Solado de alto atrito
        ".........1111..1111.............", # 23
        "................................", # 24
        "................................", # 25
        "................................", # 26
        "................................", # 27
        "................................", # 28
        "................................", # 29
        "................................", # 30
        "................................", # 31
    ])
}


def main():
    base_dir = Path(__file__).resolve().parent.parent
    concepts_dir = base_dir / "assets" / "CharacterIdeas" / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    print(f"Gerando 8 conceitos de sprite em {concepts_dir}...")

    # 1. Salvar os 8 PNGs individuais (32x32) e versões 8x para visualização direta
    individual_images = []
    for key, data in CONCEPTS_DATA.items():
        img = grid_to_image(data["grid"])
        individual_images.append((key, data, img))

        # Salva 32x32 nativo
        path_32 = concepts_dir / f"concept_{key}.png"
        img.save(path_32)

        # Salva versão ampliada 8x (256x256) com nearest neighbor (sem borrar)
        img_8x = img.resize((256, 256), Image.Resampling.NEAREST)
        path_8x = concepts_dir / f"preview_8x_{key}.png"
        img_8x.save(path_8x)
        print(f"  -> {data['title']}: {path_32.name} (32x32) e {path_8x.name} (256x256)")

    # 2. Criar Spritesheet horizontal único contendo os 8 personagens (256x32)
    sheet_img = Image.new("RGBA", (32 * 8, 32), (0, 0, 0, 0))
    for i, (_, _, img) in enumerate(individual_images):
        sheet_img.paste(img, (i * 32, 0))
    sheet_path = concepts_dir / "all_8_concepts_strip_256x32.png"
    sheet_img.save(sheet_path)
    print(f"  -> Spritesheet 256x32 salvo: {sheet_path.name}")

    # 3. Criar Cartela de Apresentação e Comparação em Alta Resolução (Showcase 8x)
    # 4 colunas x 2 linhas com cards informativos, zoom 6x e fundo escuro cyberpunk
    card_w = 260
    card_h = 290
    showcase_w = 4 * card_w + 50
    showcase_h = 2 * card_h + 120

    showcase = Image.new("RGBA", (showcase_w, showcase_h), (20, 20, 32, 255))
    draw = ImageDraw.Draw(showcase)

    # Título do Showcase
    draw.rectangle([(0, 0), (showcase_w, 60)], fill=(12, 12, 22, 255))
    draw.line([(0, 60), (showcase_w, 60)], fill=(41, 173, 255, 255), width=2)
    draw.text((30, 16), "APEX GRAPPLER — 8 CONCEITOS VISUAIS PARA O ALPINISTA INDUSTRIAL", fill=(255, 241, 232, 255))
    draw.text((30, 38), "Arte nativa 32x32 | Paleta Pyxel 16 Cores | Conexao de Gancho em (8, 10)", fill=(194, 195, 199, 255))

    # Renderiza cada card
    for i, (key, data, img) in enumerate(individual_images):
        col = i % 4
        row = i // 4
        cx = 25 + col * card_w
        cy = 80 + row * card_h

        # Moldura do card
        draw.rectangle([(cx, cy), (cx + card_w - 15, cy + card_h - 15)], fill=(28, 28, 45, 255), outline=(50, 50, 75, 255), width=1)
        # Borda de destaque superior
        draw.line([(cx, cy), (cx + card_w - 15, cy)], fill=(255, 163, 0, 255) if i == 0 else (41, 173, 255, 255), width=2)

        # Fundo do sprite com grade de xadrez sutil
        preview_box_x = cx + 55
        preview_box_y = cy + 18
        draw.rectangle([(preview_box_x - 4, preview_box_y - 4), (preview_box_x + 132, preview_box_y + 132)], fill=(15, 15, 25, 255), outline=(95, 87, 79, 255))

        # Quadriculado de transparência 8x8 no fundo
        for qy in range(16):
            for qx in range(16):
                bg_col = (24, 24, 38, 255) if (qx + qy) % 2 == 0 else (18, 18, 30, 255)
                draw.rectangle([(preview_box_x + qx * 8, preview_box_y + qy * 8), (preview_box_x + (qx + 1) * 8 - 1, preview_box_y + (qy + 1) * 8 - 1)], fill=bg_col)

        # Sprite 32x32 ampliado 4x (128x128)
        scaled_sprite = img.resize((128, 128), Image.Resampling.NEAREST)
        showcase.paste(scaled_sprite, (preview_box_x, preview_box_y), scaled_sprite)

        # Textos informativos
        draw.text((cx + 10, cy + 160), data["title"], fill=(255, 236, 39, 255))
        draw.text((cx + 10, cy + 178), data["subtitle"], fill=(41, 173, 255, 255))

        # Descrição dividida em linhas manuais
        words = data["desc"].split(" ")
        line1 = ""
        line2 = ""
        for w in words:
            if len(line1 + " " + w) <= 32:
                line1 = (line1 + " " + w).strip()
            else:
                line2 = (line2 + " " + w).strip()

        draw.text((cx + 10, cy + 202), line1, fill=(194, 195, 199, 255))
        draw.text((cx + 10, cy + 218), line2, fill=(194, 195, 199, 255))

        # Indicador de 1x nativo no cantinho
        draw.text((cx + 10, cy + 242), "Escala nativa 1x:", fill=(95, 87, 79, 255))
        showcase.paste(img, (cx + 120, cy + 236), img)

    showcase_path = concepts_dir / "concepts_showcase_comparison.png"
    showcase.save(showcase_path)
    print(f"  -> Painel Comparativo Geral salvo: {showcase_path.name}")
    print("Concluído com sucesso!")


if __name__ == "__main__":
    main()
