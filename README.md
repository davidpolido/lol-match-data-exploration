# lol-match-data-exploration

Package to download and analyse *League of Legends* match data from specific Summoners.  

## Setup:  
1) Get your api_key from https://developer.riotgames.com/ and replace the placholder with it in `.env-example` file inside the backend folder.  
2) Rename `.env-example` into `.env` in the backend folder.
  

## Usage:
Two backend methods currently implemented. Both should be run in the command line, from the root folder. 
### Update static assets for champions, queues and maps:  
    `python -m backend.assets`  

### Download all matches from specific summoners:  
    python -m backend.downloader [-m <mode>] -s <SummonerName1> <SummonerName2> ...  
The `-m` option can be used to do one of the following:  
        - `update` (default) - checks for existing data in sqlite DB and adds data for matches that are available from Riot's API but missing in the local DB.  
        - `replace` - replaces any and all existing data in sqlite DB with the data for all available matches of the requested Summoners.  
        - `output` - gets data for all available matches of the indicated Summoners and returns it (no DB writing). To be used in exploration notebooks.
