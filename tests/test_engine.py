"""Regressões das regras, dados, fronteiras de arquitetura e execução pública."""
# ruff: noqa: E402 -- permite executar os testes sem instalar o pacote src/.

import ast
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from castle_invasion.core.content import Content
from castle_invasion.entities.models import Loot
from castle_invasion.infrastructure.content_loader import ContentError, load_content, validate_content
from castle_invasion.infrastructure.save_repository import SaveError, encode_state, load_game, save_game
from castle_invasion.systems.combat_system import BattleController
from castle_invasion.systems.game import Game
from castle_invasion.systems.movement import get_new_position
from castle_invasion.ui.presenter import inventory_lines, map_lines, status_lines
from castle_invasion.ui.session import Session


def finish_battle(game):
    """Política de teste usa só comandos públicos, sem alterar vida ou equipamento."""
    for _ in range(100):
        if not game.state.battle or not game.state.player.alive:
            return
        p = game.state.player
        if p.health < 35 and p.inventory.items.get("pocao_cura"):
            game.command("pocao")
        elif p.health < 70 and p.inventory.heal and game.state.battle.cooldown == 0:
            game.command("curar")
        else:
            game.command("atacar")
    raise AssertionError("Combate não terminou em 100 turnos.")


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.content = load_content()
        self.game = Game.new(self.content, "Marcos")

    def battle(self):
        self.game.command("s")
        return BattleController(
            self.game.state.player, self.game.state.enemies["cavaleiro_indomado"], self.game.state.battle, self.content
        )

    def test_original_world_and_assets_present(self):
        self.assertEqual(len(self.content["rooms"]), 25)
        self.assertEqual(len(self.content["enemies"]), 4)
        self.assertTrue(self.content["sprites"]["player"])

    def test_movement_edges_invalid_direction_and_empty_cell(self):
        self.game.command("n")
        self.game.command("o")
        self.assertEqual(self.game.state.player.position, (0, 0))
        self.assertEqual(get_new_position((0, 0), "leste", [["A", None], ["B"]]), (0, 0))
        self.assertEqual(get_new_position((0, 1), "sul", [["A", "C"], ["B"]]), (0, 1))
        self.assertEqual(get_new_position((0, 0), "x", [["A"]]), (0, 0))

    def test_valid_movement_updates_room_and_previous_position(self):
        self.game.command("l")
        self.assertEqual(self.game.current_room, "Jardim")
        self.assertEqual(self.game.state.player.last_position, (0, 0))

    def test_normal_attack_takes_full_enemy_damage(self):
        self.battle()
        self.game.command("atacar")
        self.assertEqual(self.game.state.player.health, 95)
        self.assertEqual(self.game.state.enemies["cavaleiro_indomado"].health, 40)

    def test_empty_invalid_and_movement_commands_do_not_advance_battle(self):
        self.battle()
        before = copy.deepcopy(self.game.state)
        for command in ("", "???", "n", "equipar", "equipar -1", "equipar 3", "atacar extra", "pegar 1"):
            self.game.command(command)
        self.assertEqual(before, self.game.state)

    def test_fatal_hit_has_no_retaliation_and_loot_once(self):
        self.battle()
        for _ in range(5):
            self.game.command("atacar")
        self.assertEqual(self.game.state.player.health, 80)
        self.assertIsNone(self.game.state.battle)
        self.assertEqual(self.game.state.player.xp, 25)
        self.assertEqual(self.game.state.player.inventory.weapons.count("lanca"), 1)
        self.game.command("n")
        self.game.command("s")
        self.assertIsNone(self.game.state.battle)
        self.assertEqual(self.game.state.player.xp, 25)

    def test_active_weapon_changes_and_persists(self):
        self.game.command("equipar 2")
        self.assertEqual(self.game.state.player.inventory.equipped_weapon, "escudo")
        self.battle()
        self.game.command("atacar")
        self.assertEqual(self.game.state.enemies["cavaleiro_indomado"].health, 45)

    def test_block_reduces_once_and_resets_next_turn(self):
        self.game.command("equipar 2")
        self.battle()
        self.game.command("defender")
        self.assertEqual(self.game.state.player.health, 96.5)
        self.game.command("atacar")
        self.assertEqual(self.game.state.player.health, 91.5)

    def test_equipping_in_combat_costs_one_turn(self):
        self.battle()
        self.game.command("equipar 2")
        self.assertEqual(self.game.state.player.health, 95)
        self.assertEqual(self.game.state.player.inventory.equipped_weapon, "escudo")

    def test_heal_uses_max_hp_and_waits_two_subsequent_turns(self):
        self.game.command("l")
        self.game.command("inspecionar")
        self.game.command("l")
        self.game.command("atacar")
        self.game.command("atacar")
        self.game.command("atacar")
        self.assertEqual(self.game.state.player.health, 76)
        self.game.command("curar")
        self.assertAlmostEqual(self.game.state.player.health, 95.2)
        self.assertEqual(self.game.state.battle.cooldown, 2)
        before = copy.deepcopy(self.game.state)
        self.game.command("curar")
        self.assertEqual(before, self.game.state)
        self.game.command("defender")
        self.assertEqual(self.game.state.battle.cooldown, 1)
        self.game.command("defender")
        self.assertEqual(self.game.state.battle.cooldown, 0)

    def test_full_hp_and_missing_heal_do_not_spend_turn(self):
        self.battle()
        before = copy.deepcopy(self.game.state)
        self.game.command("curar")
        self.game.command("pocao")
        self.assertEqual(before, self.game.state)

    def test_potion_consumes_once_and_enemy_retaliates(self):
        self.battle()
        self.game.command("atacar")
        self.game.command("pocao")
        self.assertEqual(self.game.state.player.health, 95)
        self.assertEqual(self.game.state.player.inventory.items["pocao_cura"], 1)

    def test_inspect_is_idempotent(self):
        self.game.command("l")
        self.game.command("inspecionar")
        before = copy.deepcopy(self.game.state)
        self.game.command("inspecionar")
        self.assertEqual(before, self.game.state)
        self.assertEqual(self.game.state.player.inventory.heal, "semente_regeneradora")

    def test_full_weapon_slots_leave_loot_on_ground_and_trade_preserves_old(self):
        self.game.state.player.inventory.weapons[2] = "arco_flecha"
        self.battle()
        finish_battle(self.game)
        ground = self.game.state.rooms["Estábulo"].ground
        self.assertEqual(ground, [Loot("weapon", "lanca")])
        self.game.command("pegar 1")
        self.assertEqual(ground, [Loot("weapon", "lanca")])
        self.game.command("pegar 1 3")
        self.assertEqual(self.game.state.player.inventory.weapons[2], "lanca")
        self.assertEqual(ground, [Loot("weapon", "arco_flecha")])

    def test_heal_trade_preserves_old_on_ground(self):
        self.game.command("l")
        self.game.command("inspecionar")
        ground = self.game.state.rooms["Jardim"].ground
        ground.append(Loot("heal", "biblia"))
        self.game.command("pegar 1")
        self.assertEqual(self.game.state.player.inventory.heal, "semente_regeneradora")
        self.game.command("pegar 1 trocar")
        self.assertEqual(self.game.state.player.inventory.heal, "biblia")
        self.assertEqual(ground, [Loot("heal", "semente_regeneradora")])

    def test_flee_preserves_enemy_hp_and_returns_to_previous_room(self):
        self.battle()
        self.game.command("atacar")
        self.game.command("fugir")
        self.assertEqual(self.game.current_room, "Entrada")
        self.assertEqual(self.game.state.player.health, 90)
        self.game.command("s")
        self.assertEqual(self.game.state.enemies["cavaleiro_indomado"].health, 40)

    def test_death_freezes_gameplay_and_dead_player_cannot_heal(self):
        self.battle()
        for _ in range(30):
            self.game.command("defender")
        self.assertEqual(self.game.state.player.health, 0)
        before = copy.deepcopy(self.game.state)
        for action in ("pocao", "atacar", "fugir", "inspecionar"):
            self.game.command(action)
        self.assertEqual(before, self.game.state)

    def test_two_enemies_in_one_room_are_resolved_sequentially(self):
        data = copy.deepcopy(self.content.data)
        data["enemies"]["esqueleto_errante"]["placement"] = "Estábulo"
        game = Game.new(Content(data, "test"))
        game.command("s")
        for _ in range(5):
            game.command("atacar")
        self.assertEqual(game.state.battle.enemy_id, "esqueleto_errante")
        finish_battle(game)
        self.assertEqual(game.state.player.xp, 45)

    def test_magic_boost_and_level_bonus(self):
        self.game.state.player.inventory.weapons[0] = "cajado_mago"
        self.game.state.player.level = 2
        self.battle()
        self.game.command("atacar")
        self.assertEqual(self.game.state.enemies["cavaleiro_indomado"].health, 30)

    def test_complete_campaign_all_four_enemies_without_state_cheats(self):
        # Jardim -> Cavaleiro -> Esqueleto -> Serpente -> Mago -> Tesouro.
        for command in ("l", "inspecionar", "o", "s"):
            self.game.command(command)
        finish_battle(self.game)
        self.game.command("equipar 3")
        self.game.command("s")
        finish_battle(self.game)
        for command in ("l", "n", "n", "l"):
            self.game.command(command)
        finish_battle(self.game)
        for command in ("l", "l", "s", "inspecionar", "s", "s"):
            self.game.command(command)
        finish_battle(self.game)
        self.game.command("s")
        self.game.command("abrir")
        self.assertTrue(self.game.state.won)
        self.assertTrue(self.game.state.player.alive)
        self.assertEqual(self.game.state.player.xp, 125)
        self.assertEqual(self.game.state.player.level, 3)
        self.assertEqual(self.game.state.player.max_health, 120)
        self.assertTrue(all(enemy.rewarded for enemy in self.game.state.enemies.values()))
        before = copy.deepcopy(self.game.state)
        self.game.command("n")
        self.assertEqual(before, self.game.state)

    def test_treasure_requires_key(self):
        for command in ("l", "s", "s", "l", "s", "l", "s", "l", "abrir"):
            self.game.command(command)
        self.assertEqual(self.game.current_room, "Tesouro")
        self.assertFalse(self.game.state.won)

    def test_views_do_not_mutate_state(self):
        self.battle()
        before = copy.deepcopy(self.game.state)
        for _ in range(3):
            status_lines(self.game)
            inventory_lines(self.game)
            map_lines(self.game)
        self.assertEqual(before, self.game.state)


class SaveAndSessionTests(unittest.TestCase):
    def setUp(self):
        self.content = load_content()
        self.game = Game.new(self.content)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "save.json"

    def test_round_trip_mid_battle_preserves_every_field(self):
        for command in ("l", "inspecionar", "l", "atacar", "curar"):
            self.game.command(command)
        save_game(self.path, self.game.state, self.content)
        loaded = load_game(self.path, self.content)
        self.assertEqual(loaded, self.game.state)
        resumed = Game(self.content, loaded)
        self.assertEqual(resumed.command("atacar"), self.game.command("atacar"))
        self.assertEqual(resumed.state, self.game.state)

    def test_save_after_loot_does_not_duplicate_rewards(self):
        self.game.command("s")
        finish_battle(self.game)
        save_game(self.path, self.game.state, self.content)
        resumed = Game(self.content, load_game(self.path, self.content))
        resumed.command("n")
        resumed.command("s")
        self.assertEqual(resumed.state.player.xp, 25)
        self.assertEqual(resumed.state.player.inventory.weapons.count("lanca"), 1)

    def test_failed_replace_keeps_existing_save_and_removes_temp(self):
        save_game(self.path, self.game.state, self.content)
        original = self.path.read_bytes()
        self.game.command("l")
        with patch("castle_invasion.infrastructure.save_repository.os.replace", side_effect=OSError("test")):
            with self.assertRaises(SaveError):
                save_game(self.path, self.game.state, self.content)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.glob("*.tmp")), [])

    def test_invalid_saves_are_rejected(self):
        original = json.loads(json.dumps(encode_state(self.game.state, self.content)))
        mutations = [
            lambda d: d.update(save_version=9),
            lambda d: d.update(campaign_hash="different"),
            lambda d: d["player"].update(position=[-1, 0]),
            lambda d: d["player"].update(health=float("nan")),
            lambda d: d["player"].update(health=101),
            lambda d: d["player"].update(level=True),
            lambda d: d["player"]["inventory"].update(active_slot=4),
            lambda d: d["player"]["inventory"].update(weapons=["missing", None, None]),
            lambda d: d["player"]["inventory"].update(items={"pocao_cura": -1}),
            lambda d: d.update(won=True),
            lambda d: d.update(visited=[]),
            lambda d: d["enemies"]["mago"].update(rewarded=True),
            lambda d: d.update(battle={"enemy_id": "mago", "cooldown": 0}),
            lambda d: d.update(rooms={}),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                candidate = copy.deepcopy(original)
                mutation(candidate)
                self.path.write_text(json.dumps(candidate), encoding="utf-8")
                with self.assertRaises(SaveError):
                    load_game(self.path, self.content)

    def test_corrupt_save_does_not_replace_running_game(self):
        self.path.write_text("{broken", encoding="utf-8")
        session = Session(self.game, self.path)
        before = copy.deepcopy(self.game.state)
        self.assertIn("Não foi possível", session.submit("carregar")[0])
        self.assertEqual(session.game.state, before)

    def test_queries_do_not_advance_turns_or_mark_dirty(self):
        self.game.command("s")
        session = Session(self.game, self.path)
        before = copy.deepcopy(self.game.state)
        for command in ("mapa", "inventario", "ajuda", "olhar", "", "invalido"):
            session.submit(command)
        self.assertEqual(self.game.state, before)
        self.assertFalse(session.dirty)

    def test_restart_requires_confirmation_after_changes(self):
        session = Session(self.game, self.path)
        session.submit("l")
        session.submit("novo")
        self.assertEqual(session.pending, "novo")
        session.submit("n")
        self.assertEqual(session.game.current_room, "Jardim")
        session.submit("novo")
        session.submit("s")
        self.assertEqual(session.game.current_room, "Entrada")

    def test_save_load_session_and_exit(self):
        session = Session(self.game, self.path)
        session.submit("l")
        session.submit("salvar")
        self.assertFalse(session.dirty)
        session.submit("o")
        session.submit("carregar")
        session.submit("s")
        self.assertEqual(session.game.current_room, "Jardim")
        session.submit("q")
        self.assertFalse(session.running)


class ContentAndPackagingTests(unittest.TestCase):
    def test_validation_rejects_broken_references_and_rules(self):
        original = load_content().data
        mutations = [
            lambda d: d["enemies"]["mago"].update(placement="inexistente"),
            lambda d: d["enemies"]["mago"].update(sprite_key="inexistente"),
            lambda d: d["enemies"]["mago"]["loot"].append({"kind": "item", "id": "inexistente"}),
            lambda d: d["weapons"]["escudo"].update(block=1.5),
            lambda d: d["rules"].update(xp_per_level=0),
            lambda d: d["heals"]["biblia"].update(cooldown=-1),
            lambda d: d["objective"].update(key="pocao_cura"),
            lambda d: d["player"].update(weapons=["espada"] * 4),
            lambda d: d["enemies"]["mago"].update(health=float("inf")),
            lambda d: d["map"][0].__setitem__(0, "Jardim"),
            lambda d: d["enemies"]["mago"].update(loot=[]),
            lambda d: d["rooms"]["Entrada"].update(typo=True),
        ]
        for mutation in mutations:
            candidate = copy.deepcopy(original)
            mutation(candidate)
            with self.subTest(mutation=mutation), self.assertRaises(ContentError):
                validate_content(candidate)

    def test_disconnected_map_rejected(self):
        data = copy.deepcopy(load_content().data)
        data["map"].insert(1, [None] * 5)
        with self.assertRaises(ContentError):
            validate_content(data)

    def test_data_can_change_damage_without_code_change(self):
        data = copy.deepcopy(load_content().data)
        data["weapons"]["espada"]["damage"] = 50
        validate_content(data)
        game = Game.new(Content(data, "test"))
        game.command("s")
        game.command("atacar")
        self.assertIsNone(game.state.battle)
        self.assertEqual(game.state.player.health, 100)

    def test_separate_games_do_not_share_runtime_state(self):
        content = load_content()
        a, b = Game.new(content), Game.new(content)
        a.command("s")
        a.command("atacar")
        self.assertEqual(b.state.enemies["cavaleiro_indomado"].health, 50)
        self.assertEqual(content["enemies"]["cavaleiro_indomado"]["health"], 50)

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "campaign.json"
            path.write_text('{"title":"a","title":"b"}', encoding="utf-8")
            with self.assertRaises(ContentError):
                load_content(path)

    def test_dependency_direction(self):
        # Regra executável: domínio não importa sistemas, arquivos, dados ou UI.
        allowed = {"entities": {"entities"}, "core": {"core"}, "systems": {"core", "entities", "systems"}}
        for layer, dependencies in allowed.items():
            for path in (ROOT / "src" / "castle_invasion" / layer).glob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    modules = (
                        [node.module or ""]
                        if isinstance(node, ast.ImportFrom)
                        else [n.name for n in node.names]
                        if isinstance(node, ast.Import)
                        else []
                    )
                    for module in modules:
                        if module.startswith("castle_invasion."):
                            self.assertIn(module.split(".")[1], dependencies, str(path))
                        else:
                            self.assertIn(module.split(".")[0], sys.stdlib_module_names, str(path))

    def test_cli_from_other_working_directory_and_eof(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, str(ROOT / "main.py"), "--no-art"],
                input="l\ninspecionar\ninventario\n",
                text=True,
                encoding="utf-8",
                capture_output=True,
                cwd=directory,
                timeout=10,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Semente Regeneradora", result.stdout)
            self.assertIn("Sessão encerrada", result.stdout)
            self.assertNotIn("Traceback", result.stderr)

    def test_cli_validate_and_bad_data_exit_codes(self):
        for args, expected in ((["--validate-data"], 0), (["--data", "does-not-exist.json"], 2)):
            result = subprocess.run([sys.executable, str(ROOT / "main.py"), *args], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, expected)


if __name__ == "__main__":
    unittest.main()
