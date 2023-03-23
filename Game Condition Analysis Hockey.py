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

# TODO Fix bug for wrong output
# TODO Add Functionality for Statistical Significance Calculation Based on Games Played.

# Dictionary used for translation into API formats.
nhl_teams_logos = {
    "Anaheim Ducks": "Ducks",
    "Arizona Coyotes": "Coyotes",
    "Boston Bruins": "Bruins",
    "Buffalo Sabres": "Sabres",
    "Calgary Flames": "Flames",
    "Carolina Hurricanes": "Hurricanes",
    "Chicago Blackhawks": "Blackhawks",
    "Colorado Avalanche": "Avalanche",
    "Columbus Blue Jackets": "Blue Jackets",
    "Dallas Stars": "Stars",
    "Detroit Red Wings": "Red Wings",
    "Edmonton Oilers": "Oilers",
    "Florida Panthers": "Panthers",
    "Los Angeles Kings": "Kings",
    "Minnesota Wild": "Wild",
    "Montréal Canadiens": "Canadiens",
    "Nashville Predators": "Predators",
    "New Jersey Devils": "Devils",
    "New York Islanders": "Islanders",
    "New York Rangers": "Rangers",
    "Ottawa Senators": "Senators",
    "Philadelphia Flyers": "Flyers",
    "Pittsburgh Penguins": "Penguins",
    "San Jose Sharks": "Sharks",
    "Seattle Kraken": "Kraken",
    "St. Louis Blues": "Blues",
    "Tampa Bay Lightning": "Lightning",
    "Toronto Maple Leafs": "Maple Leafs",
    "Vancouver Canucks": "Canucks",
    "Vegas Golden Knights": "Golden Knights",
    "Washington Capitals": "Capitals",
    "Winnipeg Jets": "Jets"
}


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
# Defines what schedule date should be pulled from nhl.com
schedule_date = "?date=2023-03-23"
schedule_url = f"https://statsapi.web.nhl.com/api/v1/schedule{schedule_date}"

"""DEPRECATED MANUAL CALLS"""
"""Used to invoke a stat call on an individual game instead of looping through a day's schedule"""
# TEAM SHOULD BE LOOK LIKE, "Kings" AND OPPONENT SHOULD LOOK LIKE, "Detroit Wed Rings"
# team = "Bruins"
# opponent = "Chicago Blackhawks"
# Defines whether to pull stats for "Home" or "Road"
# h_or_r = "Road"

# Invokes a function that bypasses cloudflare firewalls. Only use if timed out by HockeyReference.com,
# much slower method
manual = False


def get_teams(schedule_url):
    """Pulls all team schedules from the NHL API when provided with link"""
    # Gives each game on the schedule a value so that games can be identified easier
    game_number = 0
    # Pulls text from webpage
    url = schedule_url
    response = requests.get(url)
    text = response.json()
    all_teams = text["dates"][0]["games"]
    # iterates through all_teams text.
    for i in all_teams:
        # Adds 1 to the ticker
        game_number += 1
        # Finds home team
        home_team = i["teams"]["home"]["team"]["name"]
        home_team_record = i["teams"]["home"]["leagueRecord"]
        del home_team_record["type"]
        # Finds away team
        road_team = i["teams"]["away"]["team"]["name"]
        road_team_record = i["teams"]["away"]["leagueRecord"]
        del road_team_record["type"]
        # Adds game to the teams_dict dictionary and then queries the next game
        teams_dict.update({game_number: {"home": home_team, "home team record": home_team_record, "road": road_team,
                                         "road team record": road_team_record}})
    # Prints today's schedule for accessibility. May want to comment out later when we can loop through all teams.
    for k, v in teams_dict.items():
        print(k, v)


# Define a function to retrieve a team's id
def get_team_id(team_name):
    """Translates team logo Ex. Kings, Golden Knights
     into nhl api ID Ex. 28,12,etc."""
    url = "https://statsapi.web.nhl.com/api/v1/teams"
    response = requests.get(url)
    teams = response.json()
    # Finds team section.
    teams = teams["teams"]
    # Iterates through logo team names and returns their id
    for i in teams:
        if i["teamName"] == team_name:
            return i["id"]
        else:
            None



def get_team_roster(team_id):
    """Gets a teams roster using the team ID"""
    player_ids = {}
    url = "https://statsapi.web.nhl.com/api/v1/teams/" + str(team_id) + "/?expand=team.roster"
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
        # Initiate variables
        s_per_game, sv_per_game, opp_s_per_gp, opp_sv_per_gp, month_s_per_gp, month_sv_per_gp, home_s_per_gp, \
        road_s_per_gp, home_sv_per_gp, road_sv_per_gp, h_or_r_value = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
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

        """START OF CALCULATIONS"""

        # Convert the "S" and "SV" column to integers and then run shots per game and saves per game calcs
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
        # Run opponent calculations
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
            opp_s_per_gp = 0
            opp_sv_per_gp = 0
        # Runs month calculations
        if not month_row.empty:
            if "S" in df:
                s_per_month = int(month_row['S'])
                gp_per_month = int(month_row['GP'])
                month_s_per_gp = s_per_month / gp_per_month
            elif "SV" in df:
                sv_per_month = int(month_row['SV'])
                gp_per_month = int(month_row['GP'])
                month_sv_per_gp = sv_per_month / gp_per_month
        else:
            month_s_per_gp = 0
            month_sv_per_gp = 0
        # Runs home or road data
        if not h_or_r_row.empty:
            if "S" in df and h_or_r == "Home":
                home_s_per_gp = int(h_or_r_row['S'])
                gp_per_month = int(h_or_r_row['GP'])
                home_s_per_gp = home_s_per_gp / gp_per_month
            if "SV" in df and h_or_r == "Home":
                home_sv_per_gp = int(h_or_r_row['SV'])
                gp_per_month = int(h_or_r_row['GP'])
                home_sv_per_gp = home_sv_per_gp / gp_per_month
            if "S" in df and h_or_r == "Road":
                road_s_per_gp = int(h_or_r_row['S'])
                gp_per_month = int(h_or_r_row['GP'])
                road_s_per_gp = road_s_per_gp / gp_per_month
            if "SV" in df and h_or_r == "Road":
                road_sv_per_gp = int(h_or_r_row['SV'])
                gp_per_month = int(h_or_r_row['GP'])
                road_sv_per_gp = road_sv_per_gp / gp_per_month
        else:
            h_or_r_value = 0
        # Find the value that's greater than 0 and get variable ready for print statement
        for i in [home_s_per_gp, road_s_per_gp, home_sv_per_gp, road_sv_per_gp]:
            # print(i)
            if i > 0:
                h_or_r_value = i
                break
            else:
                h_or_r_value = 0
        # if a value is found, put it in the dictionary
        if s_per_game > 0:
            stat_list = [s_per_game,opp_s_per_gp, month_s_per_gp, h_or_r_value]
            average = sum(stat_list)/len(stat_list)
            stat_list.append(average)
            player_stats.update({k: stat_list})
        if sv_per_game > 0:
            stat_list = [sv_per_game, opp_sv_per_gp, month_sv_per_gp, h_or_r_value]
            average = sum(stat_list) / len(stat_list)
            stat_list.append(average)
            player_stats.update({k: stat_list})
        """Debugging print statement"""
        # for player, stats in player_stats.items():
        #     print(player, stats)
        last_key = list(player_stats)[-1]
        last_value = list(player_stats.values())[-1]
        print(str(last_key)+": "+str(last_value))
        time.sleep(4.5)


def loop_teams(schedule_date):
    """Experimental function for looping through teams.
    Hopefully will eliminate having to type in
    each team individually"""
    for i in teams_dict.values():
        global h_or_r
        h_or_r = "Home"
        i = list(i.items())
        home_team = i[0][1]
        team = nhl_teams_logos.get(home_team)
        road_team = i[2][1]
        global opponent
        opponent = road_team
        team_id = get_team_id(team)
        player_dict = get_team_roster(team_id)
        print(player_dict)
        player_urls = parse_name_parts(player_dict)
        print(player_urls)
        get_player_dfs(player_dict)
    for i in teams_dict.values():
        h_or_r = "Road"
        i = list(i.items())
        home_team = i[0][1]
        road_team = i[2][1]
        team = nhl_teams_logos.get(road_team)
        opponent = home_team
        team_id = get_team_id(team)
        player_dict = get_team_roster(team_id)
        print(player_dict)
        player_urls = parse_name_parts(player_dict)
        print(player_urls)
        get_player_dfs(player_dict)
    csv_date = schedule_date[11:]
    csv_date = csv_date.replace("-", "_")
    with open(f"player_stats_{csv_date}.csv", "w") as f:
        f.write(
            f"Player, Shots or Saves, Shots or Saves Against Opponent, Shots or Saves in {month}, Shots or Saves at "
            f"condition\n")
        for k, v in player_stats.items():
            v = str(v)
            v = v.strip("[]")
            f.write(f"{k}, {v}\n")
        f.write("\n")




get_teams(schedule_url)
loop_teams(schedule_date)
# team_id = get_team_id(team)
# player_dict = get_team_roster(team_id)
# print(player_dict)
# player_urls = parse_name_parts(player_dict)
# print(player_urls)
# get_player_dfs(player_dict)
# with open(f"player_stats_{team}_vs_{opponent}_{today}.csv", "w") as f:
#     f.write(f"Player, Shots or Saves, Shots or Saves Against Opponent, Shots or Saves in {month}, Shots or Saves at "
#             f"{h_or_r}\n")
#     for k, v in player_stats.items():
#         v = str(v)
#         v = v.strip("{}")
#         f.write(f"{k}, {v}\n")
