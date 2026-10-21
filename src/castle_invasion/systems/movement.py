"""Coordenadas sempre no formato (linha, coluna)."""

DIRECTIONS = {"norte": (-1, 0), "sul": (1, 0), "leste": (0, 1), "oeste": (0, -1)}


def get_new_position(position, direction, game_map):
    row, col = position
    dr, dc = DIRECTIONS.get(direction, (0, 0))
    nr, nc = row + dr, col + dc
    if 0 <= nr < len(game_map) and 0 <= nc < len(game_map[nr]):
        if game_map[nr][nc] is not None:
            return nr, nc
    return position
