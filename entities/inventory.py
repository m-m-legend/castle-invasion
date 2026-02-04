class Inventory:
    def __init__(self):
        self.items = {}
        self.heals = {"Heal": None}
        self.weapons = {1: None, 2: None, 3: None}
        
    def add_item(self, item_name):
        if item_name in self.items:
            self.items[item_name] += 1
        else:
            self.items[item_name] = 1
    def add_weapon_auto(self, weapon_name):
        empty_slots = [s for s, w in self.weapons.items() if w is None]
        if empty_slots:
            slot = empty_slots[0]
            self.weapons[slot] = weapon_name
            return slot
        return None
    def set_heal(self, heal_name):
        self.heals["Heal"] = heal_name

    def get_items(self):
        return self.items
    def get_heal(self):
        return self.heals["Heal"]
    def get_weapons(self):
        return self.weapons
    def get_inventory_summary(self):
        return {
            "items": dict(self.items),
            "heal": self.heals["Heal"],
            "weapons": dict(self.weapons)
        }
    def are_there_heals(self):
        return self.heals["Heal"] is not None

    def get_equipped_weapon(self):
        for slot in sorted(self.weapons):
            if self.weapons[slot]:
                return self.weapons[slot]
        return None
    def equip_weapon(self, slot):
        if slot in self.weapons and self.weapons[slot]:
            return self.weapons[slot]
        return None
    def substitute_weapon(self, slot, new_weapon):
        if slot in self.weapons:
            old_weapon = self.weapons[slot]
            self.weapons[slot] = new_weapon
            return old_weapon
        else:
            raise ValueError("Slot inválido.")
    def substitute_heal(self, new_heal):
        old_heal = self.heals["Heal"]
        self.heals["Heal"] = new_heal
        return old_heal
    
    

    
        
        
            
        
        