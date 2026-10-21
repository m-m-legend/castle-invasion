"""UI opcional; comandos só são enviados ao pressionar Enter."""

from castle_invasion.ui.presenter import status_lines, wrap_lines
from castle_invasion.ui.session import Session


def run(session: Session, art=True) -> None:
    # Dependência externa fica exclusivamente na borda da aplicação.
    from asciimatics.event import KeyboardEvent
    from asciimatics.exceptions import ResizeScreenError
    from asciimatics.screen import Screen

    command = ""
    messages = ["Digite ajuda. Enter executa; PageUp/PageDown rolam o painel; Esc limpa a entrada."]
    scroll = 0

    def loop(screen):
        nonlocal command, messages, scroll
        previous_frame = None
        while session.running:
            if screen.has_resized():
                raise ResizeScreenError("resize")
            width = max(1, screen.width - 2)
            available = max(1, screen.height - 4)
            if screen.width < 40 or screen.height < 12:
                lines = ["Amplie o terminal para pelo menos 40x12.", "Comandos continuam ativos: sair / salvar."]
            else:
                lines = status_lines(session.game, width, art) + ["", "MENSAGENS"] + wrap_lines(messages, width)
            maximum = max(0, len(lines) - available)
            offset = max(0, maximum - scroll)
            prompt = "Confirmar (s/n)> " if session.pending else "> "
            frame = (width, available, tuple(lines), offset, prompt, command)
            if frame != previous_frame:
                screen.clear()
                for row, line in enumerate(lines[offset : offset + available]):
                    screen.print_at(line[:width], 1, row)
                footer = f"PageUp/Down: rolar | {offset + 1}-{min(offset + available, len(lines))}/{len(lines)}"
                screen.print_at(footer[:width], 1, max(0, screen.height - 3))
                screen.print_at((prompt + command)[-width:], 1, max(0, screen.height - 1))
                screen.refresh()
                previous_frame = frame
            screen.wait_for_input(0.1)
            event = screen.get_event()
            if not isinstance(event, KeyboardEvent):
                continue
            key = event.key_code
            if key in (10, 13):
                messages = session.submit(command)
                command, scroll = "", 0
            elif key in (8, 127, Screen.KEY_BACK):
                command = command[:-1]
            elif key == Screen.KEY_PAGE_UP:
                scroll = min(maximum, scroll + available)
            elif key == Screen.KEY_PAGE_DOWN:
                scroll = max(0, scroll - available)
            elif key == 27:
                command = ""
            elif key == 3:
                messages = session.submit("sair")
            elif 32 <= key <= 0x10FFFF and len(command) < 120:
                command += chr(key)

    while session.running:
        try:
            Screen.wrapper(loop, catch_interrupt=True)
        except ResizeScreenError:
            continue
        break
