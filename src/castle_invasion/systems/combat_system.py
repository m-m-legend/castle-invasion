"""Um comando válido corresponde a um turno. Consultar estado não o altera."""

from castle_invasion.core.content import Content
from castle_invasion.entities.models import BattleState, Enemy, Player


class BattleController:
    def __init__(self, player: Player, enemy: Enemy, battle: BattleState, content: Content):
        self.player = player
        self.enemy = enemy
        self.battle = battle
        self.content = content

    def take_turn(self, action: str, argument: str = "") -> tuple[bool, list[str]]:
        if not self.player.alive or not self.enemy.alive:
            return False, ["Este combate já terminou."]
        inventory = self.player.inventory
        weapon = self.content["weapons"].get(inventory.equipped_weapon, {})
        messages: list[str] = []
        incoming_multiplier = 1.0
        used_heal = False

        if action == "atacar":
            damage = weapon.get("damage", self.content["rules"]["unarmed_damage"])
            damage *= weapon.get("boost", 1.0)
            damage += (self.player.level - 1) * self.content["rules"]["damage_per_level"]
            self.enemy.take_damage(damage)
            messages.append(f"Você causou {damage:g} de dano.")
        elif action == "defender":
            block = weapon.get("block", self.content["rules"]["base_block"])
            incoming_multiplier = 1 - block
            messages.append(f"Você bloqueia {block:.0%} do próximo ataque.")
        elif action == "curar":
            if inventory.heal is None:
                return False, ["Nenhuma habilidade de cura equipada. Inspecione o Jardim ou a Capela."]
            if self.battle.cooldown > 0:
                return False, [f"Cura indisponível por {self.battle.cooldown} turno(s)."]
            if self.player.health >= self.player.max_health:
                return False, ["Sua vida já está cheia."]
            heal = self.content["heals"][inventory.heal]
            amount = self.player.heal(self.player.max_health * heal["heal_fraction"])
            self.battle.cooldown = heal["cooldown"]
            incoming_multiplier = heal["enemy_damage_multiplier"]
            used_heal = True
            messages.extend([heal["message"], f"Você recuperou {amount:g} de vida."])
        elif action == "pocao":
            ok, messages = use_consumable(self.player, self.content, argument)
            if not ok:
                return False, messages
        elif action == "equipar":
            if not argument.isdigit() or not inventory.equip(int(argument)):
                return False, ["Escolha um slot ocupado: equipar 1, 2 ou 3."]
            messages.append(f"Arma equipada: {self.content['weapons'][inventory.equipped_weapon]['name']}.")
        else:
            return False, ["Ação inválida. Use atacar, defender, curar, pocao, equipar N ou fugir."]

        # Um golpe fatal impede a retaliação; ações rejeitadas nunca chegam aqui.
        if self.enemy.alive:
            damage = self.content["enemies"][self.enemy.id]["damage"] * incoming_multiplier
            self.player.take_damage(damage)
            messages.append(f"O inimigo causou {damage:g} de dano.")
        if not used_heal and self.battle.cooldown > 0:
            self.battle.cooldown -= 1
        return True, messages


def use_consumable(player: Player, content: Content, item_id: str = "") -> tuple[bool, list[str]]:
    if not item_id:
        item_id = next((key for key in player.inventory.items if content["items"][key]["type"] == "consumable"), "")
    item = content["items"].get(item_id)
    if not item or item["type"] != "consumable" or not player.inventory.items.get(item_id):
        return False, ["Você não possui esse consumível."]
    if player.health >= player.max_health:
        return False, ["Sua vida já está cheia; a poção foi preservada."]
    player.inventory.consume(item_id)
    amount = player.heal(item["health_restore"])
    return True, [f"{item['name']}: recuperou {amount:g} de vida."]
