"""Catálogo injetado nos sistemas; não carrega dados nem mantém estado global."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Content:
    data: dict[str, Any]
    fingerprint: str

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    def room_at(self, position: tuple[int, int]) -> str:
        row, col = position
        return self.data["map"][row][col]

    def position_of(self, room: str) -> tuple[int, int]:
        for row, cells in enumerate(self.data["map"]):
            for col, name in enumerate(cells):
                if name == room:
                    return row, col
        raise ValueError(f"Sala desconhecida: {room}")

    def loot_name(self, kind: str, item_id: str) -> str:
        group = {"item": "items", "weapon": "weapons", "heal": "heals"}[kind]
        return self.data[group][item_id]["name"]
