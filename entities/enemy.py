class Enemy:
    def __init__(self, id: str, name: str, health: float, damage: float, sprite_key: str, placement: str):
        self.name = name
        self.id = id
        self.health = health
        self.damage = damage
        self.sprite_key = sprite_key
        self.placement = placement
    def get_id(self):
        return self.id
    def is_defeated(self):
        return self.health <= 0
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
    def got_defended(self, factor: float):
        if factor < 0 or factor > 1:
            raise ValueError("Defense factor must be between 0 and 1.")
        reduced_damage = self.damage * (1-factor)
        return reduced_damage
    def get_name(self):
        return self.name
    def get_health(self):
        return self.health
    def get_damage(self):
        return self.damage
    def get_sprite_key(self):
        return self.sprite_key
    def get_placement(self):
        return self.placement
    def __str__(self):
        return f"Enemy {self.name} - Health: {self.health}, Damage: {self.damage}"
    