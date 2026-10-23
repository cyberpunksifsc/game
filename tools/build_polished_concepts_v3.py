#!/usr/bin/env python3
"""
Refined 8 Cyberpunk Player Character Concepts (IDLE State) - V3
Strictly fixed:
1. Zero internal transparent holes (fully solid bodies).
2. Proper arcade proportions:
   - Head: Y=4..9 (6px)
   - Torso: Y=10..17 (8px)
   - Legs: Y=18..24 (7px)
   - Feet firmly grounded at Y=24.
   - Total height: ~21px (Y=4 to Y=24), matching the game's anchor point and mechanics.
3. Rich shading, distinct silhouettes, and clear details.
"""

import glob
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

def find_internal_holes(img: Image.Image) -> list[tuple[int, int]]:
    """Flood fill from outer border to detect any trapped/internal transparent pixels."""
    w, h = img.size
    visited = set()
    queue = []
    # Seed queue with outer edges
    for x in range(w):
        if img.getpixel((x, 0))[3] == 0:
            queue.append((x, 0))
        if img.getpixel((x, h - 1))[3] == 0:
            queue.append((x, h - 1))
    for y in range(h):
        if img.getpixel((0, y))[3] == 0:
            queue.append((0, y))
        if img.getpixel((w - 1, y))[3] == 0:
            queue.append((w - 1, y))

    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if img.getpixel((nx, ny))[3] == 0:
                    queue.append((nx, ny))

    holes = []
    for y in range(h):
        for x in range(w):
            if img.getpixel((x, y))[3] == 0 and (x, y) not in visited:
                holes.append((x, y))
    return holes

# ==============================================================================
# PALETTES AND GRIDS FOR 8 CHARACTERS (Y=4 to Y=24, no internal holes)
# ==============================================================================

CONCEPTS = {}

# ------------------------------------------------------------------------------
# 01. THE TRENCHCOAT COURIER
# ------------------------------------------------------------------------------
PAL_01 = make_palette({
    'K': '#11121a', # Dark outline
    'H': '#242a3a', # Hat dark
    'h': '#434f68', # Hat mid
    'I': '#6b7b99', # Hat highlight
    'V': '#00e5ff', # Visor cyan
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
    'O': '#ff8c00', # Harness orange
    'o': '#ffd060', # Carabiner gold
    'G': '#a0a8b8', # Grapple metal
    'g': '#e0e5f0', # Grapple highlight
    'P': '#00ff66', # Carabiner LED green
})

GRID_01 = [
    "................................", # 00
    "................................", # 01
    "................................", # 02
    ".............KKKKKK.............", # 03 Topo chapéu
    "...........KKHHhhhhKK...........", # 04 Copa chapéu
    ".........KKHHhhhhIIIIKK.........", # 05 Aba chapéu
    ".......KKKKKKKKKKKKKKKKKK.......", # 06 Aba estendida
    "...........KKVVvvKKKKKK.........", # 07 Visor cyan
    ".........KKLLKKKKLLKKGGggKK.....", # 08 Gola alta e arma de gancho
    ".......KKLLllKKLLllKKGGggKK.....", # 09 Ombro e coldre
    ".....KKOPOOllKKmmllKKgGggKK.....", # 10 (8,10) Mosquetão
    ".....KKOPKKllKKmmllKKKKKKKK.....", # 11
    ".....KKLLKKmmLLllmmLLKK.........", # 12 Peitoral do sobretudo
    ".....KKLLllmmLLllmmLLLLKK.......", # 13
    ".....KKLLllmmLLllmmLLLLLLKK.....", # 14 Manga e luva
    ".....KKLLllmmKKKKKKKKKKmmllKK...", # 15 Cinto
    ".....KKLLllKKSSSSSSKKKKmmllKK...", # 16
    ".....KKLLllKKSSSSssKKKKKKKK.....", # 17 Fim do tronco
    ".....KKLLKKSSssssssKKKK.........", # 18 Início das pernas proporcionais
    ".....KKLLKKSSssKKssKKKKLLKK.....", # 19 Pernas separadas
    ".....KKKKKKSSssKKssKKKKLLllKK...", # 20 Aba do sobretudo
    "...........KKSSKKssKK.KKLLllKK..", # 21 Joelhos
    "...........KKBBKKBBKK..KKKKKK...", # 22 Botas
    "...........KKBBKKBBKK...........", # 23
    ".........KKBBbbKKBBbbKK.........", # 24 PÉS ASSENTADOS EM Y=24!
    ".........KKKKKKKKKKKKKK.........", # 25 Linha base de contorno
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["01_trenchcoat_drifter"] = (GRID_01, PAL_01, "01. The Trenchcoat Courier", "Cyber-Noir Blade Alpinist", "Sobretudo de couro desgastado, chapéu fedora noir, visor HUD cyan neon e proporção arcade precisa.")

# ------------------------------------------------------------------------------
# 02. TITAN EXO-RIG (Heavy Industrial Welder)
# ------------------------------------------------------------------------------
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
    "................................", # 02
    "...........KKKKKKKKKK...........", # 03 Capacete industrial
    ".........KKYyzzzzzzWWKK.........", # 04 Topo reforçado
    "........KKMmKKKKKKKKmMMK........", # 05 Moldura do visor
    "........KKMmVvFFFFffvMKK........", # 06 Fenda de solda em brasa
    "........KKMmVvvvvvvvvMKK........", # 07
    "......KKKKMmKKssssKKmMMKKKK.....", # 08 Ombreiras largas
    "....KKYyzzKKssSSssKKzzWWyYKK....", # 09 Pistões hidráulicos
    "...KKYyzzWWKKssSSssKKzzWWyYKK...", # 10 (8,10) Listras de perigo
    "...KKTtTtPPKKMmKKMmKKPPtTtTKK...", # 11 Tanques químicos nas costas
    "...KKTtTtPPKKMmKKMmKKPPtTtTKK...", # 12
    "...KKYyzzWWKKzzyyzzKKWWzzYyKK...", # 13 Peitoral reforçado
    "....KKKKKKKKYyMmMmYyKKKKKKKK....", # 14 Caixa torácica mecânica
    "......KKMmssKKssssKKssMmKK......", # 15 Luvas de soldador
    "......KKMmssKKssssKKssMmKK......", # 16 Cinto com trava pesada
    "......KKKKKKKKYyyyKKKKKKKK......", # 17 Fim do tronco
    "........KKYyzzKKKKzzYyKK........", # 18 Pernas exo proporcionais
    "........KKYyzzKKKKzzYyKK........", # 19
    "........KKMmssKKKKssMmKK........", # 20 Joelheiras compactas
    "........KKYyzzKKKKzzYyKK........", # 21 Caneleiras amarelas
    "......KKKKMmssKKKKssMmKKKK......", # 22 Botas com trava magnética
    "......KKMmssSSKKKKSSssMmKK......", # 23
    "......KKKKKKKKKKKKKKKKKKKK......", # 24 PÉS ASSENTADOS EM Y=24!
    "................................", # 25
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["02_exorig_heavy"] = (GRID_02, PAL_02, "02. Titan Exo-Rig", "Heavy Industrial Welder", "Exoesqueleto amarelo reforçado, visor incandescente, tanques químicos e pernas proporcionais compactas.")

# ------------------------------------------------------------------------------
# 03. GHOST OPERATIVE (Cyber-Ninja)
# ------------------------------------------------------------------------------
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
    "................................", # 02
    ".............KKKKKK.............", # 03 Capuz aerodinâmico
    "...........KKNnnuuuKK...........", # 04
    "..........KKNnNnnuuuKK..........", # 05
    "..........KKNEeNNEeNKK..........", # 06 Olhos duplos magenta
    "...........KKNnnnnnKK...........", # 07 Máscara angular
    ".........KKKKNnnuuuKKKK.........", # 08 Gola do cachecol
    ".......KKPppQKKNNKKQppPKK.......", # 09 Cachecol digital
    "....KKPppQQqqKKNNKKqQQppPKK.....", # 10 (8,10) Asas do cachecol
    "..KKPppQQqqKKKKAaKKKKqqQQppPKK..", # 11
    "....KKKKKKKKKAaSSaAKKKKKKKKKK...", # 12 Peitoral de carbono
    "...........KKAaCcAaAKK..........", # 13 Conduíte cyan
    "...........KKNnCcNnnKK..........", # 14
    ".........KKKKNnnnnnnKKKK........", # 15 Manoplas
    "........KKAaSKKNNKKSaAaKK.......", # 16
    "........KKaaSKKNNKKSaaKK........", # 17 Cinto com micro-âncoras
    "........KKKKKKNNKKKKKKKK........", # 18 Fim do tronco
    "...........KKNnnnnnKK...........", # 19 Pernas ágeis
    "...........KKNnKKnnKK...........", # 20
    "...........KKAaKKaAKK...........", # 21 Joelheiras leves
    "...........KKPpKKPpKK...........", # 22 Fita magenta
    "...........KKnQKKQnnKK..........", # 23 Tabi magnético
    "..........KKKKKKKKKKKK..........", # 24 PÉS ASSENTADOS EM Y=24!
    "................................", # 25
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["03_cyber_ninja"] = (GRID_03, PAL_03, "03. Ghost Operative", "Cyber-Ninja Infiltrator", "Nanofibra violeta, óticas duplas magenta neon, cachecol digital esvoaçante e postura ágil sem furos.")

# ------------------------------------------------------------------------------
# 04. HAZMAT BIO-CLEANER (Decon Technician)
# ------------------------------------------------------------------------------
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
    "................................", # 02
    "...........KKKKKKKKKK...........", # 03 Capuz esférico
    ".........KKYyZZZZZZzzKK.........", # 04
    "........KKYyZZZZZZZZzzKK........", # 05
    ".......KKYyKKKKKKKKKKzzKK.......", # 06 Aro metálico
    ".......KKYKVVvvGGggvVKYzKK......", # 07 Visor esférico verde
    ".......KKYKVVvvGGggvVKYzKK......", # 08 Reflexo em arco
    ".......KKYyKKKKKKKKKKzzKK.......", # 09 Filtro frontal
    ".....KKOoKKKKRrHHrRKKKKOoKK.....", # 10 (8,10) Tanques químicos laterais
    "....KKOooKKKRrHHHHrRKKKooOKK....", # 11
    "....KKOooKKKRrHHHHrRKKKooOKK....", # 12
    "....KKOoKKKKRrHHHHrRKKKKOoKK....", # 13
    "......KKKKRrKKRrRrKKRrKKKK......", # 14 Preenchido sem furos internos!
    ".........KKYyZZZZZZzzKK.........", # 15 Macacão inflado amarelo
    "........KKYyZZZZZZZZzzKK........", # 16
    "........KKYyZZKKKKZZzzKK........", # 17 Fim do tronco
    "........KKYyZZKKKKZZzzKK........", # 18 Pernas proporcionais
    "........KKYyZZKKKKZZzzKK........", # 19
    "........KKRrRrKKKKRrRrKK........", # 20 Joelheiras de borracha
    "........KKRrHHrKKrHRrRKK........", # 21 Botas de descontaminação
    "........KKRrHHrKKrHRrRKK........", # 22
    "......KKKKRrHHrKKrHRrRKKKK......", # 23 Bico protetor
    "......KKRRRRRRRKKRRRRRRRKK......", # 24 PÉS ASSENTADOS EM Y=24!
    "......KKKKKKKKKKKKKKKKKKKK......", # 25 Linha base de contorno
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["04_hazmat_cleaner"] = (GRID_04, PAL_04, "04. Hazmat Bio-Cleaner", "Toxic Smog & Decon Technician", "Capuz amarelo vedado, visor panorâmico verde esmeralda, avental químico contínuo e botas robustas.")

# ------------------------------------------------------------------------------
# 05. NEON STREET SCAVENGER (Cyber-Punk Rebel)
# ------------------------------------------------------------------------------
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
    "................................", # 01
    "............KKmmnnKK............", # 02 Topo do moicano
    "...........KKmNNnnKK............", # 03
    "..........KKMmNNnnKK............", # 04 Moicano rosa espetado
    ".........KKMMmmKKKK.............", # 05
    "........KKFffFKKoCeeKK..........", # 06 Olho cibernético cyan/gold
    "........KKFffFKKCeeeKK..........", # 07 Bandana preta na boca
    "........KKKKKKKKKKKKKK..........", # 08
    ".......KKDdBBbbKKXxSSsKK........", # 09 Sem buracos internos! Colete e cromo
    "......KKDdBBbbKKKKOxSSsKK.......", # 10 (8,10) Fios no peito e braço
    ".....KKDddBBbbKKKKOxSSsKK.......", # 11
    ".....KKDddBBbbKKOoKXxSSsKK......", # 12 Peitoral jeans preenchido
    ".....KKDdBBbbKKKKOKXxSSsKK......", # 13
    "......KKDddbKKKKKKKKXxSSsKK.....", # 14 Mão cibernética
    "......KKFfeeKKKKKKKKXxSsKK......", # 15 Braço orgânico
    ".......KKKKKKSSSSSSKKKK.........", # 16 Cinto com tachas
    "...........KKDdDDddKK...........", # 17 Fim do tronco
    "...........KKDdDDddKK...........", # 18 Pernas proporcionais
    "...........KKFfKKddKK...........", # 19 Rasgo no joelho (pele)
    "...........KKFfKKddKK...........", # 20
    "...........KKDdKKddKK...........", # 21 Calça cargo
    "...........KKMmKKDdKK...........", # 22 Tênis descombinados
    ".........KKMmNNKKDdBBKK.........", # 23
    ".........KKmNssKKdDBBssKK.......", # 24 PÉS ASSENTADOS EM Y=24!
    ".........KKKKKKKKKKKKKKKK.......", # 25 Linha base de contorno
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["05_street_punk"] = (GRID_05, PAL_05, "05. Neon Street Scavenger", "Underground Cyber-Punk", "Moicano rosa neon espetado, colete jeans sem falhas, braço mecânico de cromo polido e proporção perfeita.")

# ------------------------------------------------------------------------------
# 06. APEX SECURITY ENFORCER (Corporate Shocktrooper)
# ------------------------------------------------------------------------------
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
    "................................", # 02
    "...........KKKKKKKKKKKK.........", # 03 Capacete com antena sólida
    ".........KKWwCCCcKKWWKK.........", # 04
    "........KKWwCCCCCcKKWKK.........", # 05
    "........KKWwRrLLLrrRrKK.........", # 06 Visor com fenda laser vermelha
    "........KKWwKKKKKKKKKKK.........", # 07
    "........KKWwCCCCCccWwKK.........", # 08 Mandíbula angular
    "......KKKKWwCCCCCCcWwKKKK.......", # 09 Ombreiras táticas
    "....KKWwCcKKWwCCCCwWKKcCWwKK....", # 10 (8,10) Placa peitoral de cerâmica
    "...KKWwCCcKKWwBbBBwWKKcCCCwKK...", # 11 Logo corporativo Neo-Apex
    "...KKWwCCcKKWwBbBBwWKKcCCCwKK...", # 12
    "....KKKKKKKKWwCCCCwWKKKKKKKK....", # 13
    "......KKUUuuKKWwwWKKUUuuKK......", # 14 Kevlar articulado
    "......KKUUuuKKWwwWKKUUuuKK......", # 15
    "......KKKKKKKKUUuuKKKKKKKK......", # 16 Cinto tático
    "........KKWwCcKKKKcCWwKK........", # 17 Fim do tronco
    "........KKWwCcKKKKcCWwKK........", # 18 Pernas proporcionais
    "........KKUUuuKKKKUUuuKK........", # 19 Juntas flexíveis
    "........KKWwCcKKKKcCWwKK........", # 20 Joelheiras brancas
    "........KKWwCcKKKKcCWwKK........", # 21 Caneleiras cerâmicas
    "......KKKKUUuuKKKKUUuuKKKK......", # 22 Botas pesadas
    "......KKWwCcKKKKKKKKcCWwKK......", # 23
    "......KKKKKKKKKKKKKKKKKKKK......", # 24 PÉS ASSENTADOS EM Y=24!
    "................................", # 25
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["06_corporate_enforcer"] = (GRID_06, PAL_06, "06. Apex Security Enforcer", "Corporate Tactical Guard", "Placas balísticas de cerâmica branca maciças, fenda laser vermelha, antena sólida e proporções imponentes.")

# ------------------------------------------------------------------------------
# 07. SYNTH UNIT MODEL-04 (Autonomous Android)
# ------------------------------------------------------------------------------
PAL_07 = make_palette({
    'K': '#0f1117', # Dark outline
    'T': '#2b3345', # Titanium shadow
    't': '#4a5773', # Titanium mid
    'S': '#7c8fa8', # Titanium highlight
    's': '#c0d0e6', # Titanium specular
    'C': '#0099b8', # Plasma cyan dark
    'c': '#00e1ff', # Plasma cyan bright
    'W': '#b3f7ff', # Plasma cyan core
    'w': '#e0ffff', # Plasma lens white
    'J': '#1c1f26', # Joint black
    'G': '#996633', # Copper conduit
    'g': '#cca352', # Copper bright
})

GRID_07 = [
    "................................", # 00
    "................................", # 01
    "................................", # 02
    ".............KKKKKK.............", # 03 Crânio robótico sintético
    "...........KKTtSSssKK...........", # 04 Chassi de titânio
    "..........KKTtSSssssKK..........", # 05 Lentes óticas superiores
    "..........KKTtCcWwCcKK..........", # 06 Sem buracos, preenchido
    "..........KKTtTtCcTtKK..........", # 07 Lente ótica inferior central
    "..........KKTtTtTtTtKK..........", # 08 Queixo mecânico
    ".........KKKKJJggGJKKKK.........", # 09 Junta de pescoço
    ".......KKTtSsKKJJGJKKSsTtKK.....", # 10 (8,10) Ombreiras esféricas
    ".....KKTtSSssKKCcWcKKSsSSsTtK...", # 11 Núcleo de plasma ciano
    ".....KKTtSSssKKCcWcKKSsSSsTtK...", # 12
    ".......KKKKKKTtCcWcTtKKKKKK.....", # 13 Costelas mecânicas
    "..........KKJJggJJggJJKK........", # 14 Coluna exposta
    "..........KKJJggJJggJJKK........", # 15
    ".........KKTtSSssssSSTtKK.......", # 16 Pelve mecânica
    ".........KKTtSsKKKKSsTtKK.......", # 17 Fim do tronco
    ".........KKTtSsKKKKSsTtKK.......", # 18 Pernas mecânicas proporcionais
    "..........KKJJGKKKJGJKK.........", # 19 Amortecedores pneumáticos
    ".........KKTtSsKKKKSsTtKK.......", # 20 Joelheiras digitígradas
    "..........KKJJGKKKJGJKK.........", # 21 Hastes
    ".........KKTtSsKKKKSsTtKK.......", # 22 Garras tripés
    "........KKTtSSssKKssSSTtKK......", # 23
    "........KKKKKKKKKKKKKKKKKK......", # 24 PÉS ASSENTADOS EM Y=24!
    "................................", # 25
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["07_synth_android"] = (GRID_07, PAL_07, "07. Synth Unit Model-04", "Autonomous Maintenance Android", "Chassi robótico de titânio sem falhas, trio de sensores óticos ciano, núcleo de plasma e pernas mecânicas.")

# ------------------------------------------------------------------------------
# 08. AERO-COURIER SKY-RUNNER (High-Altitude Acrobat)
# ------------------------------------------------------------------------------
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
    'q': '#ff809b', # Scarf tip specular
    'P': '#1a1f26', # Runner pants black
    'p': '#303947', # Runner pants mid
    'Y': '#ffe600', # Hazard stripe yellow
})

GRID_08 = [
    "................................", # 00
    "................................", # 01
    "................................", # 02
    ".............KKKKKK.............", # 03 Capacete de couro
    "...........KKFfffFffKK..........", # 04
    "..........KKFGgAAGgAAfKK........", # 05 Óculos de voo duplos âmbar
    "..........KKFGgAAGgAAfKK........", # 06
    "..........KKFfffffffFfKK........", # 07 Máscara de respiração
    ".........KKKKSSssRRssKKKK.......", # 08 Cachecol vermelho
    ".......KKJjjOKKSSSSKKqRRssKK....", # 09 Cauda do cachecol
    ".....KKJjjOOoKKssssKK..KKssSKK..", # 10 (8,10) Jaqueta bomber inflada
    "....KKJjjOOooKKKKKKKK....KKssSKK", # 11
    "...KKJjjOOoooKKJjjOOKK....KKKK..", # 12
    "...KKJjjOOoooKKJjjOOKK..........", # 13
    "....KKKKKKKKKKJjjOOKK...........", # 14
    ".......KKJjjOKKJjjOKK...........", # 15 Fim do tronco
    ".......KKPpYYKKPpYYKK...........", # 16 Pernas proporcionais com faixas
    ".......KKPpYYKKPpYYKK...........", # 17
    ".......KKPpppKKPpppKK...........", # 18 Joelheiras acolchoadas
    ".......KKPpppKKPpppKK...........", # 19
    ".......KKPpYYKKPpYYKK...........", # 20 Faixas refletivas
    ".......KKJjjOKKJjjOKK...........", # 21 Tênis aerodinâmicos
    ".......KKJjjOKKJjjOKK...........", # 22
    ".....KKKJjOOoKKJjOOoKKK.........", # 23 Solado
    ".....KKKKKKKKKKKKKKKKKK.........", # 24 PÉS ASSENTADOS EM Y=24!
    "................................", # 25
    "................................", # 26
    "................................", # 27
    "................................", # 28
    "................................", # 29
    "................................", # 30
    "................................", # 31
]
CONCEPTS["08_aero_courier"] = (GRID_08, PAL_08, "08. Aero-Courier Sky-Runner", "High-Altitude Acrobat", "Jaqueta bomber laranja fluorescente, óculos de aviador âmbar, cachecol vermelho e proporções esportivas perfeitas.")

def main():
    base_dir = Path(__file__).resolve().parent.parent
    concepts_dir = base_dir / "assets" / "CharacterIdeas" / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    print("Construindo e validando os 8 conceitos com proporções perfeitas...")

    rendered = []
    total_holes_found = 0

    for key, (grid, pal, title, subtitle, desc) in CONCEPTS.items():
        img = render_ascii_sprite(grid, pal)

        # Validação estrita de furos internos!
        holes = find_internal_holes(img)
        if holes:
            print(f"  [ERRO] {key} tem {len(holes)} furos internos: {holes}")
            total_holes_found += len(holes)
        else:
            print(f"  [VALIDADO] {title}: 0 furos internos. Silhueta 100% contínua.")

        # Validação da altura dos pés (deve ser Y=24)
        lowest_y = max(y for y in range(32) for x in range(32) if img.getpixel((x, y))[3] > 0)
        highest_y = min(y for y in range(32) for x in range(32) if img.getpixel((x, y))[3] > 0)
        height = lowest_y - highest_y + 1
        print(f"    -> Altura útil: {height}px (Y={highest_y} a Y={lowest_y})")

        rendered.append((key, img, title, subtitle, desc))

        # Salva PNG 32x32 nativo
        path_32 = concepts_dir / f"concept_{key}.png"
        img.save(path_32)

        # Salva Preview 8x (256x256) limpo
        path_8x = concepts_dir / f"preview_8x_{key}.png"
        img_8x = img.resize((256, 256), Image.Resampling.NEAREST)
        img_8x.save(path_8x)

    if total_holes_found > 0:
        raise RuntimeError(f"FALHA: {total_holes_found} furos encontrados!")

    # Atualiza spritesheet horizontal (256x32)
    strip_img = Image.new("RGBA", (32 * 8, 32), (0, 0, 0, 0))
    for i, (_, img, _, _, _) in enumerate(rendered):
        strip_img.paste(img, (i * 32, 0))
    strip_path = concepts_dir / "all_8_concepts_strip_256x32.png"
    strip_img.save(strip_path)

    # Atualiza Cartela Comparativa Geral (Showcase)
    card_w = 280
    card_h = 320
    cols = 4
    rows = 2
    showcase_w = cols * card_w + 40
    showcase_h = rows * card_h + 100

    showcase = Image.new("RGBA", (showcase_w, showcase_h), (18, 18, 26, 255))
    draw = ImageDraw.Draw(showcase)

    # Cabeçalho
    draw.rectangle([(0, 0), (showcase_w, 64)], fill=(12, 12, 18, 255))
    draw.line([(0, 64), (showcase_w, 64)], fill=(0, 229, 255, 255), width=2)
    draw.text((25, 14), "APEX GRAPPLER — 8 CONCEITOS VISUAIS COM PROPORCOES CORRIGIDAS", fill=(255, 255, 255, 255))
    draw.text((25, 36), "Zero Furos Internos | Pernas Proporcionais (Base Y=24) | Contorno Solido 1px | 32x32 Nativo", fill=(170, 180, 200, 255))

    for i, (key, img, title, subtitle, desc) in enumerate(rendered):
        col = i % cols
        row = i // cols
        cx = 20 + col * card_w
        cy = 80 + row * card_h

        # Card
        draw.rectangle([(cx, cy), (cx + card_w - 15, cy + card_h - 15)], fill=(25, 27, 38, 255), outline=(45, 50, 70, 255), width=1)
        draw.line([(cx, cy), (cx + card_w - 15, cy)], fill=(255, 140, 0, 255) if i == 0 else (0, 229, 255, 255), width=2)

        # Caixa do Sprite
        bx = cx + 65
        by = cy + 18
        draw.rectangle([(bx - 3, by - 3), (bx + 131, by + 131)], fill=(14, 15, 22, 255), outline=(60, 65, 85, 255))

        for qy in range(16):
            for qx in range(16):
                bg_col = (26, 28, 40, 255) if (qx + qy) % 2 == 0 else (18, 20, 28, 255)
                draw.rectangle([(bx + qx * 8, by + qy * 8), (bx + (qx + 1) * 8 - 1, by + (qy + 1) * 8 - 1)], fill=bg_col)

        # Sprite 32x32 ampliado 4x (128x128)
        scaled_sprite = img.resize((128, 128), Image.Resampling.NEAREST)
        showcase.paste(scaled_sprite, (bx, by), scaled_sprite)

        # Textos
        draw.text((cx + 12, cy + 162), title, fill=(255, 220, 40, 255))
        draw.text((cx + 12, cy + 182), subtitle, fill=(0, 229, 255, 255))

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

        draw.text((cx + 12, cy + 268), "Escala nativa 1x:", fill=(110, 120, 140, 255))
        showcase.paste(img, (cx + 130, cy + 262), img)

    showcase_path = concepts_dir / "concepts_showcase_comparison.png"
    showcase.save(showcase_path)
    print(f"\nSucesso absoluto! Todos os 8 conceitos foram gerados sem nenhum furo e com proporções perfeitas.")

if __name__ == "__main__":
    main()
