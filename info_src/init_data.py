import requests
from bs4 import BeautifulSoup

# Dict/Map of the rank to elo calculation for the purpose of numerical calculations
# Going to need a calibration function to determine the Master/GM/Chall mmr elo
rank_elo = {'IRON_IIII': 0,
            'IRON_III': 100,
            'IRON_II': 200,
            'IRON_I': 300,
            'BRONZE_IV': 400,
            'BRONZE_III': 500,
            'BRONZE_II': 600,
            'BRONZE_I': 700,
            'SILVER_IV': 800,
            'SILVER_III': 900,
            'SILVER_II': 1000,
            'SILVER_I': 1100,
            'GOLD_IV': 1200,
            'GOLD_III': 1300,
            'GOLD_II': 1400,
            'GOLD_I': 1500,
            'PLATINUM_IV': 1600,
            'PLATINUM_III': 1700,
            'PLATINUM_II': 1800,
            'PLATINUM_I': 1900,
            'DIAMOND_IV': 1600,
            'DIAMOND_III': 1700,
            'DIAMOND_II': 1800,
            'DIAMOND_I': 1900,
            'MASTER_I' : 2000,
            'GRANDMASTER_I' : 2200
            }

# Champ list update by scraping the league of legend offical website and stores
# it in a mapped/dict format
# yes, it could be created at the user info collection but I found this organization more clear in my head
def champ_list():
    url = "https://www.leagueoflegends.com/en-us/champions/"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    champ_lists = {}
    results = soup.findAll("span", {"class" : "style__Text-n3ovyt-3 gMLOLF"})

    for num, champ in enumerate(results):
        if (len(champ.text) > 0 and champ.text not in champ_lists):
            # get rid of any spaces
            champ_text = champ.text.replace(' ', '')
            # get rid of apostrophe
            if '\'' in champ.text.rstrip():
                champ_text = ''.join(champ.text.split('\''))
            # lol riot has wukong as monkey king
            if champ_text.lower() == "wukong":
                champ_text = "monkeyking"
            # 0th idx is for idxing the champs and other two slots for k/d/a average over all game, kda, and games played
            champ_lists[champ_text.lower()] = [num + 1, 0, 0, 0, 0, 0]
    return champ_lists