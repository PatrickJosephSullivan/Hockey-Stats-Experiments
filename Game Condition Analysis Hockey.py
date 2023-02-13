from wsgiref import headers
import json
import requests
from bs4 import BeautifulSoup
import datetime
import cloudscraper
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
# Define time variables
player_stats = {}
teams_dict = {}
now = datetime.now()
today = datetime.now().strftime("%m_%d_%Y")
month = now.strftime("%B")
# USER DEFINED SHOULD BE LIKE EX. "Kings"
schedule_date = "?date=2023-02-13"
schedule_url = f"https://statsapi.web.nhl.com/api/v1/schedule{schedule_date}"
team = "Senators"
h_or_r = "Home"
opponent = "Calgary Flames"
manual = False

def get_teams(schedule_url):
    game_number = 0
    url = schedule_url
    response = requests.get(url)
    text = response.json()
    all_teams = text["dates"][0]["games"]
    for i in all_teams:
        game_number += 1
        home_team = i["teams"]["home"]["team"]["name"]
        home_team_record = i["teams"]["home"]["leagueRecord"]
        del home_team_record["type"]
        road_team = i["teams"]["away"]["team"]["name"]
        road_team_record = i["teams"]["away"]["leagueRecord"]
        del road_team_record["type"]
        teams_dict.update({game_number: {"home": home_team, "home team record": home_team_record, "road": road_team, "road team record": road_team_record}})
    for k, v in teams_dict.items():
        print(k, v)


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
        new_name = k.replace(".", "")
        new_name = new_name.replace("'", "")
        name_parts = k.split()
        if new_name != k:
            name_parts = new_name.split()
        """Player exceptions for if two player's have same names or similar names"""
        if k == "Martin Jones":
            player_url = "https://www.hockey-reference.com/players/j/jonesma02/splits/"
            player_dict[k] = player_url
        elif len(name_parts) == 3:
            name_parts = name_parts[0] + " " + name_parts[1] + name_parts[2]
            name_parts = name_parts.split()
            first_name, last_name = name_parts[0], name_parts[1]
            first_letter_of_last_name = last_name[0]
            first_four_letters_of_last_name = last_name[:4]
            first_five_letters_of_last_name = last_name[:5]
            first_two_letters_of_first_name = first_name[:2]
            player_url = f"https://www.hockey-reference.com/players/{first_letter_of_last_name}/{first_five_letters_of_last_name}{first_two_letters_of_first_name}01/splits/"
            player_dict[k] = player_url
        elif len(name_parts) == 2:
            first_name, last_name = name_parts[0], name_parts[-1]
            first_letter_of_last_name = last_name[0]
            first_four_letters_of_last_name = last_name[:4]
            first_five_letters_of_last_name = last_name[:5]
            first_two_letters_of_first_name = first_name[:2]
            player_url = f"https://www.hockey-reference.com/players/{first_letter_of_last_name}/{first_five_letters_of_last_name}{first_two_letters_of_first_name}01/splits/"
            player_dict[k] = player_url
        elif k == "James van Riemsdyk":
            player_url = "https://www.hockey-reference.com/players/v/vanrija01.html"
            player_dict[k] = player_url
        else:
            None
    return player_dict


def get_player_dfs(player_dict):
    print(player_dict)
    for k, v in player_dict.items():
        s_per_game = 0
        sv_per_game = 0
        opp_sv_per_gp = 0
        # Receive player url from player dict
        url = v
        # Make a request to hockey reference either by selenium or requests depending on 429 status
        if manual is True:
            driver = webdriver.Firefox()
            driver.get(url)
            driver.maximize_window()
            res = driver.page_source
            print(res)
            driver.quit()
            soup = BeautifulSoup(res, 'html.parser')
        else:
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
        # scraper = cloudscraper.create_scraper(debug=True, delay=10)
        # res = scraper.get(url).text

        # Find the table in the soup
        table = soup.find("table", id="splits")
        if table is None:
            print(f"{k} Table not found")
            continue
        # Create a dataframe off of the table
        df = pd.read_html(str(table))[0]
        # Transform unimportant data
        df.drop(df[df['Value'] == "Value"].index, inplace=True)
        df.iloc[:, 1:] = df.iloc[:, 1:].fillna(0.0)
        total_row = df.loc[df['Value'] == 'Total']
        opp_row = df.loc[df['Value'] == opponent]
        month_row = df.loc[df['Value'] == month]
        h_or_r_row = df.loc[df['Value'] == h_or_r]
        # Convert the "S" column to integers
        if "S" in df:
            df["S"] = df["S"].astype(int)
            s = int(total_row['S'])
            gp = int(total_row['GP'])
            s_per_game = s / gp
        elif "SV" in df:
            df["SV"] = df["SV"].astype(int)
            sv = int(total_row['SV'])
            gp = int(total_row['GP'])
            sv_per_game = sv / gp

        if not opp_row.empty:
            if "S" in df:
                opp_s = int(opp_row['S'])
                opp_gp = int(opp_row['GP'])
                opp_s_per_gp = opp_s / opp_gp
            elif "SV" in df:
                opp_sv = int(opp_row['SV'])
                opp_gp = int(opp_row['GP'])
                opp_sv_per_gp = opp_sv / opp_gp
        else:
            opp_s_per_gp = "No Data"

        if not month_row.empty:
            if "S" in df:
                s_per_month = int(month_row['S'])
                gp_per_month = int(month_row['GP'])
                month_s_per_gp = s_per_month/gp_per_month
            elif "SV" in df:
                sv_per_month = int(month_row['SV'])
                gp_per_month = int(month_row['GP'])
                month_sv_per_gp = sv_per_month / gp_per_month
        else:
            month_s_per_gp = "No Data"

        if s_per_game > 0:
            player_stats.update({f"{k}": {"Shots Per Game": s_per_game, f"Shots Per Game vs. {opponent}": opp_s_per_gp, f"Shots Per Game in {month}": month_s_per_gp}})
        if sv_per_game > 0:
            player_stats.update({f"{k}": {"Saves Per Game": sv_per_game, f"Saves Per Game vs.{opponent}": opp_sv_per_gp, f"Shots Per Game in {month}": month_sv_per_gp}})
        s_per_game, sv_per_game, opp_sv_per_gp, opp_s_per_gp = 0,0,0,0
        # for player, stats in player_stats.items():
        #     print(player, stats)
        time.sleep(5)



get_teams(schedule_url)
# for i in teams_dict:
#     for k, v in teams_dict[i].items():
#         if k == "home":
#             team = v
#             print(team)
#         if k == "road":
#             opponent = v
#             print(opponent)

team_id = get_team_id(team)
player_dict = get_team_roster(team_id)
print(player_dict)
player_urls = parse_name_parts(player_dict)
print(player_urls)
get_player_dfs(player_dict)
with open(f"player_stats_{team}_vs_{opponent}_{today}.txt", "w") as f:
    for k, v in player_stats.items():
        f.write(f"{k}: {v}\n")
