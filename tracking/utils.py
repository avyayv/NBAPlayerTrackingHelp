def get_total_time(quarter, game_clock):
    if quarter > 4:
        return ((4-quarter)*300)+game_clock
    else:
        return ((4-quarter)*720)+game_clock
