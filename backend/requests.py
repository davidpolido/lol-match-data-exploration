import os
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
from riotwatcher import LolWatcher

BACKEND_DIR = Path(__file__).parent
ENV_PATH = (BACKEND_DIR / ".env").resolve()
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.environ["API_KEY"]
REGION = os.environ["REGION"]


def instantiate_watcher():
    return LolWatcher(API_KEY)


def get_summoner(watcher, summoner_name):
    attempt = 1

    while attempt <= 5:
        try:
            return watcher.summoner.by_name(REGION, summoner_name)
        except:
            print(f"Failed download for <{summoner_name}>")
            attempt += 1
    return None


def get_summoners(watcher, summoner_names):
    summoners = []
    for summoner_name in summoner_names:
        summoners.append(get_summoner(watcher, summoner_name))

    print(f"Downloaded Summoner profile(s).")
    return summoners


def get_matchlist(watcher, summoner):
    # Get matchlist array for all summoners
    matchlist = []

    last_index = 0
    total_games = 1
    attempt = 1

    while attempt <= 5:
        try:
            while total_games > last_index:
                # Get new partial_matchlist
                partial_matchlist = {}
                partial_matchlist = watcher.match.matchlist_by_account(
                    REGION, summoner["accountId"], begin_index=last_index
                )

                # Add partial to matchlist
                matchlist.extend(partial_matchlist["matches"])

                # Update last_index & total_games
                last_index = partial_matchlist["endIndex"]
                total_games = partial_matchlist["totalGames"]

            # Transform into dataframe
            matchlist_df = pd.DataFrame(matchlist)
            matchlist_df = matchlist_df.drop(columns=["champion", "role", "lane"])

            print(f"Downloaded {len(matchlist)} match ids for '{summoner['name']}'.")
            return matchlist_df

        except:
            attempt += 1


def get_match_data(watcher, game_id):
    try:
        match_data = watcher.match.by_id(region=REGION, match_id=game_id)
    except ApiError as err:
        print(err.response.status_code)
    return match_data
