"""Estado de execução. Nenhuma entidade conhece arquivos, UI ou sistemas."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Loot:
    kind: str
    id: str


@dataclass
class Inventory:
    weapons: list[str | None] = field(default_factory=lambda: [None, None, None])
    active_slot: int = 0
    heal: str | None = None
    items: dict[str, int] = field(default_factory=dict)

    @property
    def equipped_weapon(self) -> str | None:
        return self.weapons[self.active_slot]

    def equip(self, slot: int) -> bool:
        if not 1 <= slot <= 3 or self.weapons[slot - 1] is None:
            return False
        self.active_slot = slot - 1
        return True

    def add_item(self, item_id: str) -> None:
        self.items[item_id] = self.items.get(item_id, 0) + 1

    def consume(self, item_id: str) -> bool:
        if self.items.get(item_id, 0) <= 0:
            return False
        self.items[item_id] -= 1
        if self.items[item_id] == 0:
            del self.items[item_id]
        return True


@dataclass
class Player:
    name: str
    health: float
    max_health: float
    position: tuple[int, int]
    inventory: Inventory = field(default_factory=Inventory)
    last_position: tuple[int, int] | None = None
    xp: int = 0
    level: int = 1

    @property
    def alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: float) -> None:
        self.health = max(0, self.health - max(0, amount))

    def heal(self, amount: float) -> float:
        before = self.health
        self.health = min(self.max_health, self.health + max(0, amount))
        return self.health - before


@dataclass
class Enemy:
    id: str
    health: float
    rewarded: bool = False

    @property
    def alive(self) -> bool:
        return self.health > 0

    def take_damage(self, amount: float) -> None:
        self.health = max(0, self.health - max(0, amount))


@dataclass
class RoomState:
    inspected: bool = False
    ground: list[Loot] = field(default_factory=list)


@dataclass
class BattleState:
    enemy_id: str
    cooldown: int = 0


@dataclass
class GameState:
    player: Player
    rooms: dict[str, RoomState]
    enemies: dict[str, Enemy]
    battle: BattleState | None = None
    visited: set[str] = field(default_factory=set)
    won: bool = False
