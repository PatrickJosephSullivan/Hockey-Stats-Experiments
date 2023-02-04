import requests
from bs4 import BeautifulSoup
import datetime
import re
import webbrowser
import selenium
import time
import os
import openpyxl
import lxml
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd

# Dataframe print options
pd.options.display.max_columns = None
pd.options.display.max_rows = None
base_url = "https://statsapi.web.nhl.com/api/v1/teams"
# Define the dictionary for player stats
player_stats = {}
# USER DEFINED SHOULD BE LIKE EX. "Kings"
team = "Kings"
h_or_r = "Home"
opponent = "Anaheim Ducks"


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
    # print(player_ids)
    return player_ids

def parse_name_parts(player_dict):
    for k in player_dict:
        name_parts = k.split()
        if len(name_parts) == 2:
            first_name, last_name = name_parts[0], name_parts[-1]
            first_letter_of_last_name = last_name[0]
            first_four_letters_of_last_name = last_name[:4]
            first_five_letters_of_last_name = last_name[:5]
            first_two_letters_of_first_name = first_name[:2]
            player_url = f"https://www.hockey-reference.com/players/{first_letter_of_last_name}/{first_five_letters_of_last_name}{first_two_letters_of_first_name}01/splits/"
            player_dict[k] = player_url
        else:
            return None, None, None, None
    return player_dict


def get_player_dfs(player_dict):
    for k, v in player_dict.items():
        # Recieve player url from player dict
        url = v
        # Make a request to hockey reference
        res = requests.get(url)
        # Create a soup item
        soup = BeautifulSoup(res.text, 'html.parser')
        # Find the table in the soup
        table = soup.find("table", id="splits")
        # Create a datafram off of the table
        df = pd.read_html(str(table))[0]
        # Transform unimportant data
        df.drop(df[df['Value'] == "Value"].index, inplace=True)
        df.iloc[:, 1:] = df.iloc[:, 1:].fillna(0.0)
        # Convert the "S" column to integers
        df["S"] = df["S"].astype(int)
        # Search the "Value" column for "Total"
        total_row = df.loc[df['Value'] == 'Total']
        # find the integer in the "S" column
        s = int(total_row['S'])
        # find the integer in the "GP" column
        gp = int(total_row['GP'])
        # sum the "GP" column
        s_per_game = s/gp
        opp = df[df['Value'] == opponent]
        opp_s = int(total_row['S'])
        opp_gp = int(total_row['GP'])
        opp_s_per_gp = opp_s/opp_gp
        month = datetime.now().month
        home_or_road = h_or_r
        player_stats.update({f"{k}": {"Shots Per Game": s_per_game, f"Shots Per Game vs. {opponent}": opp_s_per_gp}})
        print(player_stats)



team_id = get_team_id(team)
player_dict = get_team_roster(team_id)
player_urls = parse_name_parts(player_dict)
get_player_dfs(player_urls)
print(player_stats)