import json
import ast

data = {}

with open('player_stats_Avalanche_vs_Edmonton Oilers_02_18_2023.txt', 'r') as f:
    contents = f.read()
    print(contents)
    players = contents.split("\n")
    for line in players:
        entry = "{" + line + "}"
        # entry = ast.literal_eval(entry)
        data.update(entry)
        # name, stats = line.split(":", 1)
        # print(name)
        # print(stats)
        # data.update(name: stats)



print(data)



# Extract Shots Per Game and Shots Per Game vs. Edmonton Oilers for each player
# players = []
# shots_per_game = []
# shots_vs_oilers = []
# for player, stats in data.items():
#     if 'Shots Per Game' in stats and 'Shots Per Game vs. Edmonton Oilers' in stats:
#         players.append(player)
#         shots_per_game.append(stats['Shots Per Game'])
#         shots_vs_oilers.append(stats['Shots Per Game vs. Edmonton Oilers'])
#
# print(players)
# print(shots_per_game)
# print(shots_vs_oilers)