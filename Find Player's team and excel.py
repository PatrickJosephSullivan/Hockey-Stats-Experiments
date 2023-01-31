import requests
from bs4 import BeautifulSoup
import re
import webbrowser
import selenium
import time
import os
# import openpyxl
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

sport_abbreviations = {
    "Football": {"url": "https://www.pro-football-reference.com/players/", "ref_num": "00"},
    "Hockey": {"url": "https://www.hockey-reference.com/players/", "ref_num": "01"}
}

team_abbreviations = {
    "Arizona Cardinals": "ARI",
    "Atlanta Falcons": "ATL",
    "Baltimore Ravens": "BAL",
    "Buffalo Bills": "BUF",
    "Carolina Panthers": "CAR",
    "Chicago Bears": "CHI",
    "Cincinnati Bengals": "CIN",
    "Cleveland Browns": "CLE",
    "Dallas Cowboys": "DAL",
    "Denver Broncos": "DEN",
    "Detroit Lions": "DET",
    "Green Bay Packers": "GB",
    "Houston Texans": "HOU",
    "Indianapolis Colts": "IND",
    "Jacksonville Jaguars": "JAX",
    "Kansas City Chiefs": "KC",
    "Las Vegas Raiders": "LV",
    "Los Angeles Chargers": "LAC",
    "Los Angeles Rams": "LAR",
    "Miami Dolphins": "MIA",
    "Minnesota Vikings": "MIN",
    "New England Patriots": "NE",
    "New Orleans Saints": "NO",
    "New York Giants": "NYG",
    "New York Jets": "NYJ",
    "Philadelphia Eagles": "PHI",
    "Pittsburgh Steelers": "PIT",
    "San Francisco 49ers": "SF",
    "Seattle Seahawks": "SEA",
    "Tampa Bay Buccaneers": "TB",
    "Tennessee Titans": "TEN",
    "Washington Football Team": "WAS",
    "Anaheim Ducks": "ANA",
    "Arizona Coyotes": "ARI",
    "Boston Bruins": "BOS",
    "Buffalo Sabres": "BUF",
    "Calgary Flames": "CGY",
    "Carolina Hurricanes": "CAR",
    "Chicago Blackhawks": "CHI",
    "Colorado Avalanche": "COL",
    "Columbus Blue Jackets": "CBJ",
    "Dallas Stars": "DAL",
    "Detroit Red Wings": "DET",
    "Edmonton Oilers": "EDM",
    "Florida Panthers": "FLA",
    "Los Angeles Kings": "LAK",
    "Minnesota Wild": "MIN",
    "Montreal Canadiens": "MTL",
    "Nashville Predators": "NSH",
    "New Jersey Devils": "NJD",
    "New York Islanders": "NYI",
    "New York Rangers": "NYR",
    "Ottawa Senators": "OTT",
    "Philadelphia Flyers": "PHI",
    "Pittsburgh Penguins": "PIT",
    "San Jose Sharks": "SJS",
    "St. Louis Blues": "STL",
    "Tampa Bay Lightning": "TBL",
    "Toronto Maple Leafs": "TOR",
    "Vancouver Canucks": "VAN",
    "Vegas Golden Knights": "VGK",
    "Washington Capitals": "WSH",
    "Winnipeg Jets": "WPG"
}


def parse_name_parts(name_string):
    name_parts = name_string.split()
    if len(name_parts) == 2:
        first_name, last_name = name_parts[0], name_parts[-1]
        first_letter_of_last_name = last_name[0]
        first_four_letters_of_last_name = last_name[:4]
        first_five_letters_of_last_name = last_name[:5]
        first_two_letters_of_first_name = first_name[:2]
        return first_letter_of_last_name, first_four_letters_of_last_name, first_five_letters_of_last_name, first_two_letters_of_first_name
    else:
        return None, None, None, None


def get_team(player_url):
    url = player_url
    response = requests.get(url)
    # webbrowser.open(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    if "football" in sport:
        href = str(soup.select("#meta > div:nth-child(2) > p:nth-child(5) > span:nth-child(2) > a:nth-child(1)"))
    if "hockey" in sport:
        href = str(soup.select("#meta > div:nth-child(2) > p:nth-child(4) > span:nth-child(2) > a:nth-child(1)"))
    team = re.search(r">(.*?)<", href).group(1)
    print(team)
    return team


def get_abbreviation(team):
    return team_abbreviations.get(team, "")


def get_sport_url(sport):
    return sport_abbreviations.get(sport, {}).get("url", "")


def get_ref_num(sport):
    if sport == "Football":
        return "00"
    elif sport == "Hockey":
        return "01"
    else:
        return None


def get_schedule(team):
    team_name = team
    abbrev = get_abbreviation(team)
    if "football" in sport:
        url = f"http://www.espn.com/nfl/team/schedule/_/name/{abbrev}/{team_name.lower().replace(' ', '')}/"
    elif "hockey" in sport:
        url = f"https://www.espn.com/nhl/team/schedule/_/name/{abbrev}/{team_name.lower().replace(' ', '')}/"
    webbrowser.open(url)
    return url


def apply_filter(player_name):
    return None


def get_excel(player_url):
    """todo LOW PRIORITY optimize time.sleep commands"""
    # Invokes a firefox window of the player on football reference
    if "football" in sport:
        player_url = player_url.replace(".htm","")
    elif "hockey" in sport:
        player_url = player_url.replace(".html", "")
    url = f"{player_url}/splits/"
    print(url)
    driver = webdriver.Firefox()
    driver.get(url)
    driver.maximize_window()
    time.sleep(3)
    # Scroll down so mouseover event is in viewport (uses x,y co-ords [could probably be optimized better])
    ActionChains(driver).scroll_by_amount(0,1000).perform()
    time.sleep(3)
    # Find mouseover element so we can download the excel sheet
    if "football" in sport:
        share_export_button = driver.find_element(By.CSS_SELECTOR,
                                                  ".sidescroll_note > ul:nth-child(1) > li:nth-child(2)")
    elif "hockey" in sport:
        share_export_button = driver.find_element(By.CSS_SELECTOR, "#splits_sh > div:nth-child(3) > ul:nth-child(1) > li:nth-child(2)")
    time.sleep(3)
    # Use action chain module to activate mouseover css event
    ActionChains(driver).move_to_element(share_export_button).perform()
    time.sleep(3)
    # Find excel download button by CSS Selector
    if "football" in sport:
        excel_button = driver.find_element(By.CSS_SELECTOR, ".sidescroll_note > ul:nth-child(1) > li:nth-child(2) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(2) > button:nth-child(1)")
    elif "hockey" in sport:
        excel_button = driver.find_element(By.CSS_SELECTOR, "#splits_sh > div:nth-child(3) > ul:nth-child(1) > li:nth-child(2) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(2) > button:nth-child(1)")
    time.sleep(3)
    # click excel button
    excel_button.click()
    time.sleep(3)
    # Set downloads folder
    download_folder = "C:/Users/Patrick/Downloads"
    # Get a list of all files in the download folder
    files = os.listdir(download_folder)
    # Sort the files based on their modification time
    files.sort(key=lambda x: os.path.getmtime(os.path.join(download_folder, x)))
    # Get the last modified file
    last_modified_file = files[-1]
    # Get the file path
    file_path = os.path.join(download_folder, last_modified_file)
    # Get the file extension
    file_extension = os.path.splitext(file_path)[1]
    # Get the date when the file was last modified
    date_time = datetime.fromtimestamp(os.path.getmtime(file_path))
    date_str = date_time.strftime("%Y-%m-%d")
    # Create new file name
    new_file_name = name_string + "_" + date_str + file_extension
    # Create new file path
    new_file_path = os.path.join(download_folder, new_file_name)
    # Rename the file
    os.rename(file_path, new_file_path)


def get_game_conditions(schedule):
    # # Make a request to the website
    # response = requests.get(schedule)
    # # Parse the HTML content
    # soup = BeautifulSoup(response.text, 'html.parser')
    # # Find the latest game row
    # games = soup.find_all('tr')
    # if "football" in sport:
    #     latest_game = soup.find(attrs={"data-idx": "2"})
    # if "hockey" in sport:
    #     latest_game = soup.find(attrs={"data-idx": "1"})
    # # Find the date in that row
    # print(latest_game)
    # if "football" in sport:
    #     date_string = latest_game.contents[1].string
    # elif "hockey" in sport:
    #     date_string = latest_game.contents[0].string
    # date_string = date_string[:-3]
    # # Extract the weekday and month
    # weekday, month = date_string.split(', ')
    # #
    # weekday = datetime.strptime(weekday, "%a").strftime("%A")
    # # Convert the abbreviated month to the full month
    # month = datetime.strptime(month, "%b").strftime("%B")
    # # Find opposing team name
    # opponent = soup.find(class_="tc pr2")
    # opponent = opponent.find(class_="AnchorLink")
    # opponent = opponent.find('img', alt=True)
    # opponent = opponent['alt']
    # # Find home or away conditions
    # conditions = [weekday, month, opponent]
    # print(conditions)
    # return conditions
    print("Enter game conditions from ESPN Window in the order below. Case Sensitive \n"
          "Weekday played on, Month played in, Opposing team, Home or Road \n"
          "(EX: Sunday, January, Seattle, Home)")
    conditions_string = input()
    conditions = conditions_string.split(',')
    conditions = [x.strip() for x in conditions]
    print(conditions)
    return conditions



"""INSERT SPORT AND PLAYER"""
sport = "Hockey"
name_string = "Adrian Kempe"
if "Hockey" in sport:
    name_string = name_string.lower()
"""INSERT SPORT AND PLAYER"""
# Gets player info and formats into usable url
reference_num = get_ref_num(sport)
sport = get_sport_url(sport)
if "football" in sport:
    first_letter_of_last_name, first_four_letters_of_last_name, first_two_letters_of_first_name = parse_name_parts(
        name_string)
elif "hockey" in sport:
    first_letter_of_last_name, first_four_letters_of_last_name, first_five_letters_of_last_name, first_two_letters_of_first_name = parse_name_parts(name_string)
if "football" in sport:
    player_url = f"{sport}{first_letter_of_last_name}/{first_four_letters_of_last_name}{first_two_letters_of_first_name}{reference_num}.htm"
elif "hockey" in sport:
    player_url = f"{sport}{first_letter_of_last_name}/{first_five_letters_of_last_name}{first_two_letters_of_first_name}{reference_num}.html"
    print(player_url)
# Gets player team as string
team = get_team(player_url)
# Gets excel page from sports reference site and names it as First, Last %Y-%m-%d
get_excel(player_url)
# Gets the ESPN.com schedule url and open it on screen
schedule = get_schedule(team)
# Gets game conditions based on schedule (Ex: Monday game, Vs Dallas, at
# game_conditions = get_game_conditions(schedule)

"""Potential upgrades"""
# get today's date
# today = datetime.now()
# # format the date as a string
# date_string = today.strftime("%Y-%m-%d")
# # Establish file name in global scope
# excel_player_name = name_string + "_" + date_string
# # Open workbook for current player
# workbook = openpyxl.load_workbook(f'C:/Users/Patrick/Downloads/{excel_player_name}')

