def get_new_position(position, direction, game_map):
    x, y = position
    
    moves = {
        "norte": (-1, 0),
        "sul": (1, 0),
        "leste": (0, 1),
        "oeste": (0, -1)
    }

    dx, dy = moves.get(direction, (0, 0))
    nx, ny = x + dx, y + dy

    if 0 <= nx < len(game_map) and 0 <= ny < len(game_map[nx]):
        if game_map[nx][ny] is not None:
            return (nx, ny)

    return position
