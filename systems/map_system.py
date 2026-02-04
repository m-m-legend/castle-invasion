from data.world_map import WORLD_MAP

ROOM_POSITIONS = {name: (i, j) for i, row in enumerate(WORLD_MAP) for j, name in enumerate(row) if name}

def get_room_name(position, game_map):
    x, y = position
    return game_map[x][y]
