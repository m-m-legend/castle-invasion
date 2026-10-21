# Dados e regras da campanha

Arquivo padrão: `src/castle_invasion/data/campaign.json`, UTF-8, JSON sem comentários.
Não é usado `eval`, `exec`, pickle ou importação de módulos enviados como campanha.
O loader rejeita campos desconhecidos nos registros, chaves JSON duplicadas e
referências inválidas antes de iniciar o jogo.

## Seções

| Seção | Conteúdo |
| --- | --- |
| `schema_version` | Inteiro `1` |
| `title` | Título da campanha |
| `map` | Lista de linhas; nomes de salas ou `null` para células bloqueadas |
| `rooms` | Descrição e loot de inspeção de cada sala |
| `weapons` | Nome, dano, tipo e modificadores de armas |
| `heals` | Habilidades reutilizáveis de cura e cooldown |
| `items` | Chaves e consumíveis empilháveis |
| `enemies` | Atributos, sala, sprite, XP e loot |
| `sprites` | Linhas de arte do castelo, personagem e inimigos |
| `player` | Vida máxima, sala inicial, equipamentos e itens iniciais |
| `rules` | Parâmetros gerais de combate e progressão |
| `objective` | Sala, chave necessária e mensagem de vitória |

Não há limite fixo de 5×5 para o mapa. Linhas irregulares são aceitas, mas todas as
salas precisam ser alcançáveis por movimentos ortogonais. Nomes de sala são únicos
e são as chaves em `rooms`. IDs de objetos são separados dos nomes exibidos.
Recomenda-se usar IDs em `snake_case`, sem espaços, para comandos como `pocao ID`.

## Loot e inspeção

Cada entrada tem exatamente `kind` e `id`:

```json
[
  {"kind": "item", "id": "pocao_cura"},
  {"kind": "weapon", "id": "lanca"},
  {"kind": "heal", "id": "biblia"}
]
```

`kind` é `item`, `weapon` ou `heal`. Quantidades maiores são representadas por
entradas repetidas. Todo ID precisa existir na categoria correspondente.

Inspecionar revela o loot da sala uma única vez. Vencer concede o loot do inimigo
uma única vez. Itens comuns empilham; armas preenchem slots livres; curas preenchem
o único slot de cura. O excedente fica no chão. Trocas deixam o equipamento anterior
no chão, sem apagá-lo. Inspecionar novamente não recria objetos já coletados.

O `rewarded` salvo com cada inimigo evita recompensas repetidas. Consultas de
estado e renderização nunca geram loot.

## Armas

Exemplo de definição adicional dentro de `weapons`:

```json
"machado": {
  "name": "Machado de Ferro",
  "damage": 14,
  "type": "melee"
}
```

Para disponibilizá-lo, adicione `{"kind":"weapon","id":"machado"}` ao loot de uma
sala ou inimigo. Não basta cadastrar uma arma: é necessário tornar possível obtê-la.

Tipos aceitos: `melee`, `ranged`, `magic` e `defense`. São classificações; o mapa
atual não modela alcance espacial dentro da batalha. `boost` multiplica o dano da
arma, e `block` indica a fração bloqueada ao defender com aquela arma ativa.

```text
dano do jogador = dano da arma × boost + (nível - 1) × damage_per_level
dano sem arma   = unarmed_damage + (nível - 1) × damage_per_level
dano recebido ao defender = dano inimigo × (1 - block)
```

O boost padrão é 1. Sem `block`, usa-se `rules.base_block`. Escudo não concede
bloqueio passivo só por estar no inventário: é preciso equipá-lo e escolher defender.
Defesa vale para uma resposta inimiga, e ataque fatal não sofre retaliação.

## Cura reutilizável e poções

```json
"semente_regeneradora": {
  "name": "Semente Regeneradora",
  "heal_fraction": 0.2,
  "enemy_damage_multiplier": 0.1,
  "cooldown": 2,
  "message": "Você sente sua vida se regenerando..."
}
```

A habilidade restaura `vida_máxima × heal_fraction`, respeitando a vida máxima.
No exemplo, restaura até 20 HP quando o máximo é 100. O inimigo responde com
10% de seu dano normal. A habilidade pode ser usada novamente depois de duas
ações válidas posteriores; a própria cura não reduz seu cooldown.

Habilidades de cura funcionam somente durante combate. O cooldown pertence ao
encontro e é reiniciado ao entrar em outra batalha, inclusive após fugir e voltar.
Isso é uma regra explícita da versão atual. Poções funcionam também na exploração.

Poções usam `type: "consumable"` e `health_restore` em pontos absolutos. Seu uso
consome uma unidade. Tentar usar cura ou poção com vida cheia não gasta item/turno.

## Inimigos e progressão

Um inimigo exige `name`, `health`, `damage`, `sprite_key`, `placement`, `loot` e `xp`.
O HP/dano originais foram preservados. A resposta inimiga é um ataque determinístico;
não existe seleção aleatória de habilidades. Mais de um inimigo na mesma sala gera
combates sequenciais na ordem em que aparecem em `enemies`.

```text
nível = 1 + XP_total // xp_per_level
vida_máxima = vida_inicial + (nível - 1) × health_per_level
```

Cada nível ganho cura o mesmo número de pontos acrescidos à vida máxima, sem cura
completa automática. Os valores iniciais são 50 XP por nível, +10 HP máximos e +2
de dano por nível. Esses valores são decisões de balanceamento editáveis nos dados.

## Objetivo

O objetivo atual é um baú que exige uma chave. `objective.room` aponta para uma
sala e `objective.key` aponta para um item de tipo `key` que deve ser obtível.
Ao chegar à sala, use `abrir`; entrar nela sozinho não finaliza a campanha.

O loader verifica existência da chave em inventário inicial ou loot, mas não
prova que o jogador terá recursos suficientes para vencer. O teste da campanha
padrão demonstra uma rota concluível com os quatro inimigos; novas campanhas
precisam de seu próprio teste de balanceamento.

## Saves e compatibilidade

Saves usam `save_version: 1` e o SHA-256 do conteúdo canônico da campanha. O formato
registra personagem, inventário, salas, chão, inimigos, recompensa, combate,
cooldown, visitas e vitória. Arquivos inválidos não substituem a partida atual.

O arquivo é escrito em um temporário no mesmo diretório e substituído com
`os.replace` após flush/fsync. Isso evita truncar o save anterior se a escrita falhar.
Não há sincronização entre processos: não use duas instâncias gravando no mesmo save.
O hash serve para compatibilidade, não como proteção contra edição deliberada.

Alterações de conteúdo invalidam saves antigos por opção conservadora. Futuras
migrações devem ser explícitas; não remova a verificação para forçar o carregamento.

## Validar

```bash
python main.py --data minha-campanha.json --validate-data
```

Sucesso retorna código 0; dados inválidos retornam 2 e uma explicação. Esse comando
valida referências e estrutura sem abrir o jogo. Executar com `--data` faz a mesma
validação automaticamente.
