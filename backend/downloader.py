import os
import time
import sys
import argparse
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from .db import Database
from .requests import Requests
from .constants import TABLE_PRIMARY_KEYS, MATCH_DETAILS_KEYS


BACKEND_DIR = Path(__file__).parent
ENV_PATH = (BACKEND_DIR / ".env").resolve()
load_dotenv(dotenv_path=ENV_PATH)

DB_PATH = os.environ["NORMALIZED_DB_PATH"]


def get_unprocessed_matchlist(matchlist):
    with Database(DB_PATH) as db:
        match_details = db.read_full_table("match_details")

    unprocessed_matchlist = pd.merge(
        matchlist,
        match_details["gameId"],
        on="gameId",
        how="outer",
        indicator=True,
    ).query('_merge=="left_only"')

    unprocessed_matchlist = (
        unprocessed_matchlist.drop(columns="_merge")
        .reset_index(drop=True)
        .drop_duplicates(subset="gameId")
    )
    print(
        f"Compared DB with downloaded data: {len(unprocessed_matchlist)} new matches found."
    )
    return unprocessed_matchlist


def process_basic_match_info(match_data):
    return {key: match_data[key] for key in MATCH_DETAILS_KEYS}


def process_teams(team_obj, game_id):
    team_obj["gameId"] = game_id
    for ban_obj in team_obj["bans"]:
        ban_index = team_obj["bans"].index(ban_obj) + 1
        team_obj[f"ban#{ban_index}"] = str(ban_obj["championId"])
    team_obj.pop("bans", "")
    return team_obj


def get_clean_match_data(matchlist, r):
    match_details = []
    teams = []
    participants = []
    participant_identities = []
    counter = 1
    fail_count = 0

    game_ids = list(matchlist["gameId"])
    print(f"Getting data on {len(game_ids)} matches.")

    while len(game_ids) > 0:
        # Get full object with match data, by game id
        try:
            match_data = r.get_match_data(game_ids[0])
            match_details.append(process_basic_match_info(match_data))

            # Get teams list
            for team_obj in match_data["teams"]:
                teams.append(process_teams(team_obj, game_ids[0]))

            # Get participants list
            for participant_obj in match_data["participants"]:
                participant_obj["gameId"] = game_ids[0]
                participants.append(participant_obj)

            # Get participants_identity list
            for participant_identity_obj in match_data["participantIdentities"]:
                participant_identity_obj["gameId"] = game_ids[0]
                participant_identities.append(participant_identity_obj)

            if counter % 50 == 0:
                print(f"Processed {counter} matches.")

            counter += 1
            game_ids.pop(0)

        except Exception as e:
            print(e)
            fail_count += 1
            print(f"Error in match #{counter} (id: <{game_ids[0]})>.")
            if fail_count % 5 == 0:
                time.sleep(120)
                fail_count = 0

    # Transform lists into object of dataframes
    new_data_obj = {}
    new_data_obj["match_details"] = pd.DataFrame(match_details)
    new_data_obj["teams"] = pd.json_normalize(teams).rename(
        columns=lambda x: x.replace(".", "_")
    )
    new_data_obj["participants"] = pd.json_normalize(participants)
    new_data_obj["participant_identities"] = pd.json_normalize(participant_identities)
    print(f"Finished processing {counter-1} matches.")

    return new_data_obj


def update_df_indexes(df, table_name):
    with Database(DB_PATH) as db:
        df.index += db.read_last_index(table_name) + 1
    return df


# def save_data(data_type, df):
#     df.to_csv(f"./outputs/{data_type}.csv")
#     print(f"File on {data_type} saved!")


# def save_game_ids(df):
#     df["gameId"].drop_duplicates().reset_index().to_csv(
#         "./outputs/processedGameIds.csv"
#     )
#     print("File with processed game ids saved!")


def get_data(summoner_names, mode="update"):

    # Instantiate watcher
    r = Requests()
    summoners = r.get_summoners(summoner_names)
    matchlist = pd.DataFrame(r.get_all_matchlists())

    # Early exit if no matches can be found
    if len(matchlist) == 0:
        print("No matches available from provided Summoner(s). Exiting.")
        return

    # Check if match_details table exists in db: if not, do full download
    # TODO: Decide what to do when any of the tables are missing. Add checks here.
    # TODO: Maybe add looping to require y/n answer?
    with Database(DB_PATH) as db:
        if not db.check_if_table_exists("match_details"):
            print("No <match_details> table found in db. One will be created.")
            mode = "replace"

    # For "update" mode, get differences between matchlist and DB;
    # Other modes want full matchlist from summoners
    unprocessed_matchlist = (
        get_unprocessed_matchlist(matchlist) if mode == "update" else matchlist
    )

    # If there are no matches to get data of, exit
    if len(unprocessed_matchlist) == 0:
        print("No new matches to process from provided Summoner(s). Exiting.")
        return

    # Get all dfs (match_details, teams, participants, participant_identities)
    new_data_obj = get_clean_match_data(unprocessed_matchlist, r)

    if mode == "replace":
        # Write to DB
        for table_name in new_data_obj:
            with Database(DB_PATH) as db:
                db.write_full_table(table_name, new_data_obj[table_name])

        print("DB fully updated.")

    elif mode == "update":
        # Make indexes continue from existing ones
        for table_name in new_data_obj:
            new_data_obj[table_name] = update_df_indexes(
                new_data_obj[table_name], table_name
            )

        # Write to DB
        for table_name in new_data_obj:
            with Database(DB_PATH) as db:
                db.append_to_table(table_name, new_data_obj[table_name])

        print(f"Data on {len(new_data_obj['match_details'])} matches downloaded.")

    elif mode == "output":
        return new_data_obj


def parse_arguments():
    parser = argparse.ArgumentParser(description="Download match info from Summoners.")
    parser.add_argument(
        "-m",
        metavar="mode",
        type=str,
        default="update",
        help="the mode to run the downloader (update, replace, output)",
    )
    parser.add_argument(
        "-s",
        metavar="summoner",
        nargs="+",
        default=max,
        help="list of Summoner names",
    )

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_arguments()
    display_names = "', '".join(args.s)
    print(f"Running downloader on {args.m} mode for Summoner(s) '{display_names}'.")
    get_data(args.s, args.m)
