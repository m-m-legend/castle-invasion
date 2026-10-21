# Contribuindo

Use Python 3.10 ou superior. A interface padrão e a maior parte dos testes não
exigem bibliotecas externas. Para o ambiente de desenvolvimento completo:

```bash
python -m venv .venv
python -m pip install -e ".[dev,tui]"
```

Ative o ambiente virtual antes de instalar dependências; consulte o README para
os comandos de cada sistema. Trabalhe em uma branch e mantenha a alteração focada.

Antes de propor mudanças:

```bash
python main.py --validate-data
python -m unittest discover -s tests -v
python -m ruff check .
python -m ruff format --check .
```

- Não importe UI, infraestrutura ou conteúdo concreto nas entidades/sistemas.
- Definições do jogo ficam no JSON; estado mutável fica em `GameState`.
- Novas regras de combate precisam de testes de turnos e condições de término.
- Nunca conceda recompensas ou altere estado durante consultas/renderização.
- Novos recursos devem incluir instruções de uso e revisão do contrato de dados.
- Não versione saves, ambientes virtuais, executáveis ou diretórios de build.
- Preserve LICENSE, autoria e o conteúdo original salvo quando a mudança de design for intencional.

Ao descrever um PR, explique o problema, o comportamento resultante, como foi
testado e eventuais mudanças de compatibilidade dos dados ou saves.
