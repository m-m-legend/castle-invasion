from core.input import get_input
from core.item_registry import get_heal, get_item, get_weapon
from systems.inventory_system import get_equipped_heal, get_inventory_summary, add_item_system, add_weapon_auto, substitute_heal, substitute_weapon, set_heal 

def show_inventory(screen, player):
    data = get_inventory_summary(player)

    screen.clear()
    
    screen.print_at("Inventário do jogador:", 2, 2)
    
    for slot, weapon in data["weapons"].items():
        weapon_name = get_weapon(weapon)['name'] if weapon else ''
        screen.print_at(f"Slot {slot}: {weapon_name}", 2, 2 + slot)

    heal_name = get_heal(data['heal'])['name'] if data['heal'] else ''
    screen.print_at(f"Item de Cura: {heal_name}", 2, 6)
    
    y = 7
    for item_id, qty in data["items"].items():
        name = get_item(item_id)["name"]
        screen.print_at(f"{name} x{qty}", 2, y)
        y += 1
    
    screen.refresh()
    
def add_weapon(screen, player, new_weapon: str):
    slot = add_weapon_auto(player, new_weapon)
    
    screen.clear()
    
    show_inventory(screen, player)
    
    if slot:
        screen.print_at(f"Arma '{get_weapon(new_weapon)['name']}' adicionada ao slot {slot}.", 2, 8)
        screen.refresh()
    else:
        screen.print_at("Nenhum slot disponível para nova arma.", 2, 9)
        screen.refresh()
        trade_weapon(screen, player, new_weapon)
    
def trade_weapon(screen, player, new_weapon: str):
    screen.print_at("Escolha um slot para substituir (1-3) ou aperte (Q) para sair: ", 2, 10)
    
    screen.refresh()
    
    while True:
        event = get_input(screen)
        if event in ('1', '2', '3'):
            slot = int(event)
            old_weapon = substitute_weapon(player, slot, new_weapon)
            screen.print_at(f"Substituído '{get_weapon(old_weapon)['name']}' por '{get_weapon(new_weapon)['name']}' no slot {slot}.", 2, 11)
            screen.refresh()
            break
        elif event in ('q', 'Q'):
            screen.print_at("Troca de arma cancelada.", 2, 11)
            screen.refresh()
            break
        else:
            screen.print_at("Entrada inválida. Pressione 1, 2 ou 3.", 2, 11)
            screen.refresh()
            
def set_heal_item(screen, player, new_heal: str):
    old_heal = get_equipped_heal(player)
    if old_heal is None:
        set_heal(player, new_heal)
        screen.print_at(f"Item de cura '{get_heal(new_heal)['name']}' adicionado ao inventário.", 2, 12)
        screen.refresh()
    else:
        screen.print_at("Já existe um item de cura.", 2, 12)
        trade_heal(screen, player, new_heal)
        
def trade_heal(screen, player, new_heal: str):
    screen.print_at("Deseja substituir o item de cura atual? (S/N): ", 2, 13)
    
    screen.refresh()
    
    while True:
        event = get_input(screen)
        if event in ('s', 'S'):
            old_heal = substitute_heal(player, new_heal)
            screen.print_at(f"Substituído '{get_heal(old_heal)['name']}' por '{get_heal(new_heal)['name']}'.", 2, 14)
            screen.refresh()
            break
        elif event in ('n', 'N'):
            screen.print_at("Troca de item de cura cancelada.", 2, 14)
            screen.refresh()
            break
        else:
            screen.print_at("Entrada inválida. Pressione S ou N.", 2, 14)
            screen.refresh()

def add_item(screen, player, new_item: str):
    add_item_system(player, new_item)
    screen.print_at(f"Novo item '{get_item(new_item)['name']}' adicionado.", 2, 14)
