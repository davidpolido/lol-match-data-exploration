ASSETS = [
    {
        "file_name": "champions",
        "url": "http://ddragon.leagueoflegends.com/cdn/10.22.1/data/en_US/champion.json",
        "df_name": "champions_df",
        "is_champions": True,
        "renames": {"key": "championId", "name": "champion"},
        "type_conversions": {"championId": "int32"},
        "relevant_columns": ["championId", "champion"],
    },
    {
        "file_name": "queues",
        "url": "http://static.developer.riotgames.com/docs/lol/queues.json",
        "df_name": "queues_df",
        "is_champions": False,
        "renames": {"description": "queue"},
        "type_conversions": {"queueId": "int32"},
        "relevant_columns": ["queueId", "map", "queue"],
    },
    {
        "file_name": "maps",
        "url": "http://static.developer.riotgames.com/docs/lol/maps.json",
        "df_name": "maps_df",
        "is_champions": False,
        "renames": {"mapName": "map"},
        "type_conversions": {"mapId": "int32"},
        "relevant_columns": ["mapId", "map", "notes"],
    },
]

TABLE_PRIMARY_KEYS = {
    "match_details": ["gameId"],
    "teams": ["gameId", "teamId"],
    "participants": ["gameId", "participantId"],
    "participant_identities": ["gameId", "participantId"],
}

MATCH_DETAILS_KEYS = [
    "gameId",
    "platformId",
    "gameCreation",
    "gameDuration",
    "queueId",
    "mapId",
    "seasonId",
    "gameVersion",
    "gameMode",
    "gameType",
]

