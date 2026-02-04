from core.item_registry import get_heal, get_weapon
from core.sprite_registry import get_enemy_sprite, get_player_sprite
from core.input import get_input
from entities.player import Player
from entities.enemy import Enemy
from systems.inventory_system import get_equipped_weapon, get_equipped_heal, has_heal, equip_weapon
from systems.combat_system import use_heal, enemy_attack_player, player_attack_enemy, player_is_dead, enemy_is_dead
from time import sleep
from ui.inventory_ui import add_weapon, add_item

def battle(screen, player : Player, enemy: Enemy):

    # Weapon ID
    equipped_weapon_id = get_equipped_weapon(player)
    
    # Heal ID
    heal_id = get_equipped_heal(player)
    
    # Cooldown for heal item
    cooldown = get_heal(heal_id)['cooldown'] if heal_id else 0
    
    # Enemy name
    enemy_name = enemy.name
    
    # Player name
    player_name = player.name
    
    # Heal name
    heal_name = get_heal(heal_id)['name'] if heal_id else 'Nenhum'
    
    # Base damage modifier
    modifier = 1.0
    
    while True:
        # TURNO JOGADOR
        screen.clear()
        
        screen.print_at(f"Vida do Jogador ({player_name}): {player.health:.2f}", 2, 8)
        
        screen.print_at(f"Vida do Inimigo ({enemy_name}): {enemy.health:.2f}", 2, 9)
        
        enemy_sprite = get_enemy_sprite(enemy.sprite_key)
        
        for i in range (0, len(enemy_sprite)):
            screen.print_at(enemy_sprite[i], 62, i)
            
        
        for i in range(0,len(get_player_sprite())):
            screen.print_at(get_player_sprite()[i], 36, 9+i)
            
        screen.print_at("1. Atacar", 2, 11)
        screen.print_at("2. Defender", 2, 12)
        if has_heal(player):
            if cooldown <= 0:
                screen.print_at(f"3. Usar item de cura ({heal_name})", 2, 13)
                screen.print_at("(Pronto para uso)", 40, 13)
            else:
                screen.print_at(f"3. Usar item de cura ({heal_name})", 2, 13)
                screen.print_at(f"(Cooldown: {cooldown} turno(s))", 40, 13)
        screen.print_at("4. Trocar arma equipada", 2, 14)
        screen.print_at('Escolha:',2,29)
        
        screen.refresh()
        
        action = get_input(screen)
        
        if action == '1':
            player_attack_enemy(player, enemy)
        elif action == '2':
            if equipped_weapon_id:
                weapon = get_weapon(equipped_weapon_id)
                block = weapon.get("block")
                if block:
                    modifier = block
                else:
                    screen.print_at("Arma equipada não pode defender!", 2, 20)
                    screen.refresh()
                    continue
            else:
                screen.print_at("Nenhuma arma equipada!", 2, 20)
                screen.refresh()
                continue

        elif action == '3' and heal_id and cooldown <= 0:
            use_heal(player, heal_id)
            modifier = get_heal(heal_id)['enemy_damage_multiplier']
            cooldown = get_heal(heal_id)['cooldown']
            message = get_heal(heal_id)['message']
            if message:
                screen.print_at(message, 2, 20)
                screen.refresh()
                sleep(2)
        elif action == '4':
            screen.print_at("Escolha o slot da arma para equipar (1-3): ", 2, 20)
            slot = get_input(screen)
            if slot in ('1', '2', '3'):
                equipped_weapon_id = equip_weapon(player, int(slot))
                screen.print_at(f"Arma '{get_weapon(equipped_weapon_id)['name']}' equipada do slot {slot}.", 2, 21)
                continue
            else:
                screen.print_at("Entrada inválida. Voltando ao menu de batalha.", 2, 21)
                continue
        else:
            continue

        if enemy_is_dead(enemy):
            if enemy_name == "Cavaleiro Indomado":
                screen.clear()
                add_weapon(screen, player, 'lanca')
            elif enemy_name == 'Mago':
                screen.clear()
                add_weapon(screen, player, 'cajado_mago')
                add_item(screen, player, 'chave_quadrada')
                screen.clear()
                screen.print_at('Ele te entrega uma chave quadrada.',2,2)
                screen.refresh()
                sleep(2)
                screen.clear()

            return player.health  # JOGADOR VENCEU

        # TURNO INIMIGO
        enemy_attack_player(enemy, player, modifier)

        if player_is_dead(player):
            return 0  # JOGADOR DERROTADO

        if cooldown > 0:
            cooldown -= 1
        
        sleep(0.5)
        # Atualiza a tela após o turno do inimigo
        screen.clear()
        
        screen.print_at(f"Vida do Jogador ({player_name}): {player.health:.2f}", 2, 2)
        screen.print_at(f"Vida do Inimigo ({enemy_name}): {enemy.health:.2f}", 2, 3)
        screen.print_at("Aguardando sua próxima ação...", 2, 5)
        
        screen.refresh()