# Castle Invasion

Mini engine para RPGs medievais de terminal, escrita em Python e orientada a dados.
A campanha incluída permite explorar um castelo, combater inimigos por turnos,
coletar equipamentos, subir de nível e abrir o tesouro com a chave do Mago.

**Versão 0.2.0 · Python 3.10+ · Licença MIT**

## Jogar agora

Não há dependências externas para a interface padrão. Na pasta do projeto:

```bash
python main.py
```

No Windows, também é possível usar `py -3 main.py` ou abrir `run.bat`.
Todos os comandos do jogo são confirmados com **Enter**.

```bash
python main.py --name Marcos
python main.py --no-art
python main.py --load
python main.py --save saves/minha-partida.json
```

O caminho padrão do save é `~/.castle-invasion/save.json`, dentro da pasta do usuário.
Use `salvar` durante o jogo. **Não há salvamento automático.** Sair, reiniciar ou
carregar com alterações pendentes exige confirmação. EOF ou interrupção forçada
encerram a sessão sem gravar alterações.

### Interface com asciimatics

```bash
python -m venv .venv
```

Ative o ambiente com `.venv\Scripts\activate` no Prompt de Comando do Windows,
`.venv\Scripts\Activate.ps1` no PowerShell ou `source .venv/bin/activate` no Linux/macOS.
Depois:

```bash
python -m pip install -e ".[tui]"
python main.py --ui asciimatics
```

Essa interface usa o mesmo motor e os mesmos comandos. PageUp/PageDown rolam o
painel; Esc limpa a entrada. Redimensionar a janela mantém a partida. Recomenda-se
um terminal de pelo menos 80×30; abaixo de 40×12 aparece um aviso. Use um terminal
real, como Windows Terminal, e não o painel de saída de uma IDE.

### Instalar como pacote

```bash
python -m pip install .
castle-invasion
python -m castle_invasion
```

O JSON da campanha acompanha o pacote. Não é necessário executar a partir da
pasta do repositório.

## Comandos

| Comando | Efeito |
| --- | --- |
| `n`, `s`, `l`, `o` | Move para norte, sul, leste ou oeste |
| `inspecionar` | Procura e coleta objetos uma vez por sala |
| `inventario` / `i` | Mostra os três slots de armas, cura e itens |
| `mapa` / `m` | Mostra coordenadas, sala atual e salas visitadas |
| `atacar` / `a` | Ataca e recebe a reação do inimigo sobrevivente |
| `defender` / `d` | Reduz apenas o próximo ataque recebido |
| `curar` / `c` | Usa a habilidade de cura equipada, com cooldown |
| `pocao` / `p` | Consome uma poção; `pocao ID` escolhe outro consumível |
| `equipar 1` | Ativa uma arma; aceita slots 1, 2 ou 3 |
| `fugir` | Recebe um ataque e retorna à sala anterior |
| `pegar 1 3` | Troca o objeto 1 do chão pela arma do slot 3 |
| `pegar 1 trocar` | Troca a cura equipada pelo objeto 1 do chão |
| `abrir` | Tenta abrir o baú da sala do objetivo |
| `salvar`, `carregar`, `novo`, `sair` / `q` | Controla a partida |
| `olhar`, `ajuda` / `?` | Consulta a sala ou os comandos |

**Primeiros passos:** vá para leste (`l`) e inspecione o Jardim para encontrar uma
cura. Volte à Entrada (`o`) e siga para o Estábulo (`s`) para enfrentar o Cavaleiro.
Consulte o inventário após a vitória: a lança coletada precisa ser equipada.

O combate avança somente com uma ação válida. Consultar o mapa/inventário, esperar,
digitar um comando inválido ou tentar usar uma cura indisponível não gasta turno.
Trocar de arma durante a batalha gasta turno. Equipamentos antigos que forem
substituídos ficam no chão; recompensas sem espaço também ficam disponíveis ali.

## O que está implementado

- Campanha com as 25 salas, quatro inimigos, descrições e sprites do projeto original.
- Exploração em grade, inspeção, coleta e combate determinístico por turnos.
- Três slots de armas, arma ativa, escudo, bônus mágico, cura com cooldown e poções.
- XP e níveis: vida máxima e dano aumentam conforme regras da campanha.
- Vitória ao obter a chave e abrir o tesouro; derrota, fuga e reinício.
- Save/load JSON, inclusive durante combate, com validação e gravação atômica.
- Catálogo JSON validado: referências, atributos, sprites e conectividade do mapa.
- Interface padrão sem dependências e adaptador opcional asciimatics.
- Testes automatizados, empacotamento Python e workflow para Linux/Windows.

Não estão implementados: renderização 2D, editor visual, missões genéricas,
árvore de habilidades, IA por estratégias, crítico/esquiva, peso, raridade e
multiplayer. A engine atual cobre RPGs de exploração em grade e combate por turnos.

## Organização

| Caminho | Responsabilidade |
| --- | --- |
| `src/castle_invasion/entities/` | Entidades e estado mutável de uma partida |
| `src/castle_invasion/core/` | Catálogo de definições recebido pelos sistemas |
| `src/castle_invasion/systems/` | Movimento, combate e casos de uso da partida |
| `src/castle_invasion/infrastructure/` | Leitura/validação de conteúdo e saves |
| `src/castle_invasion/ui/` | Apresentação, sessão e adaptadores de terminal |
| `src/castle_invasion/data/campaign.json` | Definições da campanha e sprites |
| `src/castle_invasion/bootstrap.py` | Composição das dependências e argumentos CLI |
| `tests/` | Regressões, campanha completa, CLI e dependências entre camadas |
| `scripts/` | Ferramentas de distribuição |
| `docs/` | Arquitetura, dados, migração e verificação |
| `main.py` | Entrada conveniente para executar a partir do código-fonte |

## Criar ou ajustar uma campanha

Edite `src/castle_invasion/data/campaign.json` ou copie-o para outro arquivo.
Armas, valores, inimigos, loot, posições, descrições, sprites, progressão e objetivo
são configuráveis sem modificar os sistemas Python.

```bash
python main.py --validate-data
python main.py --data minha-campanha.json --validate-data
python main.py --data minha-campanha.json --save saves/minha-campanha.json
```

Saves são vinculados ao conteúdo da campanha por hash. Alterar a campanha requer
uma partida nova ou restaurar o JSON original. Espaços e ordem de chaves do JSON
não alteram esse hash. Validação estrutural não garante balanceamento.

## Desenvolvimento e testes

```bash
python -m unittest discover -s tests -v
python -m pip install -e ".[dev,tui]"
python -m ruff check .
python -m ruff format --check .
python -m pip wheel --no-deps --wheel-dir dist .
```

No Windows, `test.bat` executa a suíte. O teste específico de asciimatics é ignorado
quando a dependência opcional não está instalada; os demais funcionam sem pacotes
externos. O GitHub Actions configura testes em Python 3.10, 3.12 e 3.13, em Linux e
Windows, e disponibiliza um executável de Windows após um push aprovado pelos testes.

### Gerar um .exe no Windows

```bash
python -m pip install -e ".[exe,tui]"
python scripts/build_exe.py
```

Saída: `dist/CastleInvasion.exe`. O programa padrão continua sendo de console.
PyInstaller deve rodar no sistema-alvo; uma execução em Linux não produz um .exe
Windows. Consulte [a verificação realizada](docs/verification.md) para distinguir
os testes executados localmente dos jobs apenas configurados.

## Documentação

- [Arquitetura e decisões](docs/architecture.md)
- [Contrato dos dados e regras](docs/data-guide.md)
- [Diagnóstico e migração do protótipo](docs/migration.md)
- [Verificação e limites](docs/verification.md)
- [Notas originais, mantidas como histórico](docs/initial-notes.txt)
- [Como contribuir](CONTRIBUTING.md)

Copyright © 2026 Marcos Mendonça. Consulte [LICENSE](LICENSE).
