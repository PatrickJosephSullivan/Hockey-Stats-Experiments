from bs4 import BeautifulSoup
import requests
import csv

url = 'https://www.espn.com/nhl/player/splits/_/id/3895074/connor-mcdavid'
response = requests.get(url)
html = response.content

soup = BeautifulSoup(html, 'html.parser')
rows = soup.find_all('tr')

with open('data.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    for row in rows:
        cells = row.find_all('td')
        row_data = []
        for cell in cells:
            row_data.append(cell.text)
        writer.writerow(row_data)
