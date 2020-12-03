import os
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
from riotwatcher import LolWatcher

from .utils import retry_function

BACKEND_DIR = Path(__file__).parent
ENV_PATH = (BACKEND_DIR / ".env").resolve()
load_dotenv(dotenv_path=ENV_PATH)

API_KEY = os.environ["API_KEY"]
REGION = os.environ["REGION"]


class Requests:
    def __init__(self, api_key_override=None):
        self.api_key = API_KEY if not api_key_override else api_key_override
        self.region = REGION
        self.watcher = LolWatcher(API_KEY)

    def get_summoner(self, summoner_name):
        summoner = self.watcher.summoner.by_name(
            region=self.region, summoner_name=summoner_name
        )
        return summoner

    def get_summoners(self, summoner_names):
        if isinstance(summoner_names, str):
            summoner_names = [summoner_names]

        self.summoners = []
        for summoner_name in summoner_names:
            self.summoners.append(retry_function(self.get_summoner, [summoner_name]))

        print(f"Downloaded {len(self.summoners)} Summoner profile(s).")
        return self.summoners

    def compute_end_index(self, match_limit, begin_index):
        if match_limit and match_limit - begin_index < 100:
            return match_limit
        else:
            return None

    def get_single_matchlist(self, summoner, match_limit=None):
        """ Get list of all (or limited) matches available for a single summoner. """
        matchlist = []
        begin_index = 0
        num_matches = 1

        while begin_index < num_matches and len(matchlist) != match_limit:
            end_index = self.compute_end_index(match_limit, begin_index)

            # Get new partial_matchlist
            partial_matchlist = {}
            partial_matchlist = self.watcher.match.matchlist_by_account(
                region=self.region,
                encrypted_account_id=summoner["accountId"],
                begin_index=begin_index,
                end_index=end_index,
            )

            # Add partial to matchlist
            matchlist.extend(partial_matchlist["matches"])

            # Update begin_index & num_matches
            begin_index = partial_matchlist["endIndex"]
            num_matches = partial_matchlist["totalGames"]

        print(f"Downloaded {len(matchlist)} match ids for '{summoner['name']}'.")
        return matchlist

    def get_all_matchlists(self, match_limit=None):
        """ Get list of all (or limited) matches available for a multiple summoners. """
        matchlist = []

        for summoner in self.summoners:
            matchlist.extend(
                retry_function(self.get_single_matchlist, [summoner, match_limit])
            )
        print(f"Total downloaded match ids: {len(matchlist)}.")
        return matchlist

    def get_match_data(self, game_id):
        """ Get all data associated with a specific with a single match. """
        try:
            match_data = self.watcher.match.by_id(region=self.region, match_id=game_id)
        except ApiError as err:
            print(err.response.status_code)
        return match_data
