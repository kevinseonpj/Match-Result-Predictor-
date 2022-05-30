import math
import json
import requests
# Multiple functions that handles different aspects of certain player's profile

api_key = "REDACTED"

# Handling Previous Matches/Match history
def match_history(league_username, server):
    # First get the Summoner ID from summoner-v4 API
    req_url = "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(server, league_username, api_key)
    req_res = requests.get(req_url)
    # Status Code Filter in case of an error either server side or api key...
    if ("200" not in str(req_res)):
        # TODO later - add some different results and response depending on the various status code returned from the request
        print("Something went wrong")
    player_data = json.loads(req_res.text)
    player_id = player_data["id"]
    print(player_id)

    #now get rest of the info

match_history("Ping Difference", "na1")