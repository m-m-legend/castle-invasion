from data.items_data import WEAPONS, HEALS, ITEMS

def get_weapon(weapon_id):
    return WEAPONS.get(weapon_id)

def get_heal(heal_id):
    return HEALS.get(heal_id)

def get_item(item_id):
    return ITEMS.get(item_id)
