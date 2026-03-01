from core.input import get_input
from systems.combat_system import BattleController
from systems.battle_view import BattleView, build_battle_view
from ui.inventory_ui import handle_loot

def battle(screen, player, enemy):
    controller = BattleController(player, enemy)

    while True:
        view = build_battle_view(controller)
        render_battle(screen, view)

        action = get_input(screen)

        if action == '1':
            controller.player_attack()
        elif action == '2':
            controller.player_defend()
        elif action == '3':
            controller.player_use_heal()
        elif action == '4':
            screen.print_at("Escolha o slot da arma para equipar (1-3): ", 2, 20)
            screen.refresh()
            
            slot_input = get_input(screen)

            if slot_input.isdigit():
                controller.player_change_weapon(int(slot_input))
            else:
                controller.messages.append("Entrada inválida.")
        if controller.enemy_is_dead():
            loot_events = controller.consume_loot()
            handle_loot(screen, player, loot_events)
            return player.health

        controller.enemy_turn()
        if controller.player_is_dead():
            return 0
        
def render_battle(screen, view: BattleView):
    
    screen.clear()
        
    screen.print_at(f"Vida do Jogador ({view.player_name}): {view.player_hp:.2f}", 2, 8)
        
    screen.print_at(f"Vida do Inimigo ({view.enemy_name}): {view.enemy_hp:.2f}", 2, 9)
        
        
    for i in range (0, len(view.enemy_sprite)):
            screen.print_at(view.enemy_sprite[i], 62, i)
            
    for i in range(0,len(view.player_sprite)):
        screen.print_at(view.player_sprite[i], 36, 9+i)
            
    screen.print_at("1. Atacar", 2, 11)
    screen.print_at("2. Defender", 2, 12)
    if view.heal_name:
        if view.heal_ready:
            screen.print_at(f"3. Usar item de cura ({view.heal_name})", 2, 13)
            screen.print_at("(Pronto para uso)", 40, 13)
        else:
            screen.print_at(f"3. Usar item de cura ({view.heal_name})", 2, 13)
            screen.print_at(f"(Cooldown: {view.heal_cooldown} turno(s))", 40, 13)
    screen.print_at("4. Trocar arma equipada", 2, 14)
    y = 19
    for msg in view.messages:
        screen.print_at(msg, 2, y)
        y += 1
    screen.print_at('Escolha:',2,29)
    
    screen.refresh()
    
    