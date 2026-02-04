def get_input(screen):
    key = screen.get_key()
    if key is None:
        return None

    if isinstance(key, int):
        return chr(key)

    return str(key).lower()