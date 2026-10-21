# Verificação da entrega 0.2.0

Base: `91bcc36`. Ambiente local: Linux, Python 3.12.14, asciimatics 1.15.0,
Ruff 0.17.1. Os resultados abaixo se referem à entrega, não a uma execução da CI
no GitHub.

| Verificação executada | Resultado |
| --- | --- |
| `python main.py --validate-data` | 25 salas e quatro inimigos válidos |
| `python -m unittest discover -s tests -v` | 39 testes passaram, incluindo o adaptador opcional |
| `python -m ruff check .` | Sem erros |
| `python -m ruff format --check .` | Formatação consistente |
| Campanha completa pela API pública | Quatro inimigos derrotados, 125 XP, nível 3 e tesouro aberto |
| Campanha completa pelo processo `main.py` | 42 comandos, vitória e 67,2/120 HP finais |
| Save e reload dessa vitória pela CLI | Vitória preservada |
| Sessão asciimatics em terminal real | Movimento, ataque, salvar e sair; HP 95 e Cavaleiro com 40 HP |
| Geração de wheel Python | Build concluído |
| Instalação do wheel em venv sem dependências | Campanha encontrada fora do diretório do projeto |
| CLI executada a partir de outro diretório | Funciona; EOF encerra sem traceback |
| Dados comparados com o protótipo | Mapa, descrições, sprites, armas e itens preservados |

## Regressões cobertas

Combate normal, defesa de um turno, golpe fatal sem retaliação, troca de arma ativa,
cura percentual, cooldown, poção consumida uma vez, ações inválidas sem turno,
fuga com HP do inimigo preservado, derrota, XP, múltiplos inimigos em uma sala,
inspeção idempotente, loot com slots cheios e troca sem perder equipamento.

Persistência cobre round-trip no meio da batalha, ausência de loot duplicado,
save inválido, hash incompatível, escrita atômica com falha simulada e preservação
do estado atual quando carregar falha. Consultas e frames ociosos não alteram a
partida. Um teste fiscaliza o sentido das dependências arquiteturais.

## Limites da verificação

- O terminal real testado foi Linux. O Windows ainda precisa executar o workflow
  ou ser testado pelo autor; não foi produzido um .exe Windows neste ambiente.
- A matriz Python 3.10/3.12/3.13 e Linux/Windows está configurada, mas não foi
  executada remotamente nesta entrega.
- O balanceamento tem uma rota concluível comprovada, não uma garantia de vitória
  para todas as escolhas. É possível morrer, gastar recursos ou usar equipamento ruim.
- Nenhuma nova campanha externa foi balanceada. A validação de conteúdo verifica
  estrutura, referências e conectividade espacial, não solvabilidade de combate.
- Não há teste de interface gráfica 2D: essa interface não faz parte da versão.
- O motor atual não fornece sistema genérico de missões, inventário por peso ou IA
  configurável além dos atributos de cada inimigo.

Para reproduzir o caminho completo, consulte
`test_complete_campaign_all_four_enemies_without_state_cheats` em `tests/test_engine.py`.
