import os
from numpy import genfromtxt
import pkgutil
import io
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from . import utils
from PIL import Image
import numpy as np

def get_frame(team1_x_values,
              team1_y_values,
              team2_x_values,
              team2_y_values,
              ball_x_values,
              ball_y_values,
              ball_r,
              team1_names,
              team2_names):

    frame = go.Frame(data=[
        go.Scatter(x=team1_x_values, y=team1_y_values, mode='markers', marker=dict(color="blue"), text=team1_names),
        go.Scatter(x=team2_x_values, y=team2_y_values, mode='markers', marker=dict(color="green"), text=team2_names),
        go.Scatter(x=ball_x_values, y=ball_y_values, mode='markers', marker=dict(color="orange", size=ball_r))
    ])

    return frame

def get_plot_from_range(df, start, end):
    frames = []
    df['total_time'] = np.vectorize(utils.get_total_time)(df['quarter'], df['game_clock'])
    plotting_df = df.loc[(df['total_time'] < start) & (df['total_time'] > end)]
    for time in plotting_df['total_time'].unique():
        this_time_df = plotting_df.loc[plotting_df['total_time'] == time]
        ball = this_time_df.loc[this_time_df['player_id'] == -1]
        players = this_time_df.loc[this_time_df['player_id'] != -1]
        team1_id = min(players['team_id'])
        
        team1_df = players.loc[players['team_id'] == team1_id].sort_values("player_id")
        team2_df = players.loc[players['team_id'] != team1_id].sort_values("player_id")

        frame = get_frame(team1_df['x_loc'], 
                             team1_df['y_loc'], 
                             team2_df['x_loc'], 
                             team2_df['y_loc'], 
                             ball['x_loc'], 
                             ball['y_loc'], 
                             ball['radius'], 
                             team1_df['player_id'], 
                             team2_df['player_id'])
    
        frames.append(frame)
        
    plot_given_frames(frames)

def plot_given_frames(frames, frame_duration=40, transition_duration=0):

    img_data = pkgutil.get_data(__name__, "fullcourt.png")
    img = Image.open(io.BytesIO(img_data))

    fig = go.Figure(
        data=[go.Scatter(x=frames[0]['data'][0]['x'], y=frames[0]['data'][0]['y'], mode='markers', marker=dict(color="blue"), text=frames[0]['data'][0]['text']),
              go.Scatter(x=frames[0]['data'][1]['x'], y=frames[0]['data'][1]['y'], mode='markers', marker=dict(color="green"), text=frames[0]['data'][1]['text']),
              go.Scatter(x=frames[0]['data'][2]['x'], y=frames[0]['data'][2]['y'], mode='markers', marker=dict(color="orange"))],
        layout=go.Layout(
            xaxis=dict(range=[0, 94], autorange=False),
            yaxis=dict(range=[0, 50], autorange=False),
            title="Live Court",
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                              method="animate",
                              args=[None, {'frame': {'duration':frame_duration, 'redraw': False},
                                'fromcurrent':True, 'transition':{'duration':transition_duration, 'easing':'linear'}}])])]),
        frames=frames
    )

    fig.update_traces(textposition='top center')

    fig.add_layout_image(
            dict(
                source=img,
                xref="x",
                yref="y",
                x=0,
                y=50,
                sizex=94,
                sizey=50,
                sizing="stretch",
                opacity=1,
                layer="below")
    )

    fig.update_layout(template="plotly_white", width=800, height=500, grid=None)
    fig.show()
