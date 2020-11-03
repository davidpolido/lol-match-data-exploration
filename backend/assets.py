import os
import json
from pathlib import Path

import requests
import pandas as pd
from dotenv import load_dotenv

from . import db
from .constants import ASSETS


BACKEND_DIR = Path(__file__).parent
ENV_PATH = (BACKEND_DIR / ".env").resolve()
load_dotenv(dotenv_path=ENV_PATH)

ASSETS_DB_PATH = os.environ["ASSETS_DB_PATH"]
ASSETS_PATH = (BACKEND_DIR / "assets").resolve()


def get_json_data_from_url(asset):
    r = requests.get(asset["url"], allow_redirects=True)
    json_data = r.json()

    return json_data


def transform_json_to_clean_df(asset, json_data):
    df = pd.DataFrame()

    # Transform into df - different format for champions.json
    if asset["is_champions"]:
        df = pd.DataFrame.from_dict(json_data["data"], orient="index").reset_index()
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


def update_all():
    print("---")
    print("Updating assets using constants.py urls...")

    # Create SQLite connection
    conn = db.create_connection(ASSETS_DB_PATH)

    for asset in ASSETS:
        json_data = get_json_data_from_url(asset)
        df = transform_json_to_clean_df(asset, json_data)

        write_to_assets(asset, json_data)
        db.write_full_table(conn, asset["file_name"], df)

        # Log file update
        print(f"Updated {asset['file_name']} asset (json & db table).")

    # Close db connection
    db.close_connection(conn)

    # Log completion
    print("---")


if __name__ == "__main__":
    update_all()
