import os
import json
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

from .db import Database
from .constants import ASSETS, GAME_VERSIONS_URL


BACKEND_DIR = Path(__file__).parent
ENV_PATH = (BACKEND_DIR / ".env").resolve()
load_dotenv(dotenv_path=ENV_PATH)

ASSETS_DB_PATH = os.environ["ASSETS_DB_PATH"]
ASSETS_PATH = (BACKEND_DIR / "assets").resolve()


def get_json_data_from_url(asset_url):
    r = requests.get(asset_url, allow_redirects=True)
    json_data = r.json()

    return json_data

def format_runes_df(json_data):
    runes = []
    for path in json_data:
        for slot in path["slots"]:
            for rune in slot["runes"]:
                rune_line = {"pathId": path["id"], 
                            "path": path["key"],
                            "runeId": rune["id"],
                            "rune": rune["name"],
                            "runeLevel": path["slots"].index(slot)
                            }
                runes.append(rune_line)

    return pd.DataFrame(runes)

def transform_json_to_clean_df(asset, json_data):
    df = pd.DataFrame()

    # Transform into df - some assets are nested > keep data only
    if asset["format"] == "nested":
        df = pd.DataFrame.from_dict(json_data["data"], orient="index").reset_index()
    elif asset["format"] == "runes_specific":
        df = format_runes_df(json_data)
    else:
        df = pd.DataFrame(json_data).reset_index()

    # Clean up df
    df = df.rename(columns=asset["renames"])
    df = df.astype(asset["type_conversions"])
    df = df[asset["relevant_columns"]]

    return df


def write_to_assets(asset, json_data):
    with open(f"{ASSETS_PATH}/{asset['file_name']}.json", "w") as outfile:
        json.dump(json_data, outfile)


def get_latest_game_version():
    r = requests.get(GAME_VERSIONS_URL, allow_redirects=True)
    game_versions = r.json()

    return game_versions[0]

def update_asset(asset_name, latest_version=get_latest_game_version()):
    asset = next((asset for asset in ASSETS if asset["file_name"] == asset_name), None)

    asset_url = asset["url"].replace("VERSION", latest_version)
    json_data = get_json_data_from_url(asset_url)
    
    df = transform_json_to_clean_df(asset, json_data)

    with Database(ASSETS_DB_PATH) as db:
            db.write_full_table(asset_name, df)

    # Log file update
    print(f"Updated {asset['file_name']} asset (json & db table).")
    

def update_all():
    print("Updating assets using constants.py urls...")

    latest_version = get_latest_game_version()

    for asset in ASSETS:
        update_asset(asset["file_name"], latest_version)

    # Log completion
    print("All assets updated")


if __name__ == "__main__":
    update_all()
