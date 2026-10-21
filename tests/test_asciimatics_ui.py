"""A UI não avança turnos em frames ociosos ou eventos de teclas especiais."""
# ruff: noqa: E402

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from castle_invasion.infrastructure.content_loader import load_content
from castle_invasion.systems.game import Game
from castle_invasion.ui.session import Session


@unittest.skipUnless(importlib.util.find_spec("asciimatics"), "Dependência opcional não instalada")
class AsciimaticsTests(unittest.TestCase):
    def test_idle_frames_special_keys_and_confirmation_do_not_attack(self):
        from asciimatics.event import KeyboardEvent
        from asciimatics.screen import Screen
        from castle_invasion.ui.asciimatics_ui import run

        game = Game.new(load_content())
        game.command("s")
        with tempfile.TemporaryDirectory() as directory:
            session = Session(game, Path(directory) / "save.json")
            # Enter só ao final de atacar; setas, mouse/None e espera não gastam turnos.
            events = iter(
                [
                    None,
                    None,
                    KeyboardEvent(Screen.KEY_LEFT),
                    KeyboardEvent(Screen.KEY_UP),
                    *[KeyboardEvent(ord(c)) for c in "atacar\n"],
                    None,
                    *[KeyboardEvent(ord(c)) for c in "sair\ns\n"],
                ]
            )

            class FakeScreen:
                width, height = 100, 35

                def has_resized(self):
                    return False

                def clear(self):
                    pass

                def refresh(self):
                    pass

                def wait_for_input(self, timeout):
                    pass

                def print_at(self, text, x, y):
                    assert 0 <= y < self.height
                    assert len(text) + x <= self.width

                def get_event(self):
                    return next(events)

            with patch.object(Screen, "wrapper", side_effect=lambda loop, **kwargs: loop(FakeScreen())):
                run(session)
            self.assertEqual(game.state.player.health, 95)
            self.assertEqual(game.state.enemies["cavaleiro_indomado"].health, 40)
            self.assertFalse(session.running)
