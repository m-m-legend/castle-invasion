# Diagnóstico e migração

Base analisada: commit `91bcc36` do repositório
[m-m-legend/castle-invasion](https://github.com/m-m-legend/castle-invasion).

## O que já existia

O protótipo já separava definições, entidades, sistemas e interface. Havia um
castelo 5×5, descrições para 25 salas, quatro inimigos, cinco armas, duas curas,
chave, poção e sprites ASCII. `BattleController` e `BattleView` indicavam a intenção
de desacoplar regras e apresentação. As notas identificavam como próximos passos
a integração de `GameState` e a construção de `main.py`.

## Problemas observados no código

| Local anterior | Problema | Solução |
| --- | --- | --- |
| `main.py` | Arquivo vazio, sem inicialização ou loop | Bootstrap e duas entradas executáveis |
| `core/state.py` | Core importava entidades e sistemas | Estado no domínio; orquestração em `Game` |
| `entities/player.py` | Entidade importava o sistema de movimento | Movimento coordenado pelo caso de uso |
| `BattleController.modifier` | Valor 1 significava bloquear 100%; era o padrão | Multiplicador recebido começa em 1 e é local ao turno |
| `player_use_heal` | Multiplicador 1.1/1.2 passado como HP absoluto | Fração explícita da vida máxima |
| `Inventory.equip_weapon` | Retornava ID sem mudar arma ativa | Slot ativo persistente |
| `enemy_is_dead` | Consulta podia gerar loot novamente após consumo | Recompensa aplicada na transição, flag persistente |
| `ui/battle_ui.py` | Chamava turno inimigo sem entrada ou após ação inválida | Uma ação válida por turno |
| `core/input.py` | `chr` sobre códigos negativos e `None.isdigit` | Adaptadores filtram eventos e processam linhas completas |
| UI de loot | Interface alterava inventário e resolvia regras | Coleta/troca nos sistemas; chão persiste excedentes |
| UI com posições fixas | Conteúdo podia se sobrepor ou sair da tela | Quebra de linhas e painel rolável |
| README | Marcava como prontas funções sem integração executável | Documentação alinhada ao comportamento testado |

## Conteúdo preservado e decisões novas

Foram preservados integralmente mapa, descrições, sprites, definições de armas e
itens. Inimigos mantêm nome, vida, dano, posição, sprite e loot. As duas curas
mantêm a intenção de 10%/20%, mas agora usam `heal_fraction: 0.1/0.2`, com semântica
explícita sobre a vida máxima. Dados Python viraram JSON validado.

Para completar uma campanha jogável, foram acrescentados:

- Equipamento inicial: espada, escudo e duas poções; HP inicial 100.
- Loot de salas: cura no Jardim/Capela, poções na Enfermaria/Cozinha/Laboratório e arco na Sala de Armas.
- XP por inimigo, progressão, defesa básica de 15% e custo de fuga igual a um ataque.
- Objetivo: obter a chave do Mago e abrir o baú em Tesouro.
- Persistência, confirmação de descarte de progresso e estados de vitória/derrota.

Essas são escolhas iniciais de design, não requisitos atribuídos ao autor.
Estão documentadas e parametrizadas no JSON para facilitar ajuste.

## Mapeamento dos arquivos

| Antes | Agora |
| --- | --- |
| `data/*.py` | `src/castle_invasion/data/campaign.json` |
| `core/item_registry.py`, `core/sprite_registry.py` | `core/content.py` e loader injetado |
| `core/state.py`, `entities/*.py` | `entities/models.py` e criação em `systems/game.py` |
| `systems/combat_system.py` | `src/castle_invasion/systems/combat_system.py` |
| `systems/movement.py`, `systems/map_system.py` | `systems/movement.py` e consultas do catálogo |
| `systems/inventory_system.py` | Operações de inventário e casos de uso em `Game` |
| `systems/battle_view.py` | `ui/presenter.py`, sem consumo de estado ao renderizar |
| `ui/*.py`, `core/input.py` | `ui/terminal.py`, `ui/asciimatics_ui.py` e `ui/session.py` |
| `notes.txt` | `docs/initial-notes.txt`, mantido como registro histórico |

Não há compatibilidade de imports com os módulos antigos. Esta versão estabelece
a API do pacote `castle_invasion`; o protótipo não tinha consumidores externos ou
saves documentados. O histórico Git preserva as implementações anteriores.

## Aplicar a entrega no repositório existente

O ZIP contém o projeto completo atualizado em `castle-invasion/` e um patch em
`castle-invasion-0.2.0.patch`. Para só jogar, extraia em uma pasta nova e execute
`python main.py` dentro de `castle-invasion`.

Para preservar o histórico do seu clone, use o patch na base indicada acima.
Primeiro confirme que `git status` está limpo; salve suas alterações locais antes
de prosseguir. Com o patch na pasta imediatamente acima do repositório:

```bash
git switch -c feat/playable-engine
git apply --check ../castle-invasion-0.2.0.patch
git apply --index ../castle-invasion-0.2.0.patch
python -m unittest discover -s tests -v
python main.py
git diff --cached --stat
git commit -m "Implement playable data-driven RPG engine"
```

Se `git apply --check` informar conflito, não force: compare o seu HEAD com
`91bcc36`. O patch deve ser adaptado se houve novos commits ou edições nos mesmos
arquivos. Copiar apenas os arquivos novos por cima do clone deixaria as antigas
pastas órfãs; o patch também registra as remoções e a mudança das notas.

O envio ao GitHub fica a cargo do autor. Os workflows só executarão depois do push.
