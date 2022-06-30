import math
import json
import sys
import requests
import info_src.init_data as loldata
from datetime import datetime
from pymongo import MongoClient

# Multiple functions that handles different aspects of certain player's profile

api_key = "none"

def error_handling():
    return

# region to routing value conversion for api
def routing_values(region):
    return {
        "NA" : "americas",
        "BR" : "americas",
        "LAN" : "americas",
        "LAS" : "americas",
        "OCE" : "americas",
        "KR" : "asia",
        "JP" : "asia",
        "EUNE" : "europe",
        "EUW" : "europe",
        "TR" : "europe",
        "RU" : "europe"
    }.get(region, "None")

# epoch start time for this season/year
def epoch_start_time():
    return int(datetime(datetime.now().year, 1, 1, 0).timestamp())

# Handling Previous Matches/Match history
def get_id(league_username, server, id_type):
    # First get the Summoner ID from summoner-v4 API
    req_url = "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(server, league_username, api_key)
    req_res = requests.get(req_url)

    # Status Code Filter in case of an error either server side or api key... which shouldn't happen but... yeah
    if ("200" not in str(req_res)):
        # TODO later - add some different results and response depending on the various status code returned from the request
        print("Something went wrong")
    player_data = json.loads(req_res.text)
    # print(player_data[id_type])
    return player_data[id_type]

# Grabs previous match history for the user ID (same return as get_id)
def get_matches(id, region, queue_id, game_type, game_count, epoch_start_time):
    # queueid
    req_url = "https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?startTime={}&queue={}&type={}&start=0&count={}&api_key={}".format(region, id, epoch_start_time, queue_id, game_type, game_count, api_key)
    req_res = requests.get(req_url)

    if ("200" not in str(req_res)):
        # TODO later - add some different results and response depending on the various status code returned from the request
        print("Something went wrong")
    match_data = json.loads(req_res.text)
    print(match_data)
    print(len(match_data))
    return match_data

# takes the entire player stats from the given input matches
# Result will be in a dict form that will include the following:
# Lane played, lane wr, champs played/wr (sorted order of num of games played)
def player_stats(region, matches, player_name):
    # final returning dict
    res = {}

    # dict for lane pos to make it more readable (however, we could just mod 5 the index of the list,
    # but it is technically more accurate to get the result from the API)
    pos_map = {
        'top' : 0,
        'jungle' : 1,
        'middle' : 2, 
        'bottom' : 3,
        'utility' : 4
    }
    #Lanes played and the respective wr
    res['pos'] = [0, 0, 0, 0, 0]
    res['pos_w'] = [0, 0, 0, 0, 0]
    res['wr'] = 0
    res['champs'] = loldata.champ_list()
    
    #for all the matches that has been fed, we will collect all info needed
    for match in matches:
        print(match)
        req_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}?api_key={}".format(region, match, api_key)
        req_res = json.loads(requests.get(req_url).text)
        player_idx = 0
        # find which index the player is located (technically it is in order and within in pattern, but... yes)
        for i in range(10):
            if req_res['info']['participants'][i]['summonerName'].lower() == player_name.lower():
                player_idx = i
                break
        # increment the position played, if win then update accordingly as well
        pos_idx = pos_map[req_res['info']['participants'][player_idx]['teamPosition'].lower()] if req_res['info']['participants'][player_idx]['teamPosition'].lower() != '' else player_idx % 5
        res['pos'][pos_idx] += 1
        if req_res['info']['participants'][player_idx]['win']: 
            res['wr'] += 1
            res['pos_w'][pos_idx] += 1

        # Champion detail update

        # k / d / a total (divided at the end)
        champion_name = req_res['info']['participants'][player_idx]['championName'].lower()
        res['champs'][champion_name][1] += req_res['info']['participants'][i]['kills']
        res['champs'][champion_name][2] += req_res['info']['participants'][i]['deaths']
        res['champs'][champion_name][3] += req_res['info']['participants'][i]['assists']

        # actual k/d/a at 4th index is updated at the end

        # champion play count
        res['champs'][champion_name][5] += 1

    # win rate per role, and overall wr updated account for non players-0matches like somebody
    res['wr'] = round(res['wr'] / len(matches) * 100)
    res['pos_w'] = [round(x / (y + sys.float_info.epsilon) * 100, 2) for x, y in zip(res['pos_w'], res['pos'])]

    # Champion data updated 
    for champ in res['champs']:
        if(res['champs'][champ][5] > 0):
            res['champs'][champ][4] = round((res['champs'][champ][3] + res['champs'][champ][1]) / res['champs'][champ][2] + sys.float_info.epsilon, 2)
            res['champs'][champ][1:4] = [round(x / res['champs'][champ][5], 2) for x in res['champs'][champ][1:4]]
    # Dictionary to list -- may need to revert if do need the dict functionality
    res['top5'] = sorted(res['champs'].items(), key=lambda x: x[1][5], reverse=1)[:5]
    return res

# Combines all the functionality to some extent
def player_summary(username, region):
    #only NA1 at the moment!
    id = get_id(username, "na1", "puuid")
    matches = get_matches(id, routing_values(region), 420, "ranked", 100, epoch_start_time())
    return player_stats(routing_values(region), matches, username)

# Now we do need to process the data into mongodb and we will use it again when we are doing the prediction
# We also will run and store the training data that we will make.
def get_database():
    

    # Provide the mongodb atlas url later
    CONNECTION_STRING = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/myFirstDatabase"
    client = MongoClient(CONNECTION_STRING)
    # Create the database for our example (we will use the same database throughout the tutorial
    return client['TEST']
    
# # This is added so that many files can reuse the function get_database()
# if __name__ == "__main__":    
#     # Get the database
#     dbname = get_database()

# Some examples of the usage

# id = get_id("Ping Difference", "na1", "puuid")
# matches = get_matches(id, routing_values("NA"), 420, "ranked", 100, epoch_start_time())
# req_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}?api_key={}".format("americas", "NA1_4220235820", api_key)
# req_res = requests.get(req_url)
# req_res = json.loads(req_res.text)
# for i in range(10):
#     print(req_res['info']['participants'][i]['summonerName'])
    # if (req_res['info']['participants'][i]['summonerName'].lower() == "Ping Difference".lower()):
    #     print(req_res['info']['participants'][i]['summonerName'])
    #     print(json.loads(req_res.text)['info']['participants'][i]['teamPosition'])
    #     print(json.loads(req_res.text)['info']['participants'][i]['kills'])
    #     print(json.loads(req_res.text)['info']['participants'][i]['deaths'])
    #     print(json.loads(req_res.text)['info']['participants'][i]['assists'])
    #     print(json.loads(req_res.text)['info']['participants'][i]['lane'])
    #     print(json.loads(req_res.text)['info']['participants'][i]['championName'])
    #     print(json.loads(req_res.text)['info']['participants'][i]['win'])
    #     print('------------------------')
# print(player_stats(routing_values("NA"), matches, "ping difference"))
