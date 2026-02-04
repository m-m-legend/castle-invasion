import textwrap

def draw_room(screen, room_name):
    width = screen.width//2
    height = screen.height//2
    room_width = width - 4
    room_height = height - 4

    room_name_x = (room_width - len(room_name)) // 2
    room_name_y = room_height // 2

    screen.print_at("+{}+".format("-" * room_width), 2, 2)
    for i in range(room_height):
        screen.print_at("|{}|".format(" " * room_width), 2, 3 + i)
    screen.print_at("+{}+".format("-" * room_width), 2, 3 + room_height)

    screen.print_at(room_name, 2 + room_name_x, 3 + room_name_y)

def draw_map(screen, game_map, current_room):
    screen.print_at("Mapa:", 30, 2)
    
    for i, row in enumerate(game_map):
        for j, room in enumerate(row):
            if room is None:
                continue
            label = f"[{room}]" if room == current_room else room
            screen.print_at(label, 26 + j * 20, 3 + i)

def show_directions(screen, game_map, position):
    x, y = position
    directions = []
    if x > 0 and game_map[x-1][y]:
        directions.append("Norte (N)")
    if x < len(game_map) - 1 and game_map[x+1][y]:
        directions.append("Sul (S)")
    if y > 0 and game_map[x][y-1]:
        directions.append("Oeste (O)")
    if y < len(game_map[x]) - 1 and game_map[x][y+1]:
        directions.append("Leste (L)")

    screen.print_at("Direções: " + ", ".join(directions), 2, 12)
    screen.print_at('1. Inspecionar',2,13)
    screen.print_at('2. Inventário',2,14)
    screen.print_at('Sair do Jogo(Q)',2,15)
    

def desc_room(screen, current_room, desc):
    START_Y = 10
    MAX_LINES = 6
    WIDTH = 60  

    rows = desc.get(current_room, ["Sem descrição disponível."])

    text = " ".join(rows)

    wrapped = textwrap.wrap(text, WIDTH)

    for i in range(MAX_LINES):
        screen.print_at(" " * 120, 2, START_Y + i)

    screen.print_at(f"{current_room}:", 2, START_Y)

    for i, row in enumerate(wrapped[:MAX_LINES-1]):
        screen.print_at(row, 2, START_Y + 1 + i)

