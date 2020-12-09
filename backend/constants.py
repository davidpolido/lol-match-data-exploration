GAME_VERSIONS_URL = "https://ddragon.leagueoflegends.com/api/versions.json"

ASSETS = [
    {
        "file_name": "champions",
        "url": "http://ddragon.leagueoflegends.com/cdn/VERSION/data/en_GB/champion.json",
        "format": "nested",
        "renames": {"key": "championId", "name": "champion"},
        "type_conversions": {"championId": "int32"},
        "relevant_columns": ["championId", "champion"],
    },
    {
        "file_name": "queues",
        "url": "http://static.developer.riotgames.com/docs/lol/queues.json",
        "format": "standard",
        "renames": {"description": "queue"},
        "type_conversions": {"queueId": "int32"},
        "relevant_columns": ["queueId", "map", "queue"],
    },
    {
        "file_name": "maps",
        "url": "http://static.developer.riotgames.com/docs/lol/maps.json",
        "format": "standard",
        "renames": {"mapName": "map"},
        "type_conversions": {"mapId": "int32"},
        "relevant_columns": ["mapId", "map", "notes"],
    },
    {
        "file_name": "runes",
        "url": "http://ddragon.leagueoflegends.com/cdn/VERSION/data/en_GB/runesReforged.json",
        "format": "runes_specific",
        "renames": {},
        "type_conversions": {"pathId": "int32", "runeId": "int32", "runeLevel": "int32"},
        "relevant_columns": ["pathId", "path", "runeId", "rune", "runeLevel"],
    },
    {
        "file_name": "summoner_spells",
        "url": "http://ddragon.leagueoflegends.com/cdn/VERSION/data/en_GB/summoner.json",
        "format": "nested",
        "renames": {"name": "summonerSpell", "key": "summonerSpellId"},
        "type_conversions": {"summonerSpellId": "int32"},
        "relevant_columns": ["summonerSpell", "summonerSpellId"],
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

