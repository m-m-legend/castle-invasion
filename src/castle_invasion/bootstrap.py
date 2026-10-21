"""Composition root: conecta dados, casos de uso, persistência e interface."""

import argparse
import sys
from pathlib import Path

from castle_invasion.infrastructure.content_loader import ContentError, load_content
from castle_invasion.infrastructure.save_repository import SaveError, load_game
from castle_invasion.systems.game import Game
from castle_invasion.ui.session import Session


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Castle Invasion — mini engine RPG orientada a dados")
    parser.add_argument("--ui", choices=("terminal", "asciimatics"), default="terminal")
    parser.add_argument("--name", default="Aventureiro", help="nome do personagem")
    parser.add_argument("--data", type=Path, help="campanha JSON alternativa")
    parser.add_argument(
        "--save", type=Path, default=Path.home() / ".castle-invasion" / "save.json", help="arquivo de salvamento"
    )
    parser.add_argument("--load", action="store_true", help="carrega o save ao iniciar")
    parser.add_argument("--validate-data", action="store_true", help="valida a campanha e encerra")
    parser.add_argument("--no-art", action="store_true", help="oculta sprites para terminais pequenos")
    args = parser.parse_args(argv)
    # Evita falha de impressão em consoles Windows com codificação legada.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    try:
        content = load_content(args.data)
        if args.validate_data:
            print(
                f"Campanha válida: {content['title']} | {len(content['rooms'])} salas | {len(content['enemies'])} inimigos."
            )
            return 0
        name = "".join(char for char in args.name if char.isprintable())
        game = Game(content, load_game(args.save, content)) if args.load else Game.new(content, name)
        session = Session(game, args.save)
        if args.ui == "asciimatics":
            try:
                import asciimatics  # noqa: F401
            except ImportError:
                print('Interface opcional indisponível. Instale: python -m pip install -e ".[tui]"', file=sys.stderr)
                print("Ou execute python main.py para usar o terminal padrão.", file=sys.stderr)
                return 2
            if not sys.stdin.isatty() or not sys.stdout.isatty():
                print("A interface asciimatics exige um terminal interativo. Use --ui terminal.", file=sys.stderr)
                return 2
            from castle_invasion.ui.asciimatics_ui import run
        else:
            from castle_invasion.ui.terminal import run
        run(session, art=not args.no_art)
        return 0
    except (ContentError, SaveError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nSessão interrompida. Use carregar para retomar o último save.")
        return 130
