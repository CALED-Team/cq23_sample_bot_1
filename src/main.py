from standard import Standard

if __name__ == "__main__":
    game = Standard()
    while game.read_next_turn_data():
        game.respond_to_turn()
