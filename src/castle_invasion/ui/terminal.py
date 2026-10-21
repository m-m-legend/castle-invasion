"""Terminal portátil da biblioteca padrão: funciona também com entrada redirecionada."""

import shutil

from castle_invasion.ui.presenter import status_lines
from castle_invasion.ui.session import Session


def run(session: Session, art=True) -> None:
    print("\n".join(session.game.content["sprites"]["castle"]) if art else session.game.content["title"])
    print("Objetivo: encontre a chave e abra o tesouro. Digite ajuda para os comandos.")
    while session.running:
        width = max(30, shutil.get_terminal_size((88, 30)).columns - 2)
        print("\n" + "─" * min(width, 88))
        print("\n".join(status_lines(session.game, width, art=art)))
        try:
            command = input("Confirmar (s/n)> " if session.pending else "> ")
        except (EOFError, KeyboardInterrupt):
            print("\nSessão encerrada. Alterações não salvas foram descartadas.")
            break
        print("\n".join(session.submit(command)))
