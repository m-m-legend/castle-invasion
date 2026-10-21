"""Adaptador de comandos de UI, incluindo persistência e consultas gratuitas."""

from pathlib import Path

from castle_invasion.infrastructure.save_repository import SaveError, load_game, save_game
from castle_invasion.systems.game import Game
from castle_invasion.ui.presenter import HELP, inventory_lines, map_lines, status_lines


class Session:
    def __init__(self, game: Game, save_path: Path):
        self.game = game
        self.save_path = save_path
        self.running = True
        self.dirty = False
        self.pending: str | None = None

    def submit(self, command: str) -> list[str]:
        command = command.strip().lower()
        if self.pending:
            pending, self.pending = self.pending, None
            if command not in ("s", "sim"):
                return ["Operação cancelada."]
            return self._execute(pending)
        aliases = {"q": "sair", "i": "inventario", "inventário": "inventario", "m": "mapa", "?": "ajuda"}
        command = aliases.get(command, command)
        if command in ("sair", "novo", "carregar") and self.dirty:
            self.pending = command
            return [f"Há alterações não salvas. Deseja {command} mesmo assim? (s/n)"]
        return self._execute(command)

    def _execute(self, command: str) -> list[str]:
        if command == "sair":
            self.running = False
            return ["Até a próxima aventura!"]
        if command == "ajuda":
            return HELP.copy()
        if command == "inventario":
            return inventory_lines(self.game)
        if command == "mapa":
            return map_lines(self.game)
        if command == "olhar":
            return status_lines(self.game, art=False)
        if command == "novo":
            self.game = Game.new(self.game.content, self.game.state.player.name)
            self.dirty = False
            return ["Nova partida iniciada."]
        try:
            if command == "salvar":
                save_game(self.save_path, self.game.state, self.game.content)
                self.dirty = False
                return [f"Partida salva em {self.save_path}."]
            if command == "carregar":
                state = load_game(self.save_path, self.game.content)
                self.game = Game(self.game.content, state)
                self.dirty = False
                return ["Partida carregada."]
        except SaveError as exc:
            return [str(exc)]
        # Comparação por valor evita marcar consultas e comandos rejeitados como alterações.
        from copy import deepcopy

        before = deepcopy(self.game.state)
        messages = self.game.command(command)
        self.dirty = self.dirty or before != self.game.state
        return messages
