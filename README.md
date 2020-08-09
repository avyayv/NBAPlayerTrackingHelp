# player_tracking_help
This repo packages some of the information at https://github.com/sealneaward/nba-movement-data in addition to getting useful plots. To begin, follow the directions and convert the JSON files into CSV files found in the README.md file of that repo.

Then clone this repo and run `pip install -e tracking`

## Useful functions
Once you have the CSV files, here are some of the simple functions used.

### Getting True Shot Times
This is using some refactored code from @sealneaward's code (had to update some minor things), but the general premise is the same. We smooth the ball height, take the derivative of the ball height, and see when the ball is being shot. 

```
import pandas as pd
from tracking.tracking import get_shot_time_from_range
game_csv = pd.read_csv("0021500056.csv")
time = get_shot_time_from_range(game_csv, start=2880, end=2860)
```

Play-by-play data (as you will find) is very messy, as it deals with human error. Thus, when a shot is recorded by the human-being, the actual timestamp will be off by a few seconds. If you feed in a range of values into this function (with the center of the range being the play-by-play recorded value), you can find the true value. I will be adding the play-by-play shot time finding functionality soon.

### Plotting Animated Plots
The need for this code is fairly straight-forward. If we want to plot the X-Y data easily, we can just use this code(using plotly)

```
from tracking.plotting import get_plot_from_range
game_csv = pd.read_csv("0021500056.csv")
get_plot_from_range(game_csv, start=2880, end=2860)
```

### Finding Player With Ball AND the Defending Player
The need for this code is also fairly straight-forward. For instance, if you want to find the player who has possession and the defender, this code could be important.

```
from tracking.tracking import get_shot_time_from_range, find_player_with_ball
game = pd.read_csv(TRACKING_DIRECTORY+"0021500056.csv")
time = get_shot_time_from_range(game_csv, start=2880, end=2860)
offense, defense = find_player_with_ball(game, time)
print(offense['player_id'], defense['player_id'])
```


