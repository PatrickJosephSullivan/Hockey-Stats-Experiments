import requests
import pandas as pd
import json
import pprint
import datetime
import numpy as np
import openpyxl
from sklearn.datasets import load_iris
from tabulate import tabulate
pdtabulate=lambda df:tabulate(df,headers='keys')

# Pretty Print Options
pretty = pprint.PrettyPrinter(width=10)
# Dataframe print options
pd.options.display.max_columns = None
pd.options.display.max_rows = None
# Define the base URL for the ESPN API
base_url = "https://statsapi.web.nhl.com/api/v1/teams"
# Define the dictionary for player stats
player_stats = {}
# USER DEFINED SHOULD BE LIKE EX. "Kings"
team = "Kings"
# versus =

# Define a function to retrieve a team's id
def get_team_id(team_name):
    url = "https://statsapi.web.nhl.com/api/v1/teams"
    response = requests.get(url)
    teams = response.json()
    teams = teams["teams"]
    for i in teams:
        if i["teamName"] == team_name:
            return i["id"]
        else:
            None

# Define a function to get team's roster
def get_team_roster(team_id):
    player_ids = {}
    url = "https://statsapi.web.nhl.com/api/v1/teams/"+str(team_id)+"/?expand=team.roster"
    response = requests.get(url)
    roster = response.json()
    roster = roster["teams"][0]["roster"]["roster"]
    for i in roster:
        player_ids.update({i["person"]["fullName"]: i["person"]["id"]})
        # for n in i["person"]:
        #     print(n)
        #     player_ids.update({n["fullName"]: n["id"]})
    return player_ids

# Define a function to retrieve player stats from the API and add to team dataframe
def get_player_stats(player_dict):
    for k, v in player_dict.items():
        url = "https://statsapi.web.nhl.com/api/v1/people/" + str(v) + "/stats/?stats=yearByYear"
        response = requests.get(url)
        content = json.loads(response.content)['stats']
        splits = content[0]['splits']

        df_splits = (pd.json_normalize(splits, sep="_")
                     .query('league_name == "National Hockey League"')
                     )
        # print(f'{k}\n', df_splits.to_string())
        shots = df_splits.get("stat_shots")
        games = df_splits["stat_games"]
        if shots is not None:
            shots_per_game = sum(shots)/sum(games)
        else:
            shots_per_game = None
        player_stats.update({f"{k}": {"Player ID": v, "Shots Per Game": shots_per_game}})
        df_splits.to_excel(f'{k}.xlsx', sheet_name="sheet_1")
        # print(f'{k}\n', df_splits.to_string())
        # return player_stats


team_id = get_team_id(team)
player_dict = get_team_roster(team_id)
get_player_stats(player_dict)
for k, v in player_stats.items():
    print(k,v)
