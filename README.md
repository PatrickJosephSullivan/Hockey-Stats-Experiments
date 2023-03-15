# Hockey-Stats-Experiments

A personal project to make more educated choices in sportsbetting.

CURRENT STATE OF THIS PROJECT:

The main file for running calculations is Game Condition Analysis. After the import statements, you can enter a team to pull their player info. 
It provides their shots/saves on goal on average, at home/road, in the current month, and against an opponent.

Please make sure to enter the team mascot for the team you are querying and the full team name for the opponent that day. 
EXAMPLE:

Query: "Kings"
Opponent: "Vegas Golden Knights" 

If you want to see my previously queried results you can open up the Hockey DB.db in any non-relational database system.
My program for personal use is SQLite and DBBrowser(SQLite) because of it's ease of access and gui tools.

GOALS:

Eventually, I'd like to simplify this to just inputting the day and then loop through the schedule.
Adding functionality to pull stats from the sportsbook PrizePicks.com so that it's easier to compare the lines and make quicker decisions.
