# systems/battle_view.py
from dataclasses import dataclass
from core.item_registry import get_heal
from core.sprite_registry import get_enemy_sprite, get_player_sprite
from systems.inventory_system import get_equipped_heal
from systems.combat_system import BattleController

@dataclass(frozen=True)
class BattleView:
    player_name: str
    player_hp: float
    player_sprite: list[str]
    enemy_name: str
    enemy_hp: float
    enemy_sprite: list[str]
    heal_name: str | None
    heal_ready: bool
    heal_cooldown: int
    messages: list[str]
    
def build_battle_view(controller: BattleController) -> BattleView:
    heal_id = get_equipped_heal(controller.player)
    heal = get_heal(heal_id) if heal_id else None

    # Buffer de mensagens
    messages = controller.consume_messages()
    
    return BattleView(
        player_name=controller.player.name,
        player_hp=controller.player.health,
        player_sprite=get_player_sprite(),
        enemy_name=controller.enemy.name,
        enemy_hp=controller.enemy.health,
        enemy_sprite=get_enemy_sprite(controller.enemy.sprite_key),
        heal_name=heal["name"] if heal else None,
        heal_ready=controller.cooldown == 0 if heal else False,
        heal_cooldown=controller.cooldown,
        messages=messages
    )