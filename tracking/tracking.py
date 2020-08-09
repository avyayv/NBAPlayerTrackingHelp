import pandas as pd
import numpy as np
import math
import os
from . import utils

def sg_filter(x, m, k=0):
    """
    x = Vector of sample times
    m = Order of the smoothing polynomial
    k = Which derivative
    """
    mid = int(len(x) / 2)
    a = x - x[mid]
    expa = lambda x: map(lambda i: i**x, a)
    A = np.r_[map(expa, range(0,m+1))].transpose()
    A = np.array([list(z) for z in list(A[0])]).transpose()
    Ai = np.linalg.pinv(np.array(A))
    return Ai[k]

def smooth(x, y, size=5, order=2, deriv=0):

    n = len(x)
    m = size

    result = np.zeros(n)

    for i in range(m, n-m):
        start, end = i - m, i + m + 1
        f = sg_filter(x[start:end], order, deriv)
        result[i] = np.dot(f, y[start:end])

    if deriv > 1:
        result *= math.factorial(deriv)

    return result

def correct_shots(ball_height, game_clock_time):

    size = 10
    order = 3

    params = (game_clock_time, ball_height, size, order)

    position_smoothed = smooth(*params, deriv=0)
    acceleration_smoothed = smooth(*params, deriv=2)
    max_ind = np.argmax(position_smoothed)

    shot_window = acceleration_smoothed[np.max([0, max_ind - 25]): max_ind]
    shot_min_ind = np.argmin(shot_window)
    shot_ind = max_ind - shot_min_ind
    shot_time = game_clock_time[shot_ind]

    return shot_time

def get_shot_time_from_range(full_game, start, end):
    full_game['total_time'] = np.vectorize(utils.get_total_time)(full_game['quarter'], full_game['game_clock'])
    this_window_of_game = full_game.loc[full_game['total_time'].between(end, start, inclusive=False)].copy().reset_index()
    ball_in_window = this_window_of_game.loc[this_window_of_game['player_id']==-1]
    shot_time = correct_shots(np.array(ball_in_window['radius']), np.array(ball_in_window['total_time']))
    return shot_time

def find_player_with_ball(game_df, time):
    time_df = game_df.loc[game_df['total_time'] == time]
    ball_sub_df = time_df.loc[time_df['player_id'] == -1]
    players_df = time_df.loc[time_df['player_id'] != -1]

    ball_x, ball_y = (ball_sub_df['x_loc'].iloc[0], ball_sub_df['y_loc'].iloc[0])
    team1_df = players_df.loc[players_df['team_id'] == players_df['team_id'].iloc[0]].copy()
    team2_df = players_df.loc[players_df['team_id'] != players_df['team_id'].iloc[0]].copy()

    team1_dist = np.array(np.sqrt((team1_df['y_loc']-ball_y)**2+(team1_df['x_loc']-ball_x)**2))
    team2_dist = np.array(np.sqrt((team2_df['y_loc']-ball_y)**2+(team2_df['x_loc']-ball_x)**2))

    smallest_team1 = np.where(team1_dist == np.amin(team1_dist))[0][0]
    smallest_team2 = np.where(team2_dist == np.amin(team2_dist))[0][0]

    if team1_dist[smallest_team1] < team2_dist[smallest_team2]:
        return team1_df.iloc[smallest_team1], team2_df.iloc[smallest_team2]
    else:
        return team2_df.iloc[smallest_team2], team1_df.iloc[smallest_team1]
