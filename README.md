
## Introduction ##
This program shows the current top trend 12 Youtube videos for the countries such as USA, Korea, Sweden, Canada.

1. The main page shows the top 12 Youtube videos
http://localhost:8080/

2. /region_db page shows the history of the tracked Youtube videos (videos that were displayed in the page so far)
Search country and see the history of Youtube trend videos of that country. For example, type in USA or Korea (case-sensitive)
http://localhost:8080/region_db


## Run command ##
$ python3 SI507F17_finalproject.py


## Precondition ##
1. Python ver.3 and external libraries are installed
$ pip3 install -r requirements.txt

2.Generate 'client_scret.json' from the google credential site and saves in the final_project folder(the same folder that the main program is in).
Follow the instruction in https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps#creatingcredinc.luding
Type in "http://localhost:8080/oauth2callback" in the 'Authorized redirect URLs' when creating the credentials.

3. create db, 'youtube_db'. Set this db name and user name in the db_config.py
db_config.py

db_name = "youtube_db"
db_user = 'sophiachoi'
db_password = ''

## Project Structure ##
1. SI507F17_finalproject.py
- run flask server
- request token using OAuth2
- referenced below API sites
- https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps
- https://developers.google.com/youtube/v3/docs/search/list
- access Youtube API 'https://www.googleapis.com/youtube/v3/videos'
- retrieve Trend Youtube videos

2. cache_manager.py
- set retrieved data to cache file
- cache expiration time is 30 min

3. youtube_manager.py
- Trend Manager Class provides lists of API queries and interfaces to database
- Video Class provides information about Youtube video
- RegionTrend Class provides information about the region and its trend videos

4. database_model.py
- manages two tables, Video and Region
- Video table has ID, Title, Kind, Code. Primary Key is a combination of ID and Code(region code)
- Region table has Code and Name. (Code is a region code)

3. SI507_finalproject_tests.py
- Unittest for the program