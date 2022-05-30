import requests
from bs4 import BeautifulSoup


url = "https://www.leagueoflegends.com/en-us/champions/"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

champ_lists = []
results = soup.findAll("span", {"class" : "style__Text-n3ovyt-3 gMLOLF"})

for champ in results:
    if (len(champ.text) > 0 and champ.text not in champ_lists):

        champ_lists.append(champ.text.rstrip())
print(champ_lists)
print(len(champ_lists))