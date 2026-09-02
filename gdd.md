# Game Design Document

Revision: 0.0.1

> GDD Template Written by: Benjamin “HeadClot” Stanley

# Overview
 
## Theme / Setting / Genre
 
Cyberpunk
 
## Core Gameplay Mechanics Brief
 
- Limpar e consertar janelas (ação com timer, mesmo botão contextual)
- Movimentação por sistema de ancoragem (arma de gancho, 3 âncoras)
- Troca de âncora ativa via salto, com risco de queda fatal
- Desviar de balas perdidas
- Power-ups (pós-MVP)
## Targeted platforms
 
- Web (browser), via export nativo do Pyxel
- Android via wrapper (Capacitor ou similar) avaliado como meta pós-MVP, não faz parte do escopo inicial
## Monetization model (Brief/Document)
 
- Power-Ups como itens pagos antes do início do jogo **pós-MVP**. A integração de pagamento é trabalho de infraestrutura à parte do jogo e não está no escopo dos 3 meses de desenvolvimento solo.
## Project Scope
 
### Game Time Scale
 
- Free
- Infinite Gameplay, Points System
### Team Size
 
**Core Team**
 
- Nícolas Pitz    Developer, Designer e Audio Designer
**Disponibilidade**: ~3 meses de desenvolvimento, ~8h semanais livres (≈ 96h totais de trabalho solo)
 
### Licenses / Hardware / Other Costs
 
- Pyxel (MIT License, gratuito)
- (a definir conforme necessidade)
### Total Costs with breakdown
 
- (a definir)
## Influences (Brief)
 
**Influence #1**
- Medium: Games
- A estética vai ser influenciada pelo jogo Cyberpunk 2077.
---
 
# The elevator Pitch
 
Já imaginou se os alpinistas industriais tivessem que se proteger dos perigos de um mundo futurista onde tiros viajam em sua direção toda hora enquanto limpam os vidros para não serem demitidos? Então, é o que o meu jogo propõe.
 
## Project Description (Brief)
 
Em New Tokyo (233 d.IA), a automação substituiu quase toda a mão de obra humana. Você é um dos poucos remanescentes trabalhando na manutenção do arranha-céu "Apex-01", deslocando-se pela fachada através de um sistema de ancoragem por gancho. Em um sistema que exige performance absoluta, você deve limpar e reparar os vidros sob fogo cruzado, equilibrando o risco físico direto com a pressão constante de uma avaliação corporativa que nunca para de cair.
 
## Project Description (Detailed)
 
Em uma New Tokyo distópica do ano 233 d.IA (depois da IA), a disparidade social atinge o topo dos arranha-céus gigantescos mantidos por megacorporações impiedosas. O jogador assume o papel de um dos últimos alpinistas industriais humanos da cidade, contratado por uma empresa de fachada para realizar a manutenção externa do maior edifício da metrópole. O trabalho consiste em limpar a sujeira acumulada e reparar vidros danificados por tiroteios e drones com defeito, tudo isso suspenso a centenas de metros do chão sob condições extremas.
 
O loop principal de gameplay combina a tensão de um sistema de ancoragem por gancho com a agilidade de um jogo arcade acelerado. O jogador planta âncoras numa fachada de vidro (até 3 simultâneas), se desloca pela corda ativa e, para trocar de posição rapidamente, salta de uma âncora em direção a outra já plantada   um movimento que só funciona se houver alinhamento vertical entre os pontos, e que resulta em morte instantânea por queda se o jogador calcular errado. Enquanto limpa e conserta os vidros (uma ação com tempo de execução fixo, durante a qual fica parado e vulnerável), o jogador também precisa desviar de balas perdidas vindas do tráfego aéreo e das disputas territoriais nos andares inferiores, e manter uma taxa de produtividade constante para não ser demitido.
 
A narrativa implícita reflete o tema do trabalhador descartável. No topo da tela, métricas da corporação avaliam a eficiência do jogador em tempo real. Erros diminuem a pontuação e aumentam o risco de "rescisão imediata de contrato" — seja por queda fatal, por dano acumulado, ou pela barra de eficiência corporativa chegando a zero. O jogo utiliza elementos visuais neon contrastando com a sujeira e a fuligem dos vidros, criando uma atmosfera imersiva que traduz o desgaste físico e mental de ser apenas mais uma engrenagem viva em uma máquina automatizada.
 
## What sets this project apart?
 
- **Premissa única de gameplay**: combina a profissão de alpinista industrial com um sistema de ancoragem por gancho de risco calculado, num ambiente cyberpunk de sobrevivência vertical.
- **Crítica social integrada ao loop de jogo**: a pontuação não reflete apenas "pontos", mas a avaliação de desempenho corporativo do trabalhador para não ser substituído e essa avaliação é, ela mesma, uma das formas de perder o jogo.
---
 
# Core Gameplay Mechanics (Detailed)
 
### Movimentação e Ancoragem
 
**Details**: O jogador carrega uma arma de gancho com até 3 âncoras disponíveis simultaneamente. Cada âncora, quando ativa, conecta o personagem a um ponto da fachada e permite movimento livre ao longo da corda (subir, descer, balançar).
 
**How it works**:
- O jogador mira e atira a arma pra plantar uma nova âncora num ponto da fachada, dentro de um alcance limitado (possível enquanto houver menos de 3 âncoras plantadas).
- A mesma arma recolhe uma âncora já plantada, liberando capacidade para plantar em outro lugar.
- Apenas uma âncora fica ativa (conectada) por vez. As demais ficam plantadas, à espera.
- Para trocar de âncora ativa, o jogador salta a corda atual se desconecta e o personagem fica no ar, em queda livre com o momentum do salto. Nesse estado, ele pode pressionar um botão de link para se reconectar a outra âncora já plantada, desde que ela esteja aproximadamente no mesmo eixo Y.
- Se o jogador saltar e não houver nenhuma âncora alinhada disponível para link, ele cai e morre instantaneamente.
- Com as 3 âncoras em uso e nenhuma recolhida, o jogador ainda pode se mover verticalmente (subir/descer) na âncora ativa atual, mas não consegue plantar uma nova.
### Limpeza e Reparo de Janelas
 
**Details**: O objetivo primário de receita no jogo. Cada painel de vidro apresenta diferentes estados: sujo ou quebrado (danificado por disparos).
 
**How it works**:
- Um único botão de ação, contextual: o jogo detecta automaticamente o estado da janela (suja ou quebrada) e aplica a ação correta.
- Limpeza: timer de 1.5 segundos. Conserto: timer de 3.5 segundos.
- Durante a ação, o personagem fica travado no local e vulnerável.
- A ação pode ser interrompida (inclusive automaticamente, se o jogador for atingido por um tiro) e retomada depois exatamente de onde parou, sem perda de progresso isso pode acontecer múltiplas vezes na mesma janela.
- Painéis limpos/consertados geram pontuação e aumentam o multiplicador de eficiência do turno.
### Power-Ups Pré-Partida (Monetização) pós-MVP
 
**Details**: Itens consumíveis adquiridos ou equipados antes do início do turno de trabalho, conferindo vantagens temporárias ou passivas. Fora do escopo do desenvolvimento inicial de 3 meses.
 
**How it works**: Através da loja interna, o jogador poderá adquirir itens (a detalhar quando esta fase for retomada).
 
---
 
# Story and Gameplay
 
## Story (Brief)
 
Em New Tokyo (233 d.IA), a automação substituiu 99% da mão de obra humana. Você é um dos poucos remanescentes trabalhando na manutenção do arranha-céu "Apex-01". Em um sistema que exige performance absoluta, você deve limpar e reparar a fachada do prédio sob fogo cruzado para manter sua pontuação acima da média e evitar ser demitido e jogado na miséria.
 
## Story (Detailed)
 
Após a Grande Singularidade no ano 0 d.IA, a humanidade foi gradualmente afastada de cargos executivos e técnicos, restando apenas funções insalubres onde o custo de manutenção de robôs é maior que o valor da vida humana. Em 233 d.IA, a megacorporação Neo-Apex mantém o edifício mais alto do planeta em New Tokyo.
 
O protagonista é um alpinista industrial contratado por uma terceirizada sub-paga. Seu trabalho diário é manter a fachada impecável para a elite que vive nos andares superiores, totalmente alienada da violência urbana que ocorre lá embaixo. Projéteis perdidos de guerras territoriais entre gangues são uma ameaça constante. No entanto, a maior ameaça é o próprio sistema de avaliação: um algoritmo implacável monitora cada segundo do turno. Se a taxa de limpeza cair ou o tempo de reparo for alto, o contrato é rescindido imediatamente e outro humano desempregado assume o lugar.
 
## Gameplay (Brief)
 
Um jogo arcade de sobrevivência e ação em ritmo acelerado onde você controla um alpinista suspenso por um sistema de ancoragem na fachada de um prédio infinito. Limpe janelas, faça reparos, evite tiros e arrisque saltos calculados entre pontos de ancoragem para alcançar a maior pontuação possível antes de falhar.
 
## Gameplay (Detailed)
 
O jogo se passa em uma perspectiva 2D da fachada do arranha-céu.
 
- **Fluxo da Partida**: o jogador inicia numa seção do prédio. O tempo começa a contar e a barra de Eficiência Corporativa cai gradualmente se o jogador ficar inativo.
- **Loop de Ação**: o jogador identifica janelas com pontos (sujas/quebradas), planta ou reutiliza uma âncora, se posiciona junto ao painel, realiza a ação de limpeza/conserto e parte para o próximo objetivo seja movendo-se na corda ativa, seja saltando para outra âncora já plantada.
- **Ameaças Dinâmicas (MVP)**: balas perdidas vindas da cidade, com trajetória e colisão simples. *(Drones de patrulha e descargas elétricas na fachada ficam como stretch goals, fora do escopo inicial.)*
- **Fim de Partida (Game Over)**: a partida encerra por qualquer uma das seguintes condições, todas independentes entre si:
  - Vida (HP) chega a zero por dano de projétil.
  - Queda fatal, ao errar um link de troca de âncora no ar.
  - A barra de Desempenho Corporativo se esgota por falta de produtividade/inatividade.
---
 
# Assets Needed
 
## 2D
 
- Spritesheet do personagem: 32x32 pixels por frame, pixel art estilo SNES, paleta reduzida, animações de ancoragem/movimento/limpeza/conserto/dano/queda.
- Texturas de vidros (Limpo, Sujo, Quebrado).
- Molduras e vigas metálicas futuristas para a estrutura do edifício construídas como **tileset modular** (peças de 8x8 ou 16x16px), compatível com o sistema de tilemap do Pyxel, respeitando a paleta fixa de 16 cores do motor.
- Texturas de fundo (skyline de New Tokyo com névoa neon, chuva sintética e luzes) também modulares, dentro do limite de 256x256px por image bank do Pyxel.
- Sprite/UI de interface (métricas corporativas, barra de vida, pontuação, HUD).
## Personagens *(reclassificado de "3D" o jogo é inteiramente 2D)*
 
- Protagonista (Alpinista Industrial): traje macacão de trabalho desgastado ou trench coat longo (referência visual definida), capacete/visor futurista, arma de gancho e equipamentos visíveis.
- Drones inimigos (stretch goal, pós-MVP): drones de patrulha com luzes vermelhas de alerta.
## Sound
 
Nota: o motor de áudio nativo do Pyxel suporta 4 canais simultâneos em estilo chiptune 8-bit. O design sonoro abaixo é a visão de longo prazo do projeto; a v1/MVP usará uma versão simplificada, compatível com essa limitação, com arquivos externos (.wav/.ogg) como possibilidade caso seja necessário som mais rico.
 
**Sound List (Ambient)**
 
*Outside*
- Level 1 (Setores Baixos): tráfego aéreo ruidoso, sirenes de emergência, eco distorcido de tiros em becos.
- Level 2 (Setores Médios): vento de média altitude, zumbido de neon, drones comerciais com anúncios holográficos.
- Level 3 (Setores Altos / Apex): vento uivante de alta altitude, silêncio corporativo interrompido por turbinas de naves executivas.
*Inside (vindo através das janelas)*
- Level 1: música industrial synth, ruído de maquinário das zonas industriais.
- Level 2: escritórios corporativos, bipes de servidores, ar condicionado.
- Level 3: música lounge futurista suave, eco de festas na cobertura.
**Sound List (Player)**
 
*Character Movement*
- Ancoragem: trava metálica do gancho se fixando, corda tensionando.
- Salto/troca de âncora: zunido de vento no ar, som de reconexão bem-sucedida (ou de queda, se falhar).
- Limpeza/Reparo: chiado do spray, rodo raspando sujeira, selamento a laser da resina.
*Character Hit / Collision*
- Impacto de projétil: bala ricocheteando ou perfurando o traje.
- Colisão forte: som surdo contra vigas ou bordas de janela.
*Character Injured / Death*
- Dano recebido: gemido abafado, respiração acelerada em baixa vida.
- Alerta de vitalidade: bipe de emergência do visor.
- Morte/queda: grito de queda livre, alarme de "Contrato Encerrado".
---
 
# Code
 
*Nomenclatura de scripts corrigida para `.py`, refletindo o uso do Pyxel/Python*
 
**Character Scripts (Player)**
- `player_anchor_system.py`: gerencia as 3 âncoras (plantar, recolher, âncora ativa), física de corda na âncora ativa, salto e link de troca com verificação de alinhamento no eixo Y, e a condição de queda fatal.
- `player_cleaning_system.py`: detecção de janelas sujas/quebradas, controle do timer de limpeza (1.5s) e conserto (3.5s), pausa/retomada de progresso, interrupção por dano.
- `player_health_and_score.py`: gerencia HP (dano por projétil), barra de Eficiência Corporativa (queda por tempo/inatividade), pontuação e condições de game over.
**Ambient Scripts**
- `building_generator.py`: geração procedural da fachada colunas de janelas, vigas, pontos válidos de ancoragem.
- `hazard_spawner.py`: spawn de balas perdidas (MVP); drones e descargas elétricas como extensão futura.
**Hazard Scripts**
- `stray_bullet.py`: trajetória e colisão dos projéteis perdidos.
- `patrol_drone_ai.py` *(stretch goal, pós-MVP)*: comportamento de patrulha e disparo de advertência.
---
 
# Animation
 
## Environment Animations
 
- Vidros e fachada: transição de estilhaçamento sob impacto, sujeira sumindo com a limpeza, iluminação neon piscando nos painéis.
## Character Animations (Player)
 
- Idle (ancorado): balanço suave do corpo, micro-ajustes de equilíbrio.
- Movimento na corda ativa: subir, descer, balançar.
- Mira e disparo da âncora: braço estendido, gancho disparando.
- Recolher âncora.
- Salto entre âncoras: corpo projetado no ar com momentum.
- Reconexão bem-sucedida: encaixe na nova âncora.
- Queda fatal: falha de link, queda livre descontrolada.
- Limpeza: movimento repetitivo de braço com o rodo (1.5s).
- Conserto: aplicação de resina/selamento a laser (3.5s).
- Reação a dano: projeção para trás ao levar um tiro.
## NPCs / Drones *(stretch goal, pós-MVP)*
 
- Drone de patrulha: estabilização no ar, escaneamento com laser, recuo de disparo.
---
 
# Schedule
 
* **Sistema de movimento e ancoragem**
   * Time Scale: Semanas 1-3 (~20h)
      * Milestone 1: Protótipo da arma de gancho (mirar, plantar âncora, recolher)
      * Milestone 2: Física de corda/pêndulo na âncora ativa
      * Milestone 3: Mecânica de salto + link entre âncoras, com queda fatal se sem alinhamento
* **Fachada, limpeza e pontuação**
   * Time Scale: Semanas 4-7 (~28h)
      * Milestone 1: Geração procedural da coluna de janelas (estados: limpo / sujo)
      * Milestone 2: Ação de limpeza/conserto com timer interrompível (1.5s / 3.5s, botão único contextual)
      * Milestone 3: Sistema de pontuação e barra de Eficiência Corporativa (queda por tempo/inatividade)
* **Ameaças e sobrevivência**
   * Time Scale: Semanas 8-9 (~15h)
      * Milestone 1: Balas perdidas (spawn, trajetória, colisão)
      * Milestone 2: Sistema de HP separado da barra corporativa, com interrupção de ação ao ser atingido
      * Milestone 3 (stretch, se sobrar tempo): Drone de patrulha com padrão de rota simples
* **Áudio, UI e polimento**
   * Time Scale: Semanas 10-12 (~33h)
      * Milestone 1: Efeitos sonoros chiptune (ancoragem, limpeza, impacto, alerta de vida/eficiência)
      * Milestone 2: HUD com métricas corporativas, pontuação e vida
      * Milestone 3: Testes, ajuste de dificuldade (curva de spawn de balas), correção de bugs
      * Milestone 4 (stretch, se sobrar tempo): Power-ups com efeito de gameplay (sem sistema de pagamento real ainda)
