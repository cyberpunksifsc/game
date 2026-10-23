#!/usr/bin/env python3
"""
Polished 8 Cyberpunk Player Character Concepts (IDLE State)
Constructed following professional pixel art guidelines:
- 32x32 native canvas resolution with continuous 1px dark contour
- Realistic anatomy proportions: Head (Y=2..8), Torso (Y=9..19), Legs (Y=20..30)
- Consistent ground contact at Y=29-30 and harness connection at (8, 10)
- Rich 3-4 shade ramps with warm highlights and cool shadows
- 8 unmistakable silhouettes and cyberpunk archetypes
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw

def hex_to_rgb(hex_str: str) -> tuple[int, int, int, int]:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r, g, b = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        return (r, g, b, 255)
    elif len(hex_str) == 8:
        r, g, b, a = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4, 6))
        return (r, g, b, a)
    raise ValueError(f"Invalid hex color: {hex_str}")

# Palette helper
def make_palette(mapping: dict[str, str]) -> dict[str, tuple[int, int, int, int]]:
    pal = {'.': (0, 0, 0, 0), ' ': (0, 0, 0, 0)}
    for k, v in mapping.items():
        pal[k] = hex_to_rgb(v)
    return pal

def render_ascii_sprite(lines: list[str], pal: dict[str, tuple[int, int, int, int]]) -> Image.Image:
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    for y, line in enumerate(lines[:32]):
        for x, char in enumerate(line[:32]):
            if char in pal and pal[char][3] > 0:
                img.putpixel((x, y), pal[char])
    return img

CONCEPTS = {}

# ==============================================================================
# 01. THE TRENCHCOAT COURIER (Cyber-Noir Blade Alpinist)
# ==============================================================================
# Fedora hat tilted, cyan HUD visor, leather duster coat, harness & grapple
PAL_01 = make_palette({
    'K': '#11121a', # Dark outline
    'H': '#242a3a', # Hat dark
    'h': '#434f68', # Hat mid
    'I': '#6b7b99', # Hat highlight
    'V': '#00e5ff', # Visor neon cyan
    'v': '#99f5ff', # Visor specular
    'C': '#0099aa', # Visor shadow
    'L': '#4a2c1b', # Coat shadow
    'l': '#8c522f', # Coat mid
    'm': '#c97c47', # Coat highlight
    'n': '#f0b078', # Coat specular
    'S': '#202533', # Pants dark
    's': '#3a445c', # Pants mid
    'B': '#1a1d26', # Boots dark
    'b': '#3f4657', # Boots mid
    'O': '#ff8c00', # Harness neon orange
    'o': '#ffd060', # Carabiner gold
    'G': '#a0a8b8', # Grappler metal
    'g': '#e0e5f0', # Grappler highlight
    'P': '#00ff66', # Carabiner LED green
})

GRID_01 = [
    "................................", # 00
    "................................", # 01
    ".............KKKKKK.............", # 02 Topo chapéu
    "...........KKHHhhhhKK...........", # 03 Copa chapéu
    ".........KKHHhhhhIIIIKK.........", # 04 Aba chapéu
    ".......KKKKKKKKKKKKKKKKKK.......", # 05 Aba estendida
    "...........KKVVvvKK.............", # 06 Visor cyan por baixo
    "...........KKCCVVKK..KKKK.......", # 07 Visor e gola
    ".........KKLLKKKKLLKKGGggKK.....", # 08 Gola alta e arma de gancho
    ".......KKLLllKKLLllKKGGggKK.....", # 09 Ombreira e coldre
    ".....KKOPOOllKKmmllKKgGggKK.....", # 10 (8,10) Mosquetão & Garra
    ".....KKOPKKllKKmmllKKKKKKKK.....", # 11
    ".....KKLLKKmmLLllmmLLKK.........", # 12 Peitoral do sobretudo
    ".....KKLLllmmLLllmmLLKKKK.......", # 13
    ".....KKLLllmmLLllmmLLLLLLKK.....", # 14 Braço esquerdo
    ".....KKLLllmmKKKKKKKKKKmmllKK...", # 15 Cinto de utilidades
    ".....KKLLllKKSSSSSSKKKKmmllKK...", # 16
    ".....KKLLllKKSSSSssKKKKKKKK.....", # 17 Fendas do sobretudo
    ".....KKLLKKSSSSssssKKKK.........", # 18 Calça escura
    ".....KKKK..KKSSssssKK.KKLLKK....", # 19 Aba do sobretudo voando
    "...........KKSSssssKK.KKLLllKK..", # 20
    "...........KKSSssssKK..KKLLllKK.", # 21
    "...........KKSSKKssKK...KKLLllKK", # 22
    "...........KKSSKKssKK....KKKKKK.", # 23
    "...........KKSSKKssKK...........", # 24 Pernas separadas
    "...........KKBBKKBBKK...........", # 25 Joelheiras
    "...........KKBBKKBBKK...........", # 26
    "...........KKbbKKbbKK...........", # 27 Botas pesadas
    ".........KKBBbbKKBBbbKK.........", # 28 Solado aderente
    ".........KKKKKKKKKKKKKK.........", # 29 Chão
    "................................", # 30
    "................................", # 31
]
CONCEPTS["01_trenchcoat_drifter"] = (GRID_01, PAL_01, "01. The Trenchcoat Courier", "Cyber-Noir Blade Alpinist", "Sobretudo de couro desgastado, chapéu fedora noir, visor HUD cyan neon e arma de gancho tática.")

# ==============================================================================
# 02. TITAN EXO-RIG (Heavy Industrial Welder)
# ==============================================================================
# Bulky yellow/black construction frame, welding mask, chemical tanks
PAL_02 = make_palette({
    'K': '#111218', # Dark outline
    'Y': '#9e680a', # Exo yellow shadow
    'y': '#e09812', # Exo yellow mid
    'z': '#ffd026', # Exo yellow highlight
    'W': '#fff28a', # Exo yellow specular
    'M': '#2a2d38', # Gunmetal shadow
    'm': '#505668', # Gunmetal mid
    's': '#8d95ab', # Steel highlight
    'S': '#dce1eb', # Chrome specular
    'V': '#3a0808', # Visor dark
    'v': '#e62e00', # Visor glow red/orange
    'F': '#ffaa00', # Visor hot gold
    'f': '#fff0aa', # Visor specular spark
    'T': '#0e4a2e', # Tank dark green
    't': '#1cb866', # Tank neon green
    'P': '#20e880', # Tank glow gauge
})

GRID_02 = [
    "................................", # 00
    "................................", # 01
    "...........KKKKKKKKKK...........", # 02 Capacete industrial
    ".........KKYyzzzzzzWWKK.........", # 03 Topo reforçado
    "........KKMmKKKKKKKKmMMK........", # 04 Moldura do visor
    "........KKMmVvFFFFffvMKK........", # 05 Fenda de solda em brasa
    "........KKMmVvvvvvvvvMKK........", # 06
    "........KKMmKKKKKKKKmMMK........", # 07
    "......KKKKMmKKssssKKmMMKKKK.....", # 08 Ombreiras largas exo
    "....KKYyzzKKssSSssKKzzWWyYKK....", # 09 Pistões hidráulicos
    "...KKYyzzWWKKssSSssKKzzWWyYKK...", # 10 (8,10) Listras de perigo
    "...KKTtTtPPKKMmKKMmKKPPtTtTKK...", # 11 Tanques químicos nas costas
    "...KKTtTtPPKKMmKKMmKKPPtTtTKK...", # 12
    "...KKYyzzWWKKzzyyzzKKWWzzYyKK...", # 13 Peitoral reforçado
    "....KKKKKKKKYyMmMmYyKKKKKKKK....", # 14 Caixa torácica mecânica
    "......KKMmssKKssssKKssMmKK......", # 15 Luvas grossas de soldador
    "......KKMmssKKssssKKssMmKK......", # 16 Cinto com trava pesada
    "......KKKKKKKKYyyyKKKKKKKK......", # 17
    "........KKYyzzKKKKzzYyKK........", # 18 Coxas com vigas externas
    "........KKYyzzKKKKzzYyKK........", # 19
    "........KKMmssKKKKssMmKK........", # 20 Articulação do joelho
    "........KKMmssKKKKssMmKK........", # 21
    "........KKYyzzKKKKzzYyKK........", # 22 Caneleiras amarelas blindadas
    "........KKYyzzKKKKzzYyKK........", # 23
    "........KKMmssKKKKssMmKK........", # 24 Pistão do tornozelo
    "........KKMmssKKKKssMmKK........", # 25
    "......KKKKMmssKKKKssMmKKKK......", # 26 Botas com trava magnética
    "......KKMmssSSKKKKSSssMmKK......", # 27 Garras de ancoragem
    "......KKKKKKKKKKKKKKKKKKKK......", # 28 Base firme
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["02_exorig_heavy"] = (GRID_02, PAL_02, "02. Titan Exo-Rig", "Heavy Industrial Welder", "Exoesqueleto hidráulico amarelo de alto impacto, capacete de solda em brasa e tanques químicos dorsais.")

# ==============================================================================
# 03. GHOST OPERATIVE (Cyber-Ninja / Shadow Infiltrator)
# ==============================================================================
# Sleek dark suit, dual magenta optics, high-tech fluttering scarf, carbon plates
PAL_03 = make_palette({
    'K': '#0f0e1a', # Dark outline
    'N': '#1c172e', # Nanofiber dark
    'n': '#352952', # Nanofiber mid
    'u': '#564282', # Nanofiber highlight
    'P': '#700940', # Scarf dark magenta
    'p': '#c41270', # Scarf neon magenta
    'Q': '#ff2a9d', # Scarf hot pink
    'q': '#ff94d2', # Scarf specular
    'C': '#00b3cc', # Cyan conduit
    'c': '#33e6ff', # Cyan bright
    'A': '#262933', # Carbon armor dark
    'a': '#4d5266', # Carbon armor mid
    'S': '#8f96ad', # Carbon edge highlight
    'E': '#ff1a75', # Visor eyes glowing
    'e': '#ff99c2', # Visor eye center
})

GRID_03 = [
    "................................", # 00
    "................................", # 01
    ".............KKKKKK.............", # 02 Capuz aerodinâmico
    "...........KKNnnuuuKK...........", # 03
    "..........KKNnNnnuuuKK..........", # 04
    "..........KKNEeNNEeNKK..........", # 05 Olhos óticos duplos magenta
    "..........KKNEeNNEeNKK..........", # 06
    "...........KKNnnnnnKK...........", # 07 Máscara angular
    ".........KKKKNnnuuuKKKK.........", # 08 Gola do cachecol
    ".......KKPppQKKNNKKQppPKK.......", # 09 Cachecol digital
    "....KKPppQQqqKKNNKKqQQppPKK.....", # 10 (8,10) Asas do cachecol
    "..KKPppQQqqKKKKAaKKKKqqQQppPKK..", # 11
    "....KKKKKKKKKAaSSaAKKKKKKKKKK...", # 12 Peitoral de placa de carbono
    "...........KKAaCcAaAKK..........", # 13 Conduíte cyan no peito
    "...........KKNnCcNnnKK..........", # 14
    ".........KKKKNnnnnnnKKKK........", # 15 Manoplas com garras
    "........KKAaSKKNNKKSaAaKK.......", # 16
    "........KKaaSKKNNKKSaaKK........", # 17 Cinto com micro-âncoras
    "........KKKKKKNNKKKKKKKK........", # 18
    "...........KKNnnnnnKK...........", # 19 Pernas ágeis
    "...........KKNnnnnnKK...........", # 20
    "...........KKNnKKnnKK...........", # 21
    "...........KKNnKKnnKK...........", # 22 Tiras de ajuste
    "...........KKAaKKaAKK...........", # 23 Joelheiras leves
    "...........KKAaKKaAKK...........", # 24
    "...........KKNnKKnnKK...........", # 25
    "...........KKPpKKPpKK...........", # 26 Fita magenta na canela
    "...........KKnQKKQnnKK..........", # 27
    "..........KKKKKKKKKKKK..........", # 28 Solado tabi magnético
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["03_cyber_ninja"] = (GRID_03, PAL_03, "03. Ghost Operative", "Cyber-Ninja Infiltrator", "Traje de nanofibra violeta, óticas duplas magenta, cachecol cibernético esvoaçante e placas de carbono.")

# ==============================================================================
# 04. HAZMAT BIO-CLEANER (Toxic Smog & Decon Technician)
# ==============================================================================
# Bulky yellow chemical hood, convex panoramic green visor, heavy apron
PAL_04 = make_palette({
    'K': '#141712', # Dark outline
    'Y': '#8c8008', # Hazmat shadow
    'y': '#d4c415', # Hazmat yellow mid
    'Z': '#faea2a', # Hazmat yellow highlight
    'z': '#ffff8f', # Hazmat yellow specular
    'V': '#073322', # Visor deep dark
    'v': '#10804e', # Visor glass green
    'G': '#26d980', # Visor bright reflection
    'g': '#a8ffd4', # Visor curved highlight
    'R': '#2a2f30', # Rubber apron dark
    'r': '#4a5254', # Rubber apron mid
    'H': '#7b878a', # Rubber apron highlight
    'O': '#b84414', # Oxygen tank rust orange
    'o': '#fa6a25', # Oxygen tank orange
})

GRID_04 = [
    "................................", # 00
    "................................", # 01
    "...........KKKKKKKKKK...........", # 02 Capuz esférico vedado
    ".........KKYyZZZZZZzzKK.........", # 03
    "........KKYyZZZZZZZZzzKK........", # 04
    ".......KKYyKKKKKKKKKKzzKK.......", # 05 Aro metálico do visor
    ".......KKYKVVvvGGggvVKYzKK......", # 06 Visor esférico panorâmico
    ".......KKYKVVvvGGggvVKYzKK......", # 07 Reflexo em arco
    ".......KKYKVVvvvvvvvVKYzKK......", # 08
    ".......KKYyKKKKKKKKKKzzKK.......", # 09 Filtro respirador
    ".....KKOoKKKKRrHHrRKKKKOoKK.....", # 10 (8,10) Tanques químicos laterais
    "....KKOooKKKRrHHHHrRKKKooOKK....", # 11
    "....KKOooKKKRrHHHHrRKKKooOKK....", # 12
    "....KKOoKKKKRrHHHHrRKKKKOoKK....", # 13 Avental de borracha química
    "......KKKK..KKRrRrKK..KKKK......", # 14
    ".........KKYyZZZZZZzzKK.........", # 15 Macacão inflado amarelo
    "........KKYyZZZZZZZZzzKK........", # 16
    "........KKYyZZKKKKZZzzKK........", # 17 Calças largas com vedação
    "........KKYyZZKKKKZZzzKK........", # 18
    "........KKYyZZKKKKZZzzKK........", # 19
    "........KKYyZZKKKKZZzzKK........", # 20
    "........KKYyZZKKKKZZzzKK........", # 21 Joelhos reforçados
    "........KKRrRrKKKKRrRrKK........", # 22
    "........KKRrRrKKKKRrRrKK........", # 23 Botas pesadas de borracha
    "........KKRrHHrKKrHRrRKK........", # 24
    "........KKRrHHrKKrHRrRKK........", # 25
    "......KKKKRrHHrKKrHRrRKKKK......", # 26 Bico de aço protetor
    "......KKRRRRRRRKKRRRRRRRKK......", # 27 Solado anti-ácido
    "......KKKKKKKKKKKKKKKKKKKK......", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["04_hazmat_cleaner"] = (GRID_04, PAL_04, "04. Hazmat Bio-Cleaner", "Toxic Smog & Decon Technician", "Traje amarelo pressurizado hermético, visor esférico espelhado em verde esmeralda e avental de borracha.")

# ==============================================================================
# 05. NEON STREET SCAVENGER (Underground Cyber-Punk)
# ==============================================================================
# Hot pink mohawk, denim vest, full chrome cybernetic left arm, torn knees
PAL_05 = make_palette({
    'K': '#12111a', # Dark outline
    'M': '#800040', # Mohawk dark
    'm': '#e60073', # Mohawk mid
    'N': '#ff3399', # Mohawk neon pink
    'n': '#ff99cc', # Mohawk tip
    'F': '#854b38', # Flesh shadow
    'f': '#d98b68', # Flesh mid
    'e': '#ffbe99', # Flesh highlight
    'D': '#1e3352', # Denim dark
    'd': '#345e96', # Denim mid
    'B': '#5b92d6', # Denim blue highlight
    'b': '#9bc0f0', # Denim light
    'X': '#2a2f3d', # Chrome dark
    'x': '#5c667a', # Chrome mid
    'S': '#a6b3c9', # Chrome bright
    's': '#ffffff', # Chrome specular gleam
    'O': '#ff6600', # Wires orange neon
    'o': '#ffcc00', # Cyber-eye yellow
    'C': '#00ffee', # Cyber-eye cyan
})

GRID_05 = [
    "................................", # 00
    "............KKmmnnKK............", # 01 Topo do moicano punk
    "...........KKmNNnnKK............", # 02
    "..........KKMmNNnnKK............", # 03
    ".........KKMmNNnnKK.............", # 04 Moicano espetado
    ".........KKMMmmKKKK.............", # 05
    "........KKFffFKKoCeeKK..........", # 06 Olho cibernético cyan/gold
    "........KKFffFKKCeeeKK..........", # 07 Bandana preta na boca
    "........KKKKKKKKKKKKKK..........", # 08
    ".......KKDdBBbbKK..KKXxSSsKK....", # 09 Colete jeans e braço cromado
    "......KKDdBBbbKK....KKXxSSsKK...", # 10 (8,10) Fiação exposta
    ".....KKDddBBbbKK.KKKKKKXxSSsKK..", # 11
    ".....KKDddBBbbKKKKOoOoKKXxSSsKK.", # 12 Peito com patches e fios
    ".....KKDdBBbbKKKKKKOoKKKXxSSsKK.", # 13
    "......KKDddbKKKKKKKKKKKKXxSSsKK.", # 14 Mão cibernética de cromo
    "......KKFfeeKKKKKKKK..KKXxSsKK..", # 15 Braço direito orgânico
    "......KKFfeeKKSSSSKK....KKKK....", # 16
    ".......KKKKKKSSSSSSKK...........", # 17 Cinto com rebites
    "...........KKDdDDddKK...........", # 18 Calça jeans rasgada
    "...........KKDdDDddKK...........", # 19
    "...........KKFfKKddKK...........", # 20 Rasgo no joelho (pele à mostra)
    "...........KKFfKKddKK...........", # 21
    "...........KKDdKKddKK...........", # 22
    "...........KKDdKKddKK...........", # 23
    "...........KKMmKKDdKK...........", # 24 Tênis cano alto descombinado
    "...........KKmNKKdDKK...........", # 25 (Pé esquerdo rosa, direito azul)
    ".........KKMmNNKKDdBBKK.........", # 26
    ".........KKmNssKKdDBBssKK.......", # 27 Solado branco esportivo
    ".........KKKKKKKKKKKKKKKK.......", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["05_street_punk"] = (GRID_05, PAL_05, "05. Neon Street Scavenger", "Underground Cyber-Punk", "Moicano rosa neon espetado, colete jeans desgastado, braço cibernético de cromo brilhante e tênis descombinados.")

# ==============================================================================
# 06. APEX SECURITY ENFORCER (High-Tech Corporate Guard)
# ==============================================================================
# White ceramic ballistic plates, menacing red sensor visor, corporate crest
PAL_06 = make_palette({
    'K': '#12141a', # Dark outline
    'W': '#63708a', # Ceramic shadow
    'w': '#a6b4cc', # Ceramic mid
    'C': '#e6edfa', # Ceramic white
    'c': '#ffffff', # Ceramic specular
    'U': '#1e222e', # Under-armor dark
    'u': '#3a4257', # Under-armor mid
    'R': '#660011', # Red sensor dark
    'r': '#d90429', # Red sensor laser
    'L': '#ff4d6d', # Red sensor flare
    'B': '#0077b6', # Corporate cyan/blue
    'b': '#00b4d8', # Corporate crest bright
})

GRID_06 = [
    "................................", # 00
    "................................", # 01
    "...........KKKKKKKKKK...........", # 02 Capacete de cerâmica branca
    ".........KKWwCCCcKK..KK.........", # 03 Antena lateral
    "........KKWwCCCCCcKK.KK.........", # 04
    "........KKWwKKKKKKKKKKK.........", # 05 Viseira tática
    "........KKWwRrLLLrrRrKK.........", # 06 Linha de sensor laser vermelho
    "........KKWwKKKKKKKKKKK.........", # 07
    "........KKWwCCCCCccWwKK.........", # 08 Mandíbula angular
    "......KKKKWwCCCCCCcWwKKKK.......", # 09 Ombreiras táticas
    "....KKWwCcKKWwCCCCwWKKcCWwKK....", # 10 (8,10) Placa peitoral blindada
    "...KKWwCCcKKWwBbBBwWKKcCCCwKK...", # 11 Logo corporativo Neo-Apex
    "...KKWwCCcKKWwBbBBwWKKcCCCwKK...", # 12
    "....KKKKKKKKWwCCCCwWKKKKKKKK....", # 13
    "......KKUUuuKKWwwWKKUUuuKK......", # 14 Cintura articulada em Kevlar
    "......KKUUuuKKWwwWKKUUuuKK......", # 15
    "......KKKKKKKKUUuuKKKKKKKK......", # 16 Cinto tático corporativo
    "........KKWwCcKKKKcCWwKK........", # 17 Placas de cerâmica nas coxas
    "........KKWwCcKKKKcCWwKK........", # 18
    "........KKUUuuKKKKUUuuKK........", # 19 Juntas flexíveis
    "........KKWwCcKKKKcCWwKK........", # 20 Joelheiras brancas
    "........KKWwCcKKKKcCWwKK........", # 21
    "........KKWwCcKKKKcCWwKK........", # 22 Caneleiras balísticas
    "........KKWwCcKKKKcCWwKK........", # 23
    "........KKUUuuKKKKUUuuKK........", # 24 Tornozelos reforçados
    "........KKUUuuKKKKUUuuKK........", # 25
    "......KKKKUUuuKKKKUUuuKKKK......", # 26 Botas de assalto pesadas
    "......KKWwCcKKKKKKKKcCWwKK......", # 27 Solado de alta aderência
    "......KKKKKKKKKKKKKKKKKKKK......", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["06_corporate_enforcer"] = (GRID_06, PAL_06, "06. Apex Security Enforcer", "Corporate Tactical Guard", "Blindagem cerâmica modular branca, visor com fenda laser vermelha e insígnia da megacorporação Neo-Apex.")

# ==============================================================================
# 07. SYNTH UNIT MODEL-04 (Autonomous Maintenance Android)
# ==============================================================================
# Robotic chassis in titanium slate, tri-optic cyan camera lenses, plasma core
PAL_07 = make_palette({
    'K': '#0f1117', # Dark outline
    'T': '#2b3345', # Titanium shadow
    't': '#4a5773', # Titanium mid
    'S': '#7c8fa8', # Titanium highlight
    's': '#c0d0e6', # Titanium specular
    'C': '#0099b8', # Plasma cyan dark
    'c': '#00e1ff', # Plasma cyan bright
    'W': '#b3f7ff', # Plasma cyan core
    'J': '#1c1f26', # Joint black
    'G': '#996633', # Copper conduit
    'g': '#cca352', # Copper bright
})

GRID_07 = [
    "................................", # 00
    "................................", # 01
    ".............KKKKKK.............", # 02 Crânio robótico sintético
    "...........KKTtSSssKK...........", # 03 Chassi de titânio
    "..........KKTtSSssssKK..........", # 04
    "..........KKTtCcWwCcKK..........", # 05 Lentes óticas superiores duplas
    "..........KKTtCcWwCcKK..........", # 06
    "..........KKTtTtCcTtKK..........", # 07 Lente ótica inferior central
    "..........KKTtTtTtTtKK..........", # 08 Queixo mecânico
    ".........KKKKJJggGJKKKK.........", # 09 Junta de pescoço com cabos de cobre
    ".......KKTtSsKKJJGJKKSsTtKK.....", # 10 (8,10) Ombreiras esféricas
    ".....KKTtSSssKKCcWcKKSsSSsTtK...", # 11 Núcleo de plasma ciano no peito
    ".....KKTtSSssKKCcWcKKSsSSsTtK...", # 12
    ".......KKKKKKTtCcWcTtKKKKKK.....", # 13 Costelas mecânicas
    "..........KKJJggJJggJJKK........", # 14 Coluna vertebral exposta
    "..........KKJJggJJggJJKK........", # 15
    ".........KKTtSSssssSSTtKK.......", # 16 Pelve robótica
    ".........KKTtSsKKKKSsTtKK.......", # 17
    ".........KKTtSsKKKKSsTtKK.......", # 18 Pernas bípede mecânicas
    "..........KKJJGKKKJGJKK.........", # 19 Êmbolos e amortecedores
    "..........KKJJGKKKJGJKK.........", # 20
    ".........KKTtSsKKKKSsTtKK.......", # 21 Joelhos digitígrados
    ".........KKTtSsKKKKSsTtKK.......", # 22
    "..........KKJJGKKKJGJKK.........", # 23 Hastes pneumáticas
    "..........KKJJGKKKJGJKK.........", # 24
    ".........KKTtSsKKKKSsTtKK.......", # 25 Garras tripés de ancoragem
    "........KKTtSSssKKssSSTtKK......", # 26 Pés com garras magnéticas
    "........KKKKKKKKKKKKKKKKKK......", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["07_synth_android"] = (GRID_07, PAL_07, "07. Synth Unit Model-04", "Autonomous Maintenance Android", "Chassi robótico em titânio e ardósia, três lentes óticas triangulares ciano e núcleo de plasma brilhante.")

# ==============================================================================
# 08. AERO-COURIER SKY-RUNNER (High-Altitude Acrobat)
# ==============================================================================
# Puffy safety orange bomber jacket, brass flight goggles, red flight scarf
PAL_08 = make_palette({
    'K': '#17110f', # Dark outline
    'J': '#8a3307', # Jacket orange shadow
    'j': '#db5912', # Jacket orange mid
    'O': '#ff802b', # Jacket orange highlight
    'o': '#ffb066', # Jacket orange specular
    'F': '#1a2b3c', # Flight helmet dark
    'f': '#334f6b', # Flight helmet blue
    'G': '#7a5214', # Goggles bronze
    'g': '#cca333', # Goggles gold
    'A': '#ffdd55', # Goggles amber glass
    'S': '#800d1e', # Scarf dark red
    's': '#c91834', # Scarf bright crimson
    'R': '#ff4763', # Scarf flutter highlight
    'P': '#1a1f26', # Runner pants black
    'p': '#303947', # Runner pants mid
    'Y': '#ffe600', # Hazard stripe yellow
})

GRID_08 = [
    "................................", # 00
    ".............KKKKKK.............", # 01 Capacete de couro de aviador
    "...........KKFfffFffKK..........", # 02
    "..........KKFGgAAGgAAfKK........", # 03 Óculos de voo duplos âmbar
    "..........KKFGgAAGgAAfKK........", # 04
    "..........KKFfffffffFfKK........", # 05 Máscara de respiração
    ".........KKKKSSssRRssKKKK.......", # 06 Cachecol de voo vermelho
    ".......KKJjjOKKSSSSKKqRRssKK....", # 07 Cauda do cachecol ao vento
    ".....KKJjjOOoKKssssKK..KKssSKK..", # 08
    "....KKJjjOOooKKKKKKKK....KKssSKK", # 09 Jaqueta bomber laranja volumosa
    "...KKJjjOOoooKKJjjOOKK....KKKK..", # 10 (8,10) Mini-propulsor dorsal
    "...KKJjjOOoooKKJjjOOKK..........", # 11
    "...KKJjjOOoooKKJjjOOKK..........", # 12 Puffer jacket inflada
    "....KKKKKKKKKKJjjOOKK...........", # 13
    ".......KKJjjOKKJjjOKK...........", # 14 Cintura com elástico
    ".......KKPpYYKKPpYYKK...........", # 15 Calça de corrida com faixas de perigo
    ".......KKPpYYKKPpYYKK...........", # 16
    ".......KKPpYYKKPpYYKK...........", # 17
    ".......KKPpppKKPpppKK...........", # 18 Joelheiras aerodinâmicas
    ".......KKPpppKKPpppKK...........", # 19
    ".......KKPpYYKKPpYYKK...........", # 20 Faixas refletivas
    ".......KKPpYYKKPpYYKK...........", # 21
    ".......KKJjjOKKJjjOKK...........", # 22 Tênis com suspensão pneumática
    ".......KKJjjOKKJjjOKK...........", # 23
    ".....KKKJjOOoKKJjOOoKKK.........", # 24 Solado de alta velocidade
    ".....KKKKKKKKKKKKKKKKKK.........", # 25
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["08_aero_courier"] = (GRID_08, PAL_08, "08. Aero-Courier Sky-Runner", "High-Altitude Acrobat", "Jaqueta bomber neon laranja volumosa, óculos duplos de aviador, cachecol vermelho esvoaçante e propulsor dorsal.")


def main():
    base_dir = Path(__file__).resolve().parent.parent
    concepts_dir = base_dir / "assets" / "CharacterIdeas" / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    print("Gerando 8 novos conceitos refinados com padrão profissional de pixel art...")

    rendered = []
    for key, (grid, pal, title, subtitle, desc) in CONCEPTS.items():
        img = render_ascii_sprite(grid, pal)
        rendered.append((key, img, title, subtitle, desc))

        # 1. Salvar PNG 32x32
        path_32 = concepts_dir / f"concept_{key}.png"
        img.save(path_32)

        # 2. Salvar Preview 8x (256x256) com nearest neighbor limpo
        path_8x = concepts_dir / f"preview_8x_{key}.png"
        img_8x = img.resize((256, 256), Image.Resampling.NEAREST)
        img_8x.save(path_8x)
        print(f"  [OK] {title} -> {path_32.name} e {path_8x.name}")

    # 3. Gerar a fita de 8 sprites horizontais (256x32)
    strip_img = Image.new("RGBA", (32 * 8, 32), (0, 0, 0, 0))
    for i, (_, img, _, _, _) in enumerate(rendered):
        strip_img.paste(img, (i * 32, 0))
    strip_path = concepts_dir / "all_8_concepts_strip_256x32.png"
    strip_img.save(strip_path)
    print(f"  [OK] Spritesheet atualizado: {strip_path.name}")

    # 4. Criar Cartela Comparativa Detalhada (Showcase)
    card_w = 280
    card_h = 320
    cols = 4
    rows = 2
    showcase_w = cols * card_w + 40
    showcase_h = rows * card_h + 100

    showcase = Image.new("RGBA", (showcase_w, showcase_h), (18, 18, 26, 255))
    draw = ImageDraw.Draw(showcase)

    # Cabeçalho da cartela
    draw.rectangle([(0, 0), (showcase_w, 64)], fill=(12, 12, 18, 255))
    draw.line([(0, 64), (showcase_w, 64)], fill=(0, 229, 255, 255), width=2)
    draw.text((25, 14), "APEX GRAPPLER — 8 NOVOS CONCEITOS VISUAIS PARA O PROTAGONISTA", fill=(255, 255, 255, 255))
    draw.text((25, 36), "Design Refinado: Silhuetas Distintas | Contorno 1px | Iluminação Direcional | Escala 32x32 Nativa", fill=(170, 180, 200, 255))

    for i, (key, img, title, subtitle, desc) in enumerate(rendered):
        col = i % cols
        row = i // cols
        cx = 20 + col * card_w
        cy = 80 + row * card_h

        # Fundo do Card
        draw.rectangle([(cx, cy), (cx + card_w - 15, cy + card_h - 15)], fill=(25, 27, 38, 255), outline=(45, 50, 70, 255), width=1)
        draw.line([(cx, cy), (cx + card_w - 15, cy)], fill=(255, 140, 0, 255) if i == 0 else (0, 229, 255, 255), width=2)

        # Caixa do Sprite com grid de xadrez de transparência sutil
        bx = cx + 65
        by = cy + 18
        draw.rectangle([(bx - 3, by - 3), (bx + 131, by + 131)], fill=(14, 15, 22, 255), outline=(60, 65, 85, 255))

        # Quadriculado de fundo 8x8
        for qy in range(16):
            for qx in range(16):
                bg_col = (26, 28, 40, 255) if (qx + qy) % 2 == 0 else (18, 20, 28, 255)
                draw.rectangle([(bx + qx * 8, by + qy * 8), (bx + (qx + 1) * 8 - 1, by + (qy + 1) * 8 - 1)], fill=bg_col)

        # Sprite 32x32 ampliado 4x (128x128)
        scaled_sprite = img.resize((128, 128), Image.Resampling.NEAREST)
        showcase.paste(scaled_sprite, (bx, by), scaled_sprite)

        # Informações textuais
        draw.text((cx + 12, cy + 162), title, fill=(255, 220, 40, 255))
        draw.text((cx + 12, cy + 182), subtitle, fill=(0, 229, 255, 255))

        # Quebra de linha manual da descrição
        words = desc.split(" ")
        l1, l2, l3 = "", "", ""
        for w in words:
            if len(l1 + " " + w) <= 34 and not l2:
                l1 = (l1 + " " + w).strip()
            elif len(l2 + " " + w) <= 34 and not l3:
                l2 = (l2 + " " + w).strip()
            else:
                l3 = (l3 + " " + w).strip()

        draw.text((cx + 12, cy + 208), l1, fill=(190, 195, 210, 255))
        draw.text((cx + 12, cy + 224), l2, fill=(190, 195, 210, 255))
        if l3:
            draw.text((cx + 12, cy + 240), l3, fill=(190, 195, 210, 255))

        # Sprite 1x nativo no canto inferior
        draw.text((cx + 12, cy + 268), "Escala nativa 1x:", fill=(110, 120, 140, 255))
        showcase.paste(img, (cx + 130, cy + 262), img)

    showcase_path = concepts_dir / "concepts_showcase_comparison.png"
    showcase.save(showcase_path)
    print(f"  [OK] Painel Comparativo Geral salvo: {showcase_path.name}")
    print("\nTodos os 8 conceitos foram recriados com sucesso!")

if __name__ == "__main__":
    main()
